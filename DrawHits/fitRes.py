import sys,os
from math import sqrt,log
import ROOT
import FitHistogram
import argparse

        
class FitCanvas:

    def __init__(self,canvas,mtype):
        self.canvas = canvas
        self.mtype = mtype
        self.pad = None
        self.fhist = None
        
        padName = canvas.GetName()+str(mtype-22)
        for o in canvas.GetListOfPrimitives():
            if o.InheritsFrom(ROOT.TPad.Class()) and o.GetName()==padName:
                assert self.pad==None
                self.pad = o
        assert self.pad!=None

        histNameBase = "h"+canvas.GetName()[1:]+str(mtype)
        self.fhist = None
        for o in self.pad.GetListOfPrimitives():
            if o.InheritsFrom(ROOT.TH1.Class()) and o.GetName().startswith(histNameBase):
                assert self.fhist==None
                self.fhist = FitHistogram(o)
        assert self.fhist!=None

    def histogram(self):
        #print("fhist",self.fhist,self.fhist.hist)
        return self.fhist.hist
            
    def fwhm(self):
        return self.fhist.fwhm()

def saveCanvas(canvas,inputName,outputDir,formats):
    canvasName = canvas.GetName()
    outputBaseName = os.path.splitext(os.path.basename(inputName))[0]
    outputName = os.path.join(outputDir,outputBaseName)
    if canvasName.split("_")[0]==outputBaseName.split("_")[0]:
        canvasName = "_".join(canvasName.split("_")[1:])
    elif canvasName.startswith("c"):
        canvasName = canvasName[1].lower() + canvasName[2:]
    outputName += "_" + canvasName
    for fmt in formats:
        print("Saving canvas as",outputName+"."+fmt)
        canvas.SaveAs(outputName+"."+fmt)

def setHistogramMinMax(histo,limits,margins=0.05):
    ''' Set minimum / maximum for histogram considering values within a range.
        Arguments:
          histo ...... histogram (TH1 or TH2)
          limits ..... lower/upper limit of the range defining values to be considered
          margins .... add this fraction of the min-max range below and above
        Return value:
          min / max value found within range
    '''
    #
    # min / max value can't be outside the range
    #
    vmin = limits[1]
    vmax = limits[0]
    #
    # loop over all bins and updated vmin/vmax
    #
    for ibx in range(histo.GetNbinsX()):
        for iby in range(histo.GetNbinsY()):
            c = histo.GetBinContent(ibx+1,iby+1)
            if c>=limits[0] and c<=limits[1]:
                vmin = min(vmin,c)
                vmax = max(vmax,c)
    #
    # apply min / max and return result
    #
    if (vmax-vmin)/(limits[1]-limits[0])<0.0001:
        vmin,vmax = limits
    histo.SetMinimum(vmin-margins*(vmax-vmin))
    histo.SetMaximum(vmax+margins*(vmax-vmin))
        
    return (vmin,vmax)

def defineWidthVsSigma(h,sigmas):
    hwName = h.GetName()+"Qw1D"
    hwTitle = h.GetTitle()+" (half-width from quantiles)"
    hwAxis1Title = "quantiles in units of #sigmas"
    hwAxis2Title = "half width from quantiles"
    hhalfwidth = ROOT.TH1F(hwName,hwTitle,len(sigmas),-0.5,len(sigmas)-0.5)
    hhalfwidth.SetStats(0)
    hhalfwidth.SetMinimum(0.)
    hhalfwidth.GetXaxis().SetTitle(hwAxis1Title)
    hhalfwidth.GetYaxis().SetTitle(hwAxis2Title)
    xaxis = hhalfwidth.GetXaxis()
    for i,s in enumerate(sigmas):
        xaxis.SetBinLabel(i+1,"{:3.1f}#sigma".format(s))

    return hhalfwidth

