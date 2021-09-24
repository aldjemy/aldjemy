#!/bin/bash

set -e

TESTDIR='test_project'
SETTINGS='test_project.settings'
while getopts ":p" opt; do
    case $opt in
        p)
            TESTDIR='test_project_postgres'
            SETTINGS='test_project_postgres.settings'
            # To consume the first parameter and pass the rest to pytest
            shift
        ;;
    esac
done

cd $TESTDIR
pytest --ds=$SETTINGS $@
