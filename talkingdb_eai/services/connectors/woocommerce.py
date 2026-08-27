import requests

DEFAULT_PAGE_SIZE = 100
DEFAULT_TIMEOUT_SECONDS = 30


class WooCommerceError(Exception):
    pass


def fetch_entity(
    store_api_url: str,
    username: str,
    password: str,
    entity: str,
    page_size: int = DEFAULT_PAGE_SIZE,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
) -> list[dict]:
    """Fetch every page of a WooCommerce REST API entity (e.g. "products",
    "products/categories"). Generic by design - which store, which
    credentials, and which entity are all caller-supplied; nothing here
    is tied to any specific tenant's store URL or catalog shape."""

    results: list[dict] = []
    page = 1

    while True:
        response = requests.get(
            f"{store_api_url}/{entity}",
            params={"page": page, "per_page": page_size},
            auth=(username, password),
            timeout=timeout,
        )
        if response.status_code != 200:
            raise WooCommerceError(
                f"WooCommerce API error {response.status_code} fetching "
                f"{entity} page {page}: {response.text}"
            )

        batch = response.json()
        if not batch:
            break

        results.extend(batch)
        if len(batch) < page_size:
            break
        page += 1

    return results


def fetch_products(store_api_url: str, username: str, password: str) -> list[dict]:
    return fetch_entity(store_api_url, username, password, "products")


def fetch_categories(store_api_url: str, username: str, password: str) -> list[dict]:
    return fetch_entity(store_api_url, username, password, "products/categories")
