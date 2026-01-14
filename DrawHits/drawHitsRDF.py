#! /bin/env python3
import sys,os
from drawHitsConfiguration import *
import ROOT
import argparse
from fnmatch import fnmatch

def divideRatios(cnv,nx,ny,widthRatios,heightRatios,canvasTopMargin=0.,canvasLeftMargin=0.):
    result = [ ]
    cnv.cd()
 
    wrs = len(widthRatios)
    hrs = len(heightRatios)
    nxl = min(nx,wrs)
    nyl = min(ny,hrs)
 
    if wrs==0: nxl = nx
    if hrs==0: nyl = ny
 
    pn = 1
    xr = 0.
    yr = 0.
    x  = 0.
    y  = 1.
    # Check the validity of the margins
    if canvasTopMargin<0 or canvasTopMargin>1:
        raise Exception("DivideRatios: The canvas top margin must be >= 0 and <= 1")
    else:
        y = 1.- canvasTopMargin
    if canvasLeftMargin <0 or canvasLeftMargin >1:
        raise Exception("DivideRatios", "The canvas left margin must be >= 0 and <= 1")
 
    # Check the validity of the ratios
    sumOfHeightRatios = canvasTopMargin
    if hrs:
      for i in range(nyl):
          yr = heightRatios[i]
          sumOfHeightRatios = sumOfHeightRatios + yr
          if yr<0 or yr>1:
              raise Exception("DivideRatios", "Y ratios plus the top margin must be >= 0 and <= 1")

    if sumOfHeightRatios>1.:
        raise Exception("DivideRatios", "The sum of Y ratios plus the top margin must be <= 1 %g",sumOfHeightRatios)
    sumOfWidthRatios = canvasLeftMargin
    if wrs:
      for j in range(nxl):
          xr = widthRatios[j]
          sumOfWidthRatios = sumOfWidthRatios + xr
          if xr <0 or xr >1:
              raise Exception("DivideRatios", "X ratios must be >= 0 and <= 1")
    if sumOfWidthRatios>1.:
        raise Exception("DivideRatios", "The sum of X ratios must be <= 1 %g ",sumOfWidthRatios)
 
    # Create the pads according to the ratios
    for i in range(nyl):
      x = canvasLeftMargin
      if hrs:
          yr = heightRatios[i]
      else:
          yr = 1./nyl
      for j in range(nxl):
          if wrs:
              xr = widthRatios[j]
          else:
              xr = 1./nxl
          x1 = max(0., x)
          y1 = max(0., y - yr)
          x2 = min(1., x + xr)
          y2 = min(1., y)
          pad = ROOT.TPad(cnv.GetName()+str(pn),cnv.GetName()+str(pn),x1, y1, x2 ,y2)
          result.append(pad)
          pad.SetNumber(pn)
          pad.Draw()
          x = x + xr
          pn += 1
      y = y - yr

    return result

def fitHistogram(mType,h):
    f1name = "f1"+str(mType)
    f1 = ROOT.TF1(f1name,"gaus(0)")
    f1.SetParameter(0,h.GetMaximum())
    f1.SetParLimits(0,0.,2*h.GetMaximum())
    f1.SetParameter(1,0.)
    f1.SetParameter(2,h.GetRMS()/10.)
    h.Fit(f1name)
    f2name = "f2"+str(mType)
    f2 = ROOT.TF1(f2name,"gaus(0)+gaus(3)")
    f2.SetParameter(0,f1.GetParameter(0))
    f2.SetParameter(1,f1.GetParameter(1))
    f2.SetParameter(2,f1.GetParameter(2))
    f2.SetParameter(3,f1.GetParameter(0)/100.)
    f2.SetParameter(4,f1.GetParameter(1))
    f2.SetParameter(5,5*f1.GetParameter(2))
    f2.SetParLimits(5,f1.GetParameter(2),10*f1.GetParameter(2))
    h.Fit(f2name)
    ROOT.gPad.SetLogy(1)
    ROOT.gPad.Update()


def cutString(*cuts):
    if len(cuts)>0 and cuts[0]!=None:
        return "&&".join([ c for c in cuts if ( c!=None and c.strip()!="" ) ])
    return None

def cutLines(cuts,maxChar=40):
    result = [ ]
    line = ""
    for ic,c in enumerate(cuts):
        line += c
        if ic<(len(cuts)-1):
            line += "&&"
        if len(line)>maxChar:
            result.append(line)
            line = ""
    if line!="":
        result.append(line)
    return result

# def drawString(pave,title,s=""):
#     t = pave.AddText(title)
#     t.SetTextFont(43)
#     t.SetTextSize(0.06)
#     t.SetTextSize(16)
#     t.SetTextAlign(13)
#     #yt += 14
#     if s!="":
#         #t = pave.AddText("")
#         t = pave.AddText("  "+s)
#         t.SetTextFont(43)
#         t.SetTextSize(14)
#         t.SetTextAlign(13)
#         #t = pave.AddText("")

