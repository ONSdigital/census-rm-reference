package uk.gov.ons.javareference.demojavaapp;

import static org.assertj.core.api.AssertionsForInterfaceTypes.assertThat;

import org.junit.jupiter.api.Test;

public class PointlessUnitTest {

  @Test
  public void doesNothing() {
    assertThat(1).isEqualTo(1);
  }
}
