import json

import pytest

from talkingdb_eai.services.tenants.config import (
    TenantConfigError,
    TenantNotFoundError,
    get_tenant,
    load_tenants,
)


@pytest.fixture
def tenants_config_path(tmp_path):
    path = tmp_path / "tenants.json"
    path.write_text(
        json.dumps(
            {
                "acme": {
                    "namespace": "acme",
                    "store_api_url": "https://acme.example.com/wp-json/wc/v3",
                    "unit_config": {"weight": "kg"},
                },
                "no_units": {
                    "namespace": "no_units",
                    "store_api_url": "https://no-units.example.com/wp-json/wc/v3",
                },
            }
        )
    )
    return path


def test_load_tenants_returns_every_configured_tenant(tenants_config_path):
    tenants = load_tenants(tenants_config_path)

    assert set(tenants) == {"acme", "no_units"}
    assert tenants["acme"].namespace == "acme"
    assert tenants["acme"].store_api_url == "https://acme.example.com/wp-json/wc/v3"
    assert tenants["acme"].unit_config == {"weight": "kg"}


def test_load_tenants_defaults_unit_config_to_empty_dict(tenants_config_path):
    tenants = load_tenants(tenants_config_path)

    assert tenants["no_units"].unit_config == {}


def test_get_tenant_returns_matching_tenant(tenants_config_path):
    tenant = get_tenant("acme", tenants_config_path)

    assert tenant.tenant_id == "acme"


def test_get_tenant_raises_for_unknown_tenant(tenants_config_path):
    with pytest.raises(TenantNotFoundError, match="unknown"):
        get_tenant("unknown", tenants_config_path)


def test_load_tenants_reads_config_path_from_env(monkeypatch, tenants_config_path):
    monkeypatch.setenv("EAI_TENANTS_CONFIG_PATH", str(tenants_config_path))

    tenants = load_tenants()

    assert set(tenants) == {"acme", "no_units"}


def test_store_api_username_reads_tenant_specific_env_var(
    monkeypatch, tenants_config_path
):
    monkeypatch.setenv("ACME_STORE_API_UN", "ck_test_user")
    tenant = get_tenant("acme", tenants_config_path)

    assert tenant.store_api_username == "ck_test_user"


def test_store_api_password_reads_tenant_specific_env_var(
    monkeypatch, tenants_config_path
):
    monkeypatch.setenv("ACME_STORE_API_PWD", "cs_test_pass")
    tenant = get_tenant("acme", tenants_config_path)

    assert tenant.store_api_password == "cs_test_pass"


def test_store_api_username_raises_when_env_var_missing(
    monkeypatch, tenants_config_path
):
    monkeypatch.delenv("ACME_STORE_API_UN", raising=False)
    tenant = get_tenant("acme", tenants_config_path)

    with pytest.raises(TenantConfigError, match="ACME_STORE_API_UN"):
        tenant.store_api_username


def test_repo_tenants_json_has_caster_concepts_configured():
    tenants = load_tenants()

    assert "caster_concepts" in tenants
    assert tenants["caster_concepts"].namespace == "caster_concepts"
    assert tenants["caster_concepts"].unit_config["capacity"] == "lbs"
