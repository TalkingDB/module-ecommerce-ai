from unittest.mock import AsyncMock, MagicMock

import pytest

from talkingdb_eai.services.search.orchestrator import search

pytestmark = pytest.mark.anyio


def make_tenant(unit_config=None):
    tenant = MagicMock()
    tenant.namespace = "acme"
    tenant.unit_config = unit_config or {}
    return tenant


async def test_search_uses_kg_path_when_a_category_resolves():
    pt_client = MagicMock()
    pt_client.extract_relations = AsyncMock(
        return_value={
            "parse_tree_output": {
                "groups": [
                    {"uri": "category-casters", "instances": [], "attributes": []}
                ]
            }
        }
    )
    pt_client.query_kg_data.return_value = [{"node_id": "CC-1", "src_name": "Caster"}]
    ds_client = MagicMock()

    results = await search(pt_client, ds_client, make_tenant(), "swivel casters")

    pt_client.query_kg_data.assert_called_once_with(
        "acme",
        filters=[{"field": "instance_of", "op": "eq", "value": "category-casters"}],
        limit=10,
    )
    ds_client.search.assert_not_called()
    assert results == [{"node_id": "CC-1", "src_name": "Caster"}]


async def test_search_falls_back_to_vector_path_when_no_category_resolves():
    pt_client = MagicMock()
    pt_client.extract_relations = AsyncMock(
        return_value={"parse_tree_output": {"groups": []}}
    )
    ds_client = MagicMock()
    ds_client.search.return_value = [{"id": "CC-2", "title": "Rigid Caster"}]

    results = await search(pt_client, ds_client, make_tenant(), "heavy duty wheel")

    pt_client.query_kg_data.assert_not_called()
    ds_client.search.assert_called_once_with(
        "acme",
        query="heavy duty wheel",
        vector_field="embedding",
        keyword_field="title",
        limit=10,
    )
    assert results == [{"id": "CC-2", "title": "Rigid Caster"}]


async def test_search_falls_back_to_vector_path_when_kg_path_returns_nothing():
    pt_client = MagicMock()
    pt_client.extract_relations = AsyncMock(
        return_value={"parse_tree_output": {"groups": [{"uri": "category-casters"}]}}
    )
    pt_client.query_kg_data.return_value = []
    ds_client = MagicMock()
    ds_client.search.return_value = [{"id": "CC-2", "title": "Rigid Caster"}]

    results = await search(pt_client, ds_client, make_tenant(), "casters")

    ds_client.search.assert_called_once()
    assert results == [{"id": "CC-2", "title": "Rigid Caster"}]


async def test_search_normalizes_pydantic_parse_tree_output():
    class FakeExtractGroups:
        def model_dump(self):
            return {"groups": [{"uri": "category-casters"}]}

    pt_client = MagicMock()
    pt_client.extract_relations = AsyncMock(
        return_value={"parse_tree_output": FakeExtractGroups()}
    )
    pt_client.query_kg_data.return_value = [{"node_id": "CC-1"}]
    ds_client = MagicMock()

    results = await search(pt_client, ds_client, make_tenant(), "casters")

    pt_client.query_kg_data.assert_called_once_with(
        "acme",
        filters=[{"field": "instance_of", "op": "eq", "value": "category-casters"}],
        limit=10,
    )
    assert results == [{"node_id": "CC-1"}]


async def test_search_applies_tenant_unit_config_to_top_level_and_extra_json_fields():
    pt_client = MagicMock()
    pt_client.extract_relations = AsyncMock(
        return_value={"parse_tree_output": {"groups": [{"uri": "category-casters"}]}}
    )
    pt_client.query_kg_data.return_value = [
        {
            "node_id": "CC-1",
            "capacity": "250",
            "extra_json": {"weight": "12"},
        }
    ]
    ds_client = MagicMock()
    tenant = make_tenant({"capacity": "lbs", "weight": "kg"})

    results = await search(pt_client, ds_client, tenant, "casters")

    assert results[0]["capacity"] == "250 lbs"
    assert results[0]["extra_json"] == {"weight": "12 kg"}


async def test_search_respects_custom_limit():
    pt_client = MagicMock()
    pt_client.extract_relations = AsyncMock(
        return_value={"parse_tree_output": {"groups": []}}
    )
    ds_client = MagicMock()
    ds_client.search.return_value = []

    await search(pt_client, ds_client, make_tenant(), "casters", limit=5)

    assert ds_client.search.call_args.kwargs["limit"] == 5
