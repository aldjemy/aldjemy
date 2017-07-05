#!/bin/bash

PWD=`pwd`

cd test_project
python manage.py test
# django.contrib.postgres support in django > 1.7
SUPPORTS_POSTGRES=$(python -c "import django; print(django.VERSION > (1,7,0,'final',0))")

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
