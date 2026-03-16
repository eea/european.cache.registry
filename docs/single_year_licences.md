## Syncronise with Licence Portal

* The licences for ODS are now taken from DG Clima and exposed:
        python -m flask sync licences -y 2025 -p 200

* The first parameter -y [2025], represents the year from which those deliveries are taken.
* The second parameter -p [200], represents the pageSize of the request made.

* The licences are taken for each company. When a new delivery arrives, all old deliveries of the company are moved to
the history object that contains that delivery and for that company.
