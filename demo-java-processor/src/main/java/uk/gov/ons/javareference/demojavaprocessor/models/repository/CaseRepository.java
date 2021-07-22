package uk.gov.ons.javareference.demojavaprocessor.models.repository;

import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;
import uk.gov.ons.javareference.demojavaprocessor.models.entities.Case;

public interface CaseRepository extends JpaRepository<Case, UUID> {}