# def drawCuts(pave,title,cuts):
#     #t = pave.AddText(title)
#     #t = pave.AddText("")
#     lines = [ ]
#     line = ""
#     for ic,c in enumerate(cuts):
#         line += c
#         if ic<(len(cuts)-1):
#             line += "&&"
#         if len(line)>40:
#             lines.append(line)
#             line = ""
#     if line!="":
#         lines.append(line)
#     for l in lines:
#         if l!="":
#             t = pave.AddText("  "+l)
#             t.SetTextFont(43)
#             t.SetTextSize(0.04)
#             t.SetTextSize(14)
#             t.SetTextAlign(13)
#         #l = "  " + c
#         #if ic<(len(cuts)-1):
#         #    l += " &&"
#         ##    if len(l
#         #if 
#         #t = pave.AddText(l)

    
def drawCutPave(cnv,ic,variable,cuts,effcuts=None):
    indBaseCuts = cuts.split("&&")
    indEffCuts = None if effcuts==None else effcuts.split("&&")
    #print(indBaseCuts)
    #print(indEffCuts)
    cnv.cd(ic+3)
    #hpave = 3*0.06+(len(indBaseCuts)+1)*0.04
    #if indEffCuts!=None:
    #    hpave += (len(indEffCuts)+2)*0.04

    #print(ROOT.gPad.UtoPixel(0.),ROOT.gPad.UtoPixel(1.))
    #print(ROOT.gPad.VtoPixel(0.),ROOT.gPad.VtoPixel(1.))
    allLines = [ ]
    allLines.append(('hdr','Variable(s)'))
    allLines.append(('txt',variable))
    allLines.append(('hdr','Basic selection'))
    for l in cutLines(indBaseCuts):
        if l!="":
            allLines.append(('txt',l))
    if indEffCuts!=None:
        allLines.append(('hdr','Efficiency selection'))
        for l in cutLines(indEffCuts):
            if l!="":
                allLines.append(('txt',l))

    hdrPixels = 16
    txtPixels = 14
    #pave = ROOT.TPaveText(0.05,max(0,1.0-hpave),0.95,1.0)
    hpave = ((hdrPixels+txtPixels+2)*len([ x for x in allLines if x[0]=='hdr' ]) + \
             (txtPixels+2)*len([ x for x in allLines if x[0]=='txt' ])) / (ROOT.gPad.VtoPixel(0.)-ROOT.gPad.VtoPixel(1.))
    #print(hpave)
    if hpave>1.:
        scale = 1./hpave
        hpave = 1
    else:
        scale = 1
        
    pave = ROOT.TPaveText(0.,1.-hpave,1.,1.)
    pave.SetBorderSize(0)
    pave.SetFillStyle(0)
    pave.SetTextFont(43)
    #pave.SetMargin(0)
    #pave.SetTextSize(0.04)
    pave.SetTextSize(int(scale*txtPixels))
    pave.SetTextAlign(13)
    nhdr = 0
    for x,y in allLines:
        if x=='hdr':
            if nhdr>0:
                t = pave.AddText("")
                t.SetTextSize(int(scale*txtPixels))
            t = pave.AddText(y)
            t.SetTextFont(63)
            t.SetTextSize(int(scale*hdrPixels))
            nhdr += 1
        else:
            t = pave.AddText("  "+y)
            t.SetTextSize(int(scale*txtPixels))
    #drawString(pave,"Variable(s)",variable)
    #drawString(pave,"Basic selection")
    #drawCuts(pave,"Basic selection",indBaseCuts)
    #if indEffCuts!=None:
    #    #t = pave.AddText("")
    #    drawString(pave,"Efficiency selection")
    #    drawCuts(pave,"Efficiency selection",indEffCuts)
        
    pave.Draw()
    ROOT.gPad.Update()
    return pave

