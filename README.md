# Catalog Indexing Engine

Efficient retrieval methods for fashion catalogs using a microservices-based architecture that supports both **structured** and **unstructured** search. 

## What this repo contains
- **Kafka Streaming/**: event-driven ingestion layer for catalog/product updates
- **Elastic Search/**: indexing + search infrastructure for low-latency retrieval 
- **search_api/**: API service to query/search the catalog (structured + semantic style queries) 
- **Product Relevancy/**: notebooks/experiments for ranking, relevancy tuning, evaluation
- **Data/**: datasets / sample data / utilities 
- **KubeFiles/**: Kubernetes manifests / deployment configs 
## High-level architecture
1. **Catalog events** (creates/updates/deletes) flow into **Kafka**
2. Consumers transform events into **Elasticsearch documents**
3. **Elasticsearch** serves low-latency retrieval
4. **search_api** exposes endpoints for search/filtering and relevance-aware ranking

## Getting started (local)
> Exact commands may vary by folder; use this as the intended workflow.

### Prerequisites
- Docker + Docker Compose
- Python 3.10+
- (Optional) Kubernetes + kubectl for cluster deploy

### Run dependencies
- Start Kafka + Elasticsearch locally (via docker-compose if provided in the repo), then:
  - Create topics / indices required by the consumers
  - Run streaming consumers to populate the index

### Run the API
- From `search_api/`:
  - create a virtual env, install deps, configure env vars, start the server

**Suggested env vars**
- `ELASTIC_URL` (e.g., `http://localhost:9200`)
- `KAFKA_BOOTSTRAP_SERVERS` (e.g., `localhost:9092`)
- `INDEX_NAME` (e.g., `catalog_products`)
- `LOG_LEVEL` (e.g., `INFO`)

## Deployment
- Kubernetes configs live in `KubeFiles/` for deploying:
  - Kafka consumers
  - Search API
  - Supporting services (as applicable) 

## Evaluation / Relevancy work
- `Product Relevancy/` contains analysis and experiments for:
  - improving ranking quality
  - tuning retrieval strategies
  - measuring precision/recall / offline metrics

## Contributing
- Keep services loosely coupled (events > direct calls where possible)
- Add tests for any query/ranking logic changes
- Document any new topics/indices and their schemas


