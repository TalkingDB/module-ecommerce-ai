import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Union

DEFAULT_TENANTS_CONFIG_PATH = (
    Path(__file__).resolve().parent.parent.parent.parent / "tenants.json"
)


class TenantConfigError(Exception):
    pass


class TenantNotFoundError(Exception):
    pass


@dataclass(frozen=True)
class TenantConfig:
    """A configured ecommerce store operator (e.g. Caster Concepts).

    Non-secret fields (namespace, store URL, per-tenant unit config) come
    from tenants.json. Store API credentials are read from env vars named
    after the tenant id at access time, never stored in tenants.json or in
    any tenant-named file or class - adding a tenant (including a fake
    test one) is purely a matter of a JSON entry plus two env vars.
    """

    tenant_id: str
    namespace: str
    store_api_url: str
    unit_config: dict[str, str] = field(default_factory=dict)

    @property
    def store_api_username(self) -> str:
        return _require_env(f"{self.tenant_id.upper()}_STORE_API_UN")

    @property
    def store_api_password(self) -> str:
        return _require_env(f"{self.tenant_id.upper()}_STORE_API_PWD")


def _require_env(var_name: str) -> str:
    value = os.getenv(var_name)
    if not value:
        raise TenantConfigError(f"{var_name} is not set")
    return value


def load_tenants(
    config_path: Optional[Union[Path, str]] = None,
) -> dict[str, TenantConfig]:
    path = Path(
        config_path
        or os.getenv("EAI_TENANTS_CONFIG_PATH")
        or DEFAULT_TENANTS_CONFIG_PATH
    )

    with path.open() as f:
        raw = json.load(f)

    return {
        tenant_id: TenantConfig(
            tenant_id=tenant_id,
            namespace=entry["namespace"],
            store_api_url=entry["store_api_url"],
            unit_config=entry.get("unit_config", {}),
        )
        for tenant_id, entry in raw.items()
    }


def get_tenant(
    tenant_id: str, config_path: Optional[Union[Path, str]] = None
) -> TenantConfig:
    tenants = load_tenants(config_path)
    if tenant_id not in tenants:
        raise TenantNotFoundError(f"no tenant configured with id {tenant_id!r}")
    return tenants[tenant_id]
