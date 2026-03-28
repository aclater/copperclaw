FROM registry.access.redhat.com/ubi9/openjdk-21:latest
WORKDIR /work
COPY target/quarkus-app/lib/ /work/lib/
COPY target/quarkus-app/*.jar /work/
COPY target/quarkus-app/app/ /work/app/
COPY target/quarkus-app/quarkus/ /work/quarkus/
COPY agents/develop-service/system-prompt.md /work/system-prompt.md
ENV JAVA_OPTS="-Djava.util.logging.manager=org.jboss.logmanager.LogManager"
ENV SYSTEM_PROMPT_PATH=/work/system-prompt.md
EXPOSE 8088
CMD ["java", "-jar", "/work/quarkus-run.jar"]
