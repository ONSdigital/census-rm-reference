package uk.gov.ons.javareference.demojavaprocessor.messaging;

import static uk.gov.ons.javareference.demojavaprocessor.utility.MsgDateHelper.getMsgTimeStamp;

import java.time.OffsetDateTime;
import java.util.Optional;
import java.util.UUID;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.integration.annotation.MessageEndpoint;
import org.springframework.integration.annotation.ServiceActivator;
import org.springframework.messaging.Message;
import org.springframework.transaction.annotation.Transactional;
import uk.gov.ons.javareference.demojavaprocessor.models.dtos.InboundCaseDto;
import uk.gov.ons.javareference.demojavaprocessor.models.dtos.OutboundCaseDto;
import uk.gov.ons.javareference.demojavaprocessor.models.entities.Case;
import uk.gov.ons.javareference.demojavaprocessor.models.entities.CaseMetadata;
import uk.gov.ons.javareference.demojavaprocessor.models.repository.CaseRepository;

@MessageEndpoint
public class SampleReceiver {
  private final CaseRepository caseRepository;
  private final RabbitTemplate rabbitTemplate;

  @Value("${queueconfig.outbound-exchange}")
  private String outboundExchange;

  @Value("${queueconfig.outbound-routing-key}")
  private String outboundRoutingKey;

  public SampleReceiver(CaseRepository caseRepository, RabbitTemplate rabbitTemplate) {
    this.caseRepository = caseRepository;
    this.rabbitTemplate = rabbitTemplate;
  }

  @Transactional
  @ServiceActivator(inputChannel = "caseSampleInputChannel")
  public void receiveMessage(Message<InboundCaseDto> message) {
    //    might want to record this
    OffsetDateTime messageTimestamp = getMsgTimeStamp(message);

    UUID caseId = createAndSaveNewCase(message.getPayload(), messageTimestamp);
    readSavedCaseAndEmitToOutbound(caseId);
  }

  private void readSavedCaseAndEmitToOutbound(UUID caseId) {

    //    pointless DB read, but we're also proving that it was saved to the DB
    Case caze = getCaseByCaseId(caseId);

    OutboundCaseDto outboundCaseDto = new OutboundCaseDto();
    outboundCaseDto.setId(caze.getId());
    outboundCaseDto.setAddressLine1(caze.getAddressLine1());
    outboundCaseDto.setPostcode(caze.getPostcode());

    rabbitTemplate.convertAndSend(outboundExchange, outboundRoutingKey, outboundCaseDto);
  }

  private UUID createAndSaveNewCase(
      InboundCaseDto inboundCaseDto, OffsetDateTime messageTimestamp) {
    Case caze = new Case();
    caze.setId(UUID.randomUUID());
    caze.setAddressLine1(inboundCaseDto.getAddressLine1());
    caze.setPostcode(inboundCaseDto.getPostcode());
    caze.setMsgDateTime(messageTimestamp);
    caze.setMetadata(getMetaData(inboundCaseDto));

    caseRepository.saveAndFlush(caze);

    return caze.getId();
  }

  private Case getCaseByCaseId(UUID caseId) {
    Optional<Case> cazeResult = caseRepository.findById(caseId);

    if (cazeResult.isEmpty()) {
      throw new RuntimeException(String.format("Case ID '%s' not present", caseId));
    }
    return cazeResult.get();
  }

  //  pointless but demos a json blob stored in the DB.
  private CaseMetadata getMetaData(InboundCaseDto inboundCaseDto) {
    CaseMetadata caseMetadata = new CaseMetadata();
    caseMetadata.setABoolean(true);
    caseMetadata.setAddressString(
        inboundCaseDto.getAddressLine1() + " " + inboundCaseDto.getPostcode() + "");
    return caseMetadata;
  }
}
