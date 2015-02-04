fgas-cache-server API Documentation
===================================

The fgas-cache-server API allows a client (BDR) to access cached data fetched
from various sources (FGas Registry, BDR Registry).

The API uses HTTP for transport, JSON as data format and does not require
authentication.

Overview
--------

Listing calls:

* `/undertaking/list` - all verified undertakings
* `/undertaking/list-small` - all verified undertakings but with fewer details
* `/undertaking/list/all` - all undertakings, including unverified
* `/undertaking/list_by_vat/[vat]` - filter by vat
* `/undertaking/filter` - count of undertakings, given field filters
* `/undertaking/[company_id]/details` - details about an undertaking
* `/user/list` - all users
* `/user/[username_or_email]/companies` - all verified companies and user has access to

Matching calls:

* `/candidate/list` -  all matching candidates
* `/candidate/verify/[company_id]/[collection_id]/` - link two objects
* `/candidate/unverify/[company_id]/` - unlink
* `/candidate/verify-none/[company_id]/` - mark an undertaking as linked, without a matching company
* `/candidate/list/verified` - list verified undertakings

Misc:

* `/matching_log` - matching logs
* `/data_sync_log` - data sync logs
* `/misc/user/export` - export users list as CSV
* `/misc/undertaking/export` - export companies list as CSV
* `/misc/settings` - overview of the middleware settings

Listing calls
=============

/undertaking/list
-----------------

