package uk.gov.ons.javareference.demojavaapp;

import static org.assertj.core.api.AssertionsForInterfaceTypes.assertThat;

import org.junit.jupiter.api.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringJUnit4ClassRunner;
import uk.gov.ons.javareference.demojavaapp.models.dtos.CreateCaseSample;
import uk.gov.ons.javareference.demojavaapp.models.dtos.OutboundCase;
import uk.gov.ons.javareference.demojavaapp.testutil.QueueSpy;
import uk.gov.ons.javareference.demojavaapp.testutil.RabbitQueueHelper;

@ContextConfiguration
@ActiveProfiles("test")
@SpringBootTest
@RunWith(SpringJUnit4ClassRunner.class)
class SampleReceiverIT {

  @Autowired private RabbitQueueHelper rabbitQueueHelper;

  @Test
  public void writeMessageToInboundEndsUpOnOutboundQueue() throws Exception {

    try (QueueSpy caseQueueSpy = rabbitQueueHelper.listen("case.sample.outbound")) {
      // Given
      CreateCaseSample createCaseSample = new CreateCaseSample();
      createCaseSample.setAddressLine1("Hello");
      createCaseSample.setPostcode("World");

      // When
      rabbitQueueHelper.sendMessage("case.sample.inbound", createCaseSample);

      OutboundCase outboundCase = caseQueueSpy.checkExpectedMessageReceived();

      assertThat(outboundCase.getAddressLine1()).isEqualTo("Hello");
      assertThat(outboundCase.getPostcode()).isEqualTo("World");
    }
  }
}
