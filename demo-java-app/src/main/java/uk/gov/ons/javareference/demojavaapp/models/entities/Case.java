package uk.gov.ons.javareference.demojavaapp.models.entities;

import com.vladmihalcea.hibernate.type.json.JsonBinaryType;
import java.time.OffsetDateTime;
import java.util.UUID;
import javax.persistence.Column;
import javax.persistence.Entity;
import javax.persistence.Id;
import javax.persistence.Table;
import lombok.Data;
import org.hibernate.annotations.*;

@Data
@Entity
@TypeDefs({@TypeDef(name = "jsonb", typeClass = JsonBinaryType.class)})
@Table(name = "cases")
public class Case {

  @Id private UUID caseId;;
  @Column private String addressLine1;
  @Column private String postcode;
  @Column OffsetDateTime msgDateTime;

  @Type(type = "jsonb")
  @Column(columnDefinition = "jsonb")
  private CaseMetadata metadata;
}
