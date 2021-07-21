package uk.gov.ons.javareference.demojavaprocessor.models.dtos;

import java.util.UUID;
import lombok.Data;

@Data
public class OutboundCaseDto {
  private UUID id;
  private String addressLine1;
  private String postcode;
}
