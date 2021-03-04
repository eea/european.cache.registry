Changelog
=========

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
