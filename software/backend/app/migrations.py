"""Historical migration runner; unsupported for schema.sql/058 databases."""

from pathlib import Path

from app.database import connect_database
from app.settings import Settings

DEFAULT_MIGRATIONS_DIRECTORY = Path("/migrations")
CREATE_MIGRATIONS_TABLE = """
CREATE TABLE IF NOT EXISTS schema_migrations (
    version TEXT PRIMARY KEY,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
)
"""


def migration_files(directory: Path) -> list[Path]:
    """Return migration files in deterministic version order."""

    if not directory.is_dir():
        raise FileNotFoundError(f"Migration directory does not exist: {directory}")
    return sorted(directory.glob("*.sql"))


def run_migrations(
    settings: Settings,
    directory: Path = DEFAULT_MIGRATIONS_DIRECTORY,
) -> int:
    """Apply each pending SQL migration once and return the applied count."""

    files = migration_files(directory)
    applied_count = 0
    with connect_database(settings) as connection:
        if connection.execute(
            """SELECT 1 FROM information_schema.columns
               WHERE table_schema = 'monitor' AND table_name = 'users'
               AND column_name = 'type'"""
        ).fetchone():
            raise RuntimeError("Legacy migrations are unsupported; see database/README.md")
        connection.execute(CREATE_MIGRATIONS_TABLE)
        connection.commit()
        applied = {
            row[0]
            for row in connection.execute("SELECT version FROM schema_migrations")
        }
        connection.commit()

        for migration in files:
            if migration.name in applied:
                continue
            with connection.transaction():
                connection.execute(migration.read_text(encoding="utf-8"))
                connection.execute(
                    "INSERT INTO schema_migrations (version) VALUES (%s)",
                    (migration.name,),
                )
            applied_count += 1

    return applied_count


def main() -> None:
    """Apply configured migrations from the command line."""

    applied_count = run_migrations(Settings())
    print(f"Applied {applied_count} migration(s).")


if __name__ == "__main__":
    main()
