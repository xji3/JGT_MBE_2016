#!/bin/bash
python get_site_posterior.py --paralog1 YJR048W --paralog2 YEL039C --model HKY --clock --force --no-dir --no-gBGC
python get_site_posterior.py --paralog1 YJR048W --paralog2 YEL039C --model HKY --clock --no-force --no-dir --no-gBGC
python get_site_posterior.py --paralog1 YJR048W --paralog2 YEL039C --model HKY --clock --no-force --no-dir --gBGC
python get_site_posterior.py --paralog1 YJR048W --paralog2 YEL039C --model HKY --clock --no-force --dir --no-gBGC
python get_site_posterior.py --paralog1 YJR048W --paralog2 YEL039C --model HKY --clock --no-force --dir --gBGC
python get_site_posterior.py --paralog1 YJR048W --paralog2 YEL039C --model MG94 --clock --force --no-dir --no-gBGC
python get_site_posterior.py --paralog1 YJR048W --paralog2 YEL039C --model MG94 --clock --no-force --no-dir --no-gBGC
python get_site_posterior.py --paralog1 YJR048W --paralog2 YEL039C --model MG94 --clock --no-force --no-dir --gBGC
python get_site_posterior.py --paralog1 YJR048W --paralog2 YEL039C --model MG94 --clock --no-force --dir --no-gBGC
python get_site_posterior.py --paralog1 YJR048W --paralog2 YEL039C --model MG94 --clock --no-force --dir --gBGC
