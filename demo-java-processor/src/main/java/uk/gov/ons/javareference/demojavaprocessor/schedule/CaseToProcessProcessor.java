package uk.gov.ons.javareference.demojavaprocessor.schedule;

import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import uk.gov.ons.javareference.demojavaprocessor.models.dtos.PrintRow;
import uk.gov.ons.javareference.demojavaprocessor.models.entities.CaseToProcess;

@Component
public class CaseToProcessProcessor {
  private final RabbitTemplate rabbitTemplate;

  @Value("${queueconfig.print-queue}")
  private String printQueue;

  public CaseToProcessProcessor(RabbitTemplate rabbitTemplate) {
    this.rabbitTemplate = rabbitTemplate;
  }

  public void process(CaseToProcess caseToProcess) {
    PrintRow printRow = new PrintRow();
    printRow.setRow(caseToProcess.getCaze().getMetadata().getAddressString());
    printRow.setBatchId(caseToProcess.getBatchId());
    printRow.setBatchQuantity(caseToProcess.getBatchQuantity());
    printRow.setPackCode("TEST_PACK");
    printRow.setPrintSupplier("SUPPLIER_A");

    rabbitTemplate.convertAndSend("", printQueue, printRow);
  }
}
