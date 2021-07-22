package uk.gov.ons.javareference.demojavaprocessor;

import static org.assertj.core.api.AssertionsForInterfaceTypes.assertThat;

import org.junit.Before;
import org.junit.jupiter.api.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit4.SpringJUnit4ClassRunner;
import org.springframework.transaction.annotation.Transactional;
import uk.gov.ons.javareference.demojavaprocessor.models.dtos.InboundCaseDto;
import uk.gov.ons.javareference.demojavaprocessor.models.dtos.OutboundCaseDto;
import uk.gov.ons.javareference.demojavaprocessor.models.entities.Case;
import uk.gov.ons.javareference.demojavaprocessor.models.repository.CaseRepository;
import uk.gov.ons.javareference.demojavaprocessor.testutil.QueueSpy;
import uk.gov.ons.javareference.demojavaprocessor.testutil.RabbitQueueHelper;

@ContextConfiguration
@ActiveProfiles("test")
@SpringBootTest
@RunWith(SpringJUnit4ClassRunner.class)
class SampleReceiverIT {

  @Autowired private RabbitQueueHelper rabbitQueueHelper;
  @Autowired private CaseRepository caseRepository;

  @Value("${queueconfig.outbound-queue}")
  private String outboundQueue;

  @Value("${queueconfig.inbound-queue}")
  private String inboundQueue;

  @Before
  @Transactional
  public void setUp() {
    rabbitQueueHelper.purgeQueue(inboundQueue);
    rabbitQueueHelper.purgeQueue(outboundQueue);
    caseRepository.deleteAllInBatch();
  }

  @Test
  public void writeMessageToInboundEndsUpOnOutboundQueue() throws Exception {

    try (QueueSpy caseQueueSpy = rabbitQueueHelper.listen("case.sample.outbound")) {
      // Given
      InboundCaseDto inboundCaseDto = new InboundCaseDto();
      inboundCaseDto.setAddressLine1("Hello");
      inboundCaseDto.setPostcode("World");

      // When
      rabbitQueueHelper.sendMessage("case.sample.inbound", inboundCaseDto);

      OutboundCaseDto outboundCaseDto = caseQueueSpy.checkExpectedMessageReceived();

      assertThat(outboundCaseDto.getAddressLine1()).isEqualTo("Hello");
      assertThat(outboundCaseDto.getPostcode()).isEqualTo("World");

      Case caze = caseRepository.findById(outboundCaseDto.getId()).get();

      assertThat(caze.getMetadata().getAddressString()).isEqualTo("Hello World");
    }
  }
}
