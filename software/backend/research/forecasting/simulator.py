"""Offline linear forecasting experiment; never imports the application or its DB."""

import argparse
import calendar
import csv
from datetime import UTC, datetime, timedelta
from decimal import Decimal, InvalidOperation
import json
import math
from pathlib import Path
from random import Random
from statistics import median
from typing import Any
from uuid import NAMESPACE_URL, uuid5

import numpy as np

START = datetime(2026, 1, 1, tzinfo=UTC)
RANDOMNESS = ("low", "mid", "high")
VARIATION = {"low": (0.1, 24), "mid": (0.4, 96), "high": (0.8, 192)}
METHODS = ("linear", "fixed", "mean")
INITIAL_RATE = 10.0


def instant(value: str) -> datetime:
    """Normalise an aware ISO timestamp; reject ambiguous local timestamps."""
    result = datetime.fromisoformat(value)
    if result.utcoffset() is None:
        raise ValueError("Timestamps must include a timezone")
    return result.astimezone(UTC)


def household(randomness: str = "mid", days: int = 730, seed: int = 42,
              cohort: str = "demo") -> dict[str, Any]:
    """Vary one household's usage and purchase timing, conserving exact integer Wh."""
    if randomness not in RANDOMNESS or days < 1 or cohort not in ("training", "demo"):
        raise ValueError("Unknown randomness/cohort or nonpositive duration")
    identity = f"monitor-simulator/{cohort}/{seed}"
    device_id = str(uuid5(NAMESPACE_URL, identity))
    usage_rng, timing_rng, amount_rng, reading_rng = [Random(f"{identity}/{part}")
        for part in ("usage", "purchase-timing", "purchase-amount", "readings")]
    amplitude, jitter = VARIATION[randomness]
    balance, consumed = 300_000, 0
    records, truth, purchase_attempts = [], [], []
    rate = INITIAL_RATE
    next_reading = 0
    next_purchase = 240 + round(timing_rng.uniform(-jitter, jitter))
    for hour in range(days * 24 + 1):
        at = (START + timedelta(hours=hour)).isoformat()
        if hour:
            if (hour - 1) % 24 == 0:
                rate = INITIAL_RATE * (1 + amplitude * usage_rng.uniform(-1, 1))
            used = round(rate * 1000 / 24)
            consumed += used
            balance -= used
            if hour >= next_purchase or balance < 50_000:
                gap = 240 + round(timing_rng.uniform(-jitter, jitter))
                purchase_attempts.append(dict(timestamp=at, next_gap_hours=gap))
                # Skip unnecessary purchases rather than stockpiling thousands of kWh.
                if balance <= 250_000:
                    bought = amount_rng.randint(150, 350) * 1000
                    balance += bought
                    records.append(dict(device_id=device_id, timestamp=at,
                                        event_type="top_up", value_kwh=f"{bought / 1000:.3f}"))
                next_purchase = hour + gap
        truth.append(dict(timestamp=at, balance_kwh=f"{balance / 1000:.3f}",
                          consumed_kwh=f"{consumed / 1000:.3f}"))
        if hour == next_reading:
            records.append(dict(device_id=device_id, timestamp=at,
                                event_type="balance", value_kwh=f"{balance / 1000:.3f}"))
            next_reading = hour + reading_rng.randint(12, 336)
    return dict(device_id=device_id, randomness=randomness, cohort=cohort, seed=seed,
                days=days, records=records, truth=truth, purchase_attempts=purchase_attempts,
                settings=dict(nominal_daily_kwh=INITIAL_RATE, daily_variation_fraction=amplitude,
                              purchase_gap_hours=[240 - jitter, 240 + jitter]))


