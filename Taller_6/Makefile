COMPOSE := docker compose

.PHONY: up down clean ps logs notebook ingest transform query pipeline status

up:
	$(COMPOSE) up -d

down:
	$(COMPOSE) down

clean:
	$(COMPOSE) down -v

ps:
	$(COMPOSE) ps

logs:
	$(COMPOSE) logs -f spark-iceberg trino

notebook:
	@echo "Jupyter disponible en: http://localhost:8888"
	$(COMPOSE) up -d

ingest:
	./scripts/ingest.sh

transform:
	./scripts/transform.sh

query:
	./scripts/query.sh

pipeline:
	./scripts/ingest.sh && ./scripts/transform.sh

status:
	./scripts/status.sh
