package uk.gov.ons.javareference.demojavaapp.models.dtos;

import java.util.UUID;
import lombok.Data;

@Data
public class OutboundCase {
  private UUID id;
  private String addressLine1;
  private String postcode;
}
