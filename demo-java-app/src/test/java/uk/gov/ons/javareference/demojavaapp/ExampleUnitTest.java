package uk.gov.ons.javareference.demojavaapp;

import static org.assertj.core.api.AssertionsForInterfaceTypes.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.verify;
import static uk.gov.ons.javareference.demojavaapp.testutil.MessageConstructor.constructMessageWithValidTimeStamp;

import java.util.Optional;
import java.util.UUID;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.mockito.ArgumentCaptor;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.Mockito;
import org.mockito.junit.MockitoJUnitRunner;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.messaging.Message;
import org.springframework.test.util.ReflectionTestUtils;
import uk.gov.ons.javareference.demojavaapp.messaging.SampleReceiver;
import uk.gov.ons.javareference.demojavaapp.models.dtos.InboundCaseDto;
import uk.gov.ons.javareference.demojavaapp.models.dtos.OutboundCaseDto;
import uk.gov.ons.javareference.demojavaapp.models.entities.Case;
import uk.gov.ons.javareference.demojavaapp.models.repository.CaseRepository;

@RunWith(MockitoJUnitRunner.class)
public class ExampleUnitTest {

  public static final String TEST_ADDRESS = "Tenby Castle";
  public static final String TEST_POSTCODE = "10 BY";
  public static final UUID TEST_UUID = UUID.randomUUID();
  private static final String EXCHANGE = "test.exchange";
  private static final String ROUTING_KEY = "test.routing.key";

  @Mock private CaseRepository caseRepository;

  @Mock private RabbitTemplate rabbitTemplate;

  @InjectMocks SampleReceiver underTest;

  @Test
  public void excitingUnitTestDemoingMocksAndReflection() {
    ReflectionTestUtils.setField(underTest, "outboundExchange", EXCHANGE);
    ReflectionTestUtils.setField(underTest, "outboundRoutingKey", ROUTING_KEY);

    InboundCaseDto inboundCaseDto = new InboundCaseDto();
    inboundCaseDto.setAddressLine1(TEST_ADDRESS);
    inboundCaseDto.setPostcode(TEST_POSTCODE);

    Case cazeToReturn = new Case();
    cazeToReturn.setCaseId(TEST_UUID);
    cazeToReturn.setAddressLine1(TEST_ADDRESS);
    cazeToReturn.setPostcode(TEST_POSTCODE);

    Mockito.when(caseRepository.findById(any())).thenReturn(Optional.of(cazeToReturn));

    Message<InboundCaseDto> message = constructMessageWithValidTimeStamp(inboundCaseDto);
    underTest.receiveMessage(message);

    ArgumentCaptor<OutboundCaseDto> caseArgumentCaptor =
        ArgumentCaptor.forClass(OutboundCaseDto.class);
    verify(rabbitTemplate)
        .convertAndSend(eq(EXCHANGE), eq(ROUTING_KEY), caseArgumentCaptor.capture());

    OutboundCaseDto actualOutboundCase = caseArgumentCaptor.getValue();
    assertThat(actualOutboundCase.getId()).isEqualTo(TEST_UUID);
    assertThat(actualOutboundCase.getAddressLine1()).isEqualTo(TEST_ADDRESS);
    assertThat(actualOutboundCase.getPostcode()).isEqualTo(TEST_POSTCODE);
  }
}
