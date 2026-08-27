from unittest.mock import MagicMock

from talkingdb_eai.services.ontology.types import (
    register_attribute_class_type,
    register_category_type,
    register_object_attribute_type,
    register_product_type,
)


def test_register_category_type_declares_has_attributes_ref_edge():
    pt_client = MagicMock()

    register_category_type(pt_client, "acme")

    pt_client.register_ontology_type.assert_called_once_with(
        "acme",
        type_name="category",
        create_class=True,
        extra_attrs={"has_attributes": {"value_type": "[REF]"}},
        metadata={"class_type": "category"},
    )


def test_register_attribute_class_type():
    pt_client = MagicMock()

    register_attribute_class_type(pt_client, "acme")

    pt_client.register_ontology_type.assert_called_once_with(
        "acme",
        type_name="attribute",
        create_class=True,
        metadata={"class_type": "attribute"},
    )


def test_register_object_attribute_type():
    pt_client = MagicMock()

    register_object_attribute_type(pt_client, "acme", "wheel_type")

    pt_client.register_ontology_type.assert_called_once_with(
        "acme",
        type_name="wheel_type",
        create_instance=True,
        relationship_triples=[["instance_of", "wheel_type"]],
        metadata={"instance_type": "wheel_type"},
    )


def test_register_product_type_declares_ref_edges_for_object_attributes():
    pt_client = MagicMock()

    register_product_type(
        pt_client, "acme", {"wheel_type": False, "compatible_with": True}
    )

    pt_client.register_ontology_type.assert_called_once_with(
        "acme",
        type_name="product",
        create_instance=True,
        extra_attrs={
            "wheel_type": {"value_type": "REF"},
            "compatible_with": {"value_type": "[REF]"},
        },
        relationship_triples=[["instance_of", "category"]],
        metadata={"instance_type": "product"},
    )


def test_register_product_type_with_no_object_attributes():
    pt_client = MagicMock()

    register_product_type(pt_client, "acme")

    pt_client.register_ontology_type.assert_called_once_with(
        "acme",
        type_name="product",
        create_instance=True,
        extra_attrs={},
        relationship_triples=[["instance_of", "category"]],
        metadata={"instance_type": "product"},
    )
