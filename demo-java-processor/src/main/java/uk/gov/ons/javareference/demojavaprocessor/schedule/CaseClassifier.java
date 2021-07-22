package uk.gov.ons.javareference.demojavaprocessor.schedule;

import java.util.UUID;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Component;
import org.springframework.util.StringUtils;
import uk.gov.ons.javareference.demojavaprocessor.models.entities.ActionRule;

@Component
public class CaseClassifier {

  private final JdbcTemplate jdbcTemplate;

  public CaseClassifier(JdbcTemplate jdbcTemplate) {
    this.jdbcTemplate = jdbcTemplate;
  }

  public void enqueueCasesForActionRule(ActionRule actionRule) {
    UUID batchId = UUID.randomUUID();

    jdbcTemplate.update(
        "INSERT INTO cases.case_to_process (batch_id, batch_quantity, action_rule_id, "
            + "caze_id) SELECT ?, COUNT(*) OVER (), ?, id FROM "
            + "cases.cases"
            + buildWhereClause(actionRule.getClassifiers()),
        batchId,
        actionRule.getId());
  }

  private String buildWhereClause(String classifiersClause) {
    StringBuilder whereClause = new StringBuilder();

    if (StringUtils.hasText(classifiersClause)) {
      whereClause.append(" WHERE ").append(classifiersClause);
    }

    return whereClause.toString();
  }
}
