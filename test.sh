#!/bin/bash

PWD=`pwd`

cd test_project
python manage.py test
EXIT1=$?

EXIT2=0
while getopts ":p" opt; do
    case $opt in
        p)
            pip install psycopg2-binary
            cd ../test_project_postgres
            python manage.py migrate
            python manage.py test --no-input
            EXIT2=$?
        ;;
    esac
done


cd $PWD

if test $EXIT1 -eq 0 && test $EXIT2 -eq 0
then
    exit 0
else
    exit 1
fi
