#!/bin/bash

if [[ $# -ne 3 ]]; then echo "Usage: $0 <corpus_directory> <number_of_runs> <folds>"; exit 1; fi

# clean up the previous runs
bash cleanup.sh

mkdir runs

for (( i=0; i<$2; ++i )); do
	bash crossvalidation.sh $1 $3
	mv globstat.csv runs/globstat$i.csv
done

python runstats.py runs runstat.csv
python overallstat.py results.log >> overall.log
