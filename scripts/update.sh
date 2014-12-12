#!/bin/bash

cd `dirname $0`/..
pwd
source sandbox/bin/activate

./manage.py sync test_fgases # update from last one
./manage.py sync test_bdr

./manage.py match run