def createHistoByDef(rdf,hDef,extraCuts,varMaskCombs):
    histos = { }

    for mType in range(23,26):
        #print("Checking mType",mType,"for",hDef.name)
        #
        # draw histogram?
        #
        if hDef.vetoMType(mType):
            continue
        is1D = hDef.getParameter('yNbins',mType)==None
        is2D = hDef.getParameter('yNbins',mType)!=None and hDef.getParameter('zNbins',mType)==None
        is3D = hDef.getParameter('yNbins',mType)!=None and hDef.getParameter('zNbins',mType)!=None
        isProfile = hDef.getParameter('profile',mType)!=None and hDef.getParameter('profile',mType)
        effCuts = hDef.getParameter('effCuts',mType)
        variable = hDef.getParameter('variable',mType)
        ##
        #cnv.cd(ic)
        #ROOT.gPad.SetGridx(1)
        #ROOT.gPad.SetGridy(1)
        #if not is1D:
        #    ROOT.gPad.SetRightMargin(0.125)
        hName = hDef.getParameter('histogramName',mType) + str(mType)
        hTitle = hDef.getParameter('histogramTitle',mType) + " module type " +str(mType)
        nbx = hDef.getParameter('xNbins',mType)
        xmin = hDef.getParameter('xMin',mType)
        xmax = hDef.getParameter('xMax',mType)
        #print("Starting for ",hDef.name,hName,hTitle)
        if is1D and ( not isProfile ):
            #print(variable+"["+cutString(extraCuts,hDef.getParameter('baseCuts',mType),"moduleType=="+str(mType))+"]")
            #histos[mType] = [ rdf.Histo1D((hName+"_1",hName+"_1",nbx,xmin,xmax), \
            #                              variable+"["+cutString(extraCuts,hDef.getParameter('baseCuts',mType),"moduleType=="+str(mType))+"]"), \
            #                              None, None, None ]
            #print(rdf.GetColumnNames())
            #print(hName,effCuts)
            #rdf = rdf.Define("pabsVar","pabs[pabs>0.3]")
            #th1m = ROOT.RDF.TH1DModel(hName+"_1",hName+"_1",nbx,xmin,xmax)
            #print(type(th1m))
            cuts = cutString(extraCuts,hDef.getParameter('baseCuts',mType),"moduleType=="+str(mType))
            rdf,varMask = varMaskCombs(rdf,variable,cuts)
            model = (hName+"_1",hName+"_1",nbx,xmin,xmax)
            #print(varMask)
            #print(rdf.GetDefinedColumnNames())
            histos[mType] = [ rdf.Histo1D(model,varMask), None, None, None ]
            if effCuts!=None:
                cuts = cutString(extraCuts,hDef.getParameter('baseCuts',mType),"moduleType=="+str(mType),effCuts)
                rdf,varMask = varMaskCombs(rdf,variable,cuts)
                model = (hName+"_2",hName+"_2",nbx,xmin,xmax)
                histos[mType][1] = rdf.Histo1D(model,varMask)
            #sys.exit()
        elif isProfile:
            ymin = hDef.getParameter('yMin',mType)
            ymax = hDef.getParameter('yMax',mType)
            v2,v1 = variable.split(":")
            cuts = cutString(extraCuts,hDef.getParameter('baseCuts',mType),"moduleType=="+str(mType))
            rdf,varMask1 = varMaskCombs(rdf,v1,cuts)
            rdf,varMask2 = varMaskCombs(rdf,v2,cuts)
            model = (hName+"_1",hName+"_1",nbx,xmin,xmax,ymin,ymax)
            histos[mType] = [ rdf.Profile1D(model,varMask1,varMask2), None, None, None ]
            #histos[mType] = [ rdf.Profile1D((hName+"_1",hName+"_1",nbx,xmin,xmax,ymin,ymax,'S'), \
            #                                v1+"["+cutString(extraCuts,hDef.getParameter('baseCuts',mType),"moduleType=="+str(mType))+"]",v2), \
            #                                None, None, None ]
        elif is2D:
            nby = hDef.getParameter('yNbins',mType)
            ymin = hDef.getParameter('yMin',mType)
            ymax = hDef.getParameter('yMax',mType)
            v2,v1 = variable.split(":")
            cuts = cutString(extraCuts,hDef.getParameter('baseCuts',mType),"moduleType=="+str(mType))
            rdf,varMask1 = varMaskCombs(rdf,v1,cuts)
            rdf,varMask2 = varMaskCombs(rdf,v2,cuts)
            model = (hName+"_1",hName+"_1",nbx,xmin,xmax,nby,ymin,ymax)
            histos[mType] = [ rdf.Histo2D(model,varMask1,varMask2), None, None, None ]
            if effCuts!=None:
                cuts = cutString(extraCuts,hDef.getParameter('baseCuts',mType),"moduleType=="+str(mType),effCuts)
                rdf,varMask1 = varMaskCombs(rdf,v1,cuts)
                rdf,varMask2 = varMaskCombs(rdf,v2,cuts)
                model = (hName+"_2",hName+"_2",nbx,xmin,xmax,nby,ymin,ymax)
                histos[mType][1] = rdf.Histo2D(model,varMask1,varMask2)
        elif is3D:
            nby = hDef.getParameter('yNbins',mType)
            ymin = hDef.getParameter('yMin',mType)
            ymax = hDef.getParameter('yMax',mType)
            nbz = hDef.getParameter('zNbins',mType)
            zmin = hDef.getParameter('zMin',mType)
            zmax = hDef.getParameter('zMax',mType)
            v3,v2,v1 = variable.split(":")
            cuts = cutString(extraCuts,hDef.getParameter('baseCuts',mType),"moduleType=="+str(mType))
            rdf,varMask1 = varMaskCombs(rdf,v1,cuts)
            rdf,varMask2 = varMaskCombs(rdf,v2,cuts)
            rdf,varMask3 = varMaskCombs(rdf,v3,cuts)
            model = (hName+"_1",hName+"_1",nbx,xmin,xmax,nby,ymin,ymax,nbz,zmin,zmax)
            histos[mType] = [ rdf.Histo3D(model,varMask1,varMask2,varMask3), None, None, None ]
            #histos[mType] = [ rdf.Histo3D((hName+"_1",hName+"_1",nbx,float(xmin),float(xmax),nby,float(ymin),float(ymax),nbz,float(zmin),float(zmax)), \
            #                              v1+"["+cutString(extraCuts,hDef.getParameter('baseCuts',mType),"moduleType=="+str(mType))+"]",v2,v3), \
            #                              None, None, None ]
            #histos[mType] = [ rdf.Histo3D((hName+"_1",hName+"_1",nbx,float(xmin),float(xmax),nby,float(ymin),float(ymax),nbz,float(zmin),float(zmax)), \
            #                              v1+"["+cutString(extraCuts,hDef.getParameter('baseCuts',mType),"moduleType=="+str(mType))+"]",v2,v3), \
            #                              None, None, None ]
            assert effCuts==None
        #print("Ending for ",hDef.name,hName,hTitle)

    #for mType in range(23,26):
    #    print(histos[mType][0].GetEntries(),histos[mType][1].GetEntries())
    #sys.exit()
    return rdf,histos



