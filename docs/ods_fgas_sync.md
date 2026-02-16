## Syncronize companies

* Fetch the latest data from a test server:

        python -m flask sync fgases [-d 30]
        python -m flask sync ods [-d 30]


* In order to sync from a long time ago, it is advised to use pagination. To use pagination, you must give -p parameter, containing the
* number of companies that are brought in one request.

        python -m flask sync fgases [-d 30] [-p 100]
        python -m flask sync ods [-d 30] [-p 100]

* Fetch a specific company by providing the external id:

        python -m flask sync fgases [-i 12345]
        python -m flask sync ods [-i 12345]


* In order to sync BDR collections title with the cache server's corresponding undertakings name:

        python -m flask sync sync_collections_title
