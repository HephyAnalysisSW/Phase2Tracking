import os
import yaml
import numpy as np
import pickle
import ROOT
#ROOT.EnableImplicitMT(4)
# Maybe let ROOT decide the number of threads to use
ROOT.EnableImplicitMT()
ROOT.gROOT.SetBatch(ROOT.kTRUE)
ROOT.TH1.SetDefaultSumw2(True)
ROOT.gStyle.SetOptStat(0)

class Plotter:
  def __init__(self,name,treeName,outputDir="./",input_filelist=None,config="",isData=False,postfix="", \
                 macros=[]):
    self.name = name 
    self.treeName = treeName
    self.outputDir = outputDir
    self.input_filelist = input_filelist
    self.isData = isData
    self.postfix = postfix
    with open(config, "r") as f_cfg:
      cfg = yaml.load(f_cfg, Loader=yaml.FullLoader)
    self.cfg = cfg
    for m in macros:
      ROOT.gROOT.ProcessLine(".L "+m+"+")

  def getFileList(self):
    self.filelist = []
    # First try to get the input file list from the txt file
    if (self.input_filelist is not None) and (os.path.exists( self.input_filelist )) and (os.path.isfile( self.input_filelist )):
      with open( self.input_filelist, 'r') as inputfile:
          for line in inputfile.readlines():
              line = line.rstrip('\n').rstrip()
              if line.endswith('.root'):
                  self.filelist.append(line)
    if len(self.filelist)==0:
      print("No files provided as input!")

  def AddVars(self,d):
      print(type(self.cfg))
      vars_to_define = ['new_variables']
      for v in vars_to_define:
        if (not v in self.cfg) or (self.cfg[v] is None):
          continue 
        if self.cfg[v] is not None:
          print(v,type(self.cfg[v]))
          for newvar in self.cfg[v]:
            if isinstance(self.cfg[v][newvar],list):
              formatstr = [self.cfg[self.cfg[v][newvar][i]] for i in range(1,len(self.cfg[v][newvar]))]
              var_define = self.cfg[v][newvar][0].format(*formatstr)
            elif isinstance(self.cfg[v][newvar],str):
              var_define = self.cfg[v][newvar]
            d = d.Define(newvar,var_define)
            print("*** Define AddVars",newvar,var_define)
      return d
  
  def AddVarsWithSelection(self,d):
    if not self.cfg['objects']:
      return d
    for obj in self.cfg['objects']:
      selections = self.cfg['objects'][obj]['selections']
      variables  = self.cfg['objects'][obj]['variables']
      for sel in selections:
        for v in variables:
          if selections[sel]:
            d = d.Define(v+sel,"{0}[{1}]".format(v,selections[sel]))
            print("*** Define AddVarsWithSelection1",sel,v+sel,"{0}[{1}]".format(v,selections[sel]))
          else:
            d = d.Define(v+sel,"{0}".format(v))
            print("*** Define AddVarsWithSelection",sel,v+sel,"{0}".format(v))
        if ('nm1' in self.cfg['objects'][obj]) and (self.cfg['objects'][obj]['nm1']):
          nm1s = self.cfg['objects'][obj]['nm1']
          cutstr_objsel = ""
          if selections[sel]:
            cutstr_objsel = "({}) && ".format(selections[sel])
          for i in range(len(nm1s)):
            cutstrs = []
            for j in range(len(nm1s)):
              if j==i:
                continue
              cutstrs.append("({})".format(''.join(nm1s[j])))
            cutstr = "&&".join(cutstrs)
            cutstr = cutstr_objsel + "({})".format(cutstr)
            d = d.Define(nm1s[i][0]+sel+'_nm1',"{0}[{1}]".format(nm1s[i][0],cutstr))
            print("*** Define AddVarsWithSelection2",nm1s[i][0]+sel+'_nm1',"{0}[{1}]".format(nm1s[i][0],cutstr))
            #print("define {}: {}".format(nm1s[i][0]+sel+'_nm1',"{0}[{1}]".format(nm1s[i][0],cutstr)))

    return d
  
  def FilterEvents(self,d):
    d_filter = d.Filter(self.presel)
    print("*** Filter",self.presel)
    return d_filter

  def AddWeights(self,d,weight):
    d = d.Define("evt_weight","{0}".format(weight))
    print("*** Define AddWeights","evt_weight","{0}".format(weight))
    return d
  
  def getRDF(self):
    '''
    This function gets RDataFrame for a given sample
    - Add desired variables
    - Filter events
    - Produce normalisation weights based on xsec
    '''
    d = ROOT.RDataFrame(self.treeName,self.filelist)
    d = self.AddVars(d)
    d = self.AddVarsWithSelection(d)
    if self.cfg['presel'] is not None:
      d = d.Filter(self.cfg['presel'])
      print("*** Filter getRDF",self.cfg['presel'])
    xsec_weights = 1
    d = self.AddWeights(d,xsec_weights)
    return d,xsec_weights

  def getplots(self,d,weight,plots_1d,plots_2d,plots_nm1,varlabel):
    hs = []
    if plots_1d is None:
      plots_1d = []
    if plots_2d is None:
      plots_2d = []
    if plots_nm1 is None:
      plots_nm1 = []
