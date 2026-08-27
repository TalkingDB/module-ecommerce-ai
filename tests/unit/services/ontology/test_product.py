from talkingdb_eai.services.ontology.product import (
    attribute_class_node,
    attribute_value_node,
    category_node,
    product_node,
)


def test_category_node_maps_basic_fields():
    node = category_node({"id": 12, "name": "Casters"})

    assert node == {
        "src_id": "12",
        "class_type": "category",
        "src_name": "Casters",
        "alternate_names": ["Casters"],
    }


def test_category_node_includes_description_as_contains():
    node = category_node({"id": 12, "name": "Casters", "description": "Wheels."})

    assert node["contains"] == "Wheels."


def test_category_node_includes_parent_as_subclass_of():
    node = category_node({"id": 12, "name": "Swivel Casters", "parent_id": 1})

    assert node["subclass_of"] == "1"


def test_category_node_omits_optional_fields_when_absent():
    node = category_node({"id": 12, "name": "Casters", "parent_id": None})

    assert "contains" not in node
    assert "subclass_of" not in node


def test_attribute_class_node():
    node = attribute_class_node("wheel_type", "Wheel Type")

    assert node == {
        "src_id": "wheel_type",
        "class_type": "attribute",
        "src_name": "Wheel Type",
    }


def test_attribute_value_node_links_back_to_its_attribute_class():
    node = attribute_value_node("wheel_type", "Swivel")

    assert node == {
        "src_id": "wheel_type:Swivel",
        "instance_type": "wheel_type",
        "src_name": "Swivel",
        "alternate_names": ["Swivel"],
        "instance_of": ["wheel_type"],
    }


def test_product_node_maps_core_fields_and_category_edges():
    node = product_node(
        {
            "sku": "CC-100",
            "name": "Swivel Caster",
            "description": "A swivel caster.",
            "url": "https://acme.example.com/products/cc-100",
            "category_ids": [12, 13],
            "attributes": {},
        },
        object_attributes={},
        unit_config={},
    )

    assert node == {
        "src_id": "CC-100",
        "instance_type": "product",
        "src_name": "Swivel Caster",
        "alternate_names": ["Swivel Caster"],
        "instance_of": ["12", "13"],
        "src_url": "https://acme.example.com/products/cc-100",
        "contains": "A swivel caster.",
    }


def test_product_node_falls_back_to_id_when_no_sku():
    node = product_node(
        {"id": 99, "name": "Caster", "category_ids": [], "attributes": {}},
        object_attributes={},
        unit_config={},
    )

    assert node["src_id"] == "99"


def test_product_node_resolves_object_attributes_to_value_node_ids():
    node = product_node(
        {
            "sku": "CC-100",
            "name": "Swivel Caster",
            "category_ids": [],
            "attributes": {"wheel_type": "Swivel", "compatible_with": ["A", "B"]},
        },
        object_attributes={"wheel_type": False, "compatible_with": True},
        unit_config={},
    )

    assert node["wheel_type"] == ["wheel_type:Swivel"]
    assert node["compatible_with"] == ["compatible_with:A", "compatible_with:B"]


def test_product_node_applies_tenant_unit_config_to_literal_attributes():
    node = product_node(
        {
            "sku": "CC-100",
            "name": "Swivel Caster",
            "category_ids": [],
            "attributes": {"capacity": "250"},
        },
        object_attributes={},
        unit_config={"capacity": "lbs"},
    )

    assert node["capacity"] == "250 lbs"