def defineMeanWidthHistograms(h,nby,ymin,ymax,nbz,zmin,zmax,isigma=None,sigma=None):
    if isigma!=None:
        y1 = ROOT.TMath.Freq(-sigma)
        y2 = ROOT.TMath.Freq(sigma)
        hcName = h.GetName()+"Qc"+str(isigma)
        hcTitle = h.GetTitle()+" (median)"
        hwName = h.GetName()+"Qhw"+str(isigma)
        hwTitle = h.GetTitle()+" (#sigma from quantiles)".format(y1,y2)
        hwAxis1Title = "median [#mum]"
        hwAxis2Title = "#sigma from {:4.1%}/{:4.1%} quantiles [#mum]".format(y1,y2)
    else:
        y1 = None
        y2 = None
        hcName = h.GetName()+"Qc fit"
        hcTitle = h.GetTitle()+" (fitted mean)"
        hwName = h.GetName()+"Qhw fit"
        hwTitle = h.GetTitle()+" (fitted sigma)"
        hwAxis1Title = "mean [#mum]"
        hwAxis2Title = "#sigma from fit [#mum]".format(y1,y2)
    if nby==1:
        hcentre = ROOT.TH1F(hcName,hcTitle,nbz,zmin,zmax)
        hcentre.GetXaxis().SetTitle(h.GetZaxis().GetTitle())
        hcentre.GetYaxis().SetTitle(hwAxis1Title)
        hhalfwidth = ROOT.TH1F(hwName,hwTitle,nbz,zmin,zmax)
        hhalfwidth.GetXaxis().SetTitle(h.GetZaxis().GetTitle())
        hhalfwidth.GetYaxis().SetTitle(hwAxis2Title)
    elif nbz==1:
        hcentre = ROOT.TH1F(hcName,hcTitle,nby,ymin,ymax)
        hcentre.GetXaxis().SetTitle(h.GetYaxis().GetTitle())
        hcentre.GetYaxis().SetTitle(hwAxis1Title)
        hhalfwidth = ROOT.TH2F(hwName,hwTitle,nby,ymin,ymax)
        hhalfwidth.GetXaxis().SetTitle(h.GetYaxis().GetTitle())
        hhalfwidth.GetYaxis().SetTitle(hwAxis2Title)
    else:
        hcentre = ROOT.TH2F(hcName,hctitle,nby,ymin,ymax,nbz,zmin,zmax)
        hcentre.GetXaxis().SetTitle(h.GetYaxis().GetTitle())
        hcentre.GetYaxis().SetTitle(h.GetZaxis().GetTitle())
        hcentre.GetZaxis().SetTitle(hwAxis1Title)
        hhalfwidth = ROOT.TH2F(hwName,hwTitle,nby,ymin,ymax,nbz,zmin,zmax)
        hhalfwidth.GetXaxis().SetTitle(h.GetYaxis().GetTitle())
        hhalfwidth.GetYaxis().SetTitle(h.GetZaxis().GetTitle())
        hhalfwidth.GetZaxis().SetTitle(hwAxis2Title)
        hhalfwidth.SetMinimum(0.)

    return hcentre,hhalfwidth

    
parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
#parser.add_argument('--moduleType', '-m', help='module type', type=int, choices=[23,24,25], default=23)
parser.add_argument('--moduleTypes', '-m', help='comma-separated list of module types', type=str, default="23,24,25")
parser.add_argument('--fwhm', help='determining FWHM', action='store_true', default=False)
parser.add_argument('--slices', '-s', help='fit in slices in y', action='store_true', default=False)
parser.add_argument('--quantile', '-q', help='calculate quantiles corresponding to +- x sigma (can be repeated)', \
                        action='append', type=float, default=[])
parser.add_argument('--dbgQuantiles', help='modX,dxdz pairs defining individual bins for the quantile determination', \
                        action='append', type=str, default=[ ])
parser.add_argument('--dbgAllQuantiles', help='show residuals distributions for all bins', \
                        action='store_true', default=False)
parser.add_argument('--output', '-o', help='output directory', type=str, default=None)
parser.add_argument('--formats', help='comma-separated list of extensions for output files', \
                        type=str, default="pdf,png")
parser.add_argument('file', help='input file', type=str, nargs=1, default=None)
args = parser.parse_args()

moduleTypes = sorted(set([ int(x) for x in args.moduleTypes.split(",") ]))
assert moduleTypes[0]>=23 and moduleTypes[-1]<=25
moduleType = moduleTypes[0]

tf = ROOT.TFile(args.file[0])
tf.ls()
mainCnv = None
for k in tf.GetListOfKeys():
    o = k.ReadObj()
    if o.IsA()==ROOT.TCanvas.Class():
        assert mainCnv==None
        mainCnv = k.ReadObj()
assert mainCnv!=None

