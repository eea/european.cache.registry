fgas-cache-server API Documentation
===================================

The fgas-cache-server API allows a client (BDR) to access cached data fetched
from various sources (FGas Registry, BDR Registry).

The API uses HTTP for transport, JSON as data format and does not require
authentication.

/undertaking/list
-----------------

Returns a list of all undertakings in the system, as fetched from FGR.
    
    [
      {
        "website": "WEBSITE--10085", 
        "status": "VALID", 
        "name": "FGAS-NMORGANIZATION--10085", 
        "undertaking_type": "FGASUndertaking", 
        "date_updated": "10/10/2014", 
        "represent_id": 1, 
        "address": {
          "city": "city--7953", 
          "country": {
            "code": "CN", 
            "type": "NONEU_TYPE", 
            "id": 1, 
            "name": "China (excluding Hong Kong and Macao)"
          }, 
          "zipcode": "zipcode--7953", 
          "number": "nrstreet--7953", 
          "street": "street--7953", 
          "id": 1
        }, 
        "domain": "FGAS", 
        "company_id": 10085, 
        "phone": "+3212310085", 
        "types": "FGAS_PRODUCER_IMPORTER_HFCS", 
        "country_code": "CN", 
        "oldcompany_id": null, 
        "date_created": "10/10/2014", 
        "users": [
          {
            "username": "nzhouray", 
            "first_name": "fname--9367", 
            "last_name": "lname--9367", 
            "id": 1, 
            "email": "9367email@climaOds2010.yyy"
          }
        ], 
        "id": 1, 
        "vat": null, 
        "businessprofile_id": 1
      }
    ]


/undertaking/detail/<pk>
------------------------

Returns a an undertakings details from the system, as fetched from FGR.
    
    {
      "website": "WEBSITE--9478", 
      "status": "VALID", 
      "represent": null, 
      "date_updated": "10/10/2014", 
      "oldcompany_id": null, 
      "domain": "FGAS", 
      "phone": "+321239478", 
      "country_code": "UK", 
      "address": {
        "city": "city--7544", 
        "country": {
          "code": "UK", 
          "type": "EU_TYPE", 
          "id": 7, 
          "name": "United Kingdom"
        }, 
        "zipcode": "zipcode--7544", 
        "number": "nrstreet--7544", 
        "street": "street--7544", 
        "id": 211
      }, 
      "id": 185, 
      "types": "FGAS_PRODUCER_IMPORTER_HFCS,FGAS_EXPORTER_HFCS", 
      "users": [
        {
          "username": "nextonhu", 
          "first_name": "fname--2904", 
          "last_name": "lname--2904", 
          "id": 208, 
          "email": "2904email@climaOds2010.yyy"
        }
      ], 
      "undertaking_type": "FGASUndertaking", 
      "name": "FGAS-NMORGANIZATION--9478", 
      "company_id": 9478, 
      "businessprofile": {
        "highleveluses": "", 
        "id": 185
      }, 
      "candidates": [], 
      "date_created": "10/10/2014", 
      "vat": "VAT9478"
    }

/user/list
----------

Returns a list of all undertakings in the system, as fetched from FGR.
    
    [
      {
        "username": "user1",
        "first_name": "User 1",
        "last_name": "User 1",
        "id": 1,
        "email": "user1@mock.ec.europa.eu"
      },
      {
        "username": "test@test.be",
        "first_name": "test",
        "last_name": "test",
        "id": 2,
        "email": "test@test.be"
      },
      {
        "username": "USERNAME9153",
        "first_name": "fname--9065",
        "last_name": "lname--9065",
        "id": 4,
        "email": "9065email@climaOds2010.yyy"
      }
    ]

/user/detail/<pk>
-----------------

Returns the list of undertakings for a user given by its unique username.

    [
      {
        "domain": "FGAS", 
        "name": "FGAS-NMORGANIZATION--10085", 
        "country": "CN", 
        "account": null, 
        "company_id": 10085, 
        "collection_id": null, 
        "id": 1
      }
    ]

/company/list
-------------

Returns a list of all EuLegalRepresentativeCompanies in the system, as fetched 
from FGR.

    [
      {
        "name": "eulegalrep org",
        "contact_last_name": "lname--9270",
        "vatnumber": "VAT23424",
        "contact_email": "email@email.com",
        "contact_first_name": "fname--9270",
        "address": {
          "city": "asdfafd",
          "country_id": 2,
          "zipcode": "1233",
          "number": null,
          "street": "street",
          "id": 2
        },
        "id": 1
      }
    ]

/candidate/list
---------------

Lists all possible Company candidates for matching with existing Undertakings.

    [
      {
        "undertaking": {
          "website": null, 
          "status": "VALID", 
          "address_id": 30, 
          "name": "Savi Technologie sp. z o.o.", 
          "undertaking_type": "FGASUndertaking", 
          "date_updated": "10/10/2014", 
          "represent_id": null, 
          "domain": "FGAS", 
          "phone": "+00000", 
          "types": "FGAS_PRODUCER_IMPORTER_HFCS", 
          "country_code": "PL", 
          "oldcompany_id": null, 
          "date_created": "10/10/2014", 
          "external_id": 9989, 
          "id": 23, 
          "vat": "PL8942815717", 
          "businessprofile_id": 23
        }, 
        "links": [
          {
            "website": null, 
            "account": "fgas24913", 
            "name": "Savi Technologie Sp. z o.o.", 
            "date_registered": "07/12/2012", 
            "country_code": "pl", 
            "active": true, 
            "vat_number": "", 
            "eori": null, 
            "external_id": 100, 
            "id": 100
          }
        ]
      }
    ]

/candidate/verify/<undertaking_id>/<oldcompany_id>/
---------------------------------------------------

Verifies a link between an Undertaking (from FGR) and a Company (from BDR
 Registry).

    {
      "oldcompany_id": 249, 
      "verified": true, 
      "undertaking_id": 73, 
      "date_verified": "21/11/2014", 
      "date_added": "18/11/2014"
    }
