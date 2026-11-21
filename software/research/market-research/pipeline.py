"""Set up or run a bounded, resumable public-site research crawl."""

import argparse
from collections import Counter, deque
from contextlib import contextmanager
from dataclasses import dataclass
from email.utils import parsedate_to_datetime
import hashlib
from html.parser import HTMLParser
import http.client
import ipaddress
import json
import math
import os
from pathlib import Path
import re
import socket
import ssl
import sys
from tempfile import NamedTemporaryFile, TemporaryFile
import time
from typing import Any, Iterator
from urllib.parse import quote, unquote, urljoin, urlsplit, urlunsplit


WORKSPACE = Path(__file__).resolve().parent
SEED_TEMPLATE = (
    "# One public HTTP(S) starting URL per line.\n"
    "# Blank lines and lines beginning with # are ignored.\n"
)
USER_AGENT = "MonitorResearchBot/1.0 (+https://monitor.roventics.com/)"
MAX_ATTEMPTS = 2
MAX_REDIRECTS = 5
EMAIL_PATTERN = re.compile(r"[A-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Z0-9](?:[A-Z0-9.-]*[A-Z0-9])?\.[A-Z]{2,}", re.I)


class CrawlStop(Exception):
    """A safe reason to defer/stop a resource, without exposing its URL."""


