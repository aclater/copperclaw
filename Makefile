# Portable container name lookup — works with _1, -1, or bare suffix
define get_container
$(shell podman ps --format "{{.Names}}" \
  | grep "copperclaw[_-]$(1)" | head -1)
endef

.PHONY: help build start stop auth-up observe metrics swagger logs-errors logs-live logs-request

help:
	@echo "OPERATION COPPERCLAW — Available targets:"
	@echo ""
	@echo "  build          Build all Quarkus services (skips tests)"
	@echo "  start          Start the full stack (./scripts/start.sh)"
	@echo "  stop           Stop the stack (./scripts/stop.sh)"
	@echo "  auth-up        Start Keycloak identity provider (--profile auth)"
	@echo "  observe        Start Prometheus + Grafana (--profile observability)"
	@echo "  metrics        Scrape /q/metrics from all running agent services"
	@echo "  swagger        Print Swagger UI and API docs URLs"
	@echo "  logs-errors    Show recent errors across services"
	@echo "  logs-live      Tail all service logs in real time"
	@echo "  logs-request   Show recent operator HTTP requests"

build:
	mvn install -f shared-java/pom.xml -DskipTests
	mvn package -f parent-pom.xml -DskipTests

start:
	./scripts/start.sh

stop:
	./scripts/stop.sh

auth-up:
	podman-compose --profile auth up -d keycloak
	@echo "Keycloak: http://localhost:8180"
	@echo "Login: admin / copperclaw"

observe:
	podman-compose --profile observability up -d prometheus grafana
	@echo "Prometheus: http://localhost:9090"
	@echo "Grafana: http://localhost:3001"
	@echo "Login: admin / copperclaw"

metrics:
	@echo "Agent service metrics:"
	@for port in 8081 8082 8083 8084 8085 8086 8087 8088 8089 8090 8091 8092; do \
	  echo "--- $$port ---"; \
	  curl -s http://localhost:$$port/q/metrics \
	    | grep "^jvm_\|^http_\|^kafka_" \
	    | head -3; \
	done

swagger:
	@echo "State API: http://localhost:8089/q/swagger-ui"
	@echo "Operator API: http://localhost:8000/docs"

logs-errors:
	@echo "=== nginx errors ===" && \
	podman logs $(call get_container,frontend) 2>&1 \
	  | grep -E "error|warn|502|503|404" \
	  | tail -20 || true
	@echo "=== operator errors ===" && \
	podman logs $(call get_container,operator-service) 2>&1 \
	  | grep -E "ERROR|WARNING|EXCEPTION|←\ [45]" \
	  | tail -20 || true
	@echo "=== ramalama errors ===" && \
	podman logs $(call get_container,ramalama) 2>&1 \
	  | grep -E "error|Error|CUDA|cuda" \
	  | tail -10 || true

logs-live:
	@echo "Tailing all service logs — Ctrl+C to stop"
	@podman logs -f $(call get_container,frontend) \
	  --since 0s 2>&1 | sed 's/^/[nginx] /' &
	@podman logs -f $(call get_container,operator-service) \
	  --since 0s 2>&1 | sed 's/^/[operator] /' &
	@podman logs -f $(call get_container,sse-bridge-service) \
	  --since 0s 2>&1 | sed 's/^/[sse] /' &
	@wait

logs-request:
	@echo "Recent operator requests:"
	@podman logs $(call get_container,operator-service) 2>&1 \
	  | grep -E "^[0-9].*[←→✗]" \
	  | tail -30 || true
