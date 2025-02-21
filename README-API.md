API Documentation
=========================================

The european.cache.registry API allows a client (BDR) to access cached data fetched
from various sources (FGas Registry, ODS Registry, BDR Registry).

The API uses HTTP for transport, JSON as data format and does not require
authentication.

Overview
--------
**Auditor calls:**

* `/auditors/list/` - list all auditors
* `/auditors/[auditor_uid]/details/` - details about an auditor
* `/undertaking/[domain]/[company_id]/auditor/[auditor_uid]/check` - verifies if the auditor and the company are from the same country. Returns the auditor information if this condition is met.
* `/undertaking/[domain]/[company_id]/auditor/[auditor_uid]/assign/` - assigns auditor to company
* `/undertaking/[domain]/[company_id]/auditor/[auditor_uid]/unassign/` - unassigns an auditor from a company

**Undertaking calls:**

* `/undertaking/[domain]/list` - all verified undertakings from domain
* `/undertaking/[domain]/list-small` - all verified undertakings from domain but with fewer details
* `/undertaking/[domain]/list/all` - all undertakings from domain, including unverified
* `/undertaking/[domain]/list_by_vat/[vat]` - filter by vat undertakings from domain
* `/undertaking/[domain]/filter` - count of undertakings from domain, given field filters
* `/undertaking/[domain]/[company_id]/details` - details about an undertaking from a domain
* `/undertaking/[domain]/[company_id]/details-short` - short details about an undertaking from a domain
* `/undertaking/[domain]/[company_id]/statusupdate` - change the status of a company from a domain

**Licences calls**

* `/undertaking/[domain]/[company_id]/licences/[year]/aggregated` - all substances(licences data aggregated) for one undertaking delivered in a year
* `/undertaking/[domain]/[company_id]/deliveries/[year]/licences` - all licences for one undertaking for a certain year
* `/undertaking/[domain]/[company_id]/deliveries/[year]/substances` - all substances for one undertaking for a certain year

**Stocks calls**

* `/stocks` - all stocks in the database
* `/stocks/[company_id]` - all stocks for one company per years
* `/stocks/years/[years]` - all stocks for one selected year
* `/stocks/import` - import new stocks

**User calls:**

* `/user/list` - all users
* `/user/[username]/companies` - all verified companies the user has access to
* `/user/companies?username=[username]&ecas_id=[ecas_id]` - all verified companies the user has access to (check is done with both parameters on both username and ecas_id fields)

**Matching calls:**

* `/candidate/[domain]/list` -  all matching candidates from domain
* `/candidate/[domain]/list/verified` - list verified undertakings from domain
* `/candidate/[domain]/verify/[undertaking_id]/[oldcompany_id]/` - mark an
undertaking-company link as verified from domain
* `/candidate/[domain]/verify-none/[undertaking_id]` - mark an
undertaking as verified from domain
* `/candidate/[domain]/unverify/[undertaking_id]/` - unverify undertaking-company link
after prior verfication from domain
* `/candidate/[domain]/manual/[undertaking_id]/[oldcompany_account]` - manualy link
undertaking with company account

* `/match/run` - run matching algorithm
* `/match/flush` - remove all matching links created by the matching algorithm,
verified or not

**Export calls:**

* `/export/user/list/[domain]` - export users list as CSV
* `/export/user/json/[domain]` - export users list as JSON
* `/export/undertaking/[domain]` - export companies list from domain as CSV

**Mails calls:**

* `/mail/list` - list the mails
* `/mail/add` - add a mail to the list
* `/mail/delete` - delete a mail from the list
* `/alert_lockdown/wrong_match` - alert on wrong matching of a company
* `/alert_lockdown/wrong_lockdown` - alert on wrong lockdown
* `/alert_lockdown/unmatch` - alert at unmatch

**Sync**:

* `/sync/collections_title`
* `/sync/fgases`
* `/sync/ods`
* `/sync/licences`

**Log calls:**
* `/log/matching/[domain]` - matching logs
* `/log/sync[domain]` - data sync logs

**Settings:**

* `/settings` - overview of the middleware settings

**Debug:**

* `/sync/fgases_debug_noneu` - returns a list with all NON EU companies without a legal representative from FGas

Auditor calls
==============

/auditors/list/
---------------

