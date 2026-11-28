# Troubleshooting

[Docs home](README.md) › Troubleshooting

| Symptom | Likely cause | Fix |
| :--- | :--- | :--- |
| `404` on any tenant route | The tenant ID is not in `tenants.json`, or the service reads another file | Check `GET /api/tenants`; set `EAI_TENANTS_CONFIG_PATH` if the file lives elsewhere |
| Sync fails asking for `..._STORE_API_UN` or `..._STORE_API_PWD` | The tenant's credential variables are not set | Export `<TENANT_ID upper>_STORE_API_UN` and `_PWD` before starting the service |
| Sync fails with 401 from the store | Wrong consumer key or secret, or the key lacks read access | Create a read key in WooCommerce and update the variables |
| Every search returns text hits, never graph results | NEL was not trained after sync, so no category resolves | `POST http://<parse-tree>/api/namespaces/<namespace>/ner/train` |
| A query with a colour or material ignores it | Only the category narrows the graph filter today | Known limitation; see the note in the [README](reference.md#two-path-search) |
| Text search fails: namespace not registered, or field errors | The document search namespace does not exist or lacks `embedding` and `title` | Create it as described in [usage](usage-and-examples.md#prepare-the-namespaces) |
| A unit shows twice or is replaced | `apply_unit` keeps only the leading number and appends the configured unit | Expected; store raw numbers in the catalogue, or remove the attribute from `unit_config` |
| Crawled guides never appear in results | The crawl went to a different namespace, or the fallback path was not reached because the graph returned rows | Check the tenant's namespace; graph results take priority over text hits |
| Works in direct mode but not API mode | `PT_HOST`, `DS_HOST` or `ST_HOST` not set with `CLIENT_MODE=api` | Set all three to the deployed services |
| `ModuleNotFoundError` for `talkingdb_pt`, `talkingdb_ds` or `talkingdb_st` | The pinned packages are not installed | `make sync MODE=git && poetry install` |

---

**Related:** [Architecture](architecture.md) · [Usage and examples](usage-and-examples.md) · [README](../README.md)
