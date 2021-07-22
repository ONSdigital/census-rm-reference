package uk.gov.ons.javareference.demojavaprocessor.schedule;

import com.godaddy.logging.Logger;
import com.godaddy.logging.LoggerFactory;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;

@Service
public class ActionRuleScheduler {
  private static final Logger log = LoggerFactory.getLogger(ActionRuleScheduler.class);
  private final ActionRuleTriggerer actionRuleTriggerer;

  public ActionRuleScheduler(ActionRuleTriggerer actionRuleTriggerer) {
    this.actionRuleTriggerer = actionRuleTriggerer;
  }

  @Scheduled(fixedDelayString = "${scheduler.frequency}")
  public void triggerActionRule() {
    try {
      actionRuleTriggerer.triggerActionRule();
    } catch (Exception e) {
      log.error("Unexpected exception while processing action rule", e);
      throw e;
    }
  }
}
