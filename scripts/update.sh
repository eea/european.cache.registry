#!/bin/bash

cd `dirname $0`/..
pwd
source sandbox/bin/activate

./manage.py sync fgases # update from last one
# todo write command sync for ods too
./manage.py sync bdr

./manage.py match run
