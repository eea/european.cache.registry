Changelog
=========

2.5.2 - (2025-04-28)
--------------------
* Mark check_passed = True for NO_HIGHLEVEL_TYPES
  [dianaboiangiu]

2.5.1 - (2025-04-11)
--------------------
* Fix auditor check
  [dianaboiangiu]

2.5.0 - (2025-03-27)
--------------------
* Upgrade python to version 3.13
* Upgrade packages to the latest available version
  [dianaboiangiu]

2.4.6 - (2025-03-17)
--------------------
* Implement final auditor checks
  [dianaboiangiu]

2.4.5 - (2025-03-07)
--------------------
* Fix fgases sync
  [dianaboiangiu]

2.4.4 - (2025-03-05)
--------------------
* Add PATCH_AUDITOR_USERS to handle contact persons patching separately
  [dianaboiangiu]

2.4.3 - (2025-03-05)
--------------------
* Add PATCH_AUDITORS option
* Block assignation on /undertaking/[domain]/[company_id]/auditor/[auditor_uid]/assign/ if an auditor already has an active assignation
* Add /auditors/verification_envelopes/?reporting_envelope_url=/reporting/envelope/url endpoint
* Add /user/companies/v2?username=[username]&ecas_id=[ecas_id] endpoint
* Use section references in Readme API
  [dianaboiangiu]

2.4.2 - (2025-02-21)
--------------------
* Fetch more information on auditors
* Add endpoints for checking/assigning and unassigning an auditor to a company
  [dianaboiangiu]

2.4.1 - (2025-02-12)
--------------------
* Save ecas_id separately from the username
  [dianaboiangiu]

2.4.0 - (2024-12-19)
--------------------
* Add sync for auditors
  [dianaboiangiu]

2.3.19 - (2024-05-13)
---------------------
* Remove breakpoint
  [dianaboiangiu]

2.3.18 - (2024-05-13)
---------------------
* Add new endpoint user/companies to include ecas_id
  [dianaboiangiu]

2.3.17 - (2024-04-15)
---------------------
* Log companies affected by the latest changes
  [dianaboiangiu]

2.3.16 - (2024-04-02)
---------------------
* Update types and business profiles for FGAS
  [dianaboiangiu]

2.3.15 - (2024-03-20)
---------------------
* Fix fgas sync
  [dianaboiangiu]

2.3.14 - (2024-03-19)
---------------------
* Add ENV var STOCKS_INCLUDE_TESTDATA
  [dianaboiangiu]

2.3.13 - (2024-03-08)
---------------------
* Fix response decode
  [dianaboiangiu]

2.3.12 - (2024-03-07)
---------------------
* Return users with email in Users endpoint
  [dianaboiangiu]

2.3.11 - (2024-01-16)
--------------------
* Improve stocks script to update entries already created
  [dianaboiangiu]

2.3.10 - (2023-10-31)
--------------------
* Fix sync stocks
  [dianaboiangiu]

2.3.9 - (2023-07-26)
--------------------
* Make HEAD calls to bdr before making full calls
  [dianaboiangiu]

2.3.8 - (2023-07-17)
--------------------
* Fix Sqlalchemy error
  [dianaboiangiu]

2.3.7 - (2023-07-13)
--------------------
* Set a smaller range for updated_since
  [dianaboiangiu]

2.3.6 - (2023-07-13)
--------------------
* Fix Dockerfile
  [dianaboiangiu]

2.3.5 - (2023-07-13)
--------------------
* Allow calls to BDR only on check passed True
  [dianaboiangiu]

2.3.4 - (2023-05-24)
--------------------
* Use GET method for Zope request (Zope2  HEAD requests treated like DAV issue)
  [dianaboiangiu]

2.3.3 - (2023-05-03)
--------------------
* Fetch test stocks from API
  [dianaboiangiu]

2.3.2 - (2023-04-27)
--------------------
* Fetch stocks from API
  [dianaboiangiu]

