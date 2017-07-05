#!/bin/bash

PWD=`pwd`

cd test_project
python manage.py test

if [ "$PY27_DJANGO17" = "0" ]; then
    while getopts ":p" opt; do
        case $opt in
            p)
                pip install psycopg2==2.6.2
                cd ../test_project_postgres
                python manage.py test
           ;;
        esac
    done
fi


cd $PWD
