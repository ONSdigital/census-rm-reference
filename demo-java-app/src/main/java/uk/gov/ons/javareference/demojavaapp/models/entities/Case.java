package uk.gov.ons.javareference.demojavaapp.models.entities;

import java.util.UUID;
import javax.persistence.Column;
import javax.persistence.Entity;
import javax.persistence.Id;
import javax.persistence.Table;
import lombok.Data;

@Data
@Entity
@Table(name = "cases")
public class Case {

  @Id private UUID caseId;;
  @Column private String addressLine1;
  @Column private String postcode;
}
