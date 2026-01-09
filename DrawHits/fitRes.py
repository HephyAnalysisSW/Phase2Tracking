import sys,os
from math import sqrt,log
import ROOT
import argparse

class FitHistogram:

    def interpolate(y,y1,y2,x1=0.,x2=1.):
        ''' Linear interpolation between two points (x1,y1) and (x2,y2) 
            to yield x corresponding to the target value y.
        '''
        return x1 + (y-y1)/(y2-y1)*(x2-x1)
        
    def __init__(self,histogram):
        self.hist = histogram
        self.graph_ = None
        self.cumulativeGraph_ = None
        self.cumNormGraph_ = None
        self.cumNormTGraph_ = None
        self.cumNormSpline_ = None               # spline corresponding to normalized cumulative graph

    def graph(self):
        ''' Histogram converted to list of (x,y) coordinates with x = bin center and y = bin contents.
            Ignores under- / overflow.
        '''
        if self.graph_==None:
            self.graph_ = [ ]

            for i in range(self.hist.GetNbinsX()):
                xbin = self.hist.GetBinLowEdge(i+1) + self.hist.GetBinWidth(i+1)/2.
                self.graph_.append( (xbin,self.hist.GetBinContent(i+1)) )

        return self.graph_

    def cumulativeGraph(self):
        ''' Histogram converted to list of (x,y) coordinates with x = bin center and y = cumulated bin contents.
            Ignores under- / overflow.
        '''
        if self.cumulativeGraph_==None:
            self.cumulativeGraph_ = [ ]
            sum = 0.
            for i in range(self.hist.GetNbinsX()):
                xbin = self.hist.GetBinLowEdge(i+1) + self.hist.GetBinWidth(i+1)/2.
                sum += self.hist.GetBinContent(i+1)
                self.cumulativeGraph_.append( (xbin,sum) )

        return self.cumulativeGraph_

    def cumulativeNormGraph(self):
        ''' Histogram converted to list of (x,y) coordinates with x = bin center and y = cumulated bin contents.
            Normalized to total histogram contents (including under- / overflow).
        '''
        if self.cumNormGraph_==None:
            cg = self.cumulativeGraph()
            sum = self.hist.GetSumOfWeights()
            self.cumNormGraph_ = [ ( x,y/sum ) for x,y in cg ]
            
        return self.cumNormGraph_

    def cumulativeNormSpline(self):
        ''' Create (TGraph and) TSpline3 from cumulativeNormGraph
        '''
        if self.cumNormTGraph_==None:
            self.cumNormTGraph_ = ROOT.TGraph()
            for x,y in self.cumulativeNormGraph():
                self.cumNormTGraph_.SetPoint(self.cumNormTGraph_.GetN(),x,y)

        if self.cumNormSpline_==None:
            self.cumNormSpline_ = ROOT.TSpline3(self.hist.GetName()+"-spline",self.cumNormTGraph_)

        return self.cumNormSpline_
            
        
    def intersects(self,value,cumulative=False,norm=False,direction=0):
        ''' Calculate x-coordinates for intersection(s) of a graph defined by a list of (x,y) points sorted in x
              with y==value. Uses linear interpolation.
            Arguments:
               value ....... target value
               cumulative .. if true, use cumulative graph
               norm ........ if true, use normalized cumulative graph
               direction ... three possible values: 0 = any intersection, +1/-1 = consider only segments
                             with positive / negative slope.
        '''
        #
        # Get graph and do basic check
        #
        graph = None
        if cumulative:
            graph = self.cumulativeNormGraph() if norm else self.cumulativeGraph()
        else:
            assert norm==False
            graph = self.graph()
            
        result = [ ]
        if len(graph)<2:
            return result
        #
        # loop over adjacent pairs of points
        #
        x1 = None
        y1 = None
        for x2,y2 in graph:
            #
            # start checking at 2nd point
            #
            if x1!=None:
                assert x2>x1
                #
                # value in interval?
                #
                if value>=min(y1,y2) and value<=max(y1,y2):
                    # check if dy is positive or negative, and compare with required sign of direction
                    if direction==0 or direction*(y2-y1)>0:
                        result.append(FitHistogram.interpolate(value,y2,y1,x2,x1))
            #
            # move to next point
            #
            x1 = x2
            y1 = y2

        return result

    def fwhm(self):
        ''' Return lowest / highest x corresponding to ymax/2, and ymax/2
        '''
        #
        # target y value (1/2 maximum)
        #
        y = self.hist.GetBinContent(self.hist.GetMaximumBin())/2.
        #
        # use first intersection with upward slope
        #
        xups = self.intersects(y,cumulative=False,direction=1)
        print("xups",xups)
        xlow = xups[0] if xups else None
        #
        # use last intersection with downward slope
        #
        xdowns = self.intersects(y,cumulative=False,direction=-1)
        print("xdowns",xdowns)
        xhigh = xdowns[-1] if xdowns else None
        #dx = self.hist.GetBinWidth(1)
        ###
        ## preset result (low / high x values)
        ##
        #xlow = None
        #xhigh = None
        ##
        ## loop over pairs of adjacent histogram bins
        ##
        #x1 = self.hist.GetBinLowEdge(1)
        #y1 = self.hist.GetBinContent(1)
        #for i in range(2,self.hist.GetNbinsX()):
        #    # check if target value between contents of neighbouring bins
        #    x2 = self.hist.GetBinLowEdge(i)
        #    y2 = self.hist.GetBinContent(i)
        #    first = None
        #    if y>=y1 and y<y2:
        #        first = True
        #    elif y<=y1 and y>y2:
        #        first = False
        #
        #    if first!=None:
        #        # calculate interpolated x value
        #        x = FitHistogram.interpolate(y,y1,y2,x1,x2)
        #        # store lowest and highest x corresponding to y
        #        if first and xlow==None:
        #            xlow = x
        #        elif not first:
        #            xhigh = x
        #    # move to next bin
        #    x1 = x2
        #    y1 = y2

        #
        # require result ( assumes that first and last bins are < ymax/2 ) and
        # correct for bin width / 2 ( assumes that bin value corresponds to center of bin )
        assert xlow!=None and xhigh!=None
        return (xlow,xhigh,y)
        #return (xlow+dx,xhigh+dx,y)

    def quantile(self,prob):
        ''' Return x-value to quantile q. 
        '''
        result = self.intersects(prob,cumulative=True,norm=True,direction=1)
        #print(prob,result)
        assert len(result)<2

        return result[0] if result else None

    def findRootSpline(self,value,eps=0.001):
        ''' Find position where spline derived from cumulative NormGraph= value. Assumes that the spline is \
            monotonously increasing. Tolerance is eps*<difference between first and last point)
        '''
        #
        # Make sure spline is available
        #
        spline = self.cumulativeNormSpline()
        #
        # No result if first / last point is above / below required value
        #
        cGraph = self.cumulativeGraph()
        if len(cGraph)==0 or cGraph[0][1]>value or cGraph[-1][1]<value:
            return None
        #
        # Initialize from first and last point and verify that monotonicity
        #
        xl = spline.GetXmin()
        yl = spline.Eval(xl)
        xh = spline.GetXmax()
        yh = spline.Eval(xh)
        if ymin>=ymax:
            print("findRootSpline: last value <= first value")
            return None
        #
        # Check if inside values spanned by spline
        #
        if value<ymin or value>ymax:
            print("findRootSpline: required value outside range")
            return None
        #
        # tolerance for distance between points
        #
        dxmax = eps*(ymax-ymin)
        #
        # loop with cutoff in case of non-convergence
        #
        found = False
        for i in range(1000):
            if (xh-xl)<dxmax:
                found = True
                break
            x = (xl+xh)/2.
            y = spline.Eval(x)
            if y<=value:
                xl = x
                yl = y
            else:
                xh = x
                yh = y
        if not found:
            print("findRootSpline: did not converge")
            return None

        return (xl+xh)/2.
            
    def fitGaus(self,prob1=0.,prob2=1.):
        assert prob2>prob1
        result = ( None, None )
        xmin = self.hist.GetXaxis().GetXmin()
        if prob1>0.:
            xmin = self.findRootSpline(prob1)
            if xmin==None:
                return result
        xmax = self.hist.GetXaxis().GetXmax()
        if prob2<1.:
            xmax = self.findRootSpline(prob2)
            if xmin==None:
                return result

        fitFunc = ROOT.TF1("mygaus","gaus(0)",xmin,xmax)
        fitFunc.SetParameter(0,self.hist.GetMaximum())
        fitFunc.SetParameter(1,0.)
        fitFunc.SetParLimits(1,-10.,10.)
        fitFunc.SetParameter(2,self.hist.GetRMS())
        
        fitPtr = self.hist.Fit(fitFunc,"S0")
        #fitPtr = self.hist.Fit("gaus","S0","",xmin,xmax)
        if ( not fitPtr.IsValid() ) or fitPtr.IsEmpty():
            return result

        #return fitPtr,self.hist.GetFunction("gaus")
        return fitPtr,fitFunc
            
        
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
parser.add_argument('--moduleType', '-m', help='module type', type=int, choices=[23,24,25], default=23)
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
fitCanvas = FitCanvas(mainCnv,args.moduleType)
fwhmArrow = ROOT.TArrow()
fwhmArrow.SetLineColor(2)
fwhmArrow.SetLineWidth(2)
quantLines = [ ]
for i in range(len(args.quantile)):
    quantLine = ROOT.TLine()
    quantLine.SetLineColor(4)
    #quantLine.SetLineWidth(2)
    quantLine.SetLineStyle(i+1)
    quantLines.append(quantLine)
