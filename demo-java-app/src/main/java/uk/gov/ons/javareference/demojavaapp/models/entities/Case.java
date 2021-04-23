package uk.gov.ons.javareference.demojavaapp.models.entities;

import lombok.Data;

import javax.persistence.Column;
import javax.persistence.Entity;
import javax.persistence.Id;
import javax.persistence.Table;
import java.util.UUID;


@Data
@Entity
@Table(
    name = "cases"
    )
public class Case {

  @Id private UUID caseId;;
  @Column private String addressLine1;
  @Column private String postcode;
}