Returns the list of all verified undertakings in the system, as fetched from FGR.
    
    [
      {
        "website": "WEBSITE--10085", 
        "status": "VALID", 
        "domain": "FGAS", 
        "users": [
          {
            "username": "nzhouray", 
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
        "oldcompany_id": true,
        "oldcompany_account": "fgas22331",
        "oldcompany_extid": 4,
        "collection_id": null, 
        "types": "FGAS_PRODUCER_IMPORTER_HFCS", 
        "undertaking_type": "FGASUndertaking", 
        "name": "FGAS-NMORGANIZATION--10085", 
        "company_id": 10085, 
        "date_created": "10/10/2014", 
        "vat": null
      },
    ]


/undertaking/list-small
-----------------------

    [
      {
        "domain": "FGAS", 
        "name": "NMORGANIZATION--11973", 
        "company_id": 11973, 
        "address": {
          "city": "city--9452", 
          "country": {
            "code": "PT", 
            "type": "EU_TYPE", 
            "name": "Portugal"
          }, 
          "zipcode": "zipcode--9452", 
          "number": "nrstreet--9452", 
          "street": "street--9452"
        }, 
        "date_created": "11/12/2014", 
        "vat": "VAT11973", 
        "users": [
          {
            "username": "nsecomic", 
            "first_name": "fname--11749", 
            "last_name": "lname--11749", 
            "email": "11749email@climaOds2010.yyy"
          }
        ]
      }
    ]

/undertaking/list/all
---------------------

Returns a list of all undertakings in the system (verified or not), as fetched 
from FGR.
    
    [
      {
        "website": "WEBSITE--10085", 
        "status": "VALID", 
        "domain": "FGAS", 
        "users": [
          {
            "username": "nzhouray", 
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
        "oldcompany_id": true,
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

/undertaking/list_by_vat/<vat>
------------------------------

Returns a list of all verified undertakings in the system given by their VAT, 
as fetched  from FGR.
    
    [
      {
        "name": "FGAS-NMORGANIZATION--10078", 
        "company_id": 10078
      }
    ]

/undertaking/filter?[name|id|vat|countrycode|OR_vat|OR_name]
------------------------------------------------------------

Return true or false if companies matching the filter exists.

The *OR_name* and *OR_vat* filters refer to EuLegalRepresentative.

The *name* and *OR_name* filters use LIKE queries.

    [
      {
        "exists": true,
        "count": 1
      }
    ]

/undertaking/[company_id]/details
---------------------------------

Returns an undertakings details from the system, as fetched from FGR.
    
    {
      "company_id": 10085, 
      "collection_id": null,      
      "oldcompany_id": null, 
      "undertaking_type": "FGASUndertaking", 
      "website": "WEBSITE--10085", 
      "status": "VALID", 
      "domain": "FGAS", 
      "name": "FGAS-NMORGANIZATION--10085", 
      "phone": "+3212310085", 
      "oldcompany_id": true,
      "oldcompany_account": "fgas22331",
      "oldcompany_extid": 4,
      "businessprofile": {
        "highleveluses": ""
      }, 
      "candidates": [], 
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
          "username": "nzhouray", 
          "first_name": "fname--9367", 
          "last_name": "lname--9367", 
          "email": "9367email@climaOds2010.yyy"
        }
      ]
    }

/user/list
----------

Returns a list of all undertakings in the system, as fetched from FGR.
    
    [
      {
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
        "name": "FGAS-NMORGANIZATION--10085"
      }
    ]

Matching calls
==============

These calls are related to the matching algorithm between Undertakings and
Old Companies. An automated process creates the links between these objects,
then manual user intervention is required for validating these links.

The methods available via HTTP POST should also encapsulate the username, for
logging purposes.

/candidate/list
---------------

Lists all possible Company candidates for matching with existing Undertakings.

    [
      {
        "undertaking": {
          "website": "WEBSITE--10085", 
          "status": "VALID", 
          "name": "FGAS-NMORGANIZATION--10085", 
          "undertaking_type": "FGASUndertaking", 
          "date_updated": "10/10/2014", 
          "domain": "FGAS", 
          "company_id": 10085, 
          "phone": "+3212310085", 
          "types": "FGAS_PRODUCER_IMPORTER_HFCS", 
          "country_code": "CN", 
          "date_created": "10/10/2014", 
          "vat": null, 
        }, 
        "links": [
          {
            "website": null, 
            "account": "fgas22331", 
            "name": "Airconditioning Group Ltd", 
            "company_id": 4, 
            "date_registered": "07/12/2012", 
            "country_code": "gb", 
            "active": true, 
            "vat_number": "634456631", 
            "eori": null,
            "obligation": "fgases"
          }, 
          {
            "website": "", 
            "account": "fgas21484", 
            "name": "Alcan International Network Ltd", 
            "company_id": 5, 
            "date_registered": "07/12/2012", 
            "country_code": "gb", 
            "active": false, 
            "vat_number": "", 
            "eori": "",
            "obligation": "fgases"
          }, 
      },
    ]

/candidate/verify/[company_id]/[collection_id]/ - POST
------------------------------------------------------

Verifies a link between an Undertaking (from FGR) and a Company (from BDR
 Registry).

    {
      "verified": true, 
      "company_id": 10085, 
      "collection_id": 4, 
      "date_verified": "24/11/2014", 
      "date_added": "24/11/2014",
    }
    
    
/candidate/unverify/[company_id]/ - POST
----------------------------------------

Removes any link between an Undertaking (from FGR) and a Company.

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
      "oldcompany_id": null,
      "date_created": "10/10/2014",
      "oldcompany_account": null,
      "vat": null,
      "businessprofile_id": 1
    }
    
/candidate/verify-none/[company_id]/ - POST
-------------------------------------------

Verifies a company is unlinked with any old companies.

    {
      "verified": true, 
      "company_id": 10085
    }


/candidate/list/verified
------------------------

Lists the already verified undertakings.

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
        "oldcompany_id": null,
        "date_created": "10/10/2014",
        "oldcompany_account": null,
        "vat": null,
        "businessprofile_id": 1
      }
    ]


/oldcompanies/list/valid/
-------------------------

List all the old valid companies.
    
    [
      {
        "website": "", 
        "account": "fgas23460", 
        "name": "3M Belgium N.V.", 
        "company_id": 1, 
        "date_registered": "07/12/2012 13:01", 
        "valid": true, 
        "country_code": "be", 
        "active": true, 
        "vat_number": "", 
        "eori": ""
      }
    ]


/oldcompanies/list/invalid/
---------------------------

List all the old invalid companies.
    
    [
      {
        "website": null, 
        "account": "fgas22700", 
        "name": "AIR PRODUCTS S.A", 
        "company_id": 3, 
        "date_registered": "07/12/2012 13:01", 
        "valid": false, 
        "country_code": "be", 
        "active": true, 
        "vat_number": null, 
        "eori": null
      }


/oldcompanies/<pk>/valid/
-------------------------

On POST method, sets the valid flag of an old company to True.


/oldcompanies/<pk>/invalid/
---------------------------

On POST method, sets the valid flag of an old company to False.


Misc calls
==========

/matching_log
-------------

Lists a matching log list for 2 companies and the user who made it at which 
time, sorted in decrease order by timestamp.

    [
      {
        "verified": true, 
        "timestamp": "27/11/2014 15:56", 
        "company_id": 10051, 
        "user": "vitalie", 
        "oldcompany_id": 4
      }
    ]


/data_sync_log
--------------

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


/misc/undertaking/export
------------------------

This URL is used to export the list of undertakings from ``/undertakings/list``
as an Excel file.


/misc/user/export
-----------------

This URL is used to export the list of users with their companies and the 
companies' contact persons as an Excel file.


/misc/settings
--------------

Display the value of the configured middleware settings

    {
      "API_URL": "http://example.com", 
      "AUTO_VERIFY_COMPANIES": false
    }
