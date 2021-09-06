#!/bin/bash
rm groundzero_ddl/casev3.sql
rm groundzero_ddl/uacqid.sql
rm groundzero_ddl/exceptionmanager.sql
rm -rf git_cloned_src

mkdir -p git_cloned_src/uk/gov/ons/javareference/demojavaprocessor/models/entities
cp ../demo-java-processor/src/main/java/uk/gov/ons/javareference/demojavaprocessor/models/entities/* git_cloned_src/uk/gov/ons/javareference/demojavaprocessor/models/entities

mvn clean package

rm -rf git_cloned_src

java -jar target/ssdc-rm-ddl-1.0-SNAPSHOT.jar cases uk.gov.ons.javareference.demojavaprocessor.models.entities
