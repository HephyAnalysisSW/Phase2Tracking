#
# Definitions for histograms from a configuration file
#
import yaml
from fnmatch import fnmatch

class HistogramDefinition:
    ''' A single histogram definition. 
    '''
    # fields that have to be present in the general section
    reqGenFields = [ 'canvasName' ]
    # fields that have to be present in a histogram section
    reqHistFields = [ ]
    requiredFields = list(set(reqGenFields + reqHistFields))
    # optional fields in the general section
    optGenFields =  [ 'variable', 'baseCuts', 'effCuts', 'logY', 'logZ' ]
    # optional fields in the histogram section
    optHistFields = [ 'variable', 'histogramName', 'histogramTitle', 'fit', \
                          'xNbins', 'xMin', 'xMax', 'xTitle', 'yTitle', 'zTitle', \
                          'yNbins', 'yMin', 'yMax', \
                          'zNbins', 'zMin', 'zMax', 'display', 'profile' ]
    optionalFields = list(set(optGenFields + optHistFields))
    allFields = list(set(requiredFields + optionalFields))
    allHistFields = list(set(reqHistFields + optHistFields))
    # fields that cannot be present for a single module type
    vetoMtypeFields = [ 'variable', 'baseCuts', 'effCuts', 'profile' ]
    vetoMtypeFields = [ 'profile' ]

    def __init__(self,name,inputDict):
        ''' Define histogram and drawing parameters from dictionary.
            Arguments:
              name ....... name of the histogram definition
              inputDict .. dictionary with values
        '''
        #
        assert name.isalnum()
        self.name = name
        #
        # read parameters
        #
        # default is None for all parameters
        #
        self.parameters = { x:None for x in HistogramDefinition.allFields }
        #
        # loop over main dictionary
        #
        for k,v in inputDict.items():
            #
            # skip standard python entries
            #
            if k.startswith('__'):
                continue
            #
            # standard entry in main dictionary - store value
            #
            if k in HistogramDefinition.allFields:
                #
                # general variable
                #
                self.parameters[k] = v
            #
            # nested dictionary with parameters for a specific module type
            #
            elif k.startswith("mType"):
                #
                # mType-specific histogram parameters
                #
                assert type(v)==dict and ( not k in self.parameters ) and len(k)>5 and k[5:].isdigit()
                self.parameters[k] = { x:None for x in HistogramDefinition.allHistFields }
                for kh,vh in v.items():
                    if kh in HistogramDefinition.allHistFields:
                        self.parameters[k][kh] = vh
                    else:
                        print("Warning: key",kh, \
                                  "is not a standard histogram field name - ignoring the entry in", \
                                  self.name)
            #
            # unknown key
            #
            else:
                print("Warning: key",k,"is not a standard field name - ignoring the entry in",self.name)
        #
        # set some parameters from other inputs if unspecified
        #
        if self.parameters['canvasName']==None:
            self.parameters['canvasName'] = "c" + self.name[0].upper() + self.name[1:]
        if self.parameters['histogramName']==None:
            self.parameters['histogramName'] = "h" + self.name[0].upper() + self.name[1:]
        #
        # make sure all required fields are present
        #
        for f in HistogramDefinition.requiredFields:
            assert ( f in self.parameters ) and self.parameters[f]!=None

    #def __getitem__(self,field):
    #    if field in self.parameters:
    #        return self.parameters[field]
    #    return None

    def getParameter(self,name,mType=None):
        ''' Retrieve a single parameter (optionally a specific one for a given module type)
        '''
        result = None
        #
        # give priority to parameter specific to a module type
        #
        mTName = "mType"+str(mType) if mType!=None else None
        if ( mTName in self.parameters ) and ( name in self.parameters[mTName] ):
          result = self.parameters[mTName][name]
          if result!=None:
            # check for parameters that can only be general
            if name in HistogramDefinition.vetoMtypeFields:
              raise Exception('Parameter '+name+' cannot be present in the section for an individual module type')
            return self.parameters[mTName][name]
        #
        # not found: use general parameter
        #
        if name in self.parameters:
            return self.parameters[name]
        return None

    def __call__(self,name,mType=None):
        ''' Make access to parameters easier - use function call
        '''
        return self.getParameter(name,mType)
    
    def vetoMType(self,mType):
        ''' Check for an mType entry with display = False
        '''
        #
        # try to get 'display' parameter
        #
        name = 'display'
        mTName = "mType"+str(mType) if mType!=None else None
        if ( mTName in self.parameters ) and ( name in self.parameters[mTName] ):
            if self.parameters[mTName][name]!=None:
                return not self.parameters[mTName][name]
        return False

class HistogramDefinitions:

    def __init__(self):
        self.allDefinitions = { }
        self.allHistoNames = set()
        self.allCanvases = set()
        self.byCanvas = { }

    def add(self,hdef):
        assert not hdef.name in self.allDefinitions

        hName = hdef.getParameter('histogramName')
        assert not hName in self.allHistoNames
        self.allHistoNames.add(hName)

        cName = hdef.getParameter('canvasName')
        assert not cName in self.allCanvases
        self.allDefinitions[hdef.name] = hdef
        self.allCanvases.add(cName)

        if not cName in self.byCanvas:
            self.byCanvas[cName] = { }
        self.byCanvas[cName][hdef.name] = hdef

    def canvasNames(self):
        return self.allCanvases
    
    def __getitem__(self,name):
        if name in self.allDefinitions:
            return self.allDefinitions[name]
        return None
        
