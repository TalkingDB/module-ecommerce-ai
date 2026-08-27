import json
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from talkingdb_eai.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def tenants_config(tmp_path, monkeypatch):
    path = tmp_path / "tenants.json"
    path.write_text(
        json.dumps(
            {
                "acme": {
                    "namespace": "acme",
                    "store_api_url": "https://acme.example.com/wp-json/wc/v3",
                    "unit_config": {"capacity": "lbs"},
                }
            }
        )
    )
    monkeypatch.setenv("EAI_TENANTS_CONFIG_PATH", str(path))
    monkeypatch.setenv("ACME_STORE_API_UN", "ck_test")
    monkeypatch.setenv("ACME_STORE_API_PWD", "cs_test")
    return path


def test_sync_tenant_pulls_woocommerce_and_calls_orchestrator():
    fake_pt_client = MagicMock()
    fake_ds_client = MagicMock()

    with (
        patch("talkingdb_eai.api.sync.PTClient", return_value=fake_pt_client),
        patch("talkingdb_eai.api.sync.DSClient", return_value=fake_ds_client),
        patch(
            "talkingdb_eai.services.connectors.woocommerce.fetch_categories",
            return_value=[{"id": 1, "name": "Casters"}],
        ) as fetch_categories,
        patch(
            "talkingdb_eai.services.connectors.woocommerce.fetch_products",
            return_value=[
                {
                    "id": 5,
                    "sku": "CC-1",
                    "name": "Swivel Caster",
                    "categories": [{"id": 1}],
                    "attributes": [],
                }
            ],
        ) as fetch_products,
        patch(
            "talkingdb_eai.api.sync.sync_ontology",
            return_value={
                "categories_indexed": 1,
                "attributes_indexed": 0,
                "products_indexed": 1,
            },
        ) as sync_ontology,
    ):
        response = client.post("/api/tenants/acme/sync", json={})

    assert response.status_code == 200
    assert response.json() == {
        "categories_indexed": 1,
        "attributes_indexed": 0,
        "products_indexed": 1,
    }
    fetch_categories.assert_called_once_with(
        "https://acme.example.com/wp-json/wc/v3", "ck_test", "cs_test"
    )
    fetch_products.assert_called_once_with(
        "https://acme.example.com/wp-json/wc/v3", "ck_test", "cs_test"
    )
    sync_ontology.assert_called_once()
    call_args = sync_ontology.call_args.args
    assert call_args[0] is fake_pt_client
    assert call_args[1] is fake_ds_client
    assert call_args[3][0]["sku"] == "CC-1"
    assert call_args[3][0]["category_ids"] == [1]
    assert call_args[4][0]["id"] == 1


def test_sync_tenant_normalizes_object_vs_literal_attributes():
    fake_pt_client = MagicMock()
    fake_ds_client = MagicMock()

    with (
        patch("talkingdb_eai.api.sync.PTClient", return_value=fake_pt_client),
        patch("talkingdb_eai.api.sync.DSClient", return_value=fake_ds_client),
        patch(
            "talkingdb_eai.services.connectors.woocommerce.fetch_categories",
            return_value=[],
        ),
        patch(
            "talkingdb_eai.services.connectors.woocommerce.fetch_products",
            return_value=[
                {
                    "id": 5,
                    "sku": "CC-1",
                    "name": "Swivel Caster",
                    "categories": [],
                    "attributes": [
                        {"name": "Wheel Type", "options": ["Swivel"]},
                        {"name": "Capacity", "options": ["250"]},
                    ],
                }
            ],
        ),
        patch("talkingdb_eai.api.sync.sync_ontology", return_value={}) as sync_ontology,
    ):
        response = client.post(
            "/api/tenants/acme/sync",
            json={"object_attributes": {"wheel_type": False}},
        )

    assert response.status_code == 200
    products = sync_ontology.call_args.args[3]
    assert products[0]["attributes"] == {"wheel_type": ["Swivel"], "capacity": "250"}


def test_sync_tenant_404_for_unknown_tenant():
    response = client.post("/api/tenants/does-not-exist/sync", json={})

    assert response.status_code == 404


def test_crawl_tenant_delegates_to_st_client():
    fake_st_client = MagicMock()
    fake_st_client.crawl_and_train.return_value = {
        "pages_crawled": 1,
        "chunks_indexed": 2,
        "failures": [],
    }

    with patch("talkingdb_eai.api.sync.STClient", return_value=fake_st_client):
        response = client.post(
            "/api/tenants/acme/crawl",
            json={
                "urls": ["https://acme.example.com/blog/buying-guide"],
                "selectors": {"title": "h1"},
                "content_field": "title",
            },
        )

    assert response.status_code == 200
    assert response.json() == {"pages_crawled": 1, "chunks_indexed": 2, "failures": []}
    fake_st_client.crawl_and_train.assert_called_once_with(
        "acme",
        ["https://acme.example.com/blog/buying-guide"],
        {"title": "h1"},
        content_field="title",
    )


def test_crawl_tenant_404_for_unknown_tenant():
    response = client.post(
        "/api/tenants/does-not-exist/crawl",
        json={"urls": [], "selectors": {}, "content_field": "title"},
    )

    assert response.status_code == 404
