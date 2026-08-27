from fastapi import APIRouter, HTTPException

from talkingdb_eai.services.tenants.config import (
    TenantNotFoundError,
    get_tenant,
    load_tenants,
)

router = APIRouter(prefix="/api/tenants", tags=["Tenants"])


@router.get("")
def list_tenants() -> list[dict]:
    tenants = load_tenants()
    return [
        {
            "tenant_id": tenant.tenant_id,
            "namespace": tenant.namespace,
            "store_api_url": tenant.store_api_url,
        }
        for tenant in tenants.values()
    ]


@router.get("/{tenant_id}")
def get_tenant_config(tenant_id: str) -> dict:
    try:
        tenant = get_tenant(tenant_id)
    except TenantNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return {
        "tenant_id": tenant.tenant_id,
        "namespace": tenant.namespace,
        "store_api_url": tenant.store_api_url,
        "unit_config": tenant.unit_config,
    }
