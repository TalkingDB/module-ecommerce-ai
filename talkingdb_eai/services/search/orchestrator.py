from talkingdb_eai.services.units import apply_units


def _to_plain_dict(value):
    """PTClient.extract_relations returns pydantic model instances
    (parse_tree_output) in DIRECT mode but plain JSON-decoded dicts in
    API mode - normalize both to plain nested dicts so this module works
    against either mode transparently."""

    if value is None:
        return {}
    if hasattr(value, "model_dump"):
        return value.model_dump()
    return value


def _kg_filters_from_groups(groups: list[dict]) -> list[dict]:
    """Only category-level matches translate into a supported filter
    today: package-parse-tree's structured filter engine only recognizes
    a fixed edge allowlist (instance_of, subclass_of, has_attributes,
    has_units, default_unit) - arbitrary per-attribute edges (e.g.
    "wheel_type") set on product nodes aren't filterable through
    query_kg_data yet, so a resolved attribute value doesn't currently
    narrow the KG-path filter, only a resolved category does."""

    return [
        {"field": "instance_of", "op": "eq", "value": group["uri"]}
        for group in groups
        if group.get("uri")
    ]


def _apply_tenant_units(result: dict, tenant) -> dict:
    updated = dict(result)
    for key, value in list(updated.items()):
        if key in tenant.unit_config:
            updated[key] = apply_units({key: value}, tenant.unit_config)[key]

    extra = updated.get("extra_json")
    if isinstance(extra, dict):
        updated["extra_json"] = apply_units(extra, tenant.unit_config)

    return updated


async def search(
    pt_client, ds_client, tenant, query: str, limit: int = 10
) -> list[dict]:
    """Two-path product search, matching the legacy Kray search flow at a
    generic level: if the query resolves to a recognized ontology
    category, filter the knowledge graph directly (precise); otherwise
    fall back to vector+keyword search over indexed product text
    (recall). Either path's results have the tenant's unit config applied
    before returning."""

    extracted = await pt_client.extract_relations(tenant.namespace, query)
    parse_tree_output = _to_plain_dict(extracted.get("parse_tree_output"))
    groups = parse_tree_output.get("groups") or []

    filters = _kg_filters_from_groups(groups)
    if filters:
        results = pt_client.query_kg_data(
            tenant.namespace, filters=filters, limit=limit
        )
        if results:
            return [_apply_tenant_units(r, tenant) for r in results]

    hits = ds_client.search(
        tenant.namespace,
        query=query,
        vector_field="embedding",
        keyword_field="title",
        limit=limit,
    )
    return [_apply_tenant_units(hit, tenant) for hit in hits]
