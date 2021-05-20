#!/bin/bash

set -e

TESTDIR='test_project'
while getopts ":p" opt; do
    case $opt in
        p)
            TESTDIR='test_project_postgres'
        ;;
    esac
done

cd $TESTDIR
python manage.py migrate
python manage.py test
