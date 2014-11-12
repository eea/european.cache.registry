class CountryType:
    (EU_TYPE,
     NONEU_TYPE) = range(2)


class OrganisationStatus:
    (DRAFT,
     REVISION,
     REQUESTED,
     VALID,
     REJECTED) = range(5)


class UndertakingType:
    (FGAS_PRODUCER_IMPORTER_HFCS,
     FGAS_EXPORTER_HFCS,
     FGAS_PRODUCER_IMPORTER_EXPORTER_NON_HFCS) = range(3)
