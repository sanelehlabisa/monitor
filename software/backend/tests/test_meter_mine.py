"""Membership-based My filtering, independent of creator metadata or admin role."""

from app.database import connect_database
from tests.support import Person, SharingCase


def _ids(person: Person, **query: str | bool) -> list[str]:
    """Read one synthetic account's scoped list and require successful HTTP."""
    response = person.client.get("/api/meters", params=query)
    assert response.status_code == 200
    return [meter["id"] for meter in response.json()]


def test_admin_mine_uses_membership_not_creator_and_combines_search(sharing_case: SharingCase) -> None:
    """Admins keep All access, but My includes shared-in and excludes left meters."""
    case = sharing_case
    owner, member, admin = case.user(), case.user(), case.user("admin")
    existing = set(_ids(admin))
    shared = owner.client.post("/api/meters", json={"name": "Needle shared"}).json()
    hidden = owner.client.post("/api/meters", json={"name": "Needle private"}).json()
    left = admin.client.post("/api/meters", json={"name": "Needle departed"}).json()
    own = admin.client.post("/api/meters", json={"name": "Other active"}).json()
    shared_url = f"/api/meters/{shared['id']}/members"
    for person in (member, admin):
        assert owner.client.post(shared_url, json={"email": person.email}).status_code == 200
    left_url = f"/api/meters/{left['id']}/members"
    assert admin.client.post(left_url, json={"email": member.email}).status_code == 200
    assert admin.client.delete(left_url + f"/{admin.id}").status_code == 204

    all_ids = existing | {meter["id"] for meter in (shared, hidden, left, own)}
    assert set(_ids(admin)) == set(_ids(admin, mine=False)) == all_ids
    my_ids = {shared["id"], own["id"]}
    assert set(_ids(admin, mine=True)) == my_ids
    assert _ids(admin, mine=True, q="NEEDLE") == [shared["id"]]
    assert _ids(admin, mine=True, q=owner.email.upper()) == [shared["id"]]
    assert _ids(admin, mine=True, q=member.email) == [shared["id"]]
    assert set(_ids(admin, q=member.email)) == {shared["id"], left["id"]}
    assert _ids(admin, mine=True, q="%") == []
    duplicate_matches = _ids(admin, mine=True, q="example.test")
    assert set(duplicate_matches) == my_ids and len(duplicate_matches) == len(my_ids)
    assert admin.client.get(f"/api/meters/{left['id']}").status_code == 200
    assert admin.client.get(f"/api/meters/{left['id']}").json()["owner_email"] == admin.email

    assert admin.client.delete(f"/api/meters/{own['id']}/members/{admin.id}").status_code == 409
    assert set(_ids(admin, mine=True)) == my_ids
    with connect_database() as connection:
        assert connection.execute("SELECT count(*) FROM monitor.meters m WHERE NOT EXISTS "
            "(SELECT 1 FROM monitor.user_meters um WHERE um.meter_id=m.id)").fetchone() == (0,)


def test_regular_mine_false_never_grants_global_scope(sharing_case: SharingCase) -> None:
    """Both flags retain regular-member scope and server-side name/email filtering."""
    case = sharing_case
    owner, member, outsider = case.user(), case.user(), case.user()
    shared = owner.client.post("/api/meters", json={"name": "Needle shared"}).json()
    own = member.client.post("/api/meters", json={"name": "Needle owned"}).json()
    hidden = outsider.client.post("/api/meters", json={"name": "Needle private"}).json()
    url = f"/api/meters/{shared['id']}/members"
    assert owner.client.post(url, json={"email": member.email}).status_code == 200
    assert owner.client.post(url, json={"email": outsider.email}).status_code == 200
    expected = {shared["id"], own["id"]}
    assert set(_ids(member)) == expected
    for mine in (False, True):
        assert set(_ids(member, mine=mine)) == expected
        assert set(_ids(member, mine=mine, q="NEEDLE")) == expected
        assert _ids(member, mine=mine, q=owner.email.upper()) == [shared["id"]]
        assert _ids(member, mine=mine, q=outsider.email) == [shared["id"]]
        assert _ids(member, mine=mine, q="private") == []
        matches = _ids(member, mine=mine, q="example.test")
        assert set(matches) == expected and len(matches) == len(expected)
        assert hidden["id"] not in matches
    assert owner.client.delete(url + f"/{member.id}").status_code == 204
    assert _ids(member, mine=True) == _ids(member, mine=False) == [own["id"]]
    assert member.client.get("/api/meters", params={"mine": "invalid"}).status_code == 422
    assert case.client().get("/api/meters", params={"mine": False}).status_code == 401
