#!/bin/sh
PWD=`pwd`
cd test_project
python manage.py test
cd $PWD
