Feature: Rabbitmq messages go in and out

  Scenario: Message in, message out
    Given a message is put on the inbound queue
    And a message is put on the outbound queue
    When a print action rule has been created
    And a print file is created with correct rows
    

