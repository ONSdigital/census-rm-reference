package uk.gov.ons.javareference.demojavaapp.models.dtos;

import lombok.Data;

import java.util.UUID;

@Data
public class OutboundCase {
    private UUID id;
    private String addressLine1;
    private String postcode;
}
