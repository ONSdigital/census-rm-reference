# A collection of reference implementations of the technologies used by the census-rm team

## Contents
### demo-java-processor
This demo processor shows a Java app connecting to rabbit and a DB.
It consumes from one rabbit queue, persists to a DB and then publishes to another queue.
It also has a scheduler which can run 'rules' at a specified date/time, to send bulk messages.

### demo-print-file-service
This demo print file service assembles batches of messages into files, encrypts and uploads to SFTP.

### census-rm-docker-reference 
This is a simple version of the RM docker environment. It creates a docker environment consisting of rabbitmq, postgres and the demo java app.

The postgres and rabbitmq images use the standard ports for these services, so for instance the rabbitmq management page can be accessed at localhost:16672 with the username and passowrd of `guest:guest`.

### reference-acceptance-tests
The acceptance test is currently a simple test that submits a message onto the inbound queue, and checks that a message appears on the outbound queue.
It uses behave and python 3.7.*.

## Running the environment
1. Clone this repository to your local machine
1. Navigate into the `demo-java-processor` directory and run `mvn clean install` and wait for this to complete
1. Navigate into the `demo-print-file-service` directory and run `make test` and wait for this to complete
1. Navigate into the `census-rm-docker-reference` directoy and run `make up` to run the docker environment
1. Navigate into the `reference-acceptance-tests` directory and run:
    1. `make install` to set up your python environment
    1. `make test` to run the acceptance tests

Instead of running the acceptance tests, you can submit messages manually into rabbitmq.
To do so, place a message using the following format onto the **`case.sample.inbound`** queue:
```json
{
   "addressLine1":"blah blah blah",
   "postcode":"bl4 61a"
}
```

Then, you can manually set up an action rule by running the following SQL into the database:
```sql
INSERT INTO cases.action_rule (id, classifiers, has_triggered, trigger_date_time)
VALUES('27773350-70b8-42a3-9728-d1f398b19283','','f','2021-07-21T12:28.000Z')
```