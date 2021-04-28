# census-rm-docker-reference
## census-rm-docker-reference 
This is a simple version of the RM docker environment. It creates a docker environment consisting of rabbitmq, postgres and the demo java app.

The postgres and rabbitmq images use the standard ports for these services, so for instance the rabbitmq management page can be accessed at localhost:16672 with the username and passowrd of `guest:guest`.

#### Docker network
```
ERROR: Network censusrmdockerdev_reference declared as external, but could not be found. Please create the network manually using `docker network create censusrmdockerdev_reference` and try again.
make: *** [up] Error 1
```

- Run `docker network create censusrmdockerdev_reference` to create the docker network.

**NB:** Docker compose may warn you that the network is unused. This is a lie, it is in use. 