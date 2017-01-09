Changelog
=========

1.2.dev0 - (unreleased)
-----------------------

1.1 - (2017-01-09)
-----------------------
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
