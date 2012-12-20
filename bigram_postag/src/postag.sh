#!/bin/bash
###########
# This script takes the corpus directory and runs a 5 fold cross validation process for
# calculating the transition and emission probabilities. The python script 'train.py'
# is used to form the transition table and emission table for one run.

if [ $# -ne 5 ]; then
	echo "Usage: <corpus-directory> <transition-prob-filename> <emission-prob-filename> [-train|-tag|-evaluate|-genstat] <iteration-number>" >&2
	exit 1
elif [ ! -d "$1" ]; then
	echo "Directory doesn't exist" >&2
	exit 2
fi
# corpus is the array with the name of the corpus files in it
corpus=($(ls -l "$1"| awk 'NR!=1 && !/^d/ {print $NF}'))

n=${#corpus[@]}

if [ $n -eq 0 ]; then
	echo "Directory empty" >&2
	exit 3
fi
# tmp is the transition table filename
ttmp="$2"
etmp="$3"

if [[ "$4" == "-train" ]]; then
	echo "Training the tagger"
	# first iteration of the cross validation, kept first $size
	# files for validation and rest are for training

	# initialize the transition table
	python initialize.py "$ttmp"
	# if there is already a etmp file, delete it
	if [[ -e $etmp ]]; then	rm "$etmp"; fi
	# iterate over the rest as training
	for (( i=0; i <$n; ++i )); do
	       python train.py "$1/${corpus[$i]}" "$ttmp" "$etmp"
	        if [ $? -ne 0 ]; then
	                exit $?
	        fi
	       echo "Training success $i:${corpus[$i]}"
	done
	# calculate the probabilities from transition table
	python calcprob.py "$ttmp" "$etmp"
elif [[ "$4" == "-tag" ]]; then
	echo "Tagging the corpus"
	# if tagged directory doesn't exist, create it
        if [[ ! -e $1/../tagged ]]; then
                mkdir $1/../tagged
        else
                rm $1/../tagged/*
        fi
	# retag all the corpuses
	for (( i=0; i <$n; ++i )); do
	        python tag.py "$ttmp" "$etmp" "$1/${corpus[$i]}"
		if [ $? -ne 0 ]; then
	                exit $?
	        fi
		mv $1/*_tagged.txt "$1/../tagged/"
	        echo "Tagging success $i:${corpus[$i]}"
	done
elif [[ "$4" == "-evaluate" ]]; then
	echo "Evaluating the tagger"
	# if cnf directory doesn't exist, create it
	if [[ ! -e $1/../cnf ]]; then
		mkdir $1/../cnf
	else
		rm $1/../cnf/*
	fi
	# form all the confusion matrices
	for (( i=0; i <$n; ++i )); do
		t=($(echo "${corpus[$i]}" | tr "." "\n"))
		tagged=$1"/../tagged/"$t"_tagged.txt"
	        python evaluation.py "$1/${corpus[$i]}" "$tagged"
		if [ $? -ne 0 ]; then
	                exit $?
	        fi
	        mv $1/*_cnf.csv "$1/../cnf/"
	        echo "Evaluation success $i:${corpus[$i]}"
	done
	# move the confusion matrices to results
	# create a directory with iteration number
	if [[ ! -e results/result$5 ]]; then mkdir "results/result"$5; fi
	mv $1/../cnf results/result$5/
	# merge the confusion matrices into one and save it in results
	
elif [[ "$4" == "-genstat" ]]; then
	echo 'Generating statistics'
	# if stat directory doesn't exist, create it
        if [[ ! -e $1/../stat ]]; then
                mkdir $1/../stat
        else
                rm $1/../stat/*
        fi
        # form the statistics for all the confusion matrices
        for (( i=0; i <$n; ++i )); do
                t=($(echo "${corpus[$i]}" | tr "." "\n"))
                cnf="results/result"$5"/cnf/"$t"_cnf.csv"
		stat=$1"/../stat/"$t"_stat.txt"
                python genstat.py "$cnf" "$stat"
                if [ $? -ne 0 ]; then
                        exit $?
                fi
                echo "Generating stat success $i:${corpus[$i]}"
        done
	# generate local statistics
	python locstat.py $1"/../stat"
	if [ $? -ne 0 ]; then exit $?; fi
	# create a directory with iteration number
	if [[ ! -e results/result$5 ]]; then mkdir "results/result"$5; fi
	# move the results to the numbered directory
	mv $1/../stat results/result$5/
	mv $1/../locstat.csv results/result$5
else
	echo "Undefined option $4"
fi

