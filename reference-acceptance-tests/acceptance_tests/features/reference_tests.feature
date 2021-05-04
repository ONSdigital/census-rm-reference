Feature: Rabbitmq messages go in and out

  Scenario: Message in, message out
    When a message is put on the inbound queue
    Then a message is put on the outbound queue
    

