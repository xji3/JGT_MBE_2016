#!/bin/bash
python Run_unfinished.py --paralog1 YDR518W --paralog2 YCL043C --model HKY --no-clock --force --no-dir --no-gBGC --switch
python Run_unfinished.py --paralog1 YDR518W --paralog2 YCL043C --model MG94 --no-clock --force --no-dir --no-gBGC --switch
python Run_unfinished.py --paralog1 YDR518W --paralog2 YCL043C --model HKY --no-clock --no-force --no-dir --no-gBGC --switch
python Run_unfinished.py --paralog1 YDR518W --paralog2 YCL043C --model MG94 --no-clock --no-force --no-dir --no-gBGC --switch
python Run_unfinished.py --paralog1 YDR518W --paralog2 YCL043C --model HKY --no-clock --no-force --no-dir --gBGC --switch
python Run_unfinished.py --paralog1 YDR518W --paralog2 YCL043C --model MG94 --no-clock --no-force --no-dir --gBGC --switch
python Run_unfinished.py --paralog1 YDR518W --paralog2 YCL043C --model HKY --no-clock --no-force --dir --no-gBGC --switch
python Run_unfinished.py --paralog1 YDR518W --paralog2 YCL043C --model MG94 --no-clock --no-force --dir --no-gBGC --switch
python Run_unfinished.py --paralog1 YDR518W --paralog2 YCL043C --model HKY --no-clock --no-force --dir --gBGC --switch
python Run_unfinished.py --paralog1 YDR518W --paralog2 YCL043C --model MG94 --no-clock --no-force --dir --gBGC --switch
