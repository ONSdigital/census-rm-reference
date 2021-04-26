package uk.gov.ons.javareference.demojavaapp.models.repository;

import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;
import uk.gov.ons.javareference.demojavaapp.models.entities.Case;

public interface CaseRepository extends JpaRepository<Case, UUID> {}
