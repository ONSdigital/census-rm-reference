package uk.gov.ons.javareference.demojavaprocessor.schedule;

import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Propagation;
import org.springframework.transaction.annotation.Transactional;
import uk.gov.ons.javareference.demojavaprocessor.models.entities.ActionRule;
import uk.gov.ons.javareference.demojavaprocessor.models.repository.ActionRuleRepository;

@Component
public class ActionRuleProcessor {
  private final CaseClassifier caseClassifier;
  private final ActionRuleRepository actionRuleRepository;

  public ActionRuleProcessor(
      CaseClassifier caseClassifier, ActionRuleRepository actionRuleRepository) {
    this.caseClassifier = caseClassifier;
    this.actionRuleRepository = actionRuleRepository;
  }

  @Transactional(
      propagation = Propagation.REQUIRES_NEW) // Start a new transaction for every action rule
  public void processTriggeredActionRule(ActionRule triggeredActionRule) {
    caseClassifier.enqueueCasesForActionRule(triggeredActionRule);
    triggeredActionRule.setHasTriggered(true);
    actionRuleRepository.save(triggeredActionRule);
  }
}
