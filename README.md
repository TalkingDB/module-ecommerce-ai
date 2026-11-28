<!-- short-readme -->
<h1 align="center">module-ecommerce-ai</h1>

<p align="center"><b>Natural language product search for online stores.</b></p>

<p align="center"><a href="#try-it">Try it</a> · <a href="docs/architecture.md">How it works</a> · <a href="docs/usage-and-examples.md">Usage and examples</a> · <a href="docs/troubleshooting.md">Troubleshooting</a> · <a href="docs/reference.md">Full reference</a></p>

<p align="center"><a href="https://github.com/TalkingDB/module-ecommerce-ai/stargazers"><img src="https://img.shields.io/github/stars/TalkingDB/module-ecommerce-ai?style=social" alt="GitHub stars"></a></p>

<p align="center">
  <img src="docs/images/demo.gif" alt="Animated demo of a real run: 'swivel casters' resolves to a category and filters the knowledge graph; 'heavy duty wheel' resolves nothing and falls back to vector plus keyword search">
</p>
<p align="center"><sub>A real run of the search orchestrator at <code>e4c037b</code> with stubbed stores, on the two cases in <code>tests/unit/services/search/test_orchestrator.py</code>.</sub></p>

It syncs a store's catalogue into a TalkingDB ontology and a search index. When it understands a query it filters the [knowledge graph](https://en.wikipedia.org/wiki/Knowledge_graph) by category; when it does not, it falls back to text search.

## What it does

- **Sync** a catalogue from WooCommerce into products and an ontology ([what sync does](docs/architecture.md)).
- **Understand** the query with [package-parse-tree](https://github.com/TalkingDB/package-parse-tree), then filter by category.
- **Fall back** to vector plus keyword search in [package-document-search](https://github.com/TalkingDB/package-document-search), with the store's units applied ([examples](docs/usage-and-examples.md)).

## Try it

```bash
make sync MODE=git
poetry install
make test
make local              # API on http://localhost:8096, Swagger at /docs
```

Needs a running [package-named-entity-linker](https://github.com/TalkingDB/package-named-entity-linker), Milvus or Milvus Lite, and an `OPENAI_API_KEY`.

## Where it fits

The shop-specific layer over [package-parse-tree](https://github.com/TalkingDB/package-parse-tree) and [package-document-search](https://github.com/TalkingDB/package-document-search).

## Learn more

| Page | Read it to |
| :--- | :--- |
| [How it works](docs/architecture.md) | see the parts and how data moves |
| [Usage and examples](docs/usage-and-examples.md) | copy working examples |
| [Troubleshooting](docs/troubleshooting.md) | fix a problem |
| [Full reference](docs/reference.md) | read everything that used to be on this page |
| [All docs](docs/README.md) | see every page |

## Support TalkingDB

If module-ecommerce-ai saved you time, please [give it a star](https://github.com/TalkingDB/module-ecommerce-ai) ⭐. Stars help other developers find the project.

Found a bug, or a document it gets wrong? [Open an issue](https://github.com/TalkingDB/module-ecommerce-ai/issues/new). We are always here to help and open to a conversation. Explore the TalkingDB applications at [talkingdb.io](https://talkingdb.io/#applications).

## License

> [!NOTE]
> This repository does not have a LICENSE file yet. Most TalkingDB repositories are licensed under [AGPL-3.0](https://www.gnu.org/licenses/agpl-3.0.html); until a LICENSE file is added here, no license is granted by this README.
