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
cd $datadir

# directories=("CivilWar" "pre-Elizabethan" "Elizabethan" "Carolinian" "Jacobean" "Interregnum" "CharlesII" "JamesII" "WilliamAndMary")
directories=("Elizabethan" "pre-Elizabethan")

for dir in "${directories[@]}"; do
    echo "Processing directory: $dir"

    qp_file="${dir}/paraphrases.csv"
    psql -d $dbname -c "\COPY QuoteParaphrase FROM '$qp_file' WITH DELIMITER ',' NULL '' CSV"
    qp_file="${dir}/paraphrases_uncertain.csv"
    psql -d $dbname -c "\COPY QuoteParaphrase FROM '$qp_file' WITH DELIMITER ',' NULL '' CSV"
    
done


