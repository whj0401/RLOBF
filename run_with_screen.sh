#!/bin/bash

`screen -t obfs -S obfs -L -Logfile ./output/screen.log time sh run_$1.sh`


