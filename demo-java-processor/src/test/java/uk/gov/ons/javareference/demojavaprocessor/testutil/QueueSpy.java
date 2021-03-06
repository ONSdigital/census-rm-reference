package uk.gov.ons.javareference.demojavaprocessor.testutil;

import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertNull;

import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.IOException;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.TimeUnit;
import lombok.AllArgsConstructor;
import lombok.Getter;
import org.springframework.amqp.rabbit.listener.SimpleMessageListenerContainer;
import uk.gov.ons.javareference.demojavaprocessor.models.dtos.OutboundCaseDto;
import uk.gov.ons.javareference.demojavaprocessor.utility.ObjectMapperFactory;

@AllArgsConstructor
public class QueueSpy implements AutoCloseable {
  private static final ObjectMapper objectMapper = ObjectMapperFactory.objectMapper();

  @Getter private BlockingQueue<String> queue;
  private SimpleMessageListenerContainer container;

  @Override
  public void close() throws Exception {
    container.stop();
  }

  public OutboundCaseDto checkExpectedMessageReceived() throws IOException, InterruptedException {
    String actualMessage = queue.poll(20, TimeUnit.SECONDS);
    assertNotNull("Did not receive message before timeout", actualMessage);
    OutboundCaseDto outboundCaseDto = objectMapper.readValue(actualMessage, OutboundCaseDto.class);
    assertNotNull(outboundCaseDto);
    return outboundCaseDto;
  }

  public void checkMessageIsNotReceived(int timeOut) throws InterruptedException {
    String actualMessage = queue.poll(timeOut, TimeUnit.SECONDS);
    assertNull("Message received when not expected", actualMessage);
  }
}
