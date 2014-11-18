#!/bin/bash

cd `basename $0`/..
source sandbox/bin/activate

./manage.py sync test_fgases # update from last one
./manage.py sync test_bdr

./manage.py match test
