from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from talkingdb_ds.client import DSClient
from talkingdb_pt.client import PTClient

from talkingdb_eai.services.search.orchestrator import search as run_search
from talkingdb_eai.services.tenants.config import TenantNotFoundError, get_tenant

router = APIRouter(prefix="/api/tenants/{tenant_id}", tags=["Search"])


class SearchRequest(BaseModel):
    query: str
    limit: int = 10


@router.post("/search")
async def search_tenant(tenant_id: str, request: SearchRequest) -> list[dict]:
    try:
        tenant = get_tenant(tenant_id)
    except TenantNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return await run_search(
        PTClient(), DSClient(), tenant, request.query, limit=request.limit
    )
