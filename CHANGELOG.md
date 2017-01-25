Changelog
=========

1.4.dev0 - (unreleased)
-----------------------
* Equipment manufacturers missing from BDR
  - added API method to print a list with
    all NON EU companies without a legal representative
  [chiridra refs #80976]

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
