from fastapi.testclient import TestClient

from talkingdb_eai.main import app

client = TestClient(app)


def test_list_tenants_includes_caster_concepts():
    response = client.get("/api/tenants")

    assert response.status_code == 200
    ids = [t["tenant_id"] for t in response.json()]
    assert "caster_concepts" in ids


def test_get_tenant_config_returns_unit_config():
    response = client.get("/api/tenants/caster_concepts")

    assert response.status_code == 200
    body = response.json()
    assert body["tenant_id"] == "caster_concepts"
    assert body["unit_config"]["capacity"] == "lbs"


def test_get_tenant_config_404_for_unknown_tenant():
    response = client.get("/api/tenants/does-not-exist")

    assert response.status_code == 404
