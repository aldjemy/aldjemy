#!/bin/bash

PWD=`pwd`

cd test_project
python manage.py test
EXIT1=$?

EXIT2=0
#if [ "$PY27_DJANGO17" = "0" ]; then
    while getopts ":p" opt; do
        case $opt in
            p)
                pip install psycopg2
                cd ../test_project_postgres
                python manage.py test
                EXIT2=$?
           ;;
        esac
    done
#fi


cd $PWD

if test $EXIT1 -eq 0 && test $EXIT2 -eq 0
then
    exit 0
else
    exit 1
fi
