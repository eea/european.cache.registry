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


/user/list
----------

/user/detail/<pk>
-----------------


/company/list
-------------

/candidate/list
---------------

Lists all possible Company candidates for matching with existing Undertakings.

/candidate/verify/<undertaking_id>/<oldcompany_id>/
---------------------------------------------------

Verifies a link between an Undertaking (from FGR) and a Company (from BDR
 Registry).