Returns the list of auditors

    [
      {
        "auditor_uid": "ABDFDFS",
        "name": "Auditor name",
        "website": "website.com",
        "phone": "12342432",
        "date_created": "01/01/2024",
        "date_updated": "01/01/2024",
        "date_created_in_ecr": "01/01/2024",
        "date_updated_in_ecr": "01/01/2024",
        "status": "VALID",
        "ets_accreditation": true,
        "ms_accreditation": true,
        "ms_accreditation_issuing_countries": [
          "BE",
        ],
        "address": {
            "street": "One",
            "number": null,
            "zipcode": null,
            "city": "City",
            "country": {
                "code": "PL",
                "name": "Poland",
                "type": "EU_TYPE"
            }
        },
        "users": [
            {
                "ecas_id": "ecas_id",
                "username": "username",
                "first_name": "First name",
                "last_name": "Last name",
                "email": "mail@test.com",
                "type": "TYPE"
            }
        ],
        "audited_companies": [
            {
                "start_date": "20/02/2025",
                "end_date": "21/03/2025",
                "reporting_envelope_url": "reporting/folder/1234",
                "verification_envelope_url": "verification/folder/12345",
                "auditor": {
                    "auditor_uid": "ABDFDFS",
                    "name": "Auditor name"
                },
                "undertaking": {
                    "company_id": 10085,
                    "domain": "FGAS",
                    "name": "Company name"
                },
                "user": {
                    "ecas_id": "ecas_id",
                    "username": "username",
                    "first_name": "First name",
                    "last_name": "Last name",
                    "email": "mail@test.com",
                    "type": "TYPE"
                }
            },
            {
                "start_date": "21/02/2025",
                "end_date": "None",
                "reporting_envelope_url": "reporting/folder/123423",
                "verification_envelope_url": "verification/folder/1234345",
                "auditor": {
                    "auditor_uid": "ABDFDFS",
                    "name": "Auditor name"
                },
                "undertaking": {
                    "company_id": 10085,
                    "domain": "FGAS",
                    "name": "Company name"
                },
                "user": {
                    "ecas_id": "ecas_id",
                    "username": "username",
                    "first_name": "First name",
                    "last_name": "Last name",
                    "email": "mail@test.com",
                    "type": "TYPE"
                }
            }
        ]
      }
    ]

auditors/[auditor_uid]/details/
-------------------------------

Returns the auditor

    {
        "auditor_uid": "ABDFDFS",
        "name": "Auditor name",
        "website": "website.com",
        "phone": "12342432",
        "date_created": "01/01/2024",
        "date_updated": "01/01/2024",
        "date_created_in_ecr": "01/01/2024",
        "date_updated_in_ecr": "01/01/2024",
        "status": "VALID",
        "ets_accreditation": true,
        "ms_accreditation": true,
        "ms_accreditation_issuing_countries": [
          "BE",
        ],
        "address": {
            "street": "One",
            "number": null,
            "zipcode": null,
            "city": "City",
            "country": {
                "code": "PL",
                "name": "Poland",
                "type": "EU_TYPE"
            }
        },
        "users": [
            {
                "ecas_id": "ecas_id",
                "username": "username",
                "first_name": "First name",
                "last_name": "Last name",
                "email": "mail@test.com",
                "type": "TYPE"
            }
        ],
        "audited_companies": [
            {
                "start_date": "20/02/2025",
                "end_date": "21/03/2025",
                "reporting_envelope_url": "reporting/folder/1234",
                "verification_envelope_url": "verification/folder/12345",
                "auditor": {
                    "auditor_uid": "ABDFDFS",
                    "name": "Auditor name"
                },
                "undertaking": {
                    "company_id": 10085,
                    "domain": "FGAS",
                    "name": "Company name"
                },
                "user": {
                    "ecas_id": "ecas_id",
                    "username": "username",
                    "first_name": "First name",
                    "last_name": "Last name",
                    "email": "mail@test.com",
                    "type": "TYPE"
                }
            },
            {
                "start_date": "21/02/2025",
                "end_date": "None",
                "reporting_envelope_url": "reporting/folder/123423",
                "verification_envelope_url": "verification/folder/1234345",
                "auditor": {
                    "auditor_uid": "ABDFDFS",
                    "name": "Auditor name"
                },
                "undertaking": {
                    "company_id": 10085,
                    "domain": "FGAS",
                    "name": "Company name"
                },
                "user": {
                    "ecas_id": "ecas_id",
                    "username": "username",
                    "first_name": "First name",
                    "last_name": "Last name",
                    "email": "mail@test.com",
                    "type": "TYPE"
                }
            }
        ]
    }

/undertaking/[domain]/[company_id]/auditor/[auditor_uid]/check
--------------------------------------------------------------