#!#
    self.isData = True
#!#
    for plt in plots_1d:
      if not plt in self.cfg['plot_setting']:
        print("{} not registered in plot setting!".format(plt))
      if self.isData:
        h = d.Histo1D(tuple(self.cfg['plot_setting'][plt]),plt+varlabel)
        print("*** Histo1D getplots",plt,self.isData,tuple(self.cfg['plot_setting'][plt]),plt+varlabel)
      else:
        h = d.Histo1D(tuple(self.cfg['plot_setting'][plt]),plt+varlabel,weight)
        print("*** Histo1D getplots",plt,self.isData,tuple(self.cfg['plot_setting'][plt]),plt+varlabel,weight)
      hs.append(h)

    for plt in plots_nm1:
      if not plt[0] in self.cfg['plot_setting']:
        print("{} not registered in plot setting!".format(plt[0]))
      nm1_setting = (self.cfg['plot_setting'][plt[0]]).copy()
      nm1_setting[0] += 'nm1'
      nm1_setting = tuple(nm1_setting)
      if self.isData:
        h = d.Histo1D(nm1_setting,plt[0]+varlabel+'_nm1')
      else:
        h = d.Histo1D(nm1_setting,plt[0]+varlabel+'_nm1',weight)
      hs.append(h)
  
    for x,y in plots_2d:
        if not x in self.cfg['plot_setting']:
          print("{} not registered in plot setting!".format(x))
        if not y in self.cfg['plot_setting']:
          print("{} not registered in plot setting!".format(y))
        xax = tuple(self.cfg['plot_setting'][x])
        yax = tuple(self.cfg['plot_setting'][y])
        xtitle_idx0 = xax[1].find(';')
        xtitle_idx1 = xax[1].find(';',xtitle_idx0+1)
        xtitle = xax[1][xtitle_idx0+1:xtitle_idx1]
        ytitle_idx0 = yax[1].find(';')
        ytitle_idx1 = yax[1].find(';',ytitle_idx0+1)
        ytitle = yax[1][ytitle_idx0+1:ytitle_idx1]
        hset = (xax[0]+'_vs_'+yax[0],";{0};{1}".format(xtitle,ytitle),xax[2],xax[3],xax[4],yax[2],yax[3],yax[4])
        x2d = x+varlabel
        if x not in plots_1d:
          print("Warning! Variable {} not registered in this level!".format(x))
          x2d = x
        y2d = y+varlabel
        if y not in plots_1d:
          print("Warning! Variable {} not registered in this level!".format(y))
          y2d = y
        #h = d.Histo2D(hset,x+varlabel,y+varlabel,weight)
        if self.isData:
          h = d.Histo2D(hset,x2d,y2d)
        else:
          h = d.Histo2D(hset,x2d,y2d,weight)
        hs.append(h)
  
    for i in range(len(hs)):
      hs[i] = hs[i].Clone()
      hs[i].SetName(hs[i].GetName())

    return hs

  def makeHistFiles(self):
      if not os.path.exists(self.outputDir):
          os.makedirs(self.outputDir)
      fout = ROOT.TFile("{}/{}_hist{}.root".format(self.outputDir,self.name,self.postfix),"RECREATE")
      self.getFileList()
      d,w = self.getRDF()

      for sr in self.cfg['regions']:
        d_sr = d
        if self.cfg['regions'][sr] is not None:
          d_sr = d_sr.Filter(self.cfg['regions'][sr])
          print("*** Filter makeHistFiles1",sr,self.cfg['regions'][sr])

        newd_evt = fout.mkdir("{}_evt".format(sr))
        hs = self.getplots(d_sr,weight="evt_weight",plots_1d=self.cfg['event_variables'],plots_2d=self.cfg['event_2d_plots'],plots_nm1=self.cfg.get('event_nm1'),varlabel="")
        newd_evt.cd()
        for h in hs:
          h.Write()
        if self.cfg['objects']:
          for obj in self.cfg['objects']:
            for sels in self.cfg['objects'][obj]['selections']:
              newd = fout.mkdir("{}_{}_{}".format(sr,obj,sels))
              hs = self.getplots(d=d_sr,weight="evt_weight",plots_1d=self.cfg['objects'][obj]['variables'],plots_2d=self.cfg['objects'][obj]['2d_plots'],plots_nm1=self.cfg['objects'][obj].get('nm1'),varlabel=sels)
              newd.cd()
              for h in hs:
                h.Write()
      fout.Close()
