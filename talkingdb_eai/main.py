from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from talkingdb_eai import __version__
from talkingdb_eai.api import search, sync, tenants

OPENAPI_TAGS = [
    {
        "name": "Tenants",
        "description": "Configured ecommerce tenants (store operators).",
    },
    {
        "name": "Sync",
        "description": "Pull a tenant's store catalog and index it for search.",
    },
    {
        "name": "Search",
        "description": "Natural-language product search over a tenant's indexed "
        "catalog.",
    },
]

app = FastAPI(
    title="TalkingDB Ecommerce AI",
    description=(
        "Ecommerce search product composing package-parse-tree, "
        "package-search-trainer, and package-document-search: syncs a "
        "tenant's store catalog into an ontology and search index, then "
        "serves natural-language product search over it. Any ecommerce "
        "store operator can be configured as a tenant; Caster Concepts is "
        "the first."
    ),
    version=__version__,
    openapi_tags=OPENAPI_TAGS,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tenants.router)
app.include_router(sync.router)
app.include_router(search.router)