def fillHistoByDef(tree,hDef,extraCuts,histos):
    #histos = { }

    savedDir = ROOT.gDirectory
    ROOT.gROOT.cd()
    #cnv = ROOT.TCanvas(hDef.getParameter('canvasName'),hDef.getParameter('canvasName'),1000,1000)
    #result['cnv'] = cnv
    #cnv.Divide(2,2)

    #print(hDef['canvasName'],'is',is1D)
    
    ic = 0
    #hEffVs = { }
    for mType in range(23,26):
        #print("Checking mType",mType,"for",hDef.name)
        ic += 1
        #
        # draw histogram?
        #
        if hDef.vetoMType(mType):
            continue
        is1D = hDef.getParameter('yNbins',mType)==None
        is2D = hDef.getParameter('yNbins',mType)!=None and hDef.getParameter('zNbins',mType)==None
        is3D = hDef.getParameter('yNbins',mType)!=None and hDef.getParameter('zNbins',mType)!=None
        isProfile = hDef.getParameter('profile',mType)!=None and hDef.getParameter('profile',mType)
        effCuts = hDef.getParameter('effCuts',mType)
        variable = hDef.getParameter('variable',mType)
        ##
        #cnv.cd(ic)
        #ROOT.gPad.SetGridx(1)
        #ROOT.gPad.SetGridy(1)
        #if not is1D:
        #    ROOT.gPad.SetRightMargin(0.125)
        hName = hDef.getParameter('histogramName',mType) + str(mType)
        hTitle = hDef.getParameter('histogramTitle',mType) + " module type " +str(mType)
        nbx = hDef.getParameter('xNbins',mType)
        xmin = hDef.getParameter('xMin',mType)
        xmax = hDef.getParameter('xMax',mType)
        #print("Starting for ",hDef.name,hName,hTitle)
        if is1D and ( not isProfile ):
            #histos[mType] = [ ROOT.TH1F(hName+"_1",hName+"_1",nbx,xmin,xmax), None, None, None ]
            #tree.Project(hName+"_1",variable, \
            #            cutString(extraCuts,hDef.getParameter('baseCuts',mType),"moduleType=="+str(mType)))
            if effCuts!=None:
                #histos[mType][1] = ROOT.TH1F(hName+"_2",hName+"_2",nbx,xmin,xmax)
                #tree.Project(hName+"_2",variable, \
                #            cutString(extraCuts,hDef.getParameter('baseCuts',mType),"moduleType=="+str(mType),effCuts))
                histos[mType][3] = ROOT.TEfficiency(histos[mType][1].GetValue(),histos[mType][0].GetValue())
                histos[mType][3].SetMarkerStyle(20)
            else:
                # always keep final histogram in 4th position
                histos[mType][3] = histos[mType][0]
        elif isProfile:
            #ymin = hDef.getParameter('yMin',mType)
            #ymax = hDef.getParameter('yMax',mType)
            ##histos[mType] = [ ROOT.TProfile(hName+"_1",hName+"_1",nbx,xmin,xmax,ymin,ymax,'S'), None, None, None ]
            #histos[mType] = [ ROOT.TProfile(hName+"_1",hName+"_1",nbx,xmin,xmax,ymin,ymax), None, None, None ]
            #tree.Project(hName+"_1",variable, \
            #              cutString(extraCuts,hDef.getParameter('baseCuts',mType),"moduleType=="+str(mType)))
            # always keep final histogram in 4th position
            histos[mType][3] = histos[mType][0]
        elif is2D:
            #nby = hDef.getParameter('yNbins',mType)
            #ymin = hDef.getParameter('yMin',mType)
            #ymax = hDef.getParameter('yMax',mType)
            #histos[mType] = [ ROOT.TH2F(hName+"_1",hName+"_1",nbx,xmin,xmax,nby,ymin,ymax), None, None, None ]
            #tree.Project(hName+"_1",variable, \
            #              cutString(extraCuts,hDef.getParameter('baseCuts',mType),"moduleType=="+str(mType)))
            if effCuts!=None:
                #histos[mType][1] = ROOT.TH2F(hName+"_2",hName+"_2",nbx,xmin,xmax,nby,ymin,ymax)
                #tree.Project(hName+"_2",variable, \
                #            cutString(extraCuts,hDef.getParameter('baseCuts',mType),"moduleType=="+str(mType),effCuts))
                #histos[mType][1].Divide(histos[mType][0])
                # always keep final histogram in 4th position
                histos[mType][3] = histos[mType][1].Divide(histos[mType][0].GetValue())
            else:
                # always keep final histogram in 4th position
                histos[mType][3] = histos[mType][0]
        elif is3D:
            #nby = hDef.getParameter('yNbins',mType)
            #ymin = hDef.getParameter('yMin',mType)
            #ymax = hDef.getParameter('yMax',mType)
            #nbz = hDef.getParameter('zNbins',mType)
            #zmin = hDef.getParameter('zMin',mType)
            #zmax = hDef.getParameter('zMax',mType)
            #histos[mType] = [ ROOT.TH3F(hName+"_1",hName+"_1",nbx,xmin,xmax,nby,ymin,ymax,nbz,zmin,zmax), \
            #                      None, None, None ]
            #tree.Project(hName+"_1",variable, \
            #              cutString(extraCuts,hDef.getParameter('baseCuts',mType),"moduleType=="+str(mType)))
            #assert effCuts==None
            # always keep final histogram in 4th position
            histos[mType][3] = histos[mType][0]
        #print("Ending for ",hDef.name,hName,hTitle)
                
    savedDir.cd()
    return histos