def reconstruct(records: list[dict], as_of: datetime) -> tuple[list, list, list]:
    """Validate known ledger facts and derive exact consumption at actual readings."""
    if as_of.utcoffset() is None:
        raise ValueError("Forecast time must include a timezone")
    balances, purchases, identities = [], [], set()
    for row in records:
        at = instant(row["timestamp"])
        if at > as_of:
            continue
        amount = Decimal(str(row["value_kwh"]))
        kind = row["event_type"]
        if (not amount.is_finite() or amount < 0 or kind not in ("balance", "top_up")
                or (kind == "top_up" and amount == 0)):
            raise ValueError("Invalid balance or purchased kWh")
        identities.add(row["device_id"])
        (balances if kind == "balance" else purchases).append((at, amount))
    if len(identities) > 1:
        raise ValueError("A forecast must contain only one meter")
    balances.sort()
    purchases.sort()
    consumed = [Decimal(0)] if balances else []
    for (start, previous), (end, current) in zip(balances, balances[1:]):
        if end <= start:
            raise ValueError("Balance timestamps must be distinct")
        bought = sum((amount for at, amount in purchases if start < at <= end), Decimal(0))
        used = previous + bought - current
        if used < 0:
            raise ValueError("Negative inferred consumption; check missing purchases/readings")
        consumed.append(consumed[-1] + used)
    return balances, purchases, consumed


def forecast(records: list[dict], as_of: datetime, default_rate: float,
             lookback: int = 90, method: str = "linear") -> dict[str, Any]:
    """Fit only available meter observations; anchor estimates to its latest balance."""
    if lookback not in (60, 90) or method not in METHODS:
        raise ValueError("Use a 60/90-day window and linear/fixed/mean method")
    if not math.isfinite(default_rate) or default_rate < 0:
        raise ValueError("Default daily rate must be finite and nonnegative")
    try:
        balances, purchases, consumed = reconstruct(records, as_of)
        as_of = as_of.astimezone(UTC)
    except (ValueError, InvalidOperation, KeyError, TypeError) as error:
        return dict(status="inconsistent_history", reason=str(error))
    if not balances or (method == "mean" and len(balances) < 2):
        return dict(status="not_enough_data", reason="Record an actual balance first")
    selected = [(at, float(used)) for (at, _), used in zip(balances, consumed)
                if as_of - timedelta(days=lookback) <= at <= as_of]
    origin = selected[0][0] if selected else balances[-1][0]
    x = [(at - origin).total_seconds() / 86400 for at, _ in selected]
    y = [used for _, used in selected]
    rate, intercept, basis = default_rate, None, "assumed default"
    if method == "fixed":
        rate, basis = INITIAL_RATE, "fixed 10 comparator"
    elif method == "mean":
        rate = float(consumed[-1]) / ((balances[-1][0] - balances[0][0]).total_seconds() / 86400)
        basis = "all-history mean"
    elif len(selected) >= 2:
        # Subtracting a constant preserves the slope and makes zero recent use exact.
        coefficients = np.linalg.lstsq(np.column_stack((x, np.ones(len(x)))),
                                       np.asarray(y) - y[0], rcond=None)[0]
        rate, intercept = map(float, coefficients)
        intercept += y[0]
        if rate < -1e-9:
            return dict(status="inconsistent_history", reason="Negative fitted usage")
        rate, basis = max(0.0, rate), f"personal linear ({lookback}d)"
    latest_at, latest_balance = balances[-1]
    later = sum((amount for at, amount in purchases if latest_at < at <= as_of), Decimal(0))
    elapsed = (as_of - latest_at).total_seconds() / 86400
    balance = max(0.0, float(latest_balance + later) - rate * elapsed)
    return dict(status="available", basis=basis, rate=rate, balance=balance,
                remaining_days=balance / rate if rate else None,
                consumption_30=rate * 30, top_up_30=max(0.0, rate * 30 - balance),
                intercept=intercept, origin=origin.isoformat(), x=x, y=y,
                point_times=[at.isoformat() for at, _ in selected],
                latest_at=latest_at.isoformat(), latest_balance=float(latest_balance))


def calibrate() -> dict[str, Any]:
    """Freeze a scalar from separate training ledgers, never demo truth or errors."""
    training = []
    for seed in range(9173, 9178):
        data = household("mid", days=90, seed=seed, cohort="training")
        result = forecast(data["records"], START + timedelta(days=90), INITIAL_RATE, method="mean")
        if result["status"] == "inconsistent_history":
            raise ValueError("Invalid training ledger")
        if result["status"] == "available":
            training.append(dict(device_id=data["device_id"], seed=seed, rate=result["rate"]))
    return dict(default_rate=median(row["rate"] for row in training) if training else INITIAL_RATE,
                initial_rate=INITIAL_RATE, seed=9173, days=90, training=training)


