import sys

def clusterEndPoints(xPos,tanTrack,tanLorentz,stripWidth,thickness):
    ''' Define entry/exit points of charge deposit.
        Arguments:
           xPos ........ position of track at sensor medium plane w.r.t. to lower edge of strip "0"
           tanTrack .... tan of track angle in the x-z plane (dx/dz)
           tanLorentz .. tan of the Lorentz angle
           stripWidth .. width of a strip
           thickness ... sensor (active) thickness
    '''
    # deltaX between track entry and exit points
    dt = thickness*tanTrack
    # displacement from Lorentz angle
    dl = thickness*tanLorentz
    # track exit point
    xs = xPos + dt/2.
    # track entry point projected to other side with tanLorentz
    xbs = xPos - dt/2. + dl
    # sort points
    x1 = min(xs,xbs)
    x2 = max(xs,xbs)

    return (x1,x2)

#def lineParameters(dx,tanLorentz,stripWidth,thickness):
#    result = ( None, None )
#    if 

#def drawLines(dx,tanLorentz,stripWidth,thickness,xmin,ymin,xmax,ymax):
#    #
#    #
#    #
#    for is in [ 1, -1 ]:
#        i = 0 if is==1 else -1
#        while True:
#            endY = False
#            for js in [ 1, -1 ]:
#                j = 0 if js==1 else -1
#                x0,dx = lineParameters(dx,tanLorentz,stripWidth,thickness)
            
def line_rectangle_intersections(k, d, xmin, ymin, xmax, ymax, tol=1e-12):
    """
    From ChatGPT
    Intersections of y = k*x + d with the border of the rectangle
    xmin <= x <= xmax, ymin <= y <= ymax.

    Returns a list of (x, y) tuples.
    """

    pts = []

    # Left edge: x = xmin
    y = k * xmin + d
    if ymin - tol <= y <= ymax + tol:
        pts.append((xmin, y))

    # Right edge: x = xmax
    y = k * xmax + d
    if ymin - tol <= y <= ymax + tol:
        pts.append((xmax, y))

    # Bottom edge: y = ymin
    if abs(k) > tol:
        x = (ymin - d) / k
        if xmin - tol <= x <= xmax + tol:
            pts.append((x, ymin))

    # Top edge: y = ymax
    if abs(k) > tol:
        x = (ymax - d) / k
        if xmin - tol <= x <= xmax + tol:
            pts.append((x, ymax))

    # Remove duplicates (corner intersections)
    unique = []
    for p in pts:
        if not any(abs(p[0] - q[0]) < tol and abs(p[1] - q[1]) < tol
                   for q in unique):
            unique.append(p)

    return unique

def lineParameters(stripNumber,stripIndex,stripWidth,thickness,tanLorentz,order,deltaPos=0):
    ''' Returns slopes and y0s of lines defined by beginning and end of charge deposit on a strip boundary.
        Coordinates are tan(track angle) (x) and position w.r.t. strip(y)
        Problem factorizes (parameters depend only on the number of either the first or the last strip).
        Arguments:
          stripNumber ... number of the strip defining begin or end (lower strip edge, indices starts at 0)
          stripIndex .... index defining whether the first strip (0) or the last strip (1) to be used
          stripWidth ....... width of a strip
          thickness ........ (active) thickness of sensor
          tanLorentz ....... tan of Lorentz angle
          order ............ sign(tan(track angle)-tanLorentz)
    '''
    assert order==-1 or order==1 
    assert stripIndex==0 or stripIndex==1

    print("deltaPos = ",deltaPos*thickness/2)
    if stripIndex==0:
        if order==1:
            k = thickness/2.
            return ( k, stripNumber*stripWidth-thickness*tanLorentz-deltaPos )
        else:
            k = -thickness/2.
            return ( k, stripNumber*stripWidth-deltaPos )
    else:
        if order==1:
            k = -thickness/2.
            return ( k, stripNumber*stripWidth-deltaPos )
        else:
            k = thickness/2.
            return ( k, stripNumber*stripWidth-thickness*tanLorentz-deltaPos )
        
    
def drawLines(stripWidth,thickness,tanLorentz,order,xmin,ymin,xmax,ymax,deltaPos=0):
    #
    #
    #
    #
    results = [ ]
    #
    # scan in positive and negative direction in x ( tan(track angle) )
    #
    for idir in [ 1, -1 ]:
        #
        # lines defined by start strip or end strip
        #
        for iend in [ 0, 1 ]:
            # strip number to start with
            i0 = 0 if idir==1 else -1
            #
            # loop until lines are outside plot area
            #
            while True:
                lpars = lineParameters(i0,iend,stripWidth,thickness,tanLorentz,order,deltaPos)
                print(idir,iend,i0,lpars)
                intersections = line_rectangle_intersections(*lpars,xmin,ymin,xmax,ymax)
                print("-",intersections)
                if len(intersections)==2:
                    results.append(intersections)
                    i0 += idir
                else:
                    break
    print("# results = ",len(results))
    return results

