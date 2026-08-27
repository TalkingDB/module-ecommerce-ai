import responses

from talkingdb_eai.services.connectors.woocommerce import (
    WooCommerceError,
    fetch_categories,
    fetch_entity,
    fetch_products,
)

STORE_URL = "https://acme.example.com/wp-json/wc/v3"


@responses.activate
def test_fetch_entity_returns_a_single_page():
    responses.add(
        responses.GET,
        f"{STORE_URL}/products",
        json=[{"id": 1}, {"id": 2}],
        status=200,
    )

    result = fetch_entity(STORE_URL, "user", "pass", "products", page_size=100)

    assert result == [{"id": 1}, {"id": 2}]
    request = responses.calls[0].request
    assert request.params == {"page": "1", "per_page": "100"}


@responses.activate
def test_fetch_entity_paginates_until_a_short_page():
    responses.add(
        responses.GET,
        f"{STORE_URL}/products",
        json=[{"id": i} for i in range(2)],
        status=200,
    )
    responses.add(
        responses.GET,
        f"{STORE_URL}/products",
        json=[{"id": 2}],
        status=200,
    )

    result = fetch_entity(STORE_URL, "user", "pass", "products", page_size=2)

    assert result == [{"id": 0}, {"id": 1}, {"id": 2}]
    assert len(responses.calls) == 2
    assert responses.calls[1].request.params["page"] == "2"


@responses.activate
def test_fetch_entity_stops_on_empty_page():
    responses.add(
        responses.GET,
        f"{STORE_URL}/products",
        json=[],
        status=200,
    )

    result = fetch_entity(STORE_URL, "user", "pass", "products")

    assert result == []
    assert len(responses.calls) == 1


@responses.activate
def test_fetch_entity_raises_woocommerce_error_on_non_200():
    responses.add(
        responses.GET,
        f"{STORE_URL}/products",
        status=401,
        body="unauthorized",
    )

    try:
        fetch_entity(STORE_URL, "user", "pass", "products")
        assert False, "expected WooCommerceError"
    except WooCommerceError as exc:
        assert "401" in str(exc)


@responses.activate
def test_fetch_entity_sends_basic_auth():
    responses.add(responses.GET, f"{STORE_URL}/products", json=[], status=200)

    fetch_entity(STORE_URL, "ck_user", "cs_pass", "products")

    auth_header = responses.calls[0].request.headers["Authorization"]
    assert auth_header.startswith("Basic ")


@responses.activate
def test_fetch_products_hits_products_entity():
    responses.add(responses.GET, f"{STORE_URL}/products", json=[{"id": 1}], status=200)

    result = fetch_products(STORE_URL, "user", "pass")

    assert result == [{"id": 1}]


@responses.activate
def test_fetch_categories_hits_categories_entity():
    responses.add(
        responses.GET,
        f"{STORE_URL}/products/categories",
        json=[{"id": 1, "name": "Casters"}],
        status=200,
    )

    result = fetch_categories(STORE_URL, "user", "pass")

    assert result == [{"id": 1, "name": "Casters"}]
