import sys,os
import ROOT
from expectedClusterSize import clusterEndPoints,drawLines

def expSize(xs,pars):
    tanTrack = xs[0]
    posx = xs[1]
    tanLorentz = pars[0]
    deltaX = pars[1]
    stripWidth = pars[2]
    thickness = pars[3]
    
    dt = thickness*tanTrack
    x1,x2 = clusterEndPoints(posx+deltaX,tanTrack,tanLorentz,stripWidth,thickness)
    is1 = round(x1/stripWidth-0.5)
    is2 = round(x2/stripWidth-0.5)
    return is2-is1+1

def chi2(h,pars,opt=""):
    xaxis = h.GetXaxis()
    yaxis = h.GetYaxis()

    result = 0.
    unweighted = "W" in opt.upper()
    for ibx in range(h.GetNbinsX()):
        x = xaxis.GetBinCenter(ibx+1)
        for iby in range(h.GetNbinsY()):
            y = yaxis.GetBinCenter(iby+1)
            ibin = h.GetBin(ibx+1,iby+1)
            f = expSize([x,y],pars)
            c = h.GetBinContent(ibin)
            e = h.GetBinError(ibin)
            if c<1.e-6 or e<1.e-6:
                continue
            if unweighted:
                result += ((c-f))**2
            else:
                result += ((c-f)/e)**2

    return result

def getHisto(fn,cnvName,ipad):
    tf = ROOT.TFile(fn)
    cnv = tf.Get(cnvName)
    cnv3 = cnv.GetPad(ipad)
    h = None
    for o in cnv3.GetListOfPrimitives():
        if o.InheritsFrom(ROOT.TH1.Class()):
            h = o
            break

    return h

def scanFCN(h,tanAlphaRef,stripWidth,thickness,lowest=None,nlowest=50):
    hp = ROOT.TH2F("hp","hp",100,tanAlphaRef-0.40,tanAlphaRef+0.40,int(stripWidth+0.5),-stripWidth/2,stripWidth/2)
    xaxis = hp.GetXaxis()
    yaxis = hp.GetYaxis()

    cmin = None
    for ibx in range(hp.GetNbinsX()):
        x = xaxis.GetBinCenter(ibx+1)
        for iby in range(hp.GetNbinsY()):
            y = yaxis.GetBinCenter(iby+1)
            ibin = hp.GetBin(ibx+1,iby+1)
            c = chi2(h,[x,y,stripWidth,thickness])
            if lowest!=None:
                if cmin==None:
                    cmin = c
                dc = c/cmin - 1
                if dc<-0.0000001:
                    #print("New value at ",c,x,y)
                    lowest.clear()
                    cmin = c
                    lowest.append((c,x,y))
                elif abs(dc)<0.0000001:
                    #print("Same value at ",c,x,y)
                    lowest.append((c,x,y))
                #lowest.sort()
                #del lowest[nlowest:]
            hp.SetBinContent(ibin,c)
    return hp
                       
