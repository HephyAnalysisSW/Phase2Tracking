#
# Show definitions for histograms from a configuration file
#
import sys
from drawHitsConfiguration import *
import argparse

def printDict(d,indent=0):
    for k,v in d.items():
        if type(v)==dict:
            print(indent*" "+k+":")
            printDict(v,indent+2)
        else:
            print(indent*" "+k+":",v)
            
if __name__=="__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--isEff', help='Select efficiency plots', action='store_true', default=False)
    parser.add_argument('--isNoEff', help='Veto efficiency plots', action='store_true', default=False)
    parser.add_argument('--isProfile', help='Select profile histograms', action='store_true', default=False)
    parser.add_argument('--isNoProfile', help='Veto profile histograms', action='store_true', default=False)
    parser.add_argument('--is1D', help='Select 1D histograms', action='store_true', default=False)
    parser.add_argument('--is2D', help='Select 2D histograms', action='store_true', default=False)
    parser.add_argument('--is3D', help='Select 3D histograms', action='store_true', default=False)
    parser.add_argument('--verbose', '-v', help='Show details for selected histograms', \
                            action='store_true', default=False)
    parser.add_argument('file', help='yaml defining efficiency histograms', type=str, nargs=1, default=None)
    args = parser.parse_args()

    allVDefs,allHDefs = loadConfiguration(args.file[0],['*'])
    print()

    for hDef in allHDefs.allDefinitions.values():
        skip = True
        if args.is1D and hDef('yNbins')==None:
            skip = False
        if args.is2D and hDef('yNbins')!=None and hDef('zNbins')==None:
            skip = False
        if args.is3D and hDef('zNbins')!=None:
            skip = False
        if skip:
            continue
        if ( args.isEff and hDef('effCuts')==None ) or ( args.isNoEff and hDef('effCuts')!=None ) :
            continue
        if ( args.isProfile and hDef('profile')==None ) or ( args.isNoProfile and hDef('profile')!=None ) :
            continue
        print(hDef.name)
        if args.verbose:
            printDict(hDef.parameters,2)
    