def drawHistoByDef(histos,hDef,logY=False,logZ=False,same=False):
    result = { 'cnv' : None, 'histos' : histos, 'pave' : None }

    savedDir = ROOT.gDirectory
    ROOT.gROOT.cd()
    cnvName = hDef.getParameter('canvasName')
    cnv = ROOT.TCanvas(cnvName,cnvName,1500,800)
    result['cnv'] = cnv
    #cnv.Divide(3,2)
    result['pads'] = divideRatios(cnv,3,2,[1./3.,1./3.,1/3.],[2/3.,1/3.])

    #print(hDef['canvasName'],'is',is1D)
    
    ic = 0
    #hEffVs = { }
    for mType in range(23,26):
        #print("Checking mType",mType,"for",hDef.name)
        ic += 1
        cnv.cd(ic)
        #padNameUp = cnvName+str(mType)+'up'
        #result[padNameUp] = ROOT.TPad(padNameUp,padNameUp,(ic-1)/3.,1/3.,ic/3.,1.)
        #result[padNameUp].Draw()
        #
        # draw histogram?
        #
        if hDef.vetoMType(mType):
            continue
        is1D = hDef.getParameter('yNbins',mType)==None
        is2D = hDef.getParameter('yNbins',mType)!=None and hDef.getParameter('zNbins',mType)==None
        is3D = hDef.getParameter('yNbins',mType)!=None and hDef.getParameter('zNbins',mType)!=None
        isProfile = hDef.getParameter('profile',mType)!=None and hDef.getParameter('profile',mType)
        effCuts = hDef.getParameter('effCuts',mType)
        variable = hDef.getParameter('variable',mType)
        #
        #result[padNameUp].cd()
        ROOT.gPad.SetGridx(1)
        ROOT.gPad.SetGridy(1)
        if not is1D:
            ROOT.gPad.SetRightMargin(0.125)
        hName = hDef.getParameter('histogramName',mType) + str(mType)
        hTitle = hDef.getParameter('histogramTitle',mType) + " module type " +str(mType)

        xtitle = hDef.getParameter('xTitle',mType) if hDef.getParameter('xTitle',mType) else variable
        nbx = hDef.getParameter('xNbins',mType)
        xmin = hDef.getParameter('xMin',mType)
        xmax = hDef.getParameter('xMax',mType)

        ytitle = hDef.getParameter('yTitle',mType) if hDef.getParameter('yTitle',mType) else ""
        ztitle = hDef.getParameter('zTitle',mType) if hDef.getParameter('zTitle',mType) else ""
        if is1D and ( not isProfile ):
            ymin = hDef.getParameter('yMin',mType) if hDef.getParameter('yMin',mType)!=None else 0.
            ymax = hDef.getParameter('yMax',mType) if hDef.getParameter('yMax',mType)!=None else 1.05
            if effCuts!=None:
                if not same:
                    histos[mType][2] = ROOT.gPad.DrawFrame(xmin,ymin,xmax,ymax)
                histos[mType][2].SetTitle(hTitle)
                histos[mType][2].GetXaxis().SetTitle(xtitle)
                histos[mType][2].GetYaxis().SetTitle(ytitle)
                histos[mType][3] = ROOT.TEfficiency(histos[mType][1].GetValue(),histos[mType][0].GetValue())
                histos[mType][3].SetMarkerStyle(20)
                histos[mType][3].Draw("same Z")
            else:
                histos[mType][0].SetTitle(hTitle)
                histos[mType][0].GetXaxis().SetTitle(xtitle)
                histos[mType][0].GetYaxis().SetTitle(ytitle)
                histos[mType][0].Draw("same" if same else "")
            fitFunc = hDef.getParameter('fit')
            if fitFunc!=None:
                histos[mType][0].Fit(fitFunc,"Q","same")
        elif isProfile:
            histos[mType][0].SetTitle(hTitle)
            histos[mType][0].GetXaxis().SetTitle(xtitle)
            histos[mType][0].GetYaxis().SetTitle(ytitle)
            histos[mType][0].SetMarkerSize(0.5)
            #histos[mType][0].SetFillColor(ROOT.TColor.GetColorBright(ROOT.kGray))
            #histos[mType][0].SetFillColor(ROOT.kGray)
            histos[mType][0].Draw("same" if same else "")
        elif is2D:
            assert not same
            zmin = hDef.getParameter('zMin',mType) if hDef.getParameter('zMin',mType)!=None else 0.
            zmax = hDef.getParameter('zMax',mType) if hDef.getParameter('zMax',mType)!=None else 1.05
            if effCuts!=None:
                histos[mType][1].SetTitle(hTitle)
                histos[mType][1].GetXaxis().SetTitle(xtitle)
                histos[mType][1].GetYaxis().SetTitle(ytitle)
                histos[mType][1].SetMinimum(zmin)
                histos[mType][1].SetMaximum(zmax)
                histos[mType][1].Draw("ZCOL")
            else:
                histos[mType][0].SetTitle(hTitle)
                histos[mType][0].GetXaxis().SetTitle(xtitle)
                histos[mType][0].GetYaxis().SetTitle(ytitle)
                histos[mType][0].Draw("ZCOL")
        elif is3D:
            assert not same
            zmin = hDef.getParameter('zMin',mType) if hDef.getParameter('zMin',mType)!=None else 0.
            zmax = hDef.getParameter('zMax',mType) if hDef.getParameter('zMax',mType)!=None else 1.05
            assert effCuts==None
            histos[mType][0].SetTitle(hTitle)
            histos[mType][0].GetXaxis().SetTitle(xtitle)
            histos[mType][0].GetYaxis().SetTitle(ytitle)
            histos[mType][0].GetZaxis().SetTitle(ztitle)
            histos[mType][0].Draw()
        if logY or hDef.getParameter('logY',mType):
            ROOT.gPad.SetLogy(1)
        if is2D and ( logZ or hDef.getParameter('logZ',mType) ):
            ROOT.gPad.SetLogz(1)
        ROOT.gPad.Update()
        
        #cnv.cd()
        #padNameDown = cnvName+str(mType)+'down'
        #result[padNameDown] = ROOT.TPad(padNameDown,padNameDown,(ic-1)/3.,0.,ic/3.,1/3.)
        #result[padNameDown].Draw()
        result['pave'+str(mType)] = drawCutPave(cnv,ic,hDef.getParameter('variable',mType), \
                                                cutString(extraCuts,hDef.getParameter('baseCuts',mType)), \
                                                cutString(hDef.getParameter('effCuts',mType)))

    #for k,v in result.items():
    #    print(k,v)
    savedDir.cd()
    return result

