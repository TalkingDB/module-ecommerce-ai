from unittest.mock import MagicMock

from talkingdb_eai.services.ingest.orchestrator import sync_ontology


def make_tenant(unit_config=None):
    tenant = MagicMock()
    tenant.namespace = "acme"
    tenant.unit_config = unit_config or {}
    return tenant


def test_sync_ontology_registers_types_in_dependency_order():
    pt_client = MagicMock()
    ds_client = MagicMock()

    sync_ontology(
        pt_client,
        ds_client,
        make_tenant(),
        products=[],
        categories=[],
        object_attributes={"wheel_type": False},
    )

    registered_type_names = [
        call.kwargs["type_name"]
        for call in pt_client.register_ontology_type.call_args_list
    ]
    assert registered_type_names == ["category", "attribute", "wheel_type", "product"]


def test_sync_ontology_writes_categories_before_products():
    pt_client = MagicMock()
    ds_client = MagicMock()

    sync_ontology(
        pt_client,
        ds_client,
        make_tenant(),
        products=[
            {
                "sku": "CC-1",
                "name": "Caster",
                "category_ids": [1],
                "attributes": {},
            }
        ],
        categories=[{"id": 1, "name": "Casters"}],
        object_attributes={},
    )

    upsert_calls = pt_client.upsert_ontology_data.call_args_list
    assert len(upsert_calls) == 2
    category_batch = upsert_calls[0].args[1]
    product_batch = upsert_calls[1].args[1]
    assert category_batch[0]["src_id"] == "1"
    assert product_batch[0]["src_id"] == "CC-1"


def test_sync_ontology_writes_distinct_attribute_values_once():
    pt_client = MagicMock()
    ds_client = MagicMock()

    sync_ontology(
        pt_client,
        ds_client,
        make_tenant(),
        products=[
            {
                "sku": "CC-1",
                "name": "A",
                "category_ids": [],
                "attributes": {"wheel_type": "Swivel"},
            },
            {
                "sku": "CC-2",
                "name": "B",
                "category_ids": [],
                "attributes": {"wheel_type": "Swivel"},
            },
            {
                "sku": "CC-3",
                "name": "C",
                "category_ids": [],
                "attributes": {"wheel_type": "Rigid"},
            },
        ],
        categories=[],
        object_attributes={"wheel_type": False},
    )

    upsert_calls = pt_client.upsert_ontology_data.call_args_list
    # attribute-class nodes batch, then attribute-value nodes batch, then products
    attribute_class_batch = upsert_calls[0].args[1]
    attribute_value_batch = upsert_calls[1].args[1]
    assert [n["src_id"] for n in attribute_class_batch] == ["wheel_type"]
    assert {n["src_id"] for n in attribute_value_batch} == {
        "wheel_type:Swivel",
        "wheel_type:Rigid",
    }


def test_sync_ontology_trains_vectors_and_keywords_when_products_present():
    pt_client = MagicMock()
    ds_client = MagicMock()

    result = sync_ontology(
        pt_client,
        ds_client,
        make_tenant(),
        products=[
            {
                "sku": "CC-1",
                "name": "Swivel Caster",
                "description": "A swivel caster.",
                "category_ids": [],
                "attributes": {},
            }
        ],
        categories=[],
        object_attributes={},
    )

    ds_client.train_vectors.assert_called_once_with(
        "acme", [["CC-1"], ["Swivel Caster A swivel caster."]], vector_index=1
    )
    ds_client.train_keywords.assert_called_once_with(
        "acme",
        [{"id": "CC-1", "title": "Swivel Caster", "description": "A swivel caster."}],
        id_field="id",
    )
    assert result == {
        "categories_indexed": 0,
        "attributes_indexed": 0,
        "products_indexed": 1,
    }


def test_sync_ontology_skips_training_when_no_products():
    pt_client = MagicMock()
    ds_client = MagicMock()

    result = sync_ontology(
        pt_client,
        ds_client,
        make_tenant(),
        products=[],
        categories=[],
        object_attributes={},
    )

    ds_client.train_vectors.assert_not_called()
    ds_client.train_keywords.assert_not_called()
    assert result == {
        "categories_indexed": 0,
        "attributes_indexed": 0,
        "products_indexed": 0,
    }