class Simulation:
    """Reveal a single household chronologically; retain immutable forecast snapshots."""

    def __init__(self, data: dict, default_rate: float, lookback: int = 90) -> None:
        self.data, self.default_rate, self.lookback = data, default_rate, lookback
        self.day, self.cursor = 0, 0
        self.records: list[dict] = []
        self.errors: list[dict] = []
        self.months: list[dict] = []
        self.estimates: list[dict] = []

    @property
    def now(self) -> datetime:
        """Current virtual UTC date, not wall-clock time."""
        return START + timedelta(days=self.day)

    def current(self, method: str = "linear", at: datetime | None = None) -> dict:
        """Recompute from surviving known observations without touching scores."""
        return forecast(self.records, at or self.now, self.default_rate, self.lookback, method)

    def _ingest(self, row: dict) -> None:
        """Score a new balance before assimilation; known same-time purchases arrive first."""
        at = instant(row["timestamp"])
        if row["event_type"] == "balance":
            if any(r["event_type"] == "balance" and instant(r["timestamp"]) == at for r in self.records):
                return
            for method in METHODS:
                result = self.current(method, at)
                predicted = result.get("balance")
                self.errors.append(dict(timestamp=at.isoformat(), method=method,
                                        basis=result.get("basis", result["status"]),
                                        predicted=predicted, actual=float(row["value_kwh"]),
                                        absolute_error=None if predicted is None else abs(predicted - float(row["value_kwh"])),
                                        error=None if predicted is None else predicted - float(row["value_kwh"])))
        self.records.append(dict(row))

    def _month_end(self, at: datetime) -> None:
        """Issue forecasts on the last calendar day's 00:00 UTC, before its reading."""
        if at.day != calendar.monthrange(at.year, at.month)[1]:
            return
        truth = self.data["truth"][self.day * 24]
        for method in METHODS:
            result = self.current(method, at)
            balance = result.get("balance")
            error = None if balance is None else balance - float(truth["balance_kwh"])
            self.months.append(dict(issued_at=at.isoformat(), issued_day=self.day,
                                    method=method, basis=result.get("basis", result["status"]),
                                    balance_error=error, absolute_balance_error=None if error is None else abs(error),
                                    forecast_30_kwh=result.get("consumption_30"),
                                    origin_consumed_kwh=float(truth["consumed_kwh"])))

    def advance(self) -> bool:
        """Advance one day, revealing events in timestamp order without future access."""
        if self.day >= self.data["days"]:
            return False
        self.day += 1
        incoming = []
        while self.cursor < len(self.data["records"]):
            row = self.data["records"][self.cursor]
            if instant(row["timestamp"]) > self.now:
                break
            incoming.append(row)
            self.cursor += 1
        for row in incoming:
            if instant(row["timestamp"]) < self.now or row["event_type"] == "top_up":
                self._ingest(row)
        self._month_end(self.now)
        for row in incoming:
            if instant(row["timestamp"]) == self.now and row["event_type"] == "balance":
                self._ingest(row)
        result = self.current()
        self.estimates.append(dict(timestamp=self.now.isoformat(), balance=result.get("balance")))
        return True

    def record_balance(self) -> None:
        """Simulate a user recording the actual balance at the current virtual instant."""
        self._ingest(dict(device_id=self.data["device_id"], timestamp=self.now.isoformat(),
                          event_type="balance", value_kwh=self.data["truth"][self.day * 24]["balance_kwh"]))

    def delete_latest_balance(self) -> None:
        """Delete only a ledger observation; never alter truth, prior forecasts or scores."""
        positions = [i for i, row in enumerate(self.records) if row["event_type"] == "balance"]
        if positions:
            self.records.pop(positions[-1])

    def monthly_results(self) -> list[dict]:
        """Score issued horizons only once their target time has actually been revealed."""
        rows = []
        for issued in self.months:
            row = dict(issued)
            target = row["issued_day"] + 30
            row["consumption_error"] = None
            row["absolute_consumption_error"] = None
            row["horizon_status"] = "unavailable" if row["forecast_30_kwh"] is None else "pending"
            if target <= self.day and row["forecast_30_kwh"] is not None:
                actual = float(self.data["truth"][target * 24]["consumed_kwh"]) - row["origin_consumed_kwh"]
                row["consumption_error"] = row["forecast_30_kwh"] - actual
                row["absolute_consumption_error"] = abs(row["consumption_error"])
                row["horizon_status"] = "scored"
            rows.append(row)
        return rows