2.3.1 - (2023-04-03)
--------------------
* Use old company id when necessary when checking if company folder exists
  [dianaboiangiu]

2.3.0 - (2023-03-31)
---------------------
* Improve format
* Improve bdr company folder creation
  [dianaboiangiu]

2.2.20 - (2023-03-29)
---------------------
* Fix sync issue on ODS/FGAS
  [dianaboiangiu]

2.2.19 - (2023-03-22)
---------------------
* Relax call bdr conditions
  [dianaboiangiu]

2.2.18 - (2023-02-14)
---------------------
* Fix ODS/FGAS companies have the same ID
  [dianaboiangiu]

2.2.17 - (2022-03-26)
---------------------
* Add env variable for checks exception
  [dianaboiangiu]

2.2.16 - (2022-03-25)
---------------------
* Add eori number to FGAS companies
  [dianaboiangiu]

2.2.15 - (2022-03-10)
---------------------
* Add eori number field to Undertaking
  [dianaboiangiu]

2.2.14 - (2022-02-23)
---------------------
* Fix types/business profile issue
* Limit calls to bdr
  [dianaboiangiu]

2.2.13 - (2022-02-15)
---------------------
* Set vat number label on FGAS companies
  [dianaboiangiu]

2.2.12 - (2022-02-04)
---------------------
* Make country conversion field longer
  [dianaboiangiu]

2.2.11 - (2022-02-02)
---------------------
* Change substance quantity postgres type
  [dianaboiangiu]

2.2.10 - (2022-01-31)
---------------------
* Add use_kind as unique field for license aggregation
  [dianaboiangiu]

2.2.9 - (2022-01-31)
--------------------
* Update country codes for licences
* Set eori number column in export companies
  [dianaboiangiu]

2.2.8 - (2022-01-12)
--------------------
* Accept fgas type without prefix
* Surpress scientific notation in quantity values
* FGAS GB companies should not report without OR
* Add new values for use kind import
* Use decimals for licences with laboratory uses desc
  [dianaboiangiu]

2.2.7 - (2021-11-16)
--------------------
* Add separate API url for FGAS/ODS
  [dianaboiangiu]

2.2.6 - (2021-09-14)
--------------------
* Fix representative data parsing
  [dianaboiangiu]

2.2.5 - (2021-09-14)
--------------------
* Fix representative data parsing
  [dianaboiangiu]

2.2.4 - (2021-09-02)
--------------------
* Add logging for company changes in synchronization
  [dianaboiangiu]

2.2.3 - (2021-07-29)
--------------------
* Fix match mail link to company details
  [dianaboiangiu]

2.2.2 - (2021-07-29)
--------------------
* Allow call bdr for all companies with check passed True
  [dianaboiangiu]

2.2.1 - (2021-06-28)
--------------------
* Fix call bdr command
  [dianaboiangiu]

2.2.0 - (2021-06-23)
--------------------
* Upgrade packages to latest version
* Upgrade python from 3.6 to 3.8
* And black and flake8 format
  [dianaboiangiu]

2.1.9 - (2021-04-13)
--------------------
* Add endpoint for all years licences listing
  [dianaboiangiu]

2.1.8 - (2021-03-31)
--------------------
* Management of old companyID and new companyID
* Fix error in stocks for FGAS companies
  [dianaboiangiu]

2.1.7 - (2021-03-25)
--------------------
* Add patch for allowing old GB OR to be used for reporting
  [dianaboiangiu]

2.1.6 - (2021-03-19)
--------------------
* Fix sync error
  [dianaboiangiu]

2.1.5 - (2021-03-18)
--------------------
* Fix country history on GB
  [dianaboiangiu]

2.1.4 - (2021-03-04)
--------------------
* Fix error
  [dianaboiangiu]

2.1.3 - (2021-03-04)
--------------------
* Fix endpoint in case address contains null values
  [dianaboiangiu]

2.1.2 - (2021-02-24)
--------------------
* Fix manufacturer restriction
  [dianaboiangiu]

