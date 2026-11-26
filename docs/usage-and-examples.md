# Usage and examples

[Docs home](README.md) › Usage and examples

```bash
EAI=http://localhost:8096
```

## Add a tenant

1. Add an entry to [`tenants.json`](../tenants.json). The key is the tenant ID.

   ```json
   {
     "demo_store": {
       "namespace": "demo_store",
       "store_api_url": "https://shop.example.com/wp-json/wc/v3",
       "unit_config": {"capacity": "lbs", "wheel_diameter": "in"}
     }
   }
   ```

2. Set the store's API credentials. The variable names are the tenant ID in upper case:

   ```bash
   export DEMO_STORE_STORE_API_UN=ck_xxxxxxxx
   export DEMO_STORE_STORE_API_PWD=cs_xxxxxxxx
   ```

   For WooCommerce these are the [REST API](https://developer.mozilla.org/en-US/docs/Glossary/REST) consumer key and secret ([how to create them](https://woocommerce.github.io/woocommerce-rest-api-docs/#authentication)).

3. Check it loaded:

   ```bash
   curl -s "$EAI/api/tenants"
   curl -s "$EAI/api/tenants/demo_store"
   ```

> [!CAUTION]
> Never put credentials in `tenants.json`. The file is committed; the environment is not.

## Prepare the namespaces

- In [package-document-search](https://github.com/TalkingDB/package-document-search/blob/main/docs/usage-and-examples.md), create a namespace named like the tenant's `namespace`, with an `id` primary key, an `embedding` vector field (1536 dimensions for `text-embedding-ada-002`) and a `title` field.
- In [package-named-entity-linker](https://github.com/TalkingDB/package-named-entity-linker/blob/main/docs/usage-and-examples.md), create the same namespace.

## Sync the catalogue

```bash
curl -s -X POST "$EAI/api/tenants/demo_store/sync" \
  -H "Content-Type: application/json" \
  -d '{"object_attributes": {"wheel_type": false, "mounting": true}}'
```

Returns `{"categories_indexed": ..., "attributes_indexed": ..., "products_indexed": ...}`.

Then teach NEL the new names, through parse-tree:

```bash
curl -s -X POST "http://localhost:8093/api/namespaces/demo_store/ner/train"
```

## Crawl extra content

Buying guides, FAQs and blog posts that the store API does not expose can be crawled into the same namespace:

```bash
curl -s -X POST "$EAI/api/tenants/demo_store/crawl" \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://shop.example.com/guides/choosing-casters"],
       "selectors": {"title": "h1", "body": "article"},
       "content_field": "body"}'
```

See [package-search-trainer](https://github.com/TalkingDB/package-search-trainer/blob/main/docs/usage-and-examples.md) for how selectors and chunks work.

## Search

```bash
curl -s -X POST "$EAI/api/tenants/demo_store/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "swivel casters for 250 lbs", "limit": 10}'
```

Returns a list of products or text hits, with the tenant's units applied. An unknown tenant ID returns `404`.

## Check which path a query took

There is no flag in the response yet. To see whether a query resolved to a category, ask parse-tree directly:

```bash
curl -s -X POST "http://localhost:8093/api/namespaces/demo_store/extract/relations" \
  -H "Content-Type: application/json" \
  -d '{"user_query": "swivel casters for 250 lbs"}'
```

If `parse_tree_output.groups` has a category with a `uri`, the search used the [knowledge graph](https://en.wikipedia.org/wiki/Knowledge_graph) path (as long as the graph returned rows).

---

**Related:** [Architecture](architecture.md) · [Troubleshooting](troubleshooting.md) · [README](../README.md)
