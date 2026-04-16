COMPOSE := docker compose

.PHONY: up down clean logs ps hdfs-init wordcount status

up:
	$(COMPOSE) up -d

down:
	$(COMPOSE) down

clean:
	$(COMPOSE) down -v

logs:
	$(COMPOSE) logs -f namenode resourcemanager

ps:
	$(COMPOSE) ps

hdfs-init:
	./scripts/bootstrap-hdfs.sh

wordcount:
	./scripts/run-wordcount.sh

status:
	./scripts/status.sh
