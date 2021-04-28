# demo-java-app

# Queues

The adapter service connects to the following queues via the exhanges listed.

|Queue | Exchange | Direction |
|------|----------|-----------|
|case.sample.inbound |  | Input |
|case.sample.outbound | outbound-exchange | Output|

# Overview

This demo service shows a Java app connecting to rabbit and a DB.  
It consumes from one rabbit queue, persists to a DB and then publishes to another queue.