def addHistogram(varString,cuts,effCuts=None,name='userHist'):
    extraHDict = { }
    # split into string defining the variable(s) and (1 or 2) axis definition(s)
    fields1 = varString.split(";")
    assert len(fields1)<=3
    extraHDict['variable'] = fields1[0]
    #extraHDict['canvasName'] = "cEffArg"
    #extraHDict['histogramName'] = "hEffArg"
    extraHDict['histogramTitle'] = name
    # x-axis
    fields2 = fields1[1].split(",")
    assert len(fields2)==3 
    extraHDict['xNbins'] = int(fields2[0])
    extraHDict['xMin'] = float(fields2[1])
    extraHDict['xMax'] = float(fields2[2])
    # check for info on y axis (== presence of 2nd variable)
    if len(fields1)==3:
        assert ":" in extraHDict['variable']
        fields3 = fields1[2].split(",")
        extraHDict['yNbins'] = int(fields3[0])
        extraHDict['yMin'] = float(fields3[1])
        extraHDict['yMax'] = float(fields3[2])
        extraHDict['xTitle'] = extraHDict['variable'].split(":")[1]
        extraHDict['yTitle'] = extraHDict['variable'].split(":")[0]
    else:
        extraHDict['yMin'] = 0.
        extraHDict['yMax'] = 1.05
        extraHDict['xTitle'] = extraHDict['variable']
        extraHDict['yTitle'] = 'efficiency' if effCuts!=None else 'events/bin'
    extraHDict['baseCuts'] = cuts
    if effCuts!=None:
        extraHDict['effCuts'] = effCuts
    #xxx = HistogramDefinition("effV",extraHDict)
    #print("xxx",xxx)
    #print("xxx",xxx.parameters)
    #allHDefs.add(HistogramDefinition("effV",extraHDict))
    #print(allHDefs.allDefinitions.keys())
    #print(allHDefs.allCanvases)
    #print(allHDefs['hEffArg'])
    return HistogramDefinition(name,extraHDict)


    
parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--definitions', '-d', help='python module with dictionaries defining efficiency histograms', \
                        type=str, default=None)
parser.add_argument('--histogram', \
                    help='definition of extra histogram (format <variable>;<nbx>,<xmin>,<xmax>[;<nny>,<ymin>,<ymax>)', \
                    action='append', type=str, default=[])
parser.add_argument('--batch', '-b', help='ROOT batch mode', action='store_true', default=False)
parser.add_argument('--dxMax', help='max. local dx for efficiency plots', type=float, default=0.0075)
parser.add_argument('--cuts', '-c', help="basic cut string", type=str, default="")
parser.add_argument('--effCuts', '-e', help="basic cut string", type=str, default=None)
parser.add_argument('--output', '-o', help='output directory for graphic output', type=str, default=None)
parser.add_argument('--formats', help='comma-separated list of extensions for output files', \
                        type=str, default="pdf,png")
parser.add_argument('--sampleName', help='sample label for output', type=str, default=None)
parser.add_argument('--fitResiduals', '-f', \
                        help='comma-separated list of names of histogram sets with residuals to be fit', \
                        type=str, default=None)
parser.add_argument('--selectedHistograms', help='comma-separated names of histogram definitions to be used', \
                        type=str, default='*')
parser.add_argument('--vetoedHistograms', help='comma-separated names of histogram definitions not to be used',
                        type=str, default='')
parser.add_argument('--logY', help='use log scale for y axis', action='store_true', default=False)
parser.add_argument('--logZ', help='use log scale for z axis', action='store_true', default=False)
parser.add_argument('--printTree', '-p', help='print TTree contents', action='store_true', default=False)
parser.add_argument('--listHistograms', '-l', help='list predefined and selected histograms', \
                        action='store_true', default=False)
parser.add_argument('--zone', '-z', help='restrict to zone in OT (barrel, tilted, endcap)', type=str, \
                        choices=['barrel','tilted','endcap'], default=None)
parser.add_argument('file', help='input file', type=str, nargs='+', default=None)
args = parser.parse_args()
outputFormats = [ ]
if args.output!=None:
    assert os.path.isdir(args.output)
    print("***",args.output)
    outputFormats = [ x.strip() for x in args.formats.strip().split(",") ]
fitResiduals = args.fitResiduals.split(",") if args.fitResiduals else [ ]
selectedHistoNames = args.selectedHistograms.split(",")
vetoedHistoNames = args.vetoedHistograms.split(",")
#
# add cut for zone definition?
#
if args.zone=="barrel":
    zoneCuts = "detNormalT>0.99"
elif args.zone=="endcap":
    zoneCuts = "detNormalT<0.01"
elif args.zone=="tilted":
    zoneCuts = "detNormalT>0.05&&detNormalT<0.095"
else:
    zoneCuts = ""
args.cuts = cutString(args.cuts,zoneCuts)
    
#
# load histogram definitions
#
allVDefs,allHDefs = loadConfiguration(args.definitions,selectedHistoNames,vetoedHistoNames)
if args.listHistograms:
    hnames = sorted(allHDefs.allHistoNames)
    for hn in hnames:
        print(hn)
    sys.exit()
    
for ih,h in enumerate(args.histogram):
    allHDefs.add(addHistogram(h,args.cuts,args.effCuts,name="userH"+str(ih+1)))

#!#     varEffDict = { }
#!#     # split into string defining the variable(s) and (1 or 2) axis definition(s)
#!#     fields1 = args.varEff.split(";")
#!#     assert len(fields1)<=3
#!#     varEffDict['variable'] = fields1[0]
#!#     #varEffDict['canvasName'] = "cEffArg"
#!#     #varEffDict['histogramName'] = "hEffArg"
#!#     varEffDict['histogramTitle'] = "hEffArg"
#!#     # x-axis
#!#     fields2 = fields1[1].split(",")
#!#     assert len(fields2)==3 
#!#     varEffDict['xNbins'] = int(fields2[0])
#!#     varEffDict['xMin'] = float(fields2[1])
#!#     varEffDict['xMax'] = float(fields2[2])
#!#     # check for info on y axis (== presence of 2nd variable)
#!#     if len(fields1)==3:
#!#         assert ":" in varEffDict['variable']
#!#         fields3 = fields1[2].split(",")
#!#         varEffDict['yNbins'] = int(fields3[0])
#!#         varEffDict['yMin'] = float(fields3[1])
#!#         varEffDict['yMax'] = float(fields3[2])
#!#         varEffDict['xTitle'] = varEffDict['variable'].split(":")[1]
#!#         varEffDict['yTitle'] = varEffDict['variable'].split(":")[0]
#!#     else:
#!#         varEffDict['yMin'] = 0.
#!#         varEffDict['yMax'] = 1.05
#!#         varEffDict['xTitle'] = varEffDict['variable']
#!#         varEffDict['yTitle'] = 'efficiency'
#!#     varEffDict['baseCuts'] = args.cuts
#!#     varEffDict['effCuts'] = cutString("hasRecHit>0","abs(localPos.x()-rhLocalPos.x())<"+str(args.dxMax))
#!#     #xxx = HistogramDefinition("effV",varEffDict)
#!#     #print("xxx",xxx)
#!#     #print("xxx",xxx.parameters)
#!#     allHDefs.add(HistogramDefinition("effV",varEffDict))
#!#     #print(allHDefs.allDefinitions.keys())
#!#     #print(allHDefs.allCanvases)
#!#     #print(allHDefs['hEffArg'])
        
