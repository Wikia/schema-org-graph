# schema-org-graph

[![Build Status](https://travis-ci.com/Wikia/schema-org-graph.svg?branch=master)](https://travis-ci.com/Wikia/schema-org-graph)

Map articles metadata and relationship to schema.org entities and stores them in graph database

## Run it

```
docker-compose up
```

[`redisgraph`](https://oss.redislabs.com/redisgraph/) binds to a local port `56379`:

```
redis-cli -p 56379
```