if __name__=="__main__":
    from array import array
    import ROOT
    import argparse

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--thickness', '-t', help="sensor thickness (in um)", type=float, default=200.)
    parser.add_argument('--nbPosX', help="number of bins for position", type=int, default=180)
    parser.add_argument('--stripWidth', '-w', help="strip width (in um)", type=float, default=90.)
    parser.add_argument('--refTanLorentzAngle',  help="tan Lorentz angle / B[T]", type=float, default=0.07)
    parser.add_argument('--bfield', '-b', help='B field [T]', type=float, default=3.8)
    parser.add_argument('--nbTanLambda', help="number of bins for tan(#lambda)", type=int, default=201)
    parser.add_argument('--maxTanLambda',  help="max. track dx/dz", type=float, default=2.01)
    parser.add_argument('--deltaX', help='offset for x position', type=float, default=0.)
    args = parser.parse_args()

    #thickness = 200     # sensor thickness in um
    #width = 90          # strip width in um
    #tanAlpha = 3.8*0.07 # tan(alpha) at 3.8T
    tanAlpha = args.bfield*args.refTanLorentzAngle

    ROOT.gStyle.SetOptStat(0)

    hw = ROOT.TH1F("hw","charge width;tan(#lambda);width [#mum]",args.nbTanLambda,-args.maxTanLambda,args.maxTanLambda)
    #hc = ROOT.TH2F("hc","cluster size;#x_0 [#mum];tan(#lambda)",args.nbPosX,0.,args.stripWidth, \
    #                args.nbTanLambda,-args.maxTanLambda,args.maxTanLambda)
    hc = ROOT.TH2F("hc","cluster size;tan(#lambda);#x_0 [#mum];cluster size",args.nbTanLambda,-args.maxTanLambda,args.maxTanLambda,args.nbPosX,0.,args.stripWidth)
    xcaxis = hc.GetXaxis()
    ycaxis = hc.GetYaxis()
    zcaxis = hc.GetZaxis()

    dl = args.thickness*tanAlpha
    for ibx in range(1,hc.GetNbinsX()+1):
        tanTrack = xcaxis.GetBinCenter(ibx)
        dt = args.thickness*tanTrack
        for iby in range(1,hc.GetNbinsY()+1):
            posx = ycaxis.GetBinCenter(iby) + args.deltaX
            ibin = hc.GetBin(ibx,iby)
            #xs = posx + dt/2.
            #xbs = posx - dt/2. + dl
            #x1 = min(xs,xbs)
            #x2 = max(xs,xbs)
            #x1,x2 = clusterEndPoints(posx,tanTrack,dl,args.stripWidth,args.thickness)
            x1,x2 = clusterEndPoints(posx,tanTrack,tanAlpha,args.stripWidth,args.thickness)
            if iby==1:
                hw.SetBinContent(ibx,x2-x1)
            #is1 = int(x1/args.stripWidth)
            #is2 = int(x2/args.stripWidth)
            is1 = round(x1/args.stripWidth-0.5)
            is2 = round(x2/args.stripWidth-0.5)
            hc.SetBinContent(ibin,is2-is1+1)
            #if (is2-is1+1)==6:
            #    print(posx,tanTrack)

    cnvW = ROOT.TCanvas("cWidth","cWidth",600,600)
    hw.Draw("cont")
    cnvW.Update()

    icmin = 1
    icmax = int(hc.GetMaximum()+0.1)
    hc.SetMinimum(icmin)
    hc.SetMaximum(icmax)
    print((icmax-icmin+1),0)
    zcaxis.SetNdivisions(10100+icmax-icmin,0)
    #zcaxis.CenterLabels(1)
    ROOT.gStyle.SetPalette(ROOT.kBird)

    cnvC = ROOT.TCanvas("cSize","cSize",600,600)
    hc.Draw("zcol")
    print(args.stripWidth,args.thickness,tanAlpha,1, \
                    hc.GetXaxis().GetXmin(),hc.GetYaxis().GetXmin(),
                    hc.GetXaxis().GetXmax(),hc.GetYaxis().GetXmax())
    limits = drawLines(args.stripWidth,args.thickness,tanAlpha,1, \
                        hc.GetXaxis().GetXmin(),hc.GetYaxis().GetXmin(),
                        hc.GetXaxis().GetXmax(),hc.GetYaxis().GetXmax())
    line0 = ROOT.TLine()
    line0.SetLineColor(1)
    line0.SetLineWidth(2)
    for p1,p2 in limits:
        line0.DrawLine(*p1,*p2)
    print(args.stripWidth,args.thickness,tanAlpha,1, \
                    hc.GetXaxis().GetXmin(),hc.GetYaxis().GetXmin(),
                    hc.GetXaxis().GetXmax(),hc.GetYaxis().GetXmax())
    limits = drawLines(args.stripWidth,args.thickness,tanAlpha,1, \
                        hc.GetXaxis().GetXmin(),hc.GetYaxis().GetXmin(),
                        hc.GetXaxis().GetXmax(),hc.GetYaxis().GetXmax())
    line1 = ROOT.TLine()
    line1.SetLineColor(2)
    line1.SetLineStyle(2)
    line1.SetLineWidth(2)
    for p1,p2 in limits:
        line1.DrawLine(*p1,*p2)
    cnvC.Update()