#quantLine.SetLineWidth(2)
if fitCanvas.histogram().GetDimension()==1 and ( not args.slices ):
    assert fitCanvas.histogram().GetDimension()==1
    #print(fitCanvas.fwhm())
    x1,x2,y = fitCanvas.fwhm()
    print("<x> = {:6.1f}um, dx = {:6.1f}um, sig = {:6.1f}um ( interval {:6.4f} - {:6.4f}cm )".format( \
            10000*(x1+x2)/2.,10000*(x2-x1),10000*(x2-x1)/2/sqrt(2*log(2)),x1,x2))

    fitCanvas.pad.cd()
    fwhmArrow.DrawArrow(x1,y,x2,y,0.005,"<>")
    
    quantiles = [ ]
    qlmax = slices[-1].hist.GetMaximum()/10.
    for isigma,sigma in enumerate(args.quantile):
        qs = [ ]
        for sgn in [-1,0,1]:
            p = ROOT.TMath.Freq(sgn*sigma)
            #qs.append(slices[-1].quantile(p))
            qs.append(slices[-1].findRootSpline(p))
            #print(sigma,sgn,p,qs[-1])
        quantiles.append(qs)
        if not ( None in qs ):
            quantLines[isigma].DrawLine(qs[0],0.,qs[0],qlmax)
            quantLines[0].DrawLine(qs[1],0.,qs[1],qlmax)
            quantLines[isigma].DrawLine(qs[2],0.,qs[2],qlmax)

    fitCanvas.pad.Update()

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
    cDbgName = "cResDbg_mT"+str(args.moduleType)
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

                hResName = "hResDbg_mT"+str(args.moduleType)+"_y{:02d}_z{:02d}".format(iy+1,iz+1)
                hResTitle = "residual mType "+str(args.moduleType)
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
    cName = "cResMeanWidth_mT"+str(args.moduleType)
    
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
    