dbgQuantPoints = [ ]
for qp in args.dbgQuantiles:
    dbgQuantPoints.append( tuple([float(x.strip()) for x in qp.strip().split(",")]) )

if args.output!=None:
    assert os.path.isdir(args.output)
    outputFormats = [ x.strip() for x in args.formats.strip().split(",") ]

canvases = [ ]
slices = [ ]

mainCnv.Draw()
fitCanvases = { x:FitCanvas(mainCnv,x) for x in moduleTypes }
fitCanvas = fitCanvases[moduleType]
#fitCanvas = FitCanvas(mainCnv,moduleType)
fwhmArrow = ROOT.TArrow()
fwhmArrow.SetLineColor(2)
fwhmArrow.SetLineWidth(2)
quantLines = [ ]
for i in range(len(args.quantile)+1):
    quantLine = ROOT.TLine()
    quantLine.SetLineColor(4-i)
    #quantLine.SetLineWidth(2)
    #quantLine.SetLineStyle(i+1)
    quantLines.append(quantLine)
#quantLine.SetLineWidth(2)
if fitCanvas.histogram().GetDimension()==1 and ( not args.slices ):
    summaries = [ ]
    for im in moduleTypes:
        print("Module type",im)
        fc = fitCanvases[im]
        print(type(fc))
        assert fc.histogram().GetDimension()==1
        slices = [ fc.fhist ]
        #print(fc.fwhm())
        x1,x2,y = fc.fwhm()
        print(" FWHM: <x> = {:6.1f}um, dx = {:6.1f}um, sig = {:6.1f}um ( interval {:6.4f} - {:6.4f}cm )".format( \
                10000*(x1+x2)/2.,10000*(x2-x1),10000*(x2-x1)/2/sqrt(2*log(2)),x1,x2))

        fc.pad.cd()
        fwhmArrow.DrawArrow(x1,y,x2,y,0.005,"<>")

        #
        # define summary histograms
        #
        summaries.append(defineWidthVsSigma(fc.histogram(),args.quantile))

        quantiles = [ ]
        qlmax = slices[-1].hist.GetMaximum()/10.
        for isigma,sigma in enumerate(args.quantile):
            qs = [ ]
            for sgn in [-1,0,1]:
                p = ROOT.TMath.Freq(sgn*sigma)
                #qs.append(slices[-1].quantile(p))
                qs.append(slices[-1].findRootSpline(p))
                print(sigma,sgn,type(slices[-1]))
                #print(sigma,sgn,p,qs[-1])
            quantiles.append(qs)
            if not ( None in qs ):
                for iq in range(3):
                    il = 0 if iq==1 else isigma+1
                    h = slices[-1].hist
                    qlmax = h.GetBinContent(h.FindBin(qs[iq]))
                    quantLines[il].DrawLine(qs[iq],0.,qs[iq],qlmax)
                line = " from sigma = {:3.1f} quantile: ".format(sigma)
                line += "median = {:6.1f}um, half-width/sigma = {:6.1f}um".format(10000*qs[1], \
                                                                                  10000*(qs[2]-qs[0])/2/sigma)
                print(line)
                summaries[-1].SetBinContent(isigma+1,10000*(qs[2]-qs[0])/2/sigma)
                #quantLines[isigma].DrawLine(qs[0],0.,qs[0],qlmax)
                #quantLines[0].DrawLine(qs[1],0.,qs[1],qlmax)
                #quantLines[isigma].DrawLine(qs[2],0.,qs[2],qlmax)
            else:
                print("(At least) one quantile computation failed: sigma =",sigma," p =",ROOT.TMath.Freq(-sigma),qs)
                print("  ",slices[-1].hist.GetSumOfWeights(),slices[-1].hist.GetMaximum())

        fc.pad.Update()

    nmod = len(moduleTypes)
    cName = "c"+"_".join(h.GetName()[1:].split("_")[:-1])
    cName = cName[:-2] + "_mT" + cName[-2:] + "_Widths"
    cName = "cResWidths_mT"+str(moduleType)
    c = ROOT.TCanvas(cName,h.GetTitle()+" (width summary)",500*nmod,500)
    c.Divide(nmod,1)
    # set common maximum for all plots
    hmax = max([ x.GetMaximum() for x in summaries ])
    for i in range(nmod):
        c.cd(i+1)
        #setHistogramMinMax(summaries[i],(-250,250),margins=0.05)
        summaries[i].SetMaximum(hmax*1.05)
        summaries[i].Draw("HIST")
        ROOT.gPad.Update()
    c.Update()
    if args.output!=None:
        saveCanvas(c,args.file[0],args.output,outputFormats)

