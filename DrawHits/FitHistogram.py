import ROOT

class FitHistogram:
    ''' Helper class to extract various quantities from a 1D histogram
    '''
    def interpolate(y,y1,y2,x1=0.,x2=1.):
        ''' Linear interpolation between two points (x1,y1) and (x2,y2) 
            to yield x corresponding to the target value y.
        '''
        return x1 + (y-y1)/(y2-y1)*(x2-x1)
        
    def __init__(self,histogram):
        ''' Store input histogram and prepare caches for various intermediate quantities
        '''
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
        #print("xups",xups)
        xlow = xups[0] if xups else None
        #
        # use last intersection with downward slope
        #
        xdowns = self.intersects(y,cumulative=False,direction=-1)
        #print("xdowns",xdowns)
        xhigh = xdowns[-1] if xdowns else None

        #
        # require result ( assumes that first and last bins are < ymax/2 ) and
        # correct for bin width / 2 ( assumes that bin value corresponds to center of bin )
        assert xlow!=None and xhigh!=None
        return (xlow,xhigh,y)
        #return (xlow+dx,xhigh+dx,y)

    def quantile(self,prob):
        ''' Return x-value to quantile q. 
        '''
        #
        # basic check - refuse to calculate quantile for probabilities beyond 1st / last non-empty bin
        #
        # use tail probability
        #
        nb = self.hist.GetNbinsX()
        sumw = self.hist.GetSumOfWeights()
        if prob<=0.5:
            # check first non-empty bin from low -> high
            cmax = prob*sumw
            rng = range(1,nb+1)
        else:
            # check first non-empty bin from high -> low
            cmax = (1-prob)*sumw
            rng = range(nb,0,-1)
        # find first non-empty bin
        for ib in rng:
            c = self.hist.GetBinContent(ib)
            if c>1.e-10:
                # return invalid result if first bin exceeds the threshold
                if c>cmax:
                    #print("<<<",self.hist.GetName(),prob,nb,cmax,range,ib,c)
                    return None
                break
        #
        # now determine quantile
        #
        result = self.intersects(prob,cumulative=True,norm=True,direction=1)
        #print(prob,result)
        if len(result)>1:
            result = None
            
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
        ymin = yl
        ymax = yh
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
            
        
if __name__=="__main__":
    #
    # test of fitting for my canvases
    #
    import sys
    from math import sqrt,log
    from fnmatch import fnmatch
    import argparse
    
    def fromQuantiles(fitHisto,isig):
        xqs = [ ]
        for sgn in [ -1, 0, 1 ]:
            xqs.append(fitHisto.quantile(ROOT.TMath.Freq(sgn*isig)))
        if None in xqs:
            return None
        return [ ( xqs[1], 0. ), ( (xqs[2]-xqs[0])/2./isig, 0. ) ]
    
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--list', '-l', help='list pads / histograms', action='store_true', default=False)
    parser.add_argument('--algorithms', '-a', help='comma-separated list of algorithms used for fit results', \
                            type=str, default='prefit' )
    parser.add_argument('--padName', help='pad name (fnmatch pattern)', type=str, default='*')
    parser.add_argument('--histogramName', help='histogram name (fnmatch pattern)', type=str, default='*')
    parser.add_argument('file', help='root file', type=str, nargs=1)
    args = parser.parse_args()
    
    #
    # select pad and histogram
    #
    mainPads = [ ]
    tf = ROOT.TFile(args.file[0])

    for k in tf.GetListOfKeys():
        oName = k.GetName()
        o = tf.Get(oName)
        if o.InheritsFrom(ROOT.TVirtualPad.Class()):
            mainPads.append(o)
    assert len(mainPads)==1

    selectedPads = [ ]
    for p in mainPads[0].GetListOfPrimitives():
        oName = p.GetName()
        if args.list or fnmatch(oName,args.padName):
            selectedPads.append(p)
    if not args.list:
        assert len(selectedPads)==1

    selectedHistograms = [ ]
    for p in selectedPads:
        if args.list:
            print("Pad ",p.GetName(),":")
        for o in p.GetListOfPrimitives():
            if o.InheritsFrom(ROOT.TH1.Class()) and o.GetDimension()==1:
                oName = o.GetName()
                if args.list:
                    print("  Histogram 1D ",oName,type(o))
                if fnmatch(oName,args.histogramName):
                    selectedHistograms.append(o)

    if args.list:
        sys.exit(0)

    selPad = selectedPads[0]
    
    assert len(selectedHistograms)==1

    ROOT.gROOT.cd()
    cnv = ROOT.TCanvas("c","c",800,800)
    if selPad.GetLogy():
        cnv.SetLogy(1)
    padHisto = selectedHistograms[0].Clone()
    fitHisto = FitHistogram(padHisto)
    padHisto.SetLineWidth(1)
    padHisto.SetMarkerStyle(20)
    padHisto.Draw("LP")
    cnv.SetGridx(1)
    cnv.SetGridy(1)
    cnv.Update()
    tf.Close()
    
    result = None
    fitHisto = FitHistogram(padHisto)


    #
    # FWHM
    #
    xmin,xmax,y = fitHisto.fwhm()
    result = [ ( (xmax+xmin)/2., 0. ), ( (xmax-xmin)/2/sqrt(2*log(2.)), 0. ) ]
    print("FWHM",[ x[0] for x in result ])
    fwhmArrow = ROOT.TArrow()
    fwhmArrow.SetLineColor(2)
    fwhmArrow.SetLineWidth(3)
    fwhmArrow.DrawArrow(xmin,y,xmax,y,0.005,"<>")
    #
    # prefit
    #
    gaus = None
    for f in padHisto.GetListOfFunctions():
        if f.GetName()=="gaus":
            assert gaus==None
            gaus = f
            #gaus = f.Clone()
            n = gaus.GetNpar()
            assert n==3
            result = [ ]
            for i in range(1,3):
                result.append((gaus.GetParameter(i),gaus.GetParError(i)))
            gaus.SetLineColor(ROOT.kCyan)
            #gaus.Draw()
    print("Prefit",[ x[0] for x in result ])
    #
    # gaus fit
    #
    fitPtr,fitFunc = fitHisto.fitGaus()
    result = [ ]
    if fitPtr!=None:
        for i in range(1,3):
            result.append((fitPtr.Parameter(i),fitPtr.ParError(i)))
    if fitFunc!=None:
        print(fitFunc.GetParameter(0),fitFunc.GetParameter(1),fitFunc.GetParameter(2))
        fitFunc.SetLineColor(ROOT.kMagenta)
        fitFunc.SetLineWidth(3)
        fitFunc.Draw("same")
    print("Gaus fit",[ x[0] for x in result ])
    #
    # quantiles (1 sigma equivalent)
    #
    quantLines = [ ]
    quantColors = [ ROOT.kBlack, ROOT.kBlue, 8, ROOT.kRed ]
    for i in range(4):
        quantLine = ROOT.TLine()
        #quantLine.SetLineColor(4-i)
        quantLine.SetLineColor(quantColors[i])
        #quantLine.SetLineColor(4-i)
        quantLine.SetLineWidth(3)
        quantLine.SetLineStyle(2)
        #quantLine.SetLineStyle(i+1)
        quantLines.append(quantLine)
    for isigma,sigma in enumerate([1,2,3]):
        qs = [ ]
        for sgn in [-1,0,1]:
            p = ROOT.TMath.Freq(sgn*sigma)
            qs.append(fitHisto.findRootSpline(p))
            #print(sigma,sgn,type(fitHisto))
            #print(sigma,sgn,p,qs[-1])
        #print(isigma,sigma,qs)
        result = fromQuantiles(fitHisto,sigma)
        if result!=None:
            print("Sig",sigma,[ x[0] if x!=None else None for x in result ])
        else:
            print("Sig",result)

        for iq in range(3):
            il = 0 if iq==1 else isigma+1
            qlmax = padHisto.GetBinContent(padHisto.FindBin(qs[iq]))
            quantLines[il].DrawLine(qs[iq],0.,qs[iq],qlmax)
            #if iq==0:
            #    line = " from sigma = {:3.1f} quantile: ".format(sigma)
            #    line += "median = {:6.1f}um, half-width/sigma = {:6.1f}um".format(10000*qs[1], \
            #            10000*(qs[2]-qs[0])/2/sigma)
            #    print(line)

    cnv.Update()
    