Returns the auditor if:
* Auditor country == Company's country code (calculated as the address country or representative country)
* the Auditor has a valid status.

      {
          "access": true,
          "auditor": {
              "auditor_uid": "ABDSDE",
              "name": "Auditor name",
              "website": null,
              "phone": "+2343243453",
              "date_created": "01/01/2024",
              "date_updated": "01/01/2024",
              "date_created_in_ecr": "01/01/2024",
              "date_updated_in_ecr": "01/01/2024",
              "status": "VALID",
              "ets_accreditation": true,
              "ms_accreditation": true,
              "ms_accreditation_issuing_countries": [
                "BE"
              ],
              "address": {
                  "street": "One",
                  "number": null,
                  "zipcode": null,
                  "city": "City",
                  "country": {
                      "code": "PL",
                      "name": "Poland",
                      "type": "EU_TYPE"
                  }
              },
              "users": [
                  {
                      "ecas_id": "ecas_id",
                      "username": "username",
                      "first_name": "First name",
                      "last_name": "Last name",
                      "email": "mail@mail.com",
                      "type": "TYPE"
                  }
              ]
          }
      }

_POST:_ /undertaking/[domain]/[company_id]/auditor/[auditor_uid]/assign/
------------------------------------------------------------------------

Assigns the auditor _[auditor_uid]_, lead by the given user _[email]_ to the company _[company_id]_ if:
* the Auditor has a VALID status
* Auditor's and Company's countries match
* There is no other assignation for the same company_id, auditor_uid, email, reporting_envelope_url, verification_envelope_url open (end_date = None)
* Given email matches a user if the Auditor's contact persons

_POST DATA:_

* _email = Lead user email (selected from auditor contact persons), required_
* _reporting_envelope_url = Original envelope URL, required_
* _verification_envelope_url = Verification envelope URL, required_

        {
          "email": "mail@test.com",
          "reporting_envelope_url": "/folder/sds/23423",
          "verification_envelope_url": "/folder/dsfs/dsfsdf"
        }

Response:

    {
      "success": true,
      "errors": [],
    }


_POST:_ /undertaking/[domain]/[company_id]/auditor/[auditor_uid]/unassign/
------------------------------------------------------------------------

Unassigns the auditor _[auditor_uid]_, lead by the given user _[email]_ to the company _[company_id]_ .
The auditor will still be visible in the undertaking detail and auditor listing/detail endpoints, but the end date field
will have a value.

_POST DATA:_

* _email = Lead user email (selected from auditor contact persons), required_
* _reporting_envelope_url = Original envelope URL, required_
* _verification_envelope_url = Verification envelope URL, required_

        {
          "email": "mail@test.com",
          "reporting_envelope_url": "/folder/sds/23423",
          "verification_envelope_url": "/folder/dsfs/dsfsdf"
        }

Response:

    {
      "success": true,
      "errors": [],
    }


Undertaking calls
=================

/undertaking/[domain]/list
--------------------------

