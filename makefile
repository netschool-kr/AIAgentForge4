
# Makefile for local + ncloud
.RECIPEPREFIX := >
SHELL := /bin/bash

# 레지스트리/배포 변수(.env.ncr로 오버라이드)
-include .env.ncr
REGISTRY ?= aiagentforge.kr.ncr.ntruss.com
IMAGE    ?= aiapp
PLATFORM ?= linux/amd64
CONTEXT  ?= ncloud
NCP_HOST ?= root@YOUR_VM_IP

DATE := $(shell date +%Y%m%d-%H%M)
GIT  := $(shell git rev-parse --short HEAD 2>/dev/null || echo nogit)
TAG  ?= $(DATE)-$(GIT)
FULL := $(REGISTRY)/$(IMAGE):$(TAG)

.PHONY: help
help:
> @echo "Targets:"
> @echo "  up-local / down-local"
> @echo "  login-ncr  build-cloud  push-cloud  release-cloud"
> @echo "  context-cloud  up-cloud  down-cloud"
> @echo ""
> @echo "Vars: REGISTRY IMAGE PLATFORM TAG NCP_HOST"

# ── 로컬 개발(기존 docker-compose.yml 사용) ───────────────
.PHONY: up-local down-local
up-local:
> docker compose up -d
down-local:
> docker compose down

# ── Ncloud: 빌드/푸시(WSL에서 실행) ───────────────────────
.PHONY: login-ncr build-cloud push-cloud release-cloud
login-ncr:
> test -n "$$NCR_USER" -a -n "$$NCR_PASS" || (echo "set NCR_USER/NCR_PASS (env or .env.ncr)"; exit 1)
> echo "$$NCR_PASS" | docker login $(REGISTRY) -u "$$NCR_USER" --password-stdin

build-cloud:
> docker compose -f docker-compose.ncloud.yml \
>   --env-file .env.ncr \
>   build

push-cloud:
> docker compose -f docker-compose.ncloud.yml \
>   --env-file .env.ncr \
>   push

release-cloud: login-ncr build-cloud push-cloud
> echo "Released: $(FULL)"

# ── Ncloud: 원격 실행(원격에서 pull만, 빌드 없음) ────────
.PHONY: context-cloud up-cloud down-cloud
NCP_HOST ?= root@223.130.141.107

context-cloud:
>	@echo "Using NCP_HOST=$(NCP_HOST)"
>	docker context rm ncloud || true
>	docker context create ncloud --docker "host=ssh://$(NCP_HOST)"
>	docker context use ncloud


up-cloud:
> test -f .env || (echo ".env missing (app runtime)"; exit 1)
> docker --context $(CONTEXT) compose \
>   -f docker-compose.ncloud.run.yml \
>   --env-file .env.ncr \
>   pull
> docker --context $(CONTEXT) compose \
>   -f docker-compose.ncloud.run.yml \
>   --env-file .env.ncr \
>   up -d

down-cloud:
> docker --context $(CONTEXT) compose \
>   -f docker-compose.ncloud.run.yml \
>   --env-file .env.ncr \
>   down
