#!/bin/bash

if [[ $# -ne 3 ]]; then echo "Usage: $0 <corpus_directory> <number_of_runs> <folds>"; exit 1; fi

# clean up the previous runs
bash cleanup.sh

for (( i=0; i<$2; ++i )); do
	bash crossvalidation.sh $1 $3
	python mergecnf.py "./results" $i
	python genstat.py conf_run$i.csv tagstat_run$i.txt >> overall.log
done
python tagstat.py tagstat_run $2
rm -rf ./results
for (( i=0; i<$2; ++i )); do
	rm tagstat_run$i.txt
done
