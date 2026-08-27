from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

from talkingdb_eai.main import app

client = TestClient(app)


def test_search_tenant_returns_results():
    fake_pt_client = MagicMock()
    fake_ds_client = MagicMock()

    with (
        patch("talkingdb_eai.api.search.PTClient", return_value=fake_pt_client),
        patch("talkingdb_eai.api.search.DSClient", return_value=fake_ds_client),
        patch(
            "talkingdb_eai.api.search.run_search",
            new=AsyncMock(return_value=[{"node_id": "CC-1", "src_name": "Caster"}]),
        ) as run_search,
    ):
        response = client.post(
            "/api/tenants/caster_concepts/search",
            json={"query": "swivel caster", "limit": 5},
        )

    assert response.status_code == 200
    assert response.json() == [{"node_id": "CC-1", "src_name": "Caster"}]
    run_search.assert_awaited_once()
    call_args = run_search.await_args.args
    assert call_args[0] is fake_pt_client
    assert call_args[1] is fake_ds_client
    assert call_args[2].tenant_id == "caster_concepts"
    assert call_args[3] == "swivel caster"
    assert run_search.await_args.kwargs == {"limit": 5}


def test_search_tenant_defaults_limit_to_ten():
    with (
        patch("talkingdb_eai.api.search.PTClient"),
        patch("talkingdb_eai.api.search.DSClient"),
        patch(
            "talkingdb_eai.api.search.run_search", new=AsyncMock(return_value=[])
        ) as run_search,
    ):
        response = client.post(
            "/api/tenants/caster_concepts/search", json={"query": "caster"}
        )

    assert response.status_code == 200
    assert run_search.await_args.kwargs["limit"] == 10


def test_search_tenant_404_for_unknown_tenant():
    response = client.post(
        "/api/tenants/does-not-exist/search", json={"query": "caster"}
    )

    assert response.status_code == 404