#extraCuts = "abs(particleType)==13"
#extraCuts = "tof<12.5"
extraCuts = args.cuts

if args.batch:
    ROOT.gROOT.SetBatch(1)
ROOT.gROOT.ProcessLine(".L setTDRStyle.C")
ROOT.gROOT.ProcessLine(".L floatMod.C+")
ROOT.setTDRStyle()
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptFit(1)
ROOT.gStyle.SetTitleFont(42)
ROOT.gStyle.SetTitleFontSize(0.03)
ROOT.gStyle.SetTitleX(0.12)
ROOT.gStyle.SetTitleY(1.00)
ROOT.gStyle.SetTitleAlign(13)
ROOT.gStyle.SetTitleBorderSize(0)
#ROOT.gStyle.SetTitleFillColor(0)
ROOT.gStyle.SetOptTitle(1)
#tf = ROOT.TFile(args.file[0])
#simHitTree = simHitTree = tf.Get("analysis").Get("SimHitTree")
simHitTree = ROOT.TChain("analysis/SimHitTree")
for fn in args.file:
    simHitTree.Add(fn)
#print(type(tchain))
#tchain.Print()
if args.printTree:
    simHitTree.Print()
    sys.exit()
#
# create RDataFrame and define additional columns
#
#simHitRDF = ROOT.RDataFrame(simHitTree)
simHitRDF = ROOT.RDataFrame("analysis/SimHitTree",args.file)
for k,v in allVDefs.items():
    simHitRDF = simHitRDF.Define(k,v)

canvases = [ ]
histos = { }
paves = [ ]
varMaskCombs = VarMaskCombinations()

allHistos = { }
for cName in allHDefs.canvasNames():
    allHistos[cName] = {}
    for hName in allHDefs.byCanvas[cName]:
        print("Processing histogram",hName,"in canvas",cName)
        print("  ",simHitRDF.GetDefinedColumnNames())
        try:
            simHitRDF,allHistos[cName][hName] = \
              createHistoByDef(simHitRDF,allHDefs.byCanvas[cName][hName],extraCuts,varMaskCombs)
        except:
            print("Exception for",cName,hName)
            raise
#sys.exit()

allObjects = [ ]
for cName in allHDefs.canvasNames():
    same = False
    cHistos = { }
    for hName in allHDefs.byCanvas[cName]:
        print("Processing histogram",hName,"in canvas",cName)
        print(allHistos[cName][hName])
        #cHistos[hName] = fillHistoByDef(simHitTree,allHDefs.byCanvas[cName][hName],extraCuts,allHistos[cName][hName])
        fillHistoByDef(simHitTree,allHDefs.byCanvas[cName][hName],extraCuts,allHistos[cName][hName])
        print(allHistos[cName][hName])
        allObjects.append(drawHistoByDef(allHistos[cName][hName],allHDefs.byCanvas[cName][hName], \
                                             logY=args.logY,logZ=args.logZ,same=same))
        same = True
    if args.output!=None:
        c = allObjects[-1]['cnv']
        #for c in [ x['cnv'] for x in allObjects ]:
        basename = os.path.join(args.output,c.GetName())
        if args.sampleName!=None:
            basename += "_" + args.sampleName
        if args.zone!=None:
            basename += "_" + args.zone
        print(basename)
        for fmt in outputFormats:
            c.SaveAs(basename+"."+fmt)
            
#    yMin = min([ x.GetMinimum() for x in cHistos
#sys.exit()

#!# allObjects = [ ]
#!# for hdef in allHDefs.allDefinitions.values():
#!#     #
#!#     # draw histograms according to definition
#!#     #
#!#     histos = fillHistoByDef(simHitTree,hdef,extraCuts)
#!#     allObjects.append(drawHistoByDef(histos,hdef))
#!#     #
#!#     # perform fit of resolution histogram
#!#     #
#!#     if hdef.name in fitResiduals:
#!#         objects = allObjects[-1]
#!#         cnv = objects['cnv']
#!#         # fit and redraw each panel
#!#         ic = 0
#!#         for mType in range(23,26):
#!#             ic += 1
#!#             cnv.cd(ic)
#!#             f = fitHistogram(mType,objects['histos'][mType][0])


#if args.output!=None:
#    for c in [ x['cnv'] for x in allObjects ]:
#        basename = os.path.join(args.output,c.GetName())
#        if args.sampleName!=None:
#            basename += "_" + args.sampleName
#        print(basename)
#        c.SaveAs(basename+".pdf")
#        c.SaveAs(basename+".png")