elif fitCanvas.histogram().GetDimension()==2 and args.slices:
    hist2D = fitCanvas.histogram()
    assert hist2D.GetDimension()==2
    yaxis = hist2D.GetYaxis()
    nby = hist2D.GetNbinsY()
    ncol = int(sqrt(nby))
    while ncol*ncol<nby:
        ncol += 1
    canvases = [ ]
    #cnv = ROOT.TCanvas("cslice","cslice",1200,1200)
    #cnv.Divide(ncol,ncol)
    #slices = [ ]
    hNameBase = hist2D.GetName()
    hTitleBase = hist2D.GetTitle()
    for iby in range(nby):
        #print(fitCanvas.histogram())
        #cnv.cd(iby+1)
        hName = hNameBase+"_"+str(iby+1)
        hTitle = hTitleBase+" (slice "+str(iby+1)+")"
        #print("new hName",hName)
        hProj = hist2D.ProjectionX(hName,iby+1,iby+1)
        #slices.append(hProj)
        #print("xxx",hProj)
        slices.append(FitHistogram(hProj))
        #print(slices[-1].hist)
        hProj.SetTitle(hTitle)
        #slices[-1].hist.Draw()
        #if hProj.GetEntries()<100:
        if hProj.GetMaximum()<100:
            continue
        canvases.append(ROOT.TCanvas("c"+hName[1:],"c"+hName[1:],800,800))
        canvases[-1].SetGridx(1)
        canvases[-1].SetGridx(2)
        hProj.Draw()
        x1,x2,y = slices[-1].fwhm()
        fmt = "{:5.2f} < dx/dz < {:5.2f} :"
        fmt += " <x> = {:6.1f}um, dx = {:6.1f}um, sig = {:6.1f}um ( interval {:6.4f} - {:6.4f}cm )"
        print(fmt.format(yaxis.GetBinLowEdge(iby+1),yaxis.GetBinUpEdge(iby+1), \
                10000*(x1+x2)/2.,10000*(x2-x1),10000*(x2-x1)/2/sqrt(2*log(2)),x1,x2))
        fwhmArrow.DrawArrow(x1,y,x2,y,0.005,"<>")

        if hProj.GetMaximum()>100:
            quantiles = [ ]
            qlmax = slices[-1].hist.GetMaximum()/10.
            for sigma in args.quantile:
                qs = [ ]
                for sgn in [-1,0,1]:
                    p = ROOT.TMath.Freq(sgn*sigma)
                    #qs.append(slices[-1].quantile(p))
                    qs.append(slices[-1].findRootSpline(p))
                    #print(sigma,sgn,p,qs[-1])
                quantiles.append(qs)
                if not ( None in qs ):
                    quantLine.DrawLine(qs[0],0.,qs[0],qlmax)
                    quantLine.DrawLine(qs[1],0.,qs[1],qlmax)
                    quantLine.DrawLine(qs[2],0.,qs[2],qlmax)
                
        ROOT.gPad.Update()
    
elif fitCanvas.histogram().GetDimension()==3:
    #
    # calculate summary of quantiles in x
    #
    h = fitCanvas.histogram()
    nby = h.GetNbinsY()
    ymin = h.GetYaxis().GetXmin()
    ymax = h.GetYaxis().GetXmax()
    nbz = h.GetNbinsZ()
    zmin = h.GetZaxis().GetXmin()
    zmax = h.GetZaxis().GetXmax()
    #
    # define summary histograms
    #
    summaries = [ ]
    for isigma,sigma in enumerate(args.quantile):
