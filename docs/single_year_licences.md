## Syncronise with Licence Portal

* The licences for ODS are now taken from DG Clima and exposed:
        python -m flask sync licences 2017 2017-1
        python -m flask sync licences 2017 2017-1

* The first parameter [2017], represents the year from which those deliveries are taken.
* The second parameter [2017-1], represents the name of the delivery.

* The licences are taken for each company. When a new delivery arrives, all old deliveries of the company are moved to
the history object that contains that delivery and for that company.