2.1.1 - (2021-02-24)
--------------------
* Add manufacturer of equipment restriction on fgases
  [dianaboiangiu]

2.1.0 - (2021-02-23)
--------------------
* Fix pulling one company in sync script
  [dianaboiangiu]

2.0.34 - (2021-02-18)
---------------------
* Set default value on commands
  [dianaboiangiu]

2.0.33 - (2021-02-15)
---------------------
* Allow GB to report without representative
  [dianaboiangiu]

2.0.32 - (2021-02-12)
---------------------
* Change endpoint to show representative history only once
  [dianaboiangiu]

2.0.31 - (2021-02-11)
---------------------
* Set correct representative folder for UK code
  [dianaboiangiu]

2.0.30 - (2021-02-10)
---------------------
* Fix GB representative folder
  [dianaboiangiu]

2.0.29 - (2021-02-05)
---------------------
* Show all years in pau endpoint
  [dianaboiangiu]

2.0.28 - (2021-02-04)
---------------------
* Fix import/export quantities  on licences aggregation
  [dianaboiangiu]

2.0.27 - (2021-02-01)
---------------------
* Fix substances quantity integer on aggregation
  [dianaboiangiu]

2.0.26 - (2021-01-29)
---------------------
* Modify aggregation for licences
  [dianaboiangiu]

2.0.25 - (2021-01-19)
---------------------
* Fix UK repr in FGAS check
  [dianaboiangiu]

2.0.24 - (2021-01-18)
---------------------
* Add command for creating collection for NI companies
  [dianaboiangiu]

2.0.23 - (2021-01-14)
---------------------
* Add patching for licences aggregated endpoint
  [dianaboiangiu]

2.0.22 - (2021-01-11)
---------------------
* Add country history to user companies
  [dianaboiangiu]

2.0.21 - (2021-01-08)
---------------------
* Split UK into separate entities for ODS
* Split UK into two separate for FGAS
* Rearange migrations
  [dianaboiangiu]

2.0.20 - (2021-01-05)
---------------------
* Fix display for UK GB companies
  [dianaboiangiu]

2.0.19 - (2020-12-17)
---------------------
* Add fixes to stocks
  [dianaboiangiu]

2.0.18 - (2020-12-17)
---------------------
* Add type primary key to stock
  [dianaboiangiu]

2.0.17 - (2020-12-17)
---------------------
* Fix stocks import
  [dianaboiangiu]

2.0.16 - (2020-12-16)
---------------------
* Add stocks
  [dianaboiangiu]

2.0.15 - (2020-08-28)
---------------------
* Fix substance column country name
  [dianaboiangiu]

2.0.14 - (2020-08-28)
---------------------
* Add substance country name to substance
  [dianaboiangiu]

2.0.13 - (2020-08-21)
---------------------
* Switch to header token authorization for fetching BDR API data
  [dianaboiangiu]

2.0.12 - (2020-07-28)
--------------------
* Fix URL to application in email template
  [dianaboiangiu]

2.0.11 - (2020-06-18)
--------------------
* Fix healthcheck for syncs
* Add certificates path for https in environment
  [dianaboiangiu]

2.0.10 - (2020-04-02)
--------------------
* Update accepted types for ODS
  [dianaboiangiu]

2.0.10 - (2020-03-26)
--------------------
* Update accepted types for ODS
  [dianaboiangiu]

2.0.9 - (2020-03-17)
--------------------
* Fix undertaking remove script
  [dianaboiangiu]

2.0.8 - (2020-03-17)
--------------------
* Add script command for removing undertakings
  [dianaboiangiu]

2.0.7 - (2020-02-28)
--------------------
* Remove hash table
* Implement use updated_since for sync with licences
  [dianaboiangiu]

2.0.6 - (2020-02-25)
--------------------
* Fix sync fgases on missing highLevelUses
  [dianaboiangiu]

2.0.5 - (2020-02-20)
--------------------
* Fix BDR call for companies collection - missing oldcompany parameter
  [dianaboiangiu]

