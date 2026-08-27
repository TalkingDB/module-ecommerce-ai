from typing import Optional


def register_category_type(pt_client, namespace: str) -> dict:
    return pt_client.register_ontology_type(
        namespace,
        type_name="category",
        create_class=True,
        extra_attrs={"has_attributes": {"value_type": "[REF]"}},
        metadata={"class_type": "category"},
    )


def register_attribute_class_type(pt_client, namespace: str) -> dict:
    return pt_client.register_ontology_type(
        namespace,
        type_name="attribute",
        create_class=True,
        metadata={"class_type": "attribute"},
    )


def register_object_attribute_type(
    pt_client, namespace: str, attribute_name: str
) -> dict:
    return pt_client.register_ontology_type(
        namespace,
        type_name=attribute_name,
        create_instance=True,
        relationship_triples=[["instance_of", attribute_name]],
        metadata={"instance_type": attribute_name},
    )


def register_product_type(
    pt_client, namespace: str, object_attributes: Optional[dict[str, bool]] = None
) -> dict:
    """object_attributes maps an attribute name to whether it's multi-valued
    on a product (True -> "[REF]" list edge, False -> "REF" single edge).
    Only object (categorical) attributes need declaring here - literal
    (free-text/numeric) attributes are written as plain scalar values on
    the product node and need no type declaration."""

    extra_attrs = {
        name: {"value_type": "[REF]" if is_multi else "REF"}
        for name, is_multi in (object_attributes or {}).items()
    }
    return pt_client.register_ontology_type(
        namespace,
        type_name="product",
        create_instance=True,
        extra_attrs=extra_attrs,
        relationship_triples=[["instance_of", "category"]],
        metadata={"instance_type": "product"},
    )
