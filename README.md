# module-ecommerce-ai

Ecommerce search product: syncs a tenant's store catalog into an ontology
and search index, then serves natural-language product search over it.
Composes `package-parse-tree` (ontology), `package-search-trainer`
(generic web-content crawling), and `package-document-search`
(vector/keyword search) via their client-mode interfaces.

This module **is** Kray, reborn as a TalkingDB module and genericized to
serve any ecommerce store operator rather than hardcoded to one client.
"Kray" is retired from all client-facing surfaces here; Caster Concepts
is simply the first configured tenant.

## What it owns

Everything that's actually ecommerce-domain vocabulary, deliberately kept
out of the generic `package-*` repos:

- **The ecommerce ontology definition** - Category/Attribute/Product types
  mapped onto `package-parse-tree`'s generic type/instance/attribute
  schema (`talkingdb_eai/services/ontology/`).
- **The WooCommerce connector** (`talkingdb_eai/services/connectors/woocommerce.py`)
  - a generic, config-driven REST client (auth and store URL are
  per-tenant config, not hardcoded).
- **Per-tenant configuration** (`tenants.json`) - a tenant is a JSON entry
  plus two env vars for its store credentials. No tenant name appears in
  any file path, class, or module.

## Tenants

`tenants.json` at the repo root holds every configured tenant's
non-secret config (namespace, store API URL, per-tenant unit-of-measure
tagging). Store API credentials are read from env vars named
`<TENANT_ID upper>_STORE_API_UN` / `_PWD` at call time - never stored in
`tenants.json`. Adding a new tenant (including a fake one, for testing
that this module carries no tenant-specific code) is purely a matter of
a new JSON entry plus its two env vars.

## Two-path search

Given a query, `services/search/orchestrator.py` calls
`PTClient.extract_relations` to see if the query resolves to a
recognized ontology category:

- **Resolved** -> filter the knowledge graph directly via
  `PTClient.query_kg_data` (precise).
- **Not resolved, or the KG path returns nothing** -> fall back to
  `DSClient.search`'s vector+keyword search over indexed product text
  (recall).

Either path's results get the tenant's unit config applied
(`services/units.py`) before returning. This mirrors the legacy system's
"7 named search types" at a structural level - see the module's Jira
history for how those names map onto this two-path design - without
hardcoding 7 branches: exact/product-type/feature/compatibility queries
naturally resolve via the KG path, thematic/slang/symptom queries fall
through to the vector path.

Known limitation: `package-parse-tree`'s structured filter engine only
recognizes a fixed edge allowlist (`instance_of`, `subclass_of`,
`has_attributes`, `has_units`, `default_unit`), so a resolved category
narrows the KG-path filter but a resolved attribute value (e.g. "red",
"swivel") doesn't yet. Follow-up: extend that filter engine to support
attribute-edge filtering.

## Ingestion

`POST /api/tenants/{tenant_id}/sync` pulls the tenant's WooCommerce
catalog, registers ontology types, writes categories/attributes/products
into `package-parse-tree`, and indexes product text into
`package-document-search` for vector/keyword search
(`services/ingest/orchestrator.py`). The target document-search
namespace/index must already exist - this only trains data into it.

`POST /api/tenants/{tenant_id}/crawl` uses `STClient.crawl_and_train` to
crawl supplementary web content (e.g. buying guides, blog posts) into the
same namespace, for content a store's REST API doesn't expose.

## Development

```
make sync MODE=git      # or MODE=local for editable base-tdb-*/package-* checkouts
poetry install
make test
make local               # run with hot reload
```

See `Makefile` for the full list of targets.
