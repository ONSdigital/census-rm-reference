package uk.gov.ons.javareference.demojavaapp.models.repository;


import org.springframework.data.jpa.repository.JpaRepository;
import uk.gov.ons.javareference.demojavaapp.models.entities.Case;

import java.util.UUID;

public interface CaseRepository extends JpaRepository<Case, UUID> {
}
