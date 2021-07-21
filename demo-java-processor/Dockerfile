FROM openjdk:11-jdk-slim

ARG JAR_FILE=census-rm-demo-java-app.jar*.jar

CMD ["/usr/local/openjdk-11/bin/java", "-jar", "/opt/census-rm-demo-java-app.jar"]
COPY healthcheck.sh /opt/healthcheck.sh
RUN chmod +x /opt/healthcheck.sh
RUN groupadd --gid 999  demo-java-app && \
    useradd --create-home --system --uid 999 --gid demo-java-app demo-java-app
USER demo-java-app

COPY target/$JAR_FILE /opt/census-rm-demo-java-app.jar