2.0.4 - (2020-02-12)
--------------------
* Add check_passed field on Excel export
  [dianaboiangiu]

2.0.3 - (2020-02-07)
--------------------
* Remove no representative exception for FGAS
* Optimize check passed command
* Fix undertaking domain on licences command
  [dianaboiangiu]

2.0.2 - (2020-02-07)
--------------------
* Add check_passed field on Excel export
  [dianaboiangiu]

2.0.1 - (2020-01-29)
--------------------
* Fix undertaking domain match on licences sync
  [dianaboiangiu]

2.0.0 - (2020-01-29)
--------------------
* Add syncronization and storage for ODS licences 
* Add aggregation for those licences into substances
* Add endpoints for exposing those substances, per year delivered
  [dianaboiangiu]

1.20.10 - (2020-01-15)
----------------------
* Add date_created, date_updated from ecr for undertakings
  [dianaboiangiu]

1.20.9 - (2019-10-18)
---------------------
* Allow only ODS companies with check_passed = True in 
  the application
  [dianaboiangiu]

1.20.8 - (2019-10-10)
---------------------
* Keep reporters for non reporting companies
  [dianaboiangiu]

1.20.7 - (2019-10-09)
---------------------
* Call bdr on check_passed changed
  [dianaboiangiu]

1.20.6 - (2019-09-27)
---------------------
* Upgraded deprecated packages with security issues
  [dianaboiangiu]

1.20.5 - (2019-09-25)
---------------------
* Upgraded deprecated packages with security issues
* Docker/README fixes
  [dianaboiangiu]

1.20.4 - (2019-08-27)
--------------------
* Return normal response for check sync
  [dianaboiangiu]

1.20.3 - (2019-08-27)
---------------------
* Remove header for check sync
  [dianaboiangiu]

1.20.2 - (2019-08-27)
---------------------
* Fix naive/aware time on check sync
  [dianaboiangiu]

1.20.1 - (2019-08-27)
---------------------
* Add endpoint for healthcheck of sync
  [dianaboiangiu]

1.20.0 - (2019-08-20)
---------------------
* Add check_passed field on Undertaking for checking if the
  company can report or not
* Add script for filling the new check_passed field
  [catalinjitea]

1.19.3 - (2019-07-12)
---------------------
* Add timeout to gunicorn
  [dianaboiangiu]

1.19.2 - (2019-05-15)
---------------------
* Fix typo
  [dianaboiangiu]

1.19.1 - (2019-05-15)
---------------------
* Patch users even if the company has no reporting obligation
  [dianaboiangiu]

1.19.0 - (2019-04-11)
*  Add back legal representative history
  [dianaboiangiu]

1.18.21 - (2019-04-08)
----------------------
* Set log execution time default
  [dianaboiangiu]

1.18.20 - (2019-04-08)
----------------------
* Fix typo
  [dianaboiangiu]

1.18.19 - (2019-04-08)
----------------------
* Set timezone for logs
  [dianaboiangiu]

1.18.18 - (2019-04-03)
----------------------
* Remove contact persons if company is rejected
  [dianaboiangiu]

1.18.17 - (2019-04-02)
----------------------
* Update rejected company if exists
  [dianaboiangiu]

1.18.16 - (2019-03-29)
----------------------
* Implement pagination for sync
* Accept Revision companies
  [dianaboiangiu]

1.18.15 - (2019-03-19)
----------------------
* Fix get_country_code Undertaking model
  [dianaboiangiu]

1.18.14 - (2019-03-13)
* Update bdr collection if representative has changed
* Remove legal representative history for now
  [dianaboiangiu]

1.18.13 - (2019-03-07)
----------------------
* Add legal representative history
  [dianaboiangiu]

1.18.12 - (2018-11-27)
----------------------
* Set double checks logging levels to warning
  [dianaboiangiu]

1.18.11 - (2018-08-09)
----------------------
* Stop accepting companies with status DISABLED
  [dianaboiangiu]

1.18.10 - (2018-03-29)
----------------------
* Set country_code 'NON-EU' for non-eu companies with no representative
  [dianaboiangiu]

