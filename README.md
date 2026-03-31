# Instructions

This repository produces the ntuples for tracker rechits.

## Install the necessary softwares
This has to be done only once.
```
cmssw-el8 # activate the container for the CMSSW
cmsrel CMSSW_15_0_0_pre3
cd CMSSW_15_0_0_pre3/src
cmsenv
git clone git@github.com:HephyAnalysisSW/Phase2Tracking.git
scram b -j 8 # compile the code
```

## Produce the ntuple

To do this, first login to CLIP/lxplus/etc. and set up the environment:
```
cmssw-el8
cd /path/to/CMSSW_15_0_0_pre3/src
cmsenv
```
If you are using files from `eos`, make sure you have a valid grid certificate and do:
```
voms-proxy-init -voms cms --valid 192:00 --vomslife 192:0
```
Then run the config to produce the ntuple (running some ttbar events for example):
```
cd Phase2Tracking/HitAnalyzer/test/
cmsRun rechittreewa_tt_cfg.py
```
This produces an root file with name `rechits_tree_tt.root`.