class VarMaskCombinations:
    ''' Combinations of a variable and a mask for use with RDF.Histo*.
    '''
    def __init__(self):
        #
        # variable+mask name indexed by variable+selection string
        #
        self.varMaskDefinitions = { }

    def __call__(self,rdf,varName,selection):
        ''' Return the name of a variable+mask combination. Define if necessary.
            Arguments:
              rdf ........ RDataFrame to be used for definition
              varName .... name of the variable
              selection .. selection string to be used as mask
        '''
        #
        # use variable name and normalized selection string (remove spaces)
        #
        selNorm = selection.replace(" ","")
        varMask = "(" + varName + ")["+selNorm+"]"
        if varMask in self.varMaskDefinitions:
            # combination exists (assume that it's also defined in the RDataFrame)
            varMaskName = self.varMaskDefinitions[varMask]
            print("*** found",varMaskName,"for",varMask,"in local definitions")
            assert varMaskName in rdf.GetDefinedColumnNames()
        else:
            # create name for combination and define it in the RDataFrame
            n = len(self.varMaskDefinitions)
            varMaskName = "varMask{:03d}".format(n)
            self.varMaskDefinitions[varMask] = varMaskName
            rdf = rdf.Define(varMaskName,varMask)
            print("+++ defined new var + mask combinations:",varMaskName,varMask)
            print(rdf.GetDefinedColumnNames())
            print("+++")
        return rdf,varMaskName
        
        
def loadConfiguration(configName,selectedNames=[],vetoedNames=[]):
    ''' Load variable and histogram definitions from a configuration file. The configuration file
        is expected to contain a "variables" and a "histograms" section. The "histogram" section
        defines dictionaries with the definitions as variable. The name of the variable
        serves as name of the HistogramDefinition.
        Arguments:
           configName ..... name of the module to import from / python file name
           selectedNames .. explicit list of histogram names to be imported (filename wildcard syntax)
           vetoedNames .... explicit list of histogram names to be skipped (filename wildcard syntax)
        Result:
           Tuple with dictionary of variable definitions and HistogramDefinitions object
    '''
    # load histogram definitions
    #
    vDefs = { }
    hDefs = HistogramDefinitions()
    if configName==None:
        return ( vDefs, hDefs )

    with open(configName,"rt") as yamlFile:
        allDicts = yaml.load(yamlFile,Loader=yaml.Loader)
        yamlFile.close()
    #
    # store variable definitions as read from configuration
    #
    if 'variables' in allDicts:
        vDefs = allDicts['variables']
    #
    # backward compatibility for histograms: treat full input as "histograms" section
    #   in case neither variables nor histograms sections are defined
    #
    if 'histograms' in allDicts:
        histDicts = allDicts['histograms']
    else:
        assert not ( 'variables' in allDicts )
        histDicts = allDicts
    #
    for n,hDict in histDicts.items():
        #
        assert type(hDict)==dict
        #
        # check if in list of histograms to be displayed
        #
        selFlg = False
        for p in selectedNames:
            if fnmatch(n,p):
                selFlg = True
                break
        if not selFlg:
            continue
        #
        # check if in list of histograms to be vetoed
        #
        selFlg = True
        for p in vetoedNames:
            if fnmatch(n,p):
                selFlg = False
                break
        if not selFlg:
            continue
        #
        # add histogram
        #
        hDef = HistogramDefinition(n,hDict)
        hDefs.add(hDef)
        print("Added",hDef.getParameter('canvasName'))
        
#!#     moduleName = configName[:-3] if configName.endswith(".py") else configName
#!#     module = __import__(moduleName)
#!#     for n in dir(module):
#!#         if n.startswith('__'):
#!#             continue
#!#         hDict = getattr(module,n)
#!#         #print(n,type(hDict))
#!#         #sys.exit()
#!#         assert type(hDict)==dict
#!#         #
#!#         # check if in list of histograms to be displayed
#!#         #
#!#         selFlg = False
#!#         for p in selectedNames:
#!#             if fnmatch(n,p):
#!#                 selFlg = True
#!#                 break
#!#         if not selFlg:
#!#             continue
#!#         #
#!#         # check if in list of histograms to be vetoed
#!#         #
#!#         selFlg = True
#!#         for p in vetoedNames:
#!#             if fnmatch(n,p):
#!#                 selFlg = False
#!#                 break
#!#         if not selFlg:
#!#             continue
#!#         #
#!#         # add histogram
#!#         #
#!#         hDef = HistogramDefinition(n,hDict)
#!#         hDefs.add(hDef)
#!#         print("Added",hDef.getParameter('canvasName'))
    return ( vDefs, hDefs )

