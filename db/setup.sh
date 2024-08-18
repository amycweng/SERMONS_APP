#!/bin/bash

mypath=`realpath $0`
mybase=`dirname $mypath`
cd $mybase

datadir="${1:-data/}"
if [ ! -d $datadir ] ; then
    echo "$datadir does not exist under $mybase"
    exit 1
fi

source /Users/amycweng/anaconda3/envs/sermons_app
dbname='sermons'

if [[ -n `psql -lqt | cut -d \| -f 1 | grep -w "$dbname"` ]]; then
    dropdb $dbname
fi
createdb $dbname

psql -af create.sql $dbname
cd $datadir
psql -af $mybase/load.sql $dbname
for i in {2..9}; do
   psql -d $dbname -c "\COPY Segment FROM 'CivilWar/A${i}_body.csv' WITH DELIMITER ',' NULL '' CSV"
   psql -d $dbname -c "\COPY Marginalia FROM 'CivilWar/A${i}_margin.csv' WITH DELIMITER ',' NULL '' CSV"
   psql -d $dbname -c "\COPY Citation FROM 'CivilWar/A${i}_citations.csv' WITH DELIMITER ',' NULL '' CSV"
done
psql -d $dbname -c "\COPY Segment FROM 'CivilWar/B_body.csv' WITH DELIMITER ',' NULL '' CSV"
psql -d $dbname -c "\COPY Marginalia FROM 'CivilWar/B_margin.csv' WITH DELIMITER ',' NULL '' CSV"
psql -d $dbname -c "\COPY Citation FROM 'CivilWar/B_citations.csv' WITH DELIMITER ',' NULL '' CSV"
