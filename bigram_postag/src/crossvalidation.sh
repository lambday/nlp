#!/bin/bash

if [ $# -ne 2 ]; then
        echo "Usage: <corpus-directory> <folds?>" >&2
        exit 1
elif [ ! -d "$1" ]; then
        echo "Directory doesn't exist" >&2
        exit 2
fi

if [[ ! -e ./results ]]; then mkdir results; else rm -rf ./results/*; fi
if [[ ! -e ./trainset ]]; then mkdir trainset; else rm -rf ./trainset/*; fi
if [[ ! -e ./testset ]]; then mkdir testset; else rm -rf ./testset/*; fi

# corpus is the array with the name of the corpus files in it
corpus=($(ls -l "$1"| awk 'NR!=1 && !/^d/ {print $NF}'))
n=${#corpus[@]}
FOLD=$2

# size will be the size of the buckets
size=`expr $n / $FOLD`

# checklist of which files are done
for (( i=1; i <$n; ++i )); do
	checklist[i]=0
done
#echo ${checklist[*]}
lim=`expr $FOLD - 1`
################# generate 5 buckets of data ######################
for (( i=0; i <$lim; ++i )); do
	for (( j=0; j <$size; ++j )); do
		number=$[ ( $RANDOM % $n )]
		while [[ checklist[$number] -ne 0 ]]; do
			number=$[ ( $RANDOM % $n )]
		done
		# enter in the checklist
		checklist[number]=1
		# enter the current index into a bucket
		bucket[j]=$number
	done
	# make corpusdata directory with i as index
	if [[ ! -e ./data$i ]]; then mkdir data$i; else rm -rf ./data$i/*; fi
	# copy the indexed files into this directory
	for (( j=0; j <$size; ++j )); do
		cp $1/${corpus[${bucket[$j]}]} ./data$i/${corpus[${bucket[$j]}]}
	done
done

j=0
for (( i=0; i<$n; ++i )); do
	if [[ ${checklist[$i]} -eq 0 ]]; then
		checklist[i]=1
		bucket[j]=$i
		j=`expr $j + 1`
	fi
done
# make corpusdata directory with i as index
if [[ ! -e ./data$lim ]]; then mkdir data$lim; else rm -rf ./data$lim/*; fi
# copy the indexed files into this directory
for (( j=0; j <${#bucket[@]}; ++j )); do
        cp $1/${corpus[${bucket[$j]}]} ./data$lim/${corpus[${bucket[$j]}]}
done
####################################################

for (( i=0; i<$FOLD; ++i )); do
	# pick ith bucket and move them to testset
	cp ./data$i/* ./testset/
	# copy the rest of the buckets to trainset
	for (( j=0; j<$FOLD; ++j )); do
		if [[ $j -ne $i ]]; then
			cp ./data$j/* ./trainset/
		fi
	done
	# run the training script with ./trainset as the corpus directory
	bash postag.sh ./trainset tmp1 tmp2 -train $i >> training.log
	# run the tag, evaluate and genstat scripts with ./testset as the corpus directory
	bash postag.sh ./testset tmp1 tmp2 -tag $i >> tagging.log
	bash postag.sh ./testset tmp1 tmp2 -evaluate $i >> evaluate.log
	bash postag.sh ./testset tmp1 tmp2 -genstat $i >> genstat.log
	python mergecnf.py ./results $i
	python genstat.py ./results/$i"_cnf.csv" ./results/$i"_stat.txt"

	rm -rf ./testset/*
	rm -rf ./trainset/*
done
python locstat.py ./results/ >> results.log
mv locstat.csv globstat.csv
rm -rf testset tagged data* trainset
