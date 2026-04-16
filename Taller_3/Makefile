COMPOSE := docker compose

.PHONY: up down clean logs ps hdfs-init wordcount-mr wordcount-spark compare status

up:
	$(COMPOSE) up -d

down:
	$(COMPOSE) down

clean:
	$(COMPOSE) down -v

logs:
	$(COMPOSE) logs -f namenode resourcemanager spark-master

ps:
	$(COMPOSE) ps

hdfs-init:
	./scripts/bootstrap-hdfs.sh

wordcount-mr:
	./scripts/run-wordcount-mr.sh

wordcount-spark:
	./scripts/run-wordcount-spark.sh

compare:
	./scripts/compare.sh

status:
	./scripts/status.sh