def replay(data: dict, default_rate: float, lookback: int = 90) -> Simulation:
    """Run the identical GUI engine without waiting for the wall-clock timer."""
    simulation = Simulation(data, default_rate, lookback)
    while simulation.advance():
        pass
    return simulation


def metrics(errors: list[float | None]) -> dict[str, Any]:
    """Summarise actual out-of-sample errors in kWh, never fitted residuals."""
    values = [value for value in errors if value is not None]
    return dict(scored=len(values), unavailable=len(errors) - len(values),
                mae=sum(abs(v) for v in values) / len(values) if values else None,
                bias=sum(values) / len(values) if values else None)


def summary(simulation: Simulation) -> dict[str, Any]:
    """Separate reading errors from month-end current and matured horizon errors."""
    result = {}
    cold_instants = {row["timestamp"] for row in simulation.errors
                     if row["method"] == "linear" and row["basis"] == "assumed default"}
    for method in METHODS:
        months = [row for row in simulation.monthly_results() if row["method"] == method]
        horizon = metrics([row["consumption_error"] for row in months])
        horizon["pending"] = sum(row["horizon_status"] == "pending" for row in months)
        horizon["unavailable"] -= horizon["pending"]
        result[method] = dict(readings=metrics([row["error"] for row in simulation.errors
                                              if row["method"] == method]),
                              cold_start=metrics([row["error"] for row in simulation.errors
                                                  if row["method"] == method and row["timestamp"] in cold_instants]),
                              month_end_balance=metrics([row["balance_error"] for row in months]),
                              consumption_30=horizon)
    return result


def draw(simulation: Simulation, axes: Any) -> None:
    """Draw only revealed truth; dotted future curves assume no further purchases."""
    import matplotlib.dates as dates

    for axis in axes:
        axis.clear()
    truth = simulation.data["truth"][:simulation.day * 24 + 1]
    times = [instant(row["timestamp"]) for row in truth]
    axes[0].plot(times, [float(row["balance_kwh"]) for row in truth], color="0.65",
                 label="Actual balance (synthetic)")
    result = simulation.current()
    try:
        balances, purchases, consumed = reconstruct(simulation.records, simulation.now)
    except (ValueError, InvalidOperation, KeyError, TypeError):
        balances, purchases, consumed = [], [], []
    offset, first_hour = 0.0, 0
    if balances:
        first_hour = round((balances[0][0] - START).total_seconds() / 3600)
        offset = float(truth[first_hour]["consumed_kwh"])
        axes[0].scatter([at for at, _ in balances], [float(v) for _, v in balances],
                        s=22, color="#005aae", label="Recorded balance", zorder=4)
        axes[1].plot([at for at, _ in balances], list(map(float, consumed)), "o--",
                     color="#005aae", markersize=4, label="Recorded consumption (inferred between readings)")
    axes[1].plot(times[first_hour:], [float(row["consumed_kwh"]) - offset for row in truth[first_hour:]],
                 color="0.65", label="Actual consumption (synthetic)")
    if purchases:
        axes[0].scatter([at for at, _ in purchases], [0.04] * len(purchases), marker="^",
                        transform=axes[0].get_xaxis_transform(), color="#007782",
                        label="Top-ups")
    estimates = [row for row in simulation.estimates if row["balance"] is not None]
    if estimates:
        axes[0].plot([instant(row["timestamp"]) for row in estimates],
                     [row["balance"] for row in estimates], color="#007782", label="Estimated balance")
    if result["status"] == "available":
        future = [simulation.now + timedelta(days=day) for day in range(31)]
        axes[0].plot(future, [max(0, result["balance"] - result["rate"] * day) for day in range(31)],
                     ":", color="#005aae", linewidth=2, label="30-day forecast (no future top-ups)")
        elapsed = (simulation.now - instant(result["latest_at"])).total_seconds() / 86400
        anchor = float(consumed[-1]) + result["rate"] * elapsed
        axes[1].plot(future, [anchor + result["rate"] * day for day in range(31)],
                     ":", color="#005aae", linewidth=2, label="30-day usage forecast")
    for axis, label in zip(axes, ("Balance (kWh)", "Total consumption (kWh)")):
        axis.set_ylabel(label)
        window_start = max(START, simulation.now - timedelta(days=simulation.lookback))
        axis.axvspan(window_start, simulation.now, color="#f28e2b", alpha=0.15,
                     label=f"{simulation.lookback}-day context window", zorder=0)
        axis.axvline(simulation.now, color="0.35", linestyle=":", linewidth=1)
        axis.grid(alpha=0.2)
        axis.legend(loc="upper left", fontsize=7)
    locator = dates.AutoDateLocator(tz=UTC)
    axes[1].xaxis.set_major_locator(locator)
    axes[1].xaxis.set_major_formatter(dates.ConciseDateFormatter(locator, tz=UTC))
    axes[1].set_xlabel("Time (UTC) · vertical line = now")