1.18.9 - (2018-03-28)
---------------------
* Fix NON-EU slug
  [dianaboiangiu]

1.18.8 - (2018-03-28)
---------------------
* Set separate collection folder for NON-EU companies with no represent
  [dianaboiangiu]

1.18.7 - (2018-03-26)
---------------------
* Fix FGAS syncronization double checks
  [dianaboiangiu]

1.18.6 - (2018-03-26)
---------------------
* Fix ODS syncronization double checks
  [dianaboiangiu]

1.18.5 - (2018-03-22)
---------------------
* Add representative field in user companies endpoint
  [dianaboiangiu]

1.18.4 - (2018-03-15)
---------------------
* Fix country_code for MANUFACTURERS
  [dianaboiangiu]

1.18.3 - (2018-03-15)
---------------------
* Fix missing country in match
  [dianaboiangiu]

1.18.2 - (2018-03-15)
---------------------
* Fix fgases sync obligation check
  [dianaboiangiu]

1.18.1 - (2018-03-14)
---------------------
- Fix legal representatives checks for FGAS
  [dianaboiangiu]

1.18 - (2018-03-14)
-------------------
* Fix missing FGAS businessprofiles
  [dianaboiangiu]

1.17 - (2018-02-02)
-------------------
* Match companies agains the EORI number
  [nico4]

1.16 - (2018-01-19)
-------------------
* allow empty high level uses for certain undertakings
  [dianaboiangiu]

1.15 - (2018-01-16)
-------------------
* Handle case of empty list of high level uses
  [arielpontes]

1.14 - (2018-01-16)
-------------------
* Add warning message for companies in the businessprofile exceptions
  [arielpontes]

1.13 - (2018-01-16)
-------------------
* Add businessprofile exceptions to reporting
  [arielpontes]

1.12 - (2018-01-14)
------------------
* Configure matching settings
  [dianaboiangiu]

1.11 - (2018-01-29)
------------------
* Add date updated in candidate listing endpoint
  [dianaboiangiu]

1.10 - (2018-01-16)
------------------
* Fix verify none
  [dianaboiangiu]

1.9 - (2018-01-15)
------------------
* Fixed indentation issue
* Allow NONEU equirement manufactures that have a representative to report
  [olimpiurob]

1.8 - (2018-01-05)
------------------
* Fix status update
* Remove automatically approve message
  [catalinjitea]

1.7 - (2018-01-04)
------------------
* Add localsetting for patching companies and users
  [dianaboiangiu]

1.6 - (2018-01-04)
------------------
* Add verify/none endpoint
  [dianaboiangiu]

1.5 - (2018-01-04)
------------------
* Fix matching companies domains
  [dianaboiangiu]

1.4 - (2017-11-15)
------------------
* Equipment manufacturers missing from BDR
  - added API method to print a list with
    all NON EU companies without a legal representative
  [chiridra refs #80976]
* BDR registry integration of invitations and reminders:
  middleware and email sending
  - added API method export all users in JSON format
  [chiridra refs #84119]
* Added support for pulling ODS companies into the cache registry
  [dianaboiangiu]


1.3 - (2017-01-17)
------------------
* Task: use logspout cu send logs to graylog
  - used gunicorn instead of waitress-serve to start app
  [chiridra refs #80762]

1.2 - (2017-01-13)
------------------
* HG zip codes
  - zipcode field increased up to 64 characters
  - upgrade revision for alembic generated
  [chiridra refs #80654]

1.1 - (2017-01-09)
------------------
* Delete organisation matching from the Fgas Cache Registry
  - removed all the code related with bdr matching
  - removed unnecessary ENV variables
  - updated api accordingly
  - dropped unneeded tables: old_company and old_company_link
  - all synced companies are automatically approved
  - added new alembic revision
  - removed oldcompany_id field
  [chiridra refs #78691]

1.0 - (2016-10-23)
------------------
* Initial release
  [chiridra refs #78691]
