.PHONY: help build start stop auth-up observe metrics swagger

help:
	@echo "OPERATION COPPERCLAW — Available targets:"
	@echo ""
	@echo "  build       Build all Quarkus services (skips tests)"
	@echo "  start       Start the full stack (./scripts/start.sh)"
	@echo "  stop        Stop the stack (./scripts/stop.sh)"
	@echo "  auth-up     Start Keycloak identity provider (--profile auth)"
	@echo "  observe     Start Prometheus + Grafana (--profile observability)"
	@echo "  metrics     Scrape /q/metrics from all running agent services"
	@echo "  swagger     Print Swagger UI and API docs URLs"

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
