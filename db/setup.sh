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

# paraphrases 
directory="paraphrases"
table_name="QuoteParaphrase"
for file in "$directory"/*.csv; do
    if [[ -f "$file" ]]; then
        echo "Loading $file into $table_name"
        psql -d $dbname -c "\COPY $table_name FROM '$file' WITH DELIMITER ',' NULL '' CSV"
    else
        echo "No CSV files found in $directory!"
    fi
done

# directories=("CivilWar" "pre-Elizabethan" "Elizabethan" "Carolinian" "Jacobean" "Interregnum" "CharlesII" "JamesII" "WilliamAndMary")
directories=("CivilWar" "pre-Elizabethan")

for dir in "${directories[@]}"; do
    echo "Processing directory: $dir"
    for i in {0..9}; do
        body_file="${dir}/A${i}_body.csv"
        margin_file="${dir}/A${i}_margin.csv"
        citations_file="${dir}/A${i}_citations.csv"

        if [[ -f "$body_file" ]]; then
            psql -d $dbname -c "\COPY Segment FROM '$body_file' WITH DELIMITER ',' NULL '' CSV"
        else
            echo "File $body_file not found!"
        fi
        
        if [[ -f "$margin_file" ]]; then
            psql -d $dbname -c "\COPY Marginalia FROM '$margin_file' WITH DELIMITER ',' NULL '' CSV"
        else
            echo "File $margin_file not found!"
        fi
        
        if [[ -f "$citations_file" ]]; then
            psql -d $dbname -c "\COPY Citation FROM '$citations_file' WITH DELIMITER ',' NULL '' CSV"
        else
            echo "File $citations_file not found!"
        fi
    done

    # Handle B files
    body_file="${dir}/B_body.csv"
    margin_file="${dir}/B_margin.csv"
    citations_file="${dir}/B_citations.csv"

    if [[ -f "$body_file" ]]; then
        psql -d $dbname -c "\COPY Segment FROM '$body_file' WITH DELIMITER ',' NULL '' CSV"
    else
        echo "File $body_file not found!"
    fi

    if [[ -f "$margin_file" ]]; then
        psql -d $dbname -c "\COPY Marginalia FROM '$margin_file' WITH DELIMITER ',' NULL '' CSV"
    else
        echo "File $margin_file not found!"
    fi

    if [[ -f "$citations_file" ]]; then
        psql -d $dbname -c "\COPY Citation FROM '$citations_file' WITH DELIMITER ',' NULL '' CSV"
    else
        echo "File $citations_file not found!"
    fi
done


