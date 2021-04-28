# A collection of reference implementations of the technologies used by the census-rm team

## Contents
### demo-java-app

### census-rm-docker-reference 
This is a simple version of the RM docker environment. It creates a docker environment consisting of rabbitmq, postgres and the demo java app.

The postgres and rabbitmq images use the standard ports for these services, so for instance the rabbitmq management page can be accessed at localhost:16672 with the username and passowrd of `guest:guest`.

#### Docker network
```
ERROR: Network censusrmdockerdev_reference declared as external, but could not be found. Please create the network manually using `docker network create censusrmdockerdev_reference` and try again.
make: *** [up] Error 1
```

- Run `docker network create censusrmdockerdev_reference` to create the docker network.

**NB:** Docker compose may warn you that the network is unused. This is a lie, it is in use. 

### reference-acceptance-tests
The acceptance test is currently a simple test that submits a message onto the inbound queue, and checks that a message appears on the outbound queue.
It uses behave and python 3.7.*.

## Running the environment
1. Clone this repository to your local machine
1. Navigate into the `demo-java-app` directory and run `maven clean install` and wait for this to complete
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