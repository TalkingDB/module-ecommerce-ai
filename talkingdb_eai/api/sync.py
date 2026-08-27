from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from talkingdb_ds.client import DSClient
from talkingdb_pt.client import PTClient
from talkingdb_st.client import STClient

from talkingdb_eai.services.connectors import woocommerce
from talkingdb_eai.services.ingest.orchestrator import sync_ontology
from talkingdb_eai.services.tenants.config import TenantNotFoundError, get_tenant

router = APIRouter(prefix="/api/tenants/{tenant_id}", tags=["Sync"])


class SyncRequest(BaseModel):
    object_attributes: dict[str, bool] = {}


class CrawlRequest(BaseModel):
    urls: list[str]
    selectors: dict[str, str]
    content_field: str


def _normalize_category(raw: dict) -> dict:
    return {
        "id": raw["id"],
        "name": raw["name"],
        "parent_id": raw.get("parent") or None,
        "description": raw.get("description") or "",
    }


def _normalize_product(raw: dict, object_attribute_names: set) -> dict:
    attributes = {}
    for attr in raw.get("attributes", []) or []:
        name = (attr.get("name") or "").strip().lower().replace(" ", "_")
        if not name:
            continue
        options = attr.get("options") or []
        if name in object_attribute_names:
            attributes[name] = options
        elif options:
            attributes[name] = options[0]

    return {
        "id": raw["id"],
        "sku": raw.get("sku") or str(raw["id"]),
        "name": raw.get("name", ""),
        "description": raw.get("short_description") or raw.get("description") or "",
        "url": raw.get("permalink"),
        "category_ids": [c["id"] for c in raw.get("categories", []) or []],
        "attributes": attributes,
    }


def _get_tenant_or_404(tenant_id: str):
    try:
        return get_tenant(tenant_id)
    except TenantNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/sync")
def sync_tenant(tenant_id: str, request: SyncRequest) -> dict:
    tenant = _get_tenant_or_404(tenant_id)

    raw_categories = woocommerce.fetch_categories(
        tenant.store_api_url, tenant.store_api_username, tenant.store_api_password
    )
    raw_products = woocommerce.fetch_products(
        tenant.store_api_url, tenant.store_api_username, tenant.store_api_password
    )

    object_attribute_names = set(request.object_attributes)
    categories = [_normalize_category(c) for c in raw_categories]
    products = [_normalize_product(p, object_attribute_names) for p in raw_products]

    return sync_ontology(
        PTClient(),
        DSClient(),
        tenant,
        products,
        categories,
        request.object_attributes,
    )


@router.post("/crawl")
def crawl_tenant(tenant_id: str, request: CrawlRequest) -> dict:
    tenant = _get_tenant_or_404(tenant_id)

    return STClient().crawl_and_train(
        tenant.namespace,
        request.urls,
        request.selectors,
        content_field=request.content_field,
    )
