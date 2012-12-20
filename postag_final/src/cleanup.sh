#!/bin/bash

# clean up the previous runs
if [[ -e ./results ]]; then rm -rf ./results; fi
if [[ -e overall.log ]]; then rm overall.log; fi
rm conf_run* tagstat_run*
