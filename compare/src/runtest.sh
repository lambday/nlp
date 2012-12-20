#!/bin/bash

if [[ $# -ne 3 ]]; then echo "Usage: $0 <corpus_directory> <number_of_runs> <folds>"; exit 1; fi
rm *.log

for (( i=0; i<$2; ++i )); do
	bash crossvalidation2.sh $1 $3
done