if __name__=="__main__":

    import argparse

    modTypeToCanvas = { 23 : 1, 24 : 2, 25 : 3 }
    modTypeToWidth = { 23 : 100, 24 : 100, 25 : 90 }
    
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--thickness', '-t', help="sensor thickness (in um)", type=float, default=290.)
    #parser.add_argument('--nbPosX', help="number of bins for position", type=int, default=180)
    parser.add_argument('--stripWidth', '-w', help="strip width (in um), default from modType", \
                            type=float, default=None)
    parser.add_argument('--refTanLorentzAngle',  help="tan Lorentz angle / B[T]", type=float, default=0.07)
    parser.add_argument('--bfield', '-b', help='B field [T]', type=float, default=3.8)
    #parser.add_argument('--nbTanLambda', help="number of bins for tan(#lambda)", type=int, default=201)
    #parser.add_argument('--maxTanLambda',  help="max. track dx/dz", type=float, default=2.01)
    #parser.add_argument('--deltaX', help='offset for x position', type=float, default=0.)
    #parser.add_argument('--canvasNumber', help='number of canvas to use (between 1 and 3)', type=int, default=3)
    parser.add_argument('--modType', help='module type', choices=sorted(modTypeToCanvas.keys()), type=int, default=25)
    parser.add_argument('--outputName', help='basic name for output file', type=str, default=None)
    parser.add_argument('--outputDir', '-o', help='directory for output file', type=str, default=None)
    parser.add_argument('--maxSize', help='max. cluster size in plot', type=int, default=6)
    parser.add_argument('file',help='input root file with canvases', type=str, nargs=1)
    args = parser.parse_args()

    infile = args.file[0]
    tanAlpha = args.refTanLorentzAngle*args.bfield

    canvasNumber = modTypeToCanvas[args.modType]
    assert canvasNumber>=1 and canvasNumber<=3

    if args.stripWidth==None:
        args.stripWidth = modTypeToWidth[args.modType]
    
    outFile = None
    if args.outputDir!=None:
        outFile = args.outputDir
        assert os.path.isdir(outFile)
        outFileName = args.outputName
        if outFileName==None:
            outFileName = os.path.splitext(os.path.basename(infile))[0]
        outFile = os.path.join(outFile,outFileName)

    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetPadRightMargin(0.15)
    h = getHisto(sys.argv[1],"cWidth3DVsDxDzModX",canvasNumber)
    print(type(h))
    xaxis = h.GetXaxis()
    yaxis = h.GetYaxis()

    linesDef = drawLines(args.stripWidth,args.thickness,tanAlpha,1, \
                             h.GetXaxis().GetXmin(),h.GetYaxis().GetXmin(),
                             h.GetXaxis().GetXmax(),h.GetYaxis().GetXmax())
    cnvH = ROOT.TCanvas("ch","ch",600,800)
    cnvH.SetBottomMargin(0.25)
    print("Max",h.GetBinContent(h.GetMaximumBin()))
    ivmax = min(args.maxSize,int(h.GetBinContent(h.GetMaximumBin())+1))
    h.SetMinimum(1)
    h.SetMaximum(ivmax)
    h.GetZaxis().SetNdivisions(-(ivmax-1))
    h.Draw("zcol")
    lDef = ROOT.TLine()
    lDef.SetLineColor(1)
    lDef.SetLineWidth(1)
    lDef.SetLineStyle(4)
    for p1,p2 in linesDef:
        lDef.DrawLine(*p1,*p2)
    cnvH.Update()
    
    cnv = ROOT.TCanvas("c","c",600,600)
    lowest = [ ]
    hp = scanFCN(h,tanAlpha,args.stripWidth,args.thickness,lowest,50)
    #for ix,x in enumerate(lowest):
    #    print(ix,x)
    hp.SetTitle("approximated #chi^{2};tan(Lorentz angle);x-shift [#mum]")
    hp.Draw("zcol")
    m = ROOT.TMarker()
    m.SetMarkerStyle(1)
    m.SetMarkerColor(2)
    cmin = None
    ns = 0
    sx = 0
    sy = 0
    for c,x,y in lowest:
        if cmin!=None and c>cmin:
            break
        m.DrawMarker(x,y)
        print(x,y)
        ns += 1
        sx += x
        sy += y
        cmin = c
    print(cmin,sx/ns,sy/ns)
    m1 = ROOT.TMarker()
    m1.SetMarkerStyle(28)
    m1.SetMarkerColor(2)
    m1.DrawMarker(sx/ns,sy/ns)
    ROOT.gPad.Update()
    if outFile!=None:
        cnv.SaveAs(outFile+"_mt"+str(args.modType)+"-chi2.pdf")
    

    linesFit = drawLines(args.stripWidth,args.thickness,sx/ns,1, \
                             h.GetXaxis().GetXmin(),h.GetYaxis().GetXmin(),
                             h.GetXaxis().GetXmax(),h.GetYaxis().GetXmax(),sy/ns)
    cnvH.cd()
    lFit = ROOT.TLine()
    lFit.SetLineColor(2)
    lFit.SetLineWidth(2)
    for p1,p2 in linesFit:
        lFit.DrawLine(*p1,*p2)

    pave1 = ROOT.TPaveText(ROOT.gPad.GetLeftMargin(),0.01,0.3,0.15,'brNDC')
    pave1.SetBorderSize(0)
    pave1.SetFillStyle(0)
    pave1.SetTextAlign(11)
    pave1.AddText("File name:")
    #pave.AddLine()
    pave1.AddText("Sensor thickness:")
    pave1.AddText("Strip width:")
    #pave.AddLine()
    pave1.AddText("Reference tan(#alpha):")
    pave1.AddText("Fitted tan(#alpha):")
    pave1.AddText("Fitted x-shift:")
    pave1.Draw()
    pave2 = ROOT.TPaveText(0.3,0.01,1-ROOT.gPad.GetRightMargin(),0.15,'brNDC')
    pave2.SetBorderSize(0)
    pave2.SetFillStyle(0)
    pave2.SetTextAlign(11)
    pave2.AddText(os.path.basename(infile))
    #pave.AddLine()
    pave2.AddText(str(args.thickness))
    pave2.AddText(str(args.stripWidth))
    #pave.AddLine()
    pave2.AddText("{:6.3f}".format(tanAlpha))
    pave2.AddText("{:6.3f}".format(sx/ns))
    pave2.AddText("{:6.1f}".format(sy/ns))
    pave2.Draw()
    cnvH.Update()

    if outFile!=None:
        cnvH.SaveAs(outFile+"_mt"+str(args.modType)+".pdf")
        
