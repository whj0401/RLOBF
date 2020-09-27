#!/bin/bash

for d in `ls explanation/*_html -d`
do
    echo $d
    `python3 ./read_html_explanation_with_toc.py $d`
done
