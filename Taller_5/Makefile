COMPOSE := docker compose

.PHONY: up down clean ps logs notebook status

up:
	$(COMPOSE) up -d

down:
	$(COMPOSE) down

clean:
	$(COMPOSE) down -v

ps:
	$(COMPOSE) ps

logs:
	$(COMPOSE) logs -f spark-iceberg rest

notebook:
	@echo "Jupyter disponible en: http://localhost:8888"
	$(COMPOSE) up -d

status:
	./scripts/status.sh
