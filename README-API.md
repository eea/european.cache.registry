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
        "id": 1,
        "external_id": 10006,
        "name": "orgTest",
        "website": null,
        "status": "VALID",
        "date_created": "06/11/2014",
        "date_updated": "06/11/2014",
        "domain": "FGAS",
        "phone": "+3234343",
        "vat": null,
        "address": {
            "city": "asdfsafsaf",
            "country": {
                "code": "CN",
                "type": "NONEU_TYPE",
                "id": 1,
                "name": "China (excluding Hong Kong and Macao)"
            },
            "zipcode": "1234", "number": null, "street": "street", "id": 1
        },
        "types": "FGAS_PRODUCER_IMPORTER_EXPORTER_NON_HFCS,",
        "users": [
            {
            "username": "user1",
            "first_name": "User 1",
            "last_name": "User 1",
            "id": 1,
            "email": "user1@mock.ec.europa.eu"
            }
        ],
        "businessprofile_id": 1
        "oldcompany_id": null,
        }
    ]


/undertaking/detail/<pk>
------------------------

Returns a an undertakings details from the system, as fetched from FGR.

    {
      "website": "WEBSITE--91542",
      "status": "VALID",
      "name": "General Gas S.r.l",
      "represent": null,
      "date_updated": "06/11/2014",
      "address": {
        "city": "city--7243",
        "country": {
          "code": "IT",
          "type": "EU_TYPE",
          "id": 3,
          "name": "Italy"
        },
        "zipcode": "zipcode--72432",
        "number": "nrstreet--7243",
        "street": "street--72432",
        "id": 3
      },
      "domain": "FGAS",
      "phone": "+3212391542",
      "businessprofile": {
        "highleveluses": "",
        "id": 2
      },
      "types": "FGAS_PRODUCER_IMPORTER_HFCS",
      "country_code": "IT",
      "oldcompany_id": null,
      "date_created": "20/10/2014",
      "users": [
        {
          "username": "test@test.be",
          "first_name": "test",
          "last_name": "test",
          "id": 2,
          "email": "test@test.be"
        },
        {
          "username": "user1",
          "first_name": "User 1",
          "last_name": "User 1",
          "id": 3,
          "email": "user1@mock.ec.europa.eu"
        },
        {
          "username": "USERNAME9153",
          "first_name": "fname--9065",
          "last_name": "lname--9065",
          "id": 4,
          "email": "9065email@climaOds2010.yyy"
        }
      ],
      "external_id": 9154,
      "id": 2,
      "vat": "IT1358910634"
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
        "account": null,
        "name": "orgTest",
        "country": "CN",
        "domain": "FGAS",
        "oldcompany_id": null,
        "external_id": 10006,
        "id": 1
      }
    ]

/company/list
-------------

Returns a list of all companies in the system, as fetched from FGR.

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

/candidate/verify/<undertaking_id>/<oldcompany_id>/
---------------------------------------------------

Verifies a link between an Undertaking (from FGR) and a Company (from BDR
 Registry).
