#
# Extract individual definitions from a yaml file to be used with drawHitsRDF.py to text files
# Text files are named with the histogram name and written to a directory derived from the configuration file name
# The individual directories are created if not yet present; existing files are not removed but will be replaced
#
import sys,os
import yaml

def writeDict(d,txtFile,indent=0):
    ''' Write contents of a dictionary to a text file
        Arguments:
           d ........ input dictionary
           txtFile .. text file object open for writing
           indent ... number of spaces at the start of each line
    '''
    #
    # define lists of dictionaries and all other (scalar!) items
    #
    kOthers = [ ]
    kDicts = [ ]
    for k,v in d.items():
        if type(v)==dict:
            kDicts.append(k)
        else:
            kOthers.append(k)
    #
    # write non-dictionary (scalar) items
    #
    for k in sorted(kOthers):
        v = d[k]
        # start with key
        line = indent*" "+k+": "
        # write variable (strings enclosed in quotes)
        if type(v)==str:
            line += "'"+v+"'"
        else:
            line += str(v)
        # write line
        txtFile.write(line+"\n")
    #
    # write dictionaries via recursive use of the function
    #
    for k in sorted(kDicts):
        # write header line
        txtFile.write(indent*" "+k+":\n")
        # write dictionary with increased indent
        writeDict(d[k],txtFile,indent+2)
#
# main body
#
if __name__=="__main__":
    #
    # arguments are the path to the config file and the base directory for the output
    #
    #
    # configuration file
    #
    configFile = sys.argv[1]
    assert os.path.isfile(configFile)
    #
    # output directory constructed from argument and the config file name
    #
    outputBase = sys.argv[2]
    assert os.path.isdir(outputBase)
    configName = os.path.splitext(os.path.basename(configFile))[0]
    outputDir = os.path.join(outputBase,configName)
    # directory is created if it doesn't exist
    if not os.path.exists(outputDir):
        os.mkdir(outputDir)
    assert os.path.isdir(outputDir)
    #
    # read all dictionaries from config file
    #
    with open(sys.argv[1],"rt") as yamlFile:
        allDicts = yaml.load(yamlFile,Loader=yaml.Loader)
        yamlFile.close()
    #
    # All variable definitions are written to a single file 'variables.txt'
    #
    if 'variables' in allDicts:
        varDict = allDicts['variables']
        with open(os.path.join(outputDir,'variables.txt'),"wt") as txtFile:
            writeDict(varDict,txtFile)
            txtFile.close()
    #
    # Histograms
    #
    if 'histograms' in allDicts:
        histDict = allDicts['histograms']
        #
        # loop over sorted keys (==histogram names) in the configuration
        #
        for k1 in sorted(histDict.keys()):
            v1 = histDict[k1]
            assert type(v1)==dict
            #
            # create output file for this histogram and write definitions, including nested dicts
            #   
            with open(os.path.join(outputDir,k1+".txt"),"wt") as txtFile:
                writeDict({k1:v1},txtFile,0)