def normalize_url(value: str, base: str = "") -> str:
    value = urljoin(base, value.strip())
    if any(ord(character) < 33 or ord(character) == 127 for character in value):
        raise ValueError("Invalid URL syntax.")
    parsed = urlsplit(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("Only HTTP(S) resource URLs are supported.")
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("URLs with credentials are not supported.")
    host = parsed.hostname.encode("idna").decode("ascii").lower().rstrip(".")
    if not host or "%" in host or "\\" in value:
        raise ValueError("Invalid URL host.")
    port = parsed.port
    if port is not None and not 1 <= port <= 65535:
        raise ValueError("Invalid URL port.")
    authority = f"[{host}]" if ":" in host else host
    if port is not None and port != (443 if parsed.scheme == "https" else 80):
        authority += f":{port}"
    path = quote(parsed.path or "/", safe="/%:@!$&'()*+,;=-._~")
    query = quote(parsed.query, safe="/%?:@!$&'()*+,;=-._~[]")
    return urlunsplit((parsed.scheme, authority, robots_path(path), robots_path(query), ""))


def read_seeds(path: Path) -> list[str]:
    seeds: list[str] = []
    try:
        with path.open(encoding="utf-8-sig") as source:
            for number, line in enumerate(source, 1):
                if not line.strip() or line.lstrip().startswith("#"):
                    continue
                try:
                    url = normalize_url(line.strip())
                except ValueError:
                    raise ValueError(f"Invalid seed URL at line {number}.") from None
                if url not in seeds:
                    seeds.append(url)
    except UnicodeError:
        raise ValueError("Seed file must be UTF-8 text.") from None
    if not seeds:
        raise ValueError("Seed file has no starting URLs.")
    return seeds


class PageText(HTMLParser):
    """Extract visible text and navigation without executing downloaded content."""

    def __init__(self, url: str) -> None:
        super().__init__(convert_charrefs=True)
        self.base = url
        self.base_seen = False
        self.hidden: list[str] = []
        self.text: list[str] = []
        self.links: list[str] = []
        self.emails: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag in {"script", "style", "noscript", "template"}:
            self.hidden.append(tag)
        if self.hidden:
            return
        if tag == "base" and not self.base_seen and values.get("href"):
            try:
                self.base = normalize_url(values["href"] or "", self.base)
                self.base_seen = True
            except ValueError:
                pass
        href = values.get("href") if tag in {"a", "area"} else None
        if tag in {"iframe", "embed", "object"}:
            href = values.get("src") or values.get("data")
        if not href:
            return
        if href.lower().startswith("mailto:"):
            self.emails.update(match.lower() for match in EMAIL_PATTERN.findall(unquote(href.split("?", 1)[0][7:])))
            return
        try:
            url = normalize_url(href, self.base)
            if url not in self.links:
                self.links.append(url)
        except ValueError:
            pass

    def handle_endtag(self, tag: str) -> None:
        if self.hidden and tag == self.hidden[-1]:
            self.hidden.pop()
        if not self.hidden:
            self.text.append(" ")

    def handle_data(self, data: str) -> None:
        if not self.hidden:
            self.text.append(data)


@dataclass
class RobotPolicy:
    rules: list[tuple[str, bool]]
    delay: float = 0.0

    def allows(self, url: str) -> bool:
        parsed = urlsplit(url)
        path = parsed.path + ("?" + parsed.query if parsed.query else "")
        path = robots_path(path)
        matches: list[tuple[int, bool]] = []
        for rule, allow in self.rules:
            end = rule.endswith("$")
            pattern = rule[:-1] if end else rule
            expression = "^" + ".*".join(re.escape(part) for part in pattern.split("*"))
            if re.search(expression + ("$" if end else ""), path):
                matches.append((len(pattern.replace("*", "")), allow))
        return max(matches, default=(0, True))[1]


def robots_path(value: str) -> str:
    encoded = quote(value, safe="/%?:@!$&'()*+,;=-._~[]")
    def normalize(match: re.Match[str]) -> str:
        character = chr(int(match[0][1:], 16))
        return character if character.isascii() and (character.isalnum() or character in "-._~") else match[0].upper()
    return re.sub(r"%[a-fA-F0-9]{2}", normalize, encoded)


def parse_robots(text: str) -> RobotPolicy:
    """Merge matching groups and use longest path matches, including * and $."""
    groups: list[tuple[list[str], list[tuple[str, bool]], float]] = []
    agents: list[str] = []
    rules: list[tuple[str, bool]] = []
    delay = 0.0
    directives = False
    for line in [*text.splitlines(), "User-agent: end-of-input"]:
        key, separator, value = line.split("#", 1)[0].partition(":")
        if not separator:
            continue
        key, value = key.strip().lower(), value.strip()
        if key == "user-agent":
            if directives:
                groups.append((agents, rules, delay))
                agents, rules, delay, directives = [], [], 0.0, False
            agents.append(value.lower())
        elif agents:
            directives = True
            if key in {"allow", "disallow"} and value:
                rules.append((robots_path(value), key == "allow"))
            try:
                if key == "crawl-delay":
                    number = float(value)
                    if math.isfinite(number) and number > 0:
                        delay = max(delay, number)
                elif key == "request-rate":
                    requests, seconds = (int(part) for part in value.split("/"))
                    if requests > 0 and seconds > 0:
                        delay = max(delay, seconds / requests)
            except ValueError:
                pass
    ranked = [(max((len(agent) if agent != "*" else 0 for agent in names
                    if agent == "*" or agent in USER_AGENT.lower()), default=-1), lines, pause)
              for names, lines, pause in groups]
    best = max((rank for rank, _, _ in ranked), default=-1)
    if best < 0:
        return RobotPolicy([])
    return RobotPolicy([rule for rank, lines, _ in ranked if rank == best for rule in lines],
                       max((pause for rank, _, pause in ranked if rank == best), default=0.0))


def public_addresses(host: str, port: int) -> list[tuple[Any, ...]]:
    if host == "localhost" or host.endswith((".localhost", ".local")):
        raise CrawlStop("non_public_target")
    addresses = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    if not addresses:
        raise CrawlStop("dns_unavailable")
    for _, _, _, _, address in addresses:
        ip = ipaddress.ip_address(address[0])
        if not ip.is_global or ip.is_multicast or ip.is_reserved:
            raise CrawlStop("non_public_target")
    return sorted(addresses, key=lambda item: item[0] != socket.AF_INET)


def request_resource(url: str, timeout: float, limit: int) -> tuple[int, dict[str, str], bytes]:
    """Connect to a checked IP directly; TLS still authenticates the URL hostname."""
    parsed = urlsplit(url)
    host = parsed.hostname or ""
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    if port != (443 if parsed.scheme == "https" else 80):
        raise CrawlStop("nonstandard_port")
    started = time.monotonic()
    family, kind, protocol, _, address = public_addresses(host, port)[0]
    connection = http.client.HTTPConnection(host, port, timeout=timeout)
    try:
        connection.sock = socket.socket(family, kind, protocol)
        connection.sock.settimeout(max(0.001, timeout - (time.monotonic() - started)))
        connection.sock.connect(address)
        if parsed.scheme == "https":
            connection.sock = ssl.create_default_context().wrap_socket(connection.sock, server_hostname=host)
        path = parsed.path + ("?" + parsed.query if parsed.query else "")
        connection.request("GET", path, headers={"User-Agent": USER_AGENT, "Accept-Encoding": "identity", "Connection": "close"})
        with http.client.HTTPResponse(connection.sock, method="GET") as response:
            response.begin()
            headers = {key.lower(): value for key, value in response.getheaders()}
            if headers.get("content-encoding", "identity").lower() not in {"identity", ""}:
                raise CrawlStop("encoded_response_unsupported")
            if headers.get("content-length", "").isdigit() and int(headers["content-length"]) > limit:
                raise CrawlStop("resource_too_large")
            body = bytearray()
            while len(body) <= limit:
                remaining = timeout - (time.monotonic() - started)
                if remaining <= 0:
                    raise TimeoutError
                connection.sock.settimeout(remaining)
                chunk = response.read1(min(65536, limit + 1 - len(body)))
                if not chunk:
                    break
                body.extend(chunk)
            if len(body) > limit:
                raise CrawlStop("resource_too_large")
            return response.status, headers, bytes(body)
    finally:
        connection.close()


class Fetcher:
    def __init__(self, args: argparse.Namespace, hosts: set[str], next_request_at: dict[str, float], robots: dict[str, Any]) -> None:
        self.args = args
        self.hosts = hosts
        self.requests = 0
        self.last: dict[str, float] = {}
        self.policies: dict[str, RobotPolicy | str] = {}
        self.next_request_at = next_request_at
        self.robots = robots

    def request(self, url: str, delay: float = 0.0, limit: int | None = None) -> tuple[int, dict[str, str], bytes]:
        if self.requests >= self.args.max_requests:
            raise CrawlStop("request_budget")
        host = urlsplit(url).hostname or ""
        if host not in self.hosts:
            raise CrawlStop("scope")
        wait = max(max(self.args.delay, delay) - (time.monotonic() - self.last.get(host, -math.inf)),
                   self.next_request_at.get(host, 0.0) - time.time())
        if wait > 30:
            raise CrawlStop("rate_deferred")
        if wait > 0:
            time.sleep(wait)
        self.requests += 1
        try:
            result = request_resource(url, self.args.request_timeout, limit or self.args.max_bytes)
            status, headers, _ = result
            if status in {429, 503}:
                retry = headers.get("retry-after", "")
                until = time.time() + 60
                try:
                    until = time.time() + int(retry) if retry.isdigit() else parsedate_to_datetime(retry).timestamp()
                except (ValueError, TypeError, OverflowError):
                    pass
                self.next_request_at[host] = max(self.next_request_at.get(host, 0.0), until)
            return result
        finally:
            self.last[host] = time.monotonic()
            self.next_request_at[host] = max(self.next_request_at.get(host, 0.0), time.time() + max(self.args.delay, delay))

    def policy(self, url: str) -> RobotPolicy:
        parsed = urlsplit(url)
        origin = urlunsplit((parsed.scheme, parsed.netloc, "", "", ""))
        cached = self.robots.get(origin)
        if origin not in self.policies and cached and 0 <= time.time() - cached["checked_at"] < 86400:
            self.policies[origin] = RobotPolicy(cached["rules"], cached["delay"])
        if origin not in self.policies:
            current = origin + "/robots.txt"
            seen: set[str] = set()
            try:
                for _ in range(MAX_REDIRECTS + 1):
                    if current in seen:
                        raise CrawlStop("robots_redirect_loop")
                    seen.add(current)
                    status, headers, body = self.request(current, limit=512 * 1024)
                    if status in {301, 302, 303, 307, 308}:
                        target = normalize_url(headers.get("location", ""), current)
                        if urlsplit(current).scheme == "https" and urlsplit(target).scheme != "https":
                            raise CrawlStop("https_downgrade")
                        current = target
                        continue
                    if status in {404, 410}:
                        self.policies[origin] = RobotPolicy([])
                    elif status == 200:
                        self.policies[origin] = parse_robots(body.decode("utf-8", errors="replace"))
                    elif status in {401, 403}:
                        self.policies[origin] = RobotPolicy([("/", False)])
                    else:
                        raise CrawlStop("robots_unavailable")
                    break
                else:
                    raise CrawlStop("robots_redirect_limit")
            except CrawlStop as error:
                if str(error) == "request_budget":
                    raise
                self.policies[origin] = str(error)
            except (OSError, ValueError, http.client.HTTPException):
                self.policies[origin] = "robots_unavailable"
            policy = self.policies[origin]
            if isinstance(policy, RobotPolicy):
                self.robots[origin] = {"rules": policy.rules, "delay": policy.delay, "checked_at": time.time()}
                host = parsed.hostname or ""
                self.next_request_at[host] = max(self.next_request_at.get(host, 0.0), time.time() + policy.delay)
        policy = self.policies[origin]
        if isinstance(policy, str):
            raise CrawlStop(policy)
        return policy


def atomic_write(path: Path, content: bytes) -> None:
    path = workspace_path(str(path))
    with NamedTemporaryFile(dir=path.parent, delete=False) as temporary:
        name = Path(temporary.name)
        try:
            temporary.write(content)
            temporary.flush()
            os.fsync(temporary.fileno())
        except BaseException:
            temporary.close()
            name.unlink(missing_ok=True)
            raise
    try:
        os.replace(name, path)
    finally:
        name.unlink(missing_ok=True)


def save_state(path: Path, state: dict[str, Any]) -> None:
    atomic_write(path, json.dumps(state, ensure_ascii=False, indent=2).encode("utf-8"))


def add_node(state: dict[str, Any], url: str, parent: str = "", hops: int = 0) -> None:
    node = state["nodes"].setdefault(url, {"status": "pending", "reason": "", "attempts": 0,
                                          "parents": [], "links": [], "redirect_hops": hops})
    node["redirect_hops"] = min(node["redirect_hops"], hops)
    if parent and parent not in node["parents"]:
        node["parents"].append(parent)


def load_state(path: Path) -> dict[str, Any]:
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
        if state["version"] != 1 or not isinstance(state["seeds"], list) or not state["seeds"] or not isinstance(state["nodes"], dict):
            raise ValueError
        backoffs = state.get("next_request_at", {})
        if not isinstance(backoffs, dict) or any(not isinstance(host, str) or type(value) not in {int, float}
                                                or not math.isfinite(value) or value < 0 for host, value in backoffs.items()):
            raise ValueError
        policies = state.get("robots", {})
        if not isinstance(policies, dict):
            raise ValueError
        for origin, policy in policies.items():
            if (normalize_url(origin).rstrip("/") != origin or not isinstance(policy["rules"], list)
                or any(not isinstance(rule, list) or len(rule) != 2 or not isinstance(rule[0], str)
                       or type(rule[1]) is not bool for rule in policy["rules"])):
                raise ValueError
            for key in ("delay", "checked_at"):
                if type(policy[key]) not in {int, float} or not math.isfinite(policy[key]) or policy[key] < 0:
                    raise ValueError
        for seed in state["seeds"]:
            if normalize_url(seed) != seed or seed not in state["nodes"]:
                raise ValueError
        for url, node in state["nodes"].items():
            if (normalize_url(url) != url or node["status"] not in {"pending", "fetched", "redirect", "failed", "blocked"}
                or type(node["attempts"]) is not int or not 0 <= node["attempts"] <= MAX_ATTEMPTS
                or not isinstance(node["reason"], str) or type(node["redirect_hops"]) is not int
                or node["redirect_hops"] < 0):
                raise ValueError
            for key in ("links", "parents"):
                if not isinstance(node[key], list) or not all(isinstance(link, str) and link in state["nodes"] for link in node[key]):
                    raise ValueError
            if node["status"] == "redirect" and len(node["links"]) != 1:
                raise ValueError
            if node["status"] == "pending" and node["attempts"] >= MAX_ATTEMPTS:
                node.update(status="failed", reason="attempt_limit")
        return state
    except (ValueError, KeyError, TypeError, AttributeError, RecursionError):
        raise ValueError("Crawl state is invalid; preserved unchanged for manual recovery.") from None


@contextmanager
def single_writer(path: Path) -> Iterator[None]:
    path = workspace_path(str(path))
    try:
        descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        raise ValueError("Crawl lock exists. Check for another writer before manually removing a stale lock.") from None
    try:
        with os.fdopen(descriptor, "w") as lock:
            lock.write(str(os.getpid()))
        yield
    finally:
        path.unlink(missing_ok=True)


def graph_depths(state: dict[str, Any]) -> dict[str, dict[str, int]]:
    distances: dict[str, dict[str, int]] = {}
    for seed in state["seeds"]:
        queue = deque([(seed, 0)])
        while queue:
            url, depth = queue.popleft()
            if distances.get(url, {}).get(seed, math.inf) <= depth:
                continue
            distances.setdefault(url, {})[seed] = depth
            node = state["nodes"][url]
            for link in node["links"]:
                queue.append((link, depth + (0 if node["status"] == "redirect" else 1)))
    return distances


def evidence(data: Path, url: str, headers: dict[str, str], body: bytes) -> tuple[dict[str, Any], list[str]]:
    content_type = headers.get("content-type", "application/octet-stream").split(";", 1)[0].strip().lower()
    prefix = body.lstrip()[:100].lower()
    html = content_type in {"text/html", "application/xhtml+xml"} or prefix.startswith((b"<!doctype html", b"<html"))
    if body.startswith(b"%PDF-"):
        content_type, html = "application/pdf", False
    elif html and content_type not in {"text/html", "application/xhtml+xml"}:
        content_type = "text/html"
    details: dict[str, Any] = {"source_url": url, "content_type": content_type,
                               "extraction": "pending_reader", "emails": [], "text": "", "links": []}
    if html:
        charset = re.search(r"charset\s*=\s*[\"']?([\w-]+)", headers.get("content-type", ""), re.I)
        try:
            text = body.decode(charset[1] if charset else "utf-8", errors="replace")
        except LookupError:
            text = body.decode("utf-8", errors="replace")
        parser = PageText(url)
        parser.feed(text)
        visible = " ".join(" ".join(parser.text).split())
        details.update(extraction="html_text", text=visible, links=parser.links,
                       emails=sorted(parser.emails | {match.lower() for match in EMAIL_PATTERN.findall(visible)}))
    name = hashlib.sha256(url.encode()).hexdigest() + "-" + hashlib.sha256(body).hexdigest()[:16]
    folder = workspace_path(str(data / "evidence"))
    for suffix, content in [(".bin", body), (".json", json.dumps(details, ensure_ascii=False, indent=2).encode("utf-8"))]:
        target = workspace_path(str(folder / (name + suffix)))
        if target.exists() and target.read_bytes() != content:
            raise ValueError("Existing evidence differs; preserved for manual recovery.")
        if not target.exists():
            atomic_write(target, content)
    return {"content_type": content_type, "extraction": details["extraction"], "evidence": name}, details["links"]


def allowed_hosts(seeds: list[str], extras: list[str]) -> set[str]:
    hosts: set[str] = set()
    for value in [*(urlsplit(seed).hostname or "" for seed in seeds), *extras]:
        if not value or "/" in value or ":" in value or "@" in value:
            raise ValueError("Allowed hosts must be plain DNS hostnames.")
        host = value.encode("idna").decode("ascii").lower().rstrip(".")
        hosts.update({host, host[4:] if host.startswith("www.") else "www." + host})
    return hosts


def crawl(args: argparse.Namespace, data: Path, seeds_path: Path) -> int:
    data.mkdir(parents=True, exist_ok=True)
    workspace_path(str(data / "evidence")).mkdir(exist_ok=True)
    state_path = workspace_path(str(data / "crawl_state.json"))
    seeds = read_seeds(seeds_path)
    with single_writer(data / "crawl.lock"):
        if args.resume:
            if not state_path.is_file():
                raise ValueError("No crawl checkpoint found. Start with --crawl.")
            state = load_state(state_path)
            if state["seeds"] != seeds:
                raise ValueError("Seed file differs from this crawl; preserve it or use a separate data directory.")
        else:
            if state_path.exists():
                raise ValueError("Crawl state already exists. Use --resume or a separate private data directory.")
            state = {"version": 1, "seeds": seeds, "nodes": {}}
            for seed in seeds:
                add_node(state, seed)
        hosts = allowed_hosts(seeds, args.allow_host)
        fetcher = Fetcher(args, hosts, state.setdefault("next_request_at", {}), state.setdefault("robots", {}))
        pages: Counter[str] = Counter()
        processed: set[str] = set()
        interrupted = False
        try:
            while True:
                distances = graph_depths(state)
                selected: tuple[str, str] | None = None
                for url, node in state["nodes"].items():
                    if node["status"] in {"fetched", "redirect"} or url in processed:
                        continue
                    if node["status"] == "blocked" and node["reason"] not in {"redirect_limit"}:
                        continue
                    if node["attempts"] >= MAX_ATTEMPTS:
                        continue
                    reason = ""
                    eligible = [root for root, depth in distances.get(url, {}).items() if depth <= args.max_depth]
                    if urlsplit(url).hostname not in hosts:
                        reason = "scope"
                    elif not eligible:
                        reason = "depth"
                    elif node["redirect_hops"] > MAX_REDIRECTS:
                        reason = "redirect_limit"
                    else:
                        roots = [root for root in eligible if pages[root] < args.max_pages_per_seed]
                        if not roots:
                            reason = "page_budget"
                        elif fetcher.requests >= args.max_requests:
                            reason = "request_budget"
                        elif selected is None:
                            selected = (url, roots[0])
                    if reason or node["status"] != "failed":
                        node["reason"] = reason
                    node["status"] = "pending" if node["status"] != "failed" else "failed"
                if selected is None:
                    break
                url, root = selected
                node = state["nodes"][url]
                previous_attempts = node["attempts"]
                processed.add(url)
                try:
                    policy = fetcher.policy(url)
                    if not policy.allows(url):
                        node.update(status="blocked", reason="robots_disallow")
                        continue
                    if fetcher.requests >= args.max_requests:
                        node.update(status="pending", reason="request_budget")
                        continue
                    node["attempts"] += 1
                    pages[root] += 1
                    save_state(state_path, state)
                    status, headers, body = fetcher.request(url, delay=policy.delay)
                    node["http_status"] = status
                    if status in {301, 302, 303, 307, 308}:
                        target = normalize_url(headers.get("location", ""), url)
                        if urlsplit(url).scheme == "https" and urlsplit(target).scheme != "https":
                            raise CrawlStop("https_downgrade")
                        seen = {url}
                        cursor = target
                        while cursor in state["nodes"]:
                            if cursor in seen:
                                raise CrawlStop("redirect_loop")
                            seen.add(cursor)
                            previous = state["nodes"][cursor]
                            if previous["status"] != "redirect":
                                break
                            cursor = previous["links"][0]
                        add_node(state, target, url, node["redirect_hops"] + 1)
                        node.update(status="redirect", reason="", links=[target])
                    elif 200 <= status < 300:
                        metadata, links = evidence(data, url, headers, body)
                        for link in links:
                            add_node(state, link, url)
                        node.update(metadata, status="fetched", reason="", links=links)
                    elif status in {401, 403}:
                        node.update(status="blocked", reason="site_restriction")
                    else:
                        node.update(status="failed", reason=f"http_{status}")
                except CrawlStop as error:
                    reason = str(error)
                    if reason in {"request_budget", "scope", "rate_deferred"}:
                        node.update(status="pending", reason=reason, attempts=previous_attempts)
                    elif reason in {"non_public_target", "nonstandard_port", "resource_too_large", "encoded_response_unsupported", "redirect_loop", "https_downgrade"}:
                        node.update(status="blocked", reason=reason)
                    else:
                        node["attempts"] = previous_attempts + 1
                        node.update(status="failed", reason=reason)
                except (OSError, ValueError, http.client.HTTPException) as error:
                    node["attempts"] = previous_attempts + 1
                    node.update(status="failed", reason=type(error).__name__)
                finally:
                    save_state(state_path, state)
        except KeyboardInterrupt:
            interrupted = True
        finally:
            save_state(state_path, state)
        counts = Counter(node["status"] for node in state["nodes"].values())
        unread = sum(node.get("extraction") == "pending_reader" for node in state["nodes"].values())
        print(f"Requests this run: {fetcher.requests}; discovered resources: {len(state['nodes'])}.")
        print(f"Fetched: {counts['fetched']}; redirects: {counts['redirect']}; pending: {counts['pending']}; "
              f"blocked: {counts['blocked']}; failed: {counts['failed']}; awaiting reader: {unread}.")
        print("Checkpoint saved. Pending/blocked/failed resources remain recorded; no complete-coverage claim.")
        return 130 if interrupted else 0


def nonnegative_int(value: str) -> int:
    number = int(value)
    if number < 0:
        raise argparse.ArgumentTypeError("must be zero or greater")
    return number


def positive_int(value: str) -> int:
    number = nonnegative_int(value)
    if number == 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return number


def positive_float(value: str) -> float:
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise argparse.ArgumentTypeError("must be finite and greater than zero")
    return number


def workspace_path(value: str) -> Path:
    """Resolve relative to the script and reject paths outside this experiment."""
    path = (WORKSPACE / value).resolve()
    if path == WORKSPACE or not path.is_relative_to(WORKSPACE):
        raise ValueError("Seed and output paths must be inside this experiment.")
    return path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog="PDF/document readers and LM Studio integration are later tickets.",
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--init", action="store_true", help="create missing private folders and seed template")
    mode.add_argument("--check", action="store_true", help="check folders, write access and seed syntax offline")
    mode.add_argument("--crawl", action="store_true", help="start a bounded crawl without replacing existing state")
    mode.add_argument("--resume", action="store_true", help="continue the saved crawl with fresh per-run budgets")
    parser.add_argument("--seeds", default="links.txt", help="seed file, relative to this experiment")
    parser.add_argument("--data-dir", default="data", help="private output directory, inside this experiment")
    parser.add_argument("--allow-host", action="append", default=[], help="additional allowed hostname; may be repeated")
    parser.add_argument("--max-depth", type=nonnegative_int, default=2, help="crawl depth limit; redirects add no depth")
    parser.add_argument("--max-pages-per-seed", type=positive_int, default=50, help="per-seed page attempts each run")
    parser.add_argument("--max-requests", type=positive_int, default=200, help="total request attempts each run, including robots")
    parser.add_argument("--max-bytes", type=positive_int, default=5 * 1024 * 1024, help="maximum bytes per resource")
    parser.add_argument("--request-timeout", type=positive_float, default=15.0, help="request timeout in seconds")
    parser.add_argument("--delay", type=positive_float, default=1.0, help="minimum per-host delay in seconds")
    return parser


def initialize(directories: list[Path], seeds: Path) -> None:
    if seeds.exists() and not seeds.is_file():
        raise ValueError("The seed path must be a file.")
    for directory in [*directories, seeds.parent]:
        directory.mkdir(parents=True, exist_ok=True)
    try:
        with seeds.open("x", encoding="utf-8", newline="\n") as output:
            output.write(SEED_TEMPLATE)
        print("Created a comment-only seed template; add starting URLs before crawling.")
    except FileExistsError:
        if not seeds.is_file():
            raise ValueError("The seed path must be a file.") from None
        print("Existing seed file preserved.")
    print("Private workspace initialized. Run --check to inspect it offline.")


def check_workspace(directories: list[Path], seeds: Path) -> bool:
    ready = True
    for directory in directories:
        label = directory.relative_to(WORKSPACE)
        if not directory.is_dir():
            print(f"Missing directory: {label}. Run --init.")
            ready = False
            continue
        try:
            with TemporaryFile(dir=directory) as probe:
                probe.write(b"workspace write check\n")
                probe.flush()
        except OSError:
            print(f"Directory is not writable: {label}.")
            ready = False

    if not seeds.is_file():
        print("Seed file missing. Run --init or use --seeds with an existing file.")
        return False
    try:
        with seeds.open(encoding="utf-8-sig") as source:
            lines = [(number, line.strip()) for number, line in enumerate(source, 1)]
    except UnicodeError:
        print("Seed file must be UTF-8 text.")
        return False

    count = 0
    invalid_lines: list[int] = []
    for number, seed in lines:
        if not seed or seed.startswith("#"):
            continue
        count += 1
        try:
            parsed = urlsplit(seed)
            valid = (
                parsed.scheme in {"http", "https"}
                and bool(parsed.hostname)
                and parsed.username is None
                and parsed.password is None
                and (parsed.port is None or parsed.port > 0)
                and not any(character.isspace() for character in seed)
            )
        except ValueError:
            valid = False
        if not valid:
            invalid_lines.append(number)

    print(f"Seed entries: {count}; invalid: {len(invalid_lines)}.")
    if invalid_lines:
        print("Fix seed lines: " + ", ".join(map(str, invalid_lines)))
        ready = False
    if count == 0:
        print("Seed file is empty or comment-only; add starting URLs before crawling.")
        ready = False
    if ready:
        print("Offline setup checks passed. Crawl permissions and targets are not checked yet.")
    return ready


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        seeds = workspace_path(args.seeds)
        data = workspace_path(args.data_dir)
        directories = [
            data,
            workspace_path(str(data / "evidence")),
            workspace_path("drafts"),
            workspace_path("logs"),
        ]
        print(f"Seeds: {seeds.relative_to(WORKSPACE)}; outputs: {data.relative_to(WORKSPACE)}.")
        print(
            f"Crawl limits: depth={args.max_depth}, pages/seed={args.max_pages_per_seed}, "
            f"requests/run={args.max_requests}, timeout={args.request_timeout:g}s, delay={args.delay:g}s."
        )
        if args.init:
            initialize(directories, seeds)
            return 0
        if args.crawl or args.resume:
            return crawl(args, data, seeds)
        return 0 if check_workspace(directories, seeds) else 1
    except ValueError as error:
        print(f"Workspace error: {error}", file=sys.stderr)
    except OSError as error:
        print(f"Workspace error: {error.strerror or 'file access failed'}. Check paths and permissions.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
