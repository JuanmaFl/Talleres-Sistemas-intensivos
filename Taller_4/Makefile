COMPOSE := docker compose

.PHONY: up down clean ps logs notebook status run-job

up:
	$(COMPOSE) up -d

down:
	$(COMPOSE) down

clean:
	$(COMPOSE) down -v

ps:
	$(COMPOSE) ps

logs:
	$(COMPOSE) logs -f spark-master jupyter

notebook:
	@echo "Jupyter disponible en: http://localhost:8888 (token: taller4)"
	$(COMPOSE) up -d

run-job:
	./scripts/run-job.sh

status:
	./scripts/status.sh
