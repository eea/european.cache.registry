#!/bin/bash

cd `dirname $0`/..
pwd
source sandbox/bin/activate

python -m flask sync fgases # update from last one
# todo write command sync for ods too
python -m flask sync bdr

python -m flask match run
