# Plotter

This script intends to make histograms in a flexible way based on RDataFrame.

## Structure

[Plotter/python/plotter.py](https://github.com/HephyAnalysisSW/Phase2Tracking/blob/main/Plotter/python/plotter.py): The main implementation of the plotting functions.

[Plotter/autoplotter.py](https://github.com/HephyAnalysisSW/Phase2Tracking/blob/main/Plotter/autoplotter.py): The interface to call plotter in command lines.

[Plotter/configs/config_hits.yaml](https://github.com/HephyAnalysisSW/Phase2Tracking/blob/main/Plotter/configs/config_hits.yaml): An example config file that defines variables and histograms to plot. Details of the config is explained in the file.

## Usage

### Run the plotter

- Setup the env:
```
cmssw-el8 #the container is needed on CLIP
cd CMSSW_15_1_1/src
cmsenv
```
- To run locally:
    - Prepare a `.txt` file for a list of files to run (for example, [Plotter/filelist.txt])
    - Run the plotter:
    ```
    python3 autoplotter.py --name phase2 --treeName "analysis/HitTree" --output ./example --config configs/config_hits.yaml --filelist filelist.txt
    ```
- To submit jobs on CLIP:
    - Put the paths and dataset names in `autoplotter.py`: https://github.com/HephyAnalysisSW/Phase2Tracking/blob/main/Plotter/autoplotter.py#L53-L58
    - Prepare the submission:
    ```
    python3 autoplotter.py --name phase2 --treeName "analysis/HitTree" --output /path/to/output --config configs/config_hits.yaml --filelist filelist.txt --submit --nfiles 1
    ```
    - Submit the jobs (this needs to be done without the `cmssw-el8` container):
    ```
    /groups/hephy/cms/ang.li/Tools/scripts/submit_el8 jobs.sh
    ```
