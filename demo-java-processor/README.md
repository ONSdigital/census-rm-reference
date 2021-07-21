# demo-java-processor

# Queues

The adapter service connects to the following queues via the exhanges listed.

|Queue | Exchange | Direction |
|------|----------|-----------|
|case.sample.inbound |  | Input |
|case.sample.outbound | outbound-exchange | Output|
|caseProcessor.printFileSvc.printBatchRow |  | Output|

# Overview

This demo processor shows a Java app connecting to rabbit and a DB.
It consumes from one rabbit queue, persists to a DB and then publishes to another queue.
It also has a scheduler which can run 'rules' at a specified date/time, to send bulk messages.
