from talkingdb_eai.services.ontology import product as product_ontology
from talkingdb_eai.services.ontology import types as ontology_types


def sync_ontology(
    pt_client,
    ds_client,
    tenant,
    products: list[dict],
    categories: list[dict],
    object_attributes: dict[str, bool],
) -> dict:
    """Register ontology types, then write categories, attribute-value
    nodes, and products into package-parse-tree, and index product
    title+description into package-document-search for vector/keyword
    search. Idempotent: re-running with the same data just upserts.

    The target namespace's document-search namespace/index (and its
    output-field config) must already exist - this only trains data into
    it, matching package-search-trainer's orchestrator convention.
    """

    ontology_types.register_category_type(pt_client, tenant.namespace)
    ontology_types.register_attribute_class_type(pt_client, tenant.namespace)
    for attribute_name in object_attributes:
        ontology_types.register_object_attribute_type(
            pt_client, tenant.namespace, attribute_name
        )
    ontology_types.register_product_type(pt_client, tenant.namespace, object_attributes)

    category_nodes = [product_ontology.category_node(c) for c in categories]
    if category_nodes:
        pt_client.upsert_ontology_data(tenant.namespace, category_nodes)

    distinct_values: dict[str, set] = {name: set() for name in object_attributes}
    for product in products:
        for attr_name, value in (product.get("attributes") or {}).items():
            if attr_name not in object_attributes:
                continue
            values = value if isinstance(value, list) else [value]
            distinct_values.setdefault(attr_name, set()).update(
                str(v) for v in values if v
            )

    attribute_class_nodes = [
        product_ontology.attribute_class_node(name, name.replace("_", " ").title())
        for name in object_attributes
    ]
    if attribute_class_nodes:
        pt_client.upsert_ontology_data(tenant.namespace, attribute_class_nodes)

    attribute_value_nodes = [
        product_ontology.attribute_value_node(name, value)
        for name, values in distinct_values.items()
        for value in values
    ]
    if attribute_value_nodes:
        pt_client.upsert_ontology_data(tenant.namespace, attribute_value_nodes)

    product_nodes = [
        product_ontology.product_node(product, object_attributes, tenant.unit_config)
        for product in products
    ]
    if product_nodes:
        pt_client.upsert_ontology_data(tenant.namespace, product_nodes)

    ids = [node["src_id"] for node in product_nodes]
    contents = [
        f"{p.get('name', '')} {p.get('description', '')}".strip() for p in products
    ]
    keyword_docs = [
        {
            "id": node["src_id"],
            "title": p.get("name", ""),
            "description": p.get("description", ""),
        }
        for node, p in zip(product_nodes, products)
    ]

    if ids:
        ds_client.train_vectors(tenant.namespace, [ids, contents], vector_index=1)
        ds_client.train_keywords(tenant.namespace, keyword_docs, id_field="id")

    return {
        "categories_indexed": len(category_nodes),
        "attributes_indexed": len(attribute_value_nodes),
        "products_indexed": len(product_nodes),
    }
