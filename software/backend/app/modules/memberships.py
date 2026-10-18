"""Transactional sharing for existing or newly provisioned regular users."""

from dataclasses import dataclass
from typing import Any
from uuid import UUID

from psycopg import Connection

from app.modules.meters import get_meter, lock_meter_access
from app.modules.otp import normalize_email


class MemberNotFoundError(Exception):
    """Raised when a requested membership does not exist."""


class LastMemberError(Exception):
    """Raised when removal would leave a meter without any members."""


@dataclass(frozen=True)
class Member:
    """One accessible meter member, without global role or account status."""

    user_id: int
    email: str


def list_members(
    connection: Connection[Any], meter_id: UUID, access_user_id: int | None
) -> list[Member]:
    """List members only after checking access to their parent meter."""

    get_meter(connection, meter_id, access_user_id)
    rows = connection.execute(
        """SELECT users.id, users.email FROM monitor.user_meters AS members
           JOIN monitor.users AS users ON users.id = members.user_id
           WHERE members.meter_id = %s ORDER BY users.email, users.id""",
        (meter_id,),
    ).fetchall()
    return [Member(*row) for row in rows]


def share_member(
    connection: Connection[Any],
    meter_id: UUID,
    access_user_id: int | None,
    email: str,
) -> Member:
    """Idempotently share after authorization, preserving every existing role."""

    normalized = normalize_email(email)
    with connection.transaction():
        lock_meter_access(connection, meter_id, access_user_id)
        connection.execute(
            """INSERT INTO monitor.users (email, type) VALUES (%s, 'user')
               ON CONFLICT (email) DO NOTHING""",
            (normalized,),
        )
        # A separate statement sees a concurrent signup's committed conflict row.
        user = connection.execute(
            "SELECT id, email FROM monitor.users WHERE email = %s", (normalized,)
        ).fetchone()
        assert user is not None
        connection.execute(
            """INSERT INTO monitor.user_meters (user_id, meter_id) VALUES (%s, %s)
               ON CONFLICT (user_id, meter_id) DO NOTHING""",
            (user[0], meter_id),
        )
        return Member(*user)


def remove_member(
    connection: Connection[Any],
    meter_id: UUID,
    access_user_id: int | None,
    user_id: int,
) -> None:
    """Remove a member under the shared lock, never leaving an orphan meter."""

    with connection.transaction():
        lock_meter_access(connection, meter_id, access_user_id)
        member = connection.execute(
            "SELECT 1 FROM monitor.user_meters WHERE meter_id = %s AND user_id = %s",
            (meter_id, user_id),
        ).fetchone()
        if not member:
            raise MemberNotFoundError("Member not found")
        count = connection.execute(
            "SELECT COUNT(*) FROM monitor.user_meters WHERE meter_id = %s", (meter_id,)
        ).fetchone()
        assert count is not None
        if count[0] <= 1:
            raise LastMemberError("Cannot remove the last member")
        connection.execute(
            "DELETE FROM monitor.user_meters WHERE meter_id = %s AND user_id = %s",
            (meter_id, user_id),
        )
