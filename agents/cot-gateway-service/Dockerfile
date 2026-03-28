FROM registry.access.redhat.com/ubi9/openjdk-21:latest
WORKDIR /work
COPY target/quarkus-app/lib/ /work/lib/
COPY target/quarkus-app/*.jar /work/
COPY target/quarkus-app/app/ /work/app/
COPY target/quarkus-app/quarkus/ /work/quarkus/
ENV JAVA_OPTS="-Djava.util.logging.manager=org.jboss.logmanager.LogManager"
EXPOSE 8092
CMD ["java", "-jar", "/work/quarkus-run.jar"]
