from talkingdb_eai.services.units import apply_unit


def category_node(category: dict) -> dict:
    """category: {id, name, parent_id (optional), description (optional)}."""

    node = {
        "src_id": str(category["id"]),
        "class_type": "category",
        "src_name": category["name"],
        "alternate_names": [category["name"]],
    }
    if category.get("description"):
        node["contains"] = category["description"]
    if category.get("parent_id"):
        node["subclass_of"] = str(category["parent_id"])
    return node


def attribute_class_node(attribute_name: str, display_name: str) -> dict:
    return {
        "src_id": attribute_name,
        "class_type": "attribute",
        "src_name": display_name,
    }


def attribute_value_node(attribute_name: str, value: str) -> dict:
    return {
        "src_id": f"{attribute_name}:{value}",
        "instance_type": attribute_name,
        "src_name": str(value),
        "alternate_names": [str(value)],
        "instance_of": [attribute_name],
    }


def product_node(
    product: dict, object_attributes: dict[str, bool], unit_config: dict[str, str]
) -> dict:
    """product: {sku or id, name, description (optional), url (optional),
    category_ids: list, attributes: {name: value or list[value]}} where an
    object attribute's value(s) are the raw attribute values (this
    function resolves them to attribute-value node ids), and a literal
    attribute's value is a raw scalar (this function applies the tenant's
    unit config to it)."""

    node = {
        "src_id": str(product.get("sku") or product["id"]),
        "instance_type": "product",
        "src_name": product.get("name", ""),
        "alternate_names": [product["name"]] if product.get("name") else [],
        "instance_of": [str(cid) for cid in product.get("category_ids", [])],
    }
    if product.get("url"):
        node["src_url"] = product["url"]
    if product.get("description"):
        node["contains"] = product["description"]

    for attr_name, value in (product.get("attributes") or {}).items():
        if attr_name in object_attributes:
            values = value if isinstance(value, list) else [value]
            node[attr_name] = [f"{attr_name}:{v}" for v in values]
        else:
            node[attr_name] = apply_unit(attr_name, value, unit_config)

    return node