class SimulatorWindow:
    """A small native Matplotlib window sharing the exact headless replay engine."""

    def __init__(self, arguments: argparse.Namespace, calibration: dict) -> None:
        import matplotlib.pyplot as plt
        from matplotlib.widgets import Button, Slider

        self.arguments, self.calibration = arguments, calibration
        self.level, self.playing = arguments.randomness, False
        with plt.rc_context({"toolbar": "None"}):
            self.figure, self.axes = plt.subplots(2, 1, figsize=(12, 8.5), sharex=True)
        self.figure.subplots_adjust(left=0.08, right=0.97, top=0.79, bottom=0.23, hspace=0.20)
        self.figure.canvas.manager.set_window_title("Monitor forecasting research — synthetic data only")
        self.info = self.figure.text(0.08, 0.97, "", va="top", fontsize=10)
        self.values = {}
        headings = (("balance", "Estimated balance"), ("remaining_days", "Days remaining"),
                    ("consumption_30", "Predicted monthly requirement (30 days)"))
        for index, (key, label) in enumerate(headings):
            x = 0.08 + index * 0.30
            self.figure.text(x, 0.91, label, fontsize=11, color="0.35")
            self.values[key] = self.figure.text(x, 0.86, "—", fontsize=19, color="#005aae")
        self.buttons = {}
        actions = (("play", "Play", self.toggle), ("reset", "Reset", self.reset))
        for index, (key, label, callback) in enumerate(actions):
            button = Button(self.figure.add_axes((0.08 + index * 0.16, 0.065, 0.14, 0.045)), label)
            button.on_clicked(callback)
            self.buttons[key] = button
        self.randomness = Slider(self.figure.add_axes((0.53, 0.08, 0.40, 0.025)),
                                 "Randomness", 0, 2, valstep=1, valinit=RANDOMNESS.index(self.level))
        self.randomness.valtext.set_visible(False)
        for index, label in enumerate(("Low", "Mid", "High")):
            self.randomness.ax.text(index / 2, -0.8, label, ha="center", va="top",
                                    transform=self.randomness.ax.transAxes, fontsize=10)
        self.randomness.on_changed(self.change_randomness)
        self.timer = self.figure.canvas.new_timer(interval=round(arguments.seconds_per_day * 1000))
        self.timer.add_callback(self.tick)
        self.figure.canvas.mpl_connect("close_event", lambda event: self.timer.stop())
        self.reset()

    def reset(self, event: Any = None) -> None:
        """Restart with the same seed/prior and explicitly record the known starting balance."""
        self.playing = False
        self.timer.stop()
        self.buttons["play"].label.set_text("Play")
        data = household(self.level, self.arguments.days, self.arguments.seed)
        self.simulation = Simulation(data, self.calibration["default_rate"], self.arguments.lookback)
        self.simulation.record_balance()
        self.render()

    def toggle(self, event: Any = None) -> None:
        """Play/pause without changing the frozen model or virtual dates."""
        self.playing = not self.playing
        self.buttons["play"].label.set_text("Pause" if self.playing else "Play")
        if self.playing:
            self.timer.start()
        else:
            self.timer.stop()
        self.figure.canvas.draw_idle()

    def change_randomness(self, value: float) -> None:
        """Restart when variation changes, without rewriting an already scored history."""
        level = RANDOMNESS[int(value)]
        if level != self.level:
            self.level = level
            self.reset()

    def tick(self) -> None:
        """Reveal one fictional day per timer callback, stopping cleanly at the end."""
        if not self.playing:
            return
        if self.simulation.advance():
            self.render()
        else:
            self.toggle()

    def render(self) -> None:
        """Show only three planning estimates, a compact date/source and two graphs."""
        simulation = self.simulation
        draw(simulation, self.axes)
        result = simulation.current()
        source = "Press Play to reveal a balance before predicting."
        displays = dict(balance="—", remaining_days="—", consumption_30="—")
        if result["status"] == "available":
            displays = dict(balance=f"{result['balance']:.1f} kWh",
                            remaining_days="No finite run-out" if result["remaining_days"] is None else f"{result['remaining_days']:.1f}",
                            consumption_30=f"{result['consumption_30']:.1f} kWh")
            basis = "Assumed default" if result["basis"] == "assumed default" else "Based on recorded usage"
            source = f"{basis} · {result['rate']:.2f} kWh/day"
        elif result["status"] == "inconsistent_history":
            source = "Inconsistent history: " + result["reason"]
        for key, text in self.values.items():
            text.set_text(displays[key])
        self.info.set_text(f"Synthetic demo · {simulation.now:%Y-%m-%d} UTC · day {simulation.day}/{self.arguments.days} · {source}")
        self.figure.canvas.draw_idle()