#!#         y1 = ROOT.TMath.Freq(-sigma)
#!#         y2 = ROOT.TMath.Freq(sigma)
#!#         if nby==1:
#!#             hcentre = ROOT.TH1F(h.GetName()+"Qc"+str(isigma), \
#!#                                 h.GetTitle()+" (median)", \
#!#                                 nbz,zmin,zmax)
#!#             hcentre.GetXaxis().SetTitle(h.GetZaxis().GetTitle())
#!#             hcentre.GetYaxis().SetTitle("median [#mum]")
#!#             hhalfwidth = ROOT.TH1F(h.GetName()+"Qhw"+str(isigma), \
#!#                                    h.GetTitle()+" (#sigma from quantiles)".format(y1,y2), \
#!#                                    nbz,zmin,zmax)
#!#             hhalfwidth.GetXaxis().SetTitle(h.GetZaxis().GetTitle())
#!#             hhalfwidth.GetYaxis().SetTitle("#sigma from {:4.1%}/{:4.1%} quantiles [#mum]".format(y1,y2))
#!#         elif nbz==1:
#!#             hcentre = ROOT.TH1F(h.GetName()+"Qc"+str(isigma), \
#!#                                 h.GetTitle()+" (median)", \
#!#                                 nby,ymin,ymax)
#!#             hcentre.GetXaxis().SetTitle(h.GetYaxis().GetTitle())
#!#             hcentre.GetYaxis().SetTitle("median [#mum]")
#!#             hhalfwidth = ROOT.TH2F(h.GetName()+"Qhw"+str(isigma), \
#!#                                    h.GetTitle()+" (#sigma from quantiles)".format(y1,y2), \
#!#                                    nby,ymin,ymax)
#!#             hhalfwidth.GetXaxis().SetTitle(h.GetYaxis().GetTitle())
#!#             hhalfwidth.GetYaxis().SetTitle("#sigma from {:4.1%}/{:4.1%} quantiles [#mum]".format(y1,y2))
#!#         else:
#!#             hcentre = ROOT.TH2F(h.GetName()+"Qc"+str(isigma), \
#!#                                 h.GetTitle()+" (median)", \
#!#                                 nby,ymin,ymax,nbz,zmin,zmax)
#!#             hcentre.GetXaxis().SetTitle(h.GetYaxis().GetTitle())
#!#             hcentre.GetYaxis().SetTitle(h.GetZaxis().GetTitle())
#!#             hcentre.GetZaxis().SetTitle("median [#mum]")
 #!#             hhalfwidth = ROOT.TH2F(h.GetName()+"Qhw"+str(isigma), \
