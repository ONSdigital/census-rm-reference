package uk.gov.ons.javareference.demojavaapp;

import com.rabbitmq.http.client.domain.OutboundMessage;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import uk.gov.ons.javareference.demojavaapp.models.dtos.CreateCaseSample;
import uk.gov.ons.javareference.demojavaapp.models.dtos.OutboundCase;
import uk.gov.ons.javareference.demojavaapp.models.repository.CaseRepository;
import uk.gov.ons.javareference.demojavaapp.testutil.QueueSpy;
import uk.gov.ons.javareference.demojavaapp.testutil.RabbitQueueHelper;

import static org.assertj.core.api.AssertionsForInterfaceTypes.assertThat;

@SpringBootTest
class DemoJavaAppApplicationTests {

  @Autowired
  private RabbitQueueHelper rabbitQueueHelper;
  @Autowired private CaseRepository caseRepository;

  @Test
  void contextLoads() {}

  @Test
  public void writeMessageToInboundEndsUpOnOutboundQueue() throws Exception {

    try (QueueSpy caseQueueSpy = rabbitQueueHelper.listen("case.sample.outbound"))
    {
      //Given
      CreateCaseSample createCaseSample = new CreateCaseSample();
      createCaseSample.setAddressLine1("Hello");
      createCaseSample.setPostcode("World");

      //When
      rabbitQueueHelper.sendMessage("case.sample.inbound", createCaseSample);


      OutboundCase outboundCase = caseQueueSpy.checkExpectedMessageReceived();

      assertThat(outboundCase.getAddressLine1()).isEqualTo("Hello");
      assertThat(outboundCase.getPostcode()).isEqualTo("World");

    }
  }
}