Returns the list of all verified undertakings in the system, as fetched from domain registry.

    [
      {
        "website": "WEBSITE--10085",
        "status": "VALID",
        "domain": "FGAS",
        "users": [
          {
            "username": "nzhouray",
            "ecas_id": "nzhouray",
            "first_name": "fname--9367",
            "last_name": "lname--9367",
            "id": 1,
            "email": "9367email@climaOds2010.yyy"
          }
        ],
        "representative": {
          "name": "EULEGALNAME44",
          "contact_last_name": "lname--9853",
          "vatnumber": "EUVAT44",
          "contact_email": "9853email@climaOds2010.yyy",
          "contact_first_name": "fname--9853",
          "address": {
            "city": "city--7954",
            "country": {
              "code": "IE",
              "type": "EU_TYPE",
              "name": "Ireland"
            },
            "zipcode": "zipcode--7954",
            "number": "nrstreet--7954",
            "street": "street--7954"
        },
        "country_history": [],
        "represent_history": [
          {
          "name": "EULEGALNAME44 OLD",
          "contact_last_name": "lname--9853",
          "vatnumber": "EUVAT45",
          "contact_email": "9853email@climaOds2010.yyy",
          "contact_first_name": "fname--9853",
          "address": {
            "city": "city--7954",
            "country": {
              "code": "IE",
              "type": "EU_TYPE",
              "name": "Ireland"
            },
            "zipcode": "zipcode--7954",
            "number": "nrstreet--7954",
            "street": "street--7954"
        }
        ],
        "date_updated": "10/10/2014",
        "phone": "+3212310085",
        "country_code": "CN",
        "address": {
          "city": "city--7953",
          "country": {
            "code": "CN",
            "type": "NONEU_TYPE",
            "name": "China (excluding Hong Kong and Macao)"
          },
          "zipcode": "zipcode--7953",
          "number": "nrstreet--7953",
          "street": "street--7953"
        },
        "businessprofile": {
          "highleveluses": "fgas.importer.of.refrigeration.ac..and.heatpump.equipment.containing.hfcs"
        },
        "oldcompany_verified": true,
        "oldcompany_account": "fgas22331",
        "oldcompany_extid": 4,
        "collection_id": null,
        "types": "FGAS_PRODUCER_IMPORTER_HFCS",
        "undertaking_type": "FGASUndertaking",
        "name": "FGAS-NMORGANIZATION--10085",
        "company_id": 10085,
        "date_created": "10/10/2014",
        "vat": null
      }
    ]


/undertaking/[domain]/list-small
--------------------------------

    [
    {
        "domain": "ODS",
        "name": "NMORGANIZATION--26610",
        "company_id": 26610,
        "address": {
            "city": " Sofia",
            "country": {
                "code": "BG",
                "type": "EU_TYPE",
                "name": "Bulgaria"
            },
            "zipcode": "cp19855",
            "number": "1",
            "street": "str--19855"
        },
        "date_created": "07/04/2017",
        "vat": "NREORI26610",
        "users": [
            {
                "ecas_id": "nwuderra",
                "username": "nwuderra",
                "first_name": "fname--25688",
                "last_name": "lname--25688",
                "email": "25688email@climaOds2010.yyy"
            }
        ]
    }
    ]

/undertaking/[domain]/list/all
------------------------------

Returns a list of all undertakings in the system (verified or not), as fetched from domain registry.

    [
      {
        "website": "WEBSITE--10085",
        "status": "VALID",
        "domain": "FGAS",
        "users": [
          {
            "username": "nzhouray",
            "ecas_id": "nzhouray",
            "first_name": "fname--9367",
            "last_name": "lname--9367",
            "id": 1,
            "email": "9367email@climaOds2010.yyy"
          }
        ],
        "representative": {
          "name": "EULEGALNAME44",
          "contact_last_name": "lname--9853",
          "vatnumber": "EUVAT44",
          "contact_email": "9853email@climaOds2010.yyy",
          "contact_first_name": "fname--9853",
          "address": {
            "city": "city--7954",
            "country": {
              "code": "IE",
              "type": "EU_TYPE",
              "name": "Ireland"
            },
            "zipcode": "zipcode--7954",
            "number": "nrstreet--7954",
            "street": "street--7954"
        },
        "represent_history": [
          {
          "name": "EULEGALNAME44 OLD",
          "contact_last_name": "lname--9853",
          "vatnumber": "EUVAT45",
          "contact_email": "9853email@climaOds2010.yyy",
          "contact_first_name": "fname--9853",
          "address": {
            "city": "city--7954",
            "country": {
              "code": "IE",
              "type": "EU_TYPE",
              "name": "Ireland"
            },
            "zipcode": "zipcode--7954",
            "number": "nrstreet--7954",
            "street": "street--7954"
        }
        ],
        "date_updated": "10/10/2014",
        "phone": "+3212310085",
        "country_code": "CN",
        "address": {
          "city": "city--7953",
          "country": {
            "code": "CN",
            "type": "NONEU_TYPE",
            "name": "China (excluding Hong Kong and Macao)"
          },
          "zipcode": "zipcode--7953",
          "number": "nrstreet--7953",
          "street": "street--7953"
        },
        "businessprofile": {
          "highleveluses": "fgas.importer.of.refrigeration.ac..and.heatpump.equipment.containing.hfcs"
        },
        "collection_id": null,
        "oldcompany_account": "fgas22331",
        "oldcompany_extid": 4,
        "types": "FGAS_PRODUCER_IMPORTER_HFCS",
        "undertaking_type": "FGASUndertaking",
        "name": "FGAS-NMORGANIZATION--10085",
        "company_id": 10085,
        "date_created": "10/10/2014",
        "vat": null
      },
    ]

/undertaking/[domain]/list_by_vat/<vat>
---------------------------------------

Returns a list of all verified undertakings in the system given by their VAT, as fetched from domain registry.

    [
      {
        "name": "FGAS-NMORGANIZATION--10078",
        "company_id": 10078
      }
    ]

/undertaking/[domain]/filter?[name|id|vat|countrycode|OR_vat|OR_name]
---------------------------------------------------------------------

Return true or false if there are companies for the given filter.

The *OR_name* and *OR_vat* filters refer to EuLegalRepresentative.

The *name* and *OR_name* filters use LIKE queries.

    [
      {
        "exists": true,
        "count": 1
      }
    ]

/undertaking/[domain]/[company_id]/details
------------------------------------------

Returns an undertakings details from the system, as fetched from domain registry.

    {
      "company_id": 10085,
      "collection_id": null,
      "undertaking_type": "FGASUndertaking",
      "website": "WEBSITE--10085",
      "status": "VALID",
      "domain": "FGAS",
      "name": "FGAS-NMORGANIZATION--10085",
      "phone": "+3212310085",
      "oldcompany_account": "fgas22331",
      "oldcompany_extid": 4,
      "businessprofile": {
        "highleveluses": ""
      },
      "representative": {
        "name": "EULEGALNAME44",
        "contact_last_name": "lname--9853",
        "vatnumber": "EUVAT44",
        "contact_email": "9853email@climaOds2010.yyy",
        "contact_first_name": "fname--9853",
        "address": {
          "city": "city--7954",
          "country": {
            "code": "IE",
            "type": "EU_TYPE",
            "name": "Ireland"
          },
          "zipcode": "zipcode--7954",
          "number": "nrstreet--7954",
          "street": "street--7954"
        }
      },
      "country_history": [],
      "represent_history": [
          {
          "name": "EULEGALNAME44 OLD",
          "contact_last_name": "lname--9853",
          "vatnumber": "EUVAT45",
          "contact_email": "9853email@climaOds2010.yyy",
          "contact_first_name": "fname--9853",
          "address": {
            "city": "city--7954",
            "country": {
              "code": "IE",
              "type": "EU_TYPE",
              "name": "Ireland"
            },
            "zipcode": "zipcode--7954",
            "number": "nrstreet--7954",
            "street": "street--7954"
        }
      ],
      "auditors": [
          {
              "start_date": "20/02/2025",
              "end_date": "21/03/2025",
              "reporting_envelope_url": "reporting/folder/1234",
              "verification_envelope_url": "verification/folder/12345",
              "auditor": {
                  "auditor_uid": "ABCDEDF",
                  "name": "Auditor name"
              },
              "undertaking": {
                  "company_id": 10085,
                  "domain": "FGAS",
                  "name": "Company name"
              },
              "user": {
                  "ecas_id": "ecas_id",
                  "username": "username",
                  "first_name": "First name",
                  "last_name": "Last name",
                  "email": "mail@test.com",
                  "type": "TYPE"
              }
          },
          {
              "start_date": "21/02/2025",
              "end_date": "None",
              "reporting_envelope_url": "reporting/folder/123423",
              "verification_envelope_url": "verification/folder/1234345",
              "auditor": {
                  "auditor_uid": "ABCDEDF",
                  "name": "Auditor name"
              },
              "undertaking": {
                  "company_id": 10085,
                  "domain": "FGAS",
                  "name": "Company name"
              },
              "user": {
                  "ecas_id": "ecas_id",
                  "username": "username",
                  "first_name": "First name",
                  "last_name": "Last name",
                  "email": "mail@test.com",
                  "type": "TYPE"
              }
          }
      ],
      "address": {
        "city": "city--7953",
        "country": {
          "code": "CN",
          "type": "NONEU_TYPE",
          "name": "China (excluding Hong Kong and Macao)"
        },
        "zipcode": "zipcode--7953",
        "number": "nrstreet--7953",
        "street": "street--7953"
      },
      "vat": null,
      "users": [
        {
          "ecas_id": "nzhouray",
          "username": "nzhouray",
          "first_name": "fname--9367",
          "last_name": "lname--9367",
          "email": "9367email@climaOds2010.yyy"
        }
      ]
    }

/undertaking/[domain]/[company_id]/details-short
-------------------------------------------------

This url is used to retrive details of a certain company and the contact persons of that company.

{
    "company_id": 324,
    "company_name": "NMORGANIZATION--324",
    "address": "str--567, 1",
    "postal_code": "cp567",
    "city": "Darmstadt",
    "country": "Germany",
    "eori_code": "NREORI324",
    "contact_persons": [
      {
        "first_name": "fname25716",
        "last_name": "lname25716",
        "email": "25716email@test.yyy"
      },
      {
        "first_name": "fname--25717",
        "last_name": "lname--25717",
        "email": "25717email@test.yyy"
      }
    ]
}

/undertaking/[domain]/[company_id]/statusupdate - POST
------------------------------------------------------

This url is used to update the status of a company from a certain domain by POST method with the new status

Licences calls
==============

/undertaking/[domain]/[company_id]/licences/[year]/aggregated - POST
-------------------------------------------------------------

This url is used to retrive the current delivery of substances for one undertaking in a certain year.
The substances can be also filtered by substance name or types(actions), by suppling a JSON of the form:

    {
      "substances": ["Substance name1", "Substance name 2" ],
      "actions": ["action1", "action2"]
    }

Response example:

    [
      {
        "year": 2019,
        "substance": "HCFC-142b (virgin)",
        "quantity": 1234,
        "company_id": 234,
        "use_kind": "",
        "use_desc": "feedstock",
        "type": "export"
      },
      {
        "year": 2019,
        "substance": "Halon 2402 (non-virgin)",
        "quantity": 23,
        "company_id": 234,
        "use_kind": "",
        "use_desc": "critical uses",
        "type": "export"
      }
    ]


/undertaking/[domain]/[pk]/deliveries/[year]/licences - GET
---------------------------------------------------------------------------

Provies a list with all the licences for one undertaking for a certain year


    [
      {
        "year": 2018,
        "licence_id": 1234,
        "chemical_name": "HBFC-31 B1",
        "organization_country_name": "IT",
        "organization_country_name_orig": "Italy",
        "custom_procedure_name": "Name",
        "international_party_country_name": "US",
        "international_party_country_name_orig": "United States of America",
        "total_odp_mass": 20,
        "net_mass": 4,
        "licence_state": "CLOSED",
        "long_licence_number": "NUMBER2342",
        "template_detailed_use_code": "import.of.substance.for.feedstock.use.detailed.use",
        "licence_type": "IFDS",
        "mixture_nature_type": "VIRGIN",
        "date_created": "16/01/2020",
        "date_updated": null,
        "substance_id": 2
      },
      {
        "year": 2018,
        "licence_id": 1235,
        "chemical_name": "HBFC-31 B1",
        "organization_country_name": "IT",
        "organization_country_name_orig": "Italy",
        "custom_procedure_name": "Release for free circulation",
        "international_party_country_name": "US",
        "international_party_country_name_orig": "United States of America",
        "total_odp_mass": 43,
        "net_mass": 32,
        "licence_state": "CLOSED",
        "long_licence_number": "NUMBER23131",
        "template_detailed_use_code": "import.of.substance.for.feedstock.use.detailed.use",
        "licence_type": "IFDS",
        "mixture_nature_type": "VIRGIN",
        "date_created": "16/01/2020",
        "date_updated": null,
        "substance_id": 2
      }
    ]


/undertaking/[domain]/[pk]/deliveries/[year]/substances - GET
-----------------------------------------------------------------------------

Provies a list with all the substances for one undertaking for a certain year


  [
    {
      "year": 2018,
      "substance": "HBFC-31 B1 (virgin)",
      "lic_use_kind": "free circulation",
      "lic_use_desc": "feedstock",
      "lic_type": "import",
      "quantity": 2342,
      "date_created": "16/01/2020",
      "date_updated": "16/01/2020",
      "delivery_id": 2
    },
    {
      "year": 2018,
      "substance": "HCFC-22 (virgin)",
      "lic_use_kind": "",
      "lic_use_desc": "refrigeration",
      "lic_type": "export",
      "quantity": 5433,
      "date_created": "16/01/2020",
      "date_updated": "16/01/2020",
      "delivery_id": 2
    }
  ]

Stocks calls
============

/stocks - GET
--------------

This url is used to retrive all the stocks in the database:

Response example:

    [
        {
          "year": 2019,
          "type": "fr",
          "substance_name_form": "cfd",
          "is_virgin": true,
          "code": "12412",
          "result": 1234,
          "company_id": 12412,
          "company_name": "NMORGANIZATION--12412"
        },
        {
          "year": 2019,
          "type": "fr",
          "substance_name_form": "cdf",
          "is_virgin": true,
          "code": "43523",
          "result": 54354,
          "company_id": 1243,
          "company_name": "NMORGANIZATION--43523"
        }
    ]

/stocks/years/2019 - GET

[
  {
    "type": "cb",
    "substance_name_form": "Cdf",
    "is_virgin": true,
    "code": "ods12345",
    "result": 12345
  },
  {
    "type": "d",
    "substance_name_form": "Cdf",
    "is_virgin": true,
    "code": "ods12345",
    "result": 12345
  },
]

/stocks/12345 - POST
{
  "12345": {
    "2019":
  }
}
User calls
==========


/user/list
----------

Returns a list of all undertakings in the system, as fetched from all registries.

    [
      {
        "ecas_id": "user1",
        "username": "user1",
        "first_name": "User 1",
        "last_name": "User 1",
        "email": "user1@mock.ec.europa.eu"
      },
    ]

/user/[username]/companies
--------------------------

The _username_ should be a username (ex: "user1")

Returns the list of undertakings for a user given by its unique username.


    [
      {
        "collection_id": null,
        "domain": "FGAS",
        "country": "CN",
        "company_id": 10085,
        "name": "FGAS-NMORGANIZATION--10085",
        "respresentative_country": "DE",
        "country_history": [],
        "represent_history": [
          {
          "name": "EULEGALNAME44 OLD",
          "contact_last_name": "lname--9853",
          "vatnumber": "EUVAT45",
          "contact_email": "9853email@climaOds2010.yyy",
          "contact_first_name": "fname--9853",
          "address": {
            "city": "city--7954",
            "country": {
              "code": "IE",
              "type": "EU_TYPE",
              "name": "Ireland"
            },
            "zipcode": "zipcode--7954",
            "number": "nrstreet--7954",
            "street": "street--7954"
        }
      ],
      }
    ]


/user/companies?username=[username]&ecas_id=[ecas_id]
-----------------------------------------------------

The _username_ should be a username (ex: "user1")
The _ecas_id_ should be of the same format as the username

Returns the list of undertakings for a user given by its username or ecas_id.
The values given are checked against both the username and ecas_id field, to ensure that the user is found.


    [
      {
        "collection_id": null,
        "domain": "FGAS",
        "country": "CN",
        "company_id": 10085,
        "name": "FGAS-NMORGANIZATION--10085",
        "respresentative_country": "DE",
        "country_history": [],
        "represent_history": [
          {
          "name": "EULEGALNAME44 OLD",
          "contact_last_name": "lname--9853",
          "vatnumber": "EUVAT45",
          "contact_email": "9853email@climaOds2010.yyy",
          "contact_first_name": "fname--9853",
          "address": {
            "city": "city--7954",
            "country": {
              "code": "IE",
              "type": "EU_TYPE",
              "name": "Ireland"
            },
            "zipcode": "zipcode--7954",
            "number": "nrstreet--7954",
            "street": "street--7954"
        }
      ],
      }
    ]

Matching calls
==============

The methods available via HTTP POST should also encapsulate the username, for
logging purposes.

/candidate/[domain]/list
------------------------

Lists all possible Company candidates for matching with existing Undertakings from domain.

    [
      {
        "status": "VALID",
        "country": "Italy",
        "company_id": 22549,
        "name": "NMORGANIZATION--22549"
      },
    ]


/candidate/[domain]/verify/[undertaking_id]/[oldcompany_id]/ - POST
-----------------------------------------------

Verifies the link created by the matching algorithm between an Undertaking (from a
domain) and a Company from BDR.

    {
      "verified": true,
      "company_id": 10085,
      "collection_id": 3934
    }


/candidate/[domain]/verify-none/[undertaking_id]/ - POST
-----------------------------------------------

Verifies the Undertaking without a Company link.

    {
      "verified": true,
      "company_id": 10085,
      "collection_id": 3934
    }


/candidate/[domain]/unverify/[undertaking_id]/ - POST
-------------------------------------------------

Unverify any link between an Undertaking (from a domain) and a Company.

    {
      "website": "WEBSITE--10085",
      "status": "VALID",
      "address_id": 1,
      "name": "FGAS-NMORGANIZATION--10085",
      "undertaking_type": "FGASUndertaking",
      "date_updated": "10/10/2014",
      "represent_id": 1,
      "domain": "FGAS",
      "oldcompany_extid": null,
      "phone": "+3212310085",
      "oldcompany_verified": false,
      "company_id": 10085,
      "types": "FGAS_PRODUCER_IMPORTER_HFCS",
      "country_code": "CN",
      "date_created": "10/10/2014",
      "oldcompany_account": null,
      "vat": null,
      "businessprofile_id": 1
    }

/candidate/[domain]/manual/[undertaking_id]/[oldcompany_account] - POST
-----------------------------------------------------------------------

Manualy link an Undertaking and a Company account, without previous linking by the
matching algorithm.

    {
        "undertaking_id": 234,
        "oldcompany_account": "fgas22331",
        "verified": true,
    }

/candidate/[domain]/list/verified - GET
---------------------------------------

Lists the already verified undertakings from a domain.

    [
      {
        "website": "WEBSITE--10085",
        "status": "VALID",
        "address_id": 1,
        "name": "FGAS-NMORGANIZATION--10085",
        "undertaking_type": "FGASUndertaking",
        "date_updated": "10/10/2014",
        "represent_id": 1,
        "domain": "FGAS",
        "oldcompany_extid": null,
        "phone": "+3212310085",
        "oldcompany_verified": true,
        "company_id": 10085,
        "types": "FGAS_PRODUCER_IMPORTER_HFCS",
        "country_code": "CN",
        "date_created": "10/10/2014",
        "oldcompany_account": null,
        "vat": null,
        "businessprofile_id": 1
      }
    ]

/match/run - GET
----------------

Run the matching algorithm. This creates a link between a matching Undertaking and a
Company. These links must be manualy verified, using the verified routes explained above.

    {
        'success': True/False,
        'message': 'Success/Error message'
    }

/match/flush - GET
------------------

Clean-up all matching links created by the algorithm, **including** those that were
verified by a user.

    {
        'success': True/False,
        'message': 'Success/Error message'
    }

Export calls
============

/export/user/list/[domain]
-----------------

This URL is used to export the list of users with their companies and the companies' contact persons as an Excel file.

/export/undertaking/[domain]
----------------------------

This URL is used to export the list of undertakings from ``/undertakings/[domain]/list`` as an Excel file.

Mails calls
===========


/mail/list
----------

Display the list of all mails to be notified about companies matching.

    [
      {
        'mail': 'new@mail.com',
        'first_name': 'first_name',
        'last_name': 'last_name'
      }
    ]


/mail/add - POST
----------------

Add a new contact to be notified on matching. The POST should contain the following data:

    {
      'mail': 'new@mail.com',
      'first_name': 'first_name',
      'last_name': 'last_name'
    }

On success returns:

    {
        'success': True
    }

On failure returns:

    {
        'success': False,
        'message': 'This email address already exists'
    }

/mail/delete - POST
-------------------

Delete a contact from the mailing list. The POST should contain the following data:

    {
      'mail': 'mail_to_be_deleted@example.com',
    }

On success returns:

    {
        'success': True
    }

On failure returns:

    {
        'success': False,
        'message': 'This email address does not exists'
    }

/alert_lockdown/wrong_match - POST
----------------------------------

Send an alert email when a company matching was done wrong. 
The expected input POST data should consist of an ``user`` and a ``company_id``.


/alert_lockdown/wrong_lockdown - POST
-------------------------------------

In case the lock down is over and no matching should be changed, the interested parties will be alerted with an email.
The expected input POST data should consist of an ``user`` and a ``company_id``.


/alert_lockdown/unmatch - POST
------------------------------

This mail should be sent when an unmatching call has been made.
The expected input POST data should consist of an ``user`` and a ``company_id``.

Sync calls
==================

All endpoints in this category return a json response with the following format:


    {
        'success': True/False,
        'message': 'Success/Error message'
    }

/sync/collections_title - GET
-----------------------------

/sync/fgases - GET
------------------

Optional parameters:

* days (integer, default = 7)
* updated_since (string, datetime format DD/MM/YYYY)
* id (integer, the external id of the company) 

/sync/ods - GET
---------------

Optional parameters:

* days (integer, default = 7)
* updated_since (string, datetime format DD/MM/YYYY)
* id (integer, the external id of the company)


/sync/licences -  GET
---------------------

Log calls
=========

/log/matching/[domain]
-------------

Lists a matching log list for 2 companies and the user who made it at which
time, sorted in decrease order by timestamp.

    [
      {
        "verified": true,
        "timestamp": "27/11/2014 15:56",
        "company_id": 10051,
        "user": "vitalie",
      }
    ]


/log/sync/[domain]
---------

Lists a data sync log which shows when the sync was ran, sorted in decrease
order by execution_time

    [
      {
        "execution_time": "26/11/2014 16:42",
        "organizations": 413,
        "using_last_update": "10/10/2014"
        "for_user": False,
      }
    ]

Settings calls
==============

/settings
---------

Display the value of the configured middleware settings

    {
      "BASE_URL": "http://example.com",
      "BASE_URL_FGAS": "http://example.com",
      "BASE_URL_ODS": "http://example.com"
    }


Debug calls
==================

All endpoints in this category return a json response with the following format:

    {
        'success': True/False,
        'message': 'Success/Error message'
    }

/sync/fgases_debug_noneu - GET
------------------------------

Optional parameters:

* days (integer, default = 7)
* updated_since (string, datetime format DD/MM/YYYY)


Settings calls
==============

/settings
---------

Display the value of the configured middleware settings

    {
      "BASE_URL": "http://example.com",
      "BASE_URL_FGAS": "http://example.com",
      "BASE_URL_ODS": "http://example.com"
    }


Debug calls
==================

All endpoints in this category return a json response with the following format:

    {
        'success': True/False,
        'message': 'Success/Error message'
    }

/sync/fgases_debug_noneu - GET
------------------------------

Optional parameters:

* days (integer, default = 7)
* updated_since (string, datetime format DD/MM/YYYY)