#!#                                    h.GetTitle()+" (#sigma from quantiles)".format(y1,y2), \
#!#                                    nby,ymin,ymax,nbz,zmin,zmax)
#!#             hhalfwidth.GetXaxis().SetTitle(h.GetYaxis().GetTitle())
#!#             hhalfwidth.GetYaxis().SetTitle(h.GetZaxis().GetTitle())
#!#             hhalfwidth.GetZaxis().SetTitle("#sigma from {:4.1%}/{:4.1%} quantiles [#mum]".format(y1,y2))
 #!#             hhalfwidth.SetMinimum(0.)
        hcentre,hhalfwidth = defineMeanWidthHistograms(h,nby,ymin,ymax,nbz,zmin,zmax,isigma,sigma)
        summaries.append((hcentre,hhalfwidth))
    hcentre,hhalfwidth = defineMeanWidthHistograms(h,nby,ymin,ymax,nbz,zmin,zmax,None,None)
    summaries.append((hcentre,hhalfwidth))

    dbgBins = set()
    if args.dbgAllQuantiles:
        # get histograms for all bins
        for iy in range(nby):
            for iz in range(nbz):
                dbgBins.add((iy+1,iz+1))
    else:
        for y,z in dbgQuantPoints:
            dbgBins.add( (h.GetYaxis().FindBin(y), h.GetZaxis().FindBin(z)) )
    dbgBins = sorted(dbgBins)

    allDbgObjects = { x:[ ] for x in range(len(args.quantile)) }
    allFitObjects = [ ]
    nDbg = len(dbgBins)
    nrow = ncol = int(sqrt(nDbg))
    while nrow*ncol<nDbg:
        ncol += 1
    savePad = ROOT.gPad
    cDbgName = "cResDbg_mT"+str(moduleType)
    allDbgObjects['canvas'] = ROOT.TCanvas(cDbgName,cDbgName,min(1500,ncol*250),min(1500,nrow*250))
    allDbgObjects['canvas'].Divide(nrow,ncol)
    iDbgPad = 0
    for iy in range(nby):
        for iz in range(nbz):
            htmp = h.ProjectionX(iymin=iy+1,iymax=iy+1,izmin=iz+1,izmax=iz+1)
            fhtmp = FitHistogram(htmp)
            quantiles = [ ]
            for isigma,sigma in enumerate(args.quantile):
                #if htmp.GetSumOfWeights()>100:
                # ensure sufficient statistics
                p1 = ROOT.TMath.Freq(-sigma)
                if htmp.GetSumOfWeights()>3/p1:
                    #q1 = fhtmp.quantile(ROOT.TMath.Freq(-sigma))
                    #q2 = fhtmp.quantile(ROOT.TMath.Freq(sigma))
                    qm1  = fhtmp.findRootSpline(ROOT.TMath.Freq(-sigma))
                    q0  = fhtmp.findRootSpline(ROOT.TMath.Freq(0))
                    qp1  = fhtmp.findRootSpline(ROOT.TMath.Freq(sigma))
                else:
                    qm1 = None
                    q0 = None
                    qp1 = None
                quantiles.append((qm1,q0,qp1))
                hsum = summaries[isigma][0]
                if nby==1:
                    ibin = hsum.GetBin(iz+1)
                elif nbz==1:
                    ibin = hsum.GetBin(iy+1)
                else:
                    ibin = hsum.GetBin(iy+1,iz+1)
                if q0!=None:
                    hsum.SetBinContent(ibin,q0)
                else:
                    print("No median for bins",iy+1,iz+1,"of",htmp.GetName())
                    hsum.SetBinContent(ibin,-999999)
                if htmp.GetName()=="hPull3DXVsDxDzW223_1_px" and (iy+1)==1  and (iz+1)==3:
                    print("...",isigma,sigma,qm1,q0,qp1,htmp.GetSumOfWeights())
                hsum = summaries[isigma][1]
                if qm1!=None and qp1!=None:
                    hsum.SetBinContent(ibin,(qp1-qm1)/2./sigma)

            #allDbgObjects[isigma] = [ ]
            if (iy+1,iz+1) in dbgBins:
                y1 = htmp.GetYaxis().GetBinLowEdge(iy+1)
                y2 = y1 + htmp.GetYaxis().GetBinWidth(iy+1)
                z1 = htmp.GetZaxis().GetBinLowEdge(iz+1)
                z2 = z1 + htmp.GetZaxis().GetBinWidth(iz+1)

                hResName = "hResDbg_mT"+str(moduleType)+"_y{:02d}_z{:02d}".format(iy+1,iz+1)
                hResTitle = "residual mType "+str(moduleType)
                if nby>1:
                    hResTitle += " {:6.3f}<y<{:6.3f}".format(y1,y2)
                if nbz>1:
                    hResTitle += " {:6.3f}<z<{:6.3f}".format(z1,z2)
                
                dbgObjects = [ ]
                #hResDbg =htmp.Clone("hResDbg_"+str(isigma)+"_"+str(len(allDbgObjects[isigma])))
                #hResDbg.SetTitle("hResDbg "+str(isigma)+" y"+str(iy+1)+" z"+str(iz+1))
                hResDbg = htmp.Clone(hResName)
                hResDbg.SetTitle(hResTitle)
                hResDbg.GetXaxis().SetTitle(h.GetXaxis().GetTitle())
                hResDbg.GetYaxis().SetTitle("fraction per bin / cumulatitive fraction")
                hResDbg.SetFillStyle(1001)
                hResDbg.SetFillColor(ROOT.kOrange)
                #dbgObjects.append(ROOT.TCanvas("c"+hResDbg.GetName()[1:],"c"+hResDbg.GetName()[1:],500,500))
                iDbgPad += 1
                dbgObjects.append(allDbgObjects['canvas'].cd(iDbgPad))
                dbgObjects[0].SetGridx(1)
                dbgObjects[0].SetGridy(1)
                dbgObjects.append(hResDbg)
                hResDbgMax = hResDbg.GetMaximum()
                hResDbg.Scale(1./hResDbgMax)
                hResDbg.Draw("hist")
                for isigma,sigma in enumerate(args.quantile):
                    #qm1  = fhtmp.findRootSpline(ROOT.TMath.Freq(-sigma))
                    #q0  = fhtmp.findRootSpline(ROOT.TMath.Freq(0.))
                    #qp1  = fhtmp.findRootSpline(ROOT.TMath.Freq(sigma))
                    qm1,q0,qp1 = quantiles[isigma]
                    if qm1!=None:
                        quantLines[isigma].DrawLine(qm1,0.,qm1,hResDbg.GetMaximum()/1.)
                    if q0!=None:
                        quantLines[0].DrawLine(q0,0.,q0,hResDbg.GetMaximum()/1.)
                    if qp1!=None:
                        quantLines[isigma].DrawLine(qp1,0.,qp1,hResDbg.GetMaximum()/1.)
                    g = ROOT.TGraph()
                    g.SetLineColor(ROOT.kMagenta)
                    g.SetLineStyle(2)
                    #g.SetMarkerStyle(20)
                    for x,y in fhtmp.cumulativeNormGraph():
                        g.SetPoint(g.GetN(),x,y)
                    g.Draw("L")
                    dbgObjects.append(g)
                    #

                dbgObjects[0].Update()
                allDbgObjects[isigma].append(dbgObjects)
                fitPtr = None
                fitFunc = None
                print(htmp.GetName(),"Sum of weights",htmp.GetSumOfWeights())
                if htmp.GetSumOfWeights()>100:
                    fitPtr,fitFunc = fhtmp.fitGaus(ROOT.TMath.Freq(-2.),ROOT.TMath.Freq(2.))
                    print(fitPtr,fitFunc)
                    if fitPtr!=None:
                        fitFunc2 = fitFunc.Clone()
                        fitFunc2.SetParameter(0,fitFunc.GetParameter(0)/hResDbgMax)
                        fitFunc2.Draw("same")
                        allFitObjects.append((fitPtr,fitFunc2))
                        dbgObjects[0].Update()
                        hsum = summaries[-1][0]
                        if nby==1:
                            ibin = hsum.GetBin(iz+1)
                        elif nbz==1:
                            ibin = hsum.GetBin(iy+1)
                        else:
                            ibin = hsum.GetBin(iy+1,iz+1)
                        hsum.SetBinContent(ibin,fitPtr.Parameter(1))
                        hsum.SetBinError(ibin,fitPtr.Error(1))
                        hsum = summaries[-1][1]
                        if nby==1:
                            ibin = hsum.GetBin(iz+1)
                        elif nbz==1:
                            ibin = hsum.GetBin(iy+1)
                        else:
                            ibin = hsum.GetBin(iy+1,iz+1)
                        hsum.SetBinContent(ibin,fitPtr.Parameter(2))
                        hsum.SetBinError(ibin,fitPtr.Error(2))
                else:
                    print("No median for bins",iy+1,iz+1,"of",htmp.GetName())
                    hsum.SetBinContent(ibin,-999999)

                        
            allDbgObjects['canvas'].Update()

    if args.output:
        saveCanvas(allDbgObjects['canvas'],args.file[0],args.output,outputFormats)
    savePad.cd()

    nsigma = len(args.quantile)
    # create from histogram name (remove version number last "_", split of last two digits (mod. type)

    cName = "c"+"_".join(h.GetName()[1:].split("_")[:-1])
    cName = cName[:-2] + "_mT" + cName[-2:] + "_MeanWidth"
    cName = "cResMeanWidth_mT"+str(moduleType)
    c = ROOT.TCanvas(cName,h.GetTitle()+" (mean/width summary)",500*nsigma,1000)
    c.Divide(nsigma+1,2)
    for i in range(nsigma+1):
        hopt = "HIST" if i<nsigma else ""
        c.cd(i+1)
        if summaries[i][0].GetDimension()==2:
            ROOT.gPad.SetRightMargin(0.15)
            setHistogramMinMax(summaries[i][0],(-250,250),margins=0.05)
            summaries[i][0].Draw("ZCOL")
        else:
            setHistogramMinMax(summaries[i][0],(-250,250),margins=0.05)
            summaries[i][0].Draw(hopt)
        ROOT.gPad.Update()
        c.cd(nsigma+1+i+1)
        if summaries[i][1].GetDimension()==2:
            summaries[i][1].Draw("ZCOL")
        else:
            summaries[i][1].Draw(hopt)
        ROOT.gPad.Update()
    
    c.Update()
    if args.output!=None:
        saveCanvas(c,args.file[0],args.output,outputFormats)
    