def export(arguments: argparse.Namespace, calibration: dict) -> dict:
    """Compare all randomness levels; retain detailed errors outside the simple GUI."""
    import matplotlib.pyplot as plt

    arguments.output.mkdir(parents=True, exist_ok=True)
    results = {}
    for level in RANDOMNESS:
        data = household(level, arguments.days, arguments.seed)
        simulation = replay(data, calibration["default_rate"], arguments.lookback)
        results[level] = summary(simulation)
        figure, axes = plt.subplots(2, 1, figsize=(13, 9), sharex=True, layout="constrained")
        try:
            draw(simulation, axes)
            figure.suptitle(f"{level.title()} randomness · {arguments.days} days · {arguments.lookback}d lookback · synthetic only")
            figure.savefig(arguments.output / f"{level}.png", dpi=140)
        finally:
            plt.close(figure)
        for suffix, rows in (("monthly", simulation.monthly_results()), ("readings", simulation.errors)):
            if rows:
                with (arguments.output / f"{level}-{suffix}.csv").open("w", newline="", encoding="utf-8") as stream:
                    writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
                    writer.writeheader()
                    writer.writerows(rows)
    manifest = dict(days=arguments.days, lookback=arguments.lookback, seed=arguments.seed,
                    randomness={name: dict(daily_fraction=values[0], purchase_jitter_hours=values[1])
                                for name, values in VARIATION.items()},
                    calibration=calibration, interval="(previous, current]", units="kWh",
                    month_end="00:00 UTC last calendar day; before reading", error="prediction minus truth",
                    horizon="30 days; score only when revealed; no assumed future purchases")
    for name, value in (("manifest", manifest), ("summary", results)):
        (arguments.output / f"{name}.json").write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return results


def main() -> None:
    """Launch the native GUI or a deterministic fast headless review run."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--days", type=int, default=730)
    parser.add_argument("--lookback", type=int, choices=(60, 90), default=90)
    parser.add_argument("--seconds-per-day", type=float, default=0.1)
    parser.add_argument("--randomness", choices=RANDOMNESS, default="mid")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--output", type=Path, default=Path(__file__).parent / "out" / "randomness")
    arguments = parser.parse_args()
    if arguments.days < 1 or not math.isfinite(arguments.seconds_per_day) or arguments.seconds_per_day < 0.1:
        parser.error("days must be positive and seconds-per-day finite and at least 0.1")
    import os
    os.environ.setdefault("MPLCONFIGDIR", str(arguments.output / ".matplotlib"))
    import matplotlib
    matplotlib.use("Agg" if arguments.headless else "TkAgg")
    calibration = calibrate()
    if arguments.headless:
        results = export(arguments, calibration)
        print(f"Frozen training default: {calibration['default_rate']:.3f} kWh/day")
        for level, scores in results.items():
            print(level, json.dumps(scores["linear"]))
        print(f"Saved plots and error reports to {arguments.output}")
    else:
        import matplotlib.pyplot as plt
        window = SimulatorWindow(arguments, calibration)
        plt.show()
        window.timer.stop()


if __name__ == "__main__":
    main()
