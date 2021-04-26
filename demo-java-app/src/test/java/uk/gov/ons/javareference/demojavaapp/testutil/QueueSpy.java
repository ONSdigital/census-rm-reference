package uk.gov.ons.javareference.demojavaapp.testutil;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.rabbitmq.http.client.domain.OutboundMessage;
import lombok.AllArgsConstructor;
import lombok.Getter;
import org.springframework.amqp.rabbit.listener.SimpleMessageListenerContainer;
import uk.gov.ons.javareference.demojavaapp.models.dtos.OutboundCase;
import uk.gov.ons.javareference.demojavaapp.utility.ObjectMapperFactory;


import java.io.IOException;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.TimeUnit;

import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertNull;

@AllArgsConstructor
public class QueueSpy implements AutoCloseable {
  private static final ObjectMapper objectMapper = ObjectMapperFactory.objectMapper();

  @Getter private BlockingQueue<String> queue;
  private SimpleMessageListenerContainer container;

  @Override
  public void close() throws Exception {
    container.stop();
  }

  public OutboundCase checkExpectedMessageReceived()
      throws IOException, InterruptedException {
    String actualMessage = queue.poll(20, TimeUnit.SECONDS);
    assertNotNull("Did not receive message before timeout", actualMessage);
    OutboundCase outboundCase =
        objectMapper.readValue(actualMessage, OutboundCase.class);
    assertNotNull(outboundCase);
    return outboundCase;
  }

  public void checkMessageIsNotReceived(int timeOut) throws InterruptedException {
    String actualMessage = queue.poll(timeOut, TimeUnit.SECONDS);
    assertNull("Message received when not expected", actualMessage);
  }
}
