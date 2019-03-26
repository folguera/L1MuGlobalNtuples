#!/bin/python 

# import ROOT in batch mode
from ROOT import *
from multiprocessing import Pool
from array import array
from copy import deepcopy

import sys,os
import argparse
import math
import ROOT

from setTDRStyle import setTDRStyle

oldargv = sys.argv[:]
sys.argv = [ '-b-' ]
gROOT.SetBatch(True)
sys.argv = oldargv

INPUTFILENAME=""
OUTPUTFILENAME=""

### ----  convert hw values to numbers that do make sense --- ###
def ptvalue(pt):
    return (pt-1.)/2.

def etavalue(eta):
    return eta/240.*2.61

def modulo2PI(phi): 
    while phi > 2*math.pi:
        phi = phi - 2*math.pi
    while phi < 0.:  
        phi = phi + 2*math.pi

    return phi

def phivalue(phi, processor): 
    return modulo2PI( ( (15.+processor*60.)/360. + phi/576. ) *2*math.pi) 

def chargevalue(charge):
    return pow(-1,charge)

def printprogress(nevents, i):
    ''' Prints some output from time to time... '''
    if int(i) % int(1000) == 0:
        print 'Processing... %i / %i (%1.2f'%(i,nevents, (float(i))/nevents*100) + '%)'


def readtree(treename="L1MuGlobalNtupleMaker/mytree"): 
    
    ## CREATING HISTOGRAMS:
    h_genmu_pt  = TH1F("h_genmu_pt" , "Gen Muon p_{T};gen #mu p_{T}", 100, 0., 100.)
    h_genmu_eta = TH1F("h_genmu_eta", "Gen Muon #eta;gen #mu #eta", 32, -1.6, 1.6)
    h_genmu_phi = TH1F("h_genmu_phi", "Gen Muon #phi;gen #mu #phi", 30, -math.pi, math.pi)
    h_genmu_dxy = TH1F("h_genmu_dxy", "Gen Muon d_{xy};gen #mu d_{xy}", 20, 0., 10.)

    h_omtfmu_pt  = TH1F("h_omtfmu_pt",  "L1 Muon p_{T};L1 #mu p_{t}"  , 100, 0., 100.)
    h_omtfmu_eta = TH1F("h_omtfmu_eta", "L1 Muon #eta;L1 #mu #eta", 32, -1.6, 1.6)
    h_omtfmu_phi = TH1F("h_omtfmu_phi", "L1 Muon #phi;L1 #mu #phi", 30, 0., 2*math.pi)

    heff_omtfVsgenmu_pt  = TEfficiency("heff_omtfVsgenmu_pt",  "Efficiency vs Muon p_{T};gen #mu p_{T}"  , 100, 0., 100.)
    heff_omtfVsgenmu_eta = TEfficiency("heff_omtfVsgenmu_eta", "Efficiency vs Muon #eta;gen #mu #eta", 32, -1.6, 1.6)
    heff_omtfVsgenmu_phi = TEfficiency("heff_omtfVsgenmu_phi", "Efficiency vs Muon #phi;gen #mu #phi", 30, -math.pi, math.pi)
    heff_omtfVsgenmu_dxy = TEfficiency("heff_omtfVsgenmu_dxy", "Efficiency vs Muon d_{xy};gen #mu d_{xy}", 20, 0., 10.)
    
    _file = ROOT.TFile(INPUTFILENAME)
    _tree = _file.Get(treename)
    
    for num,evt in enumerate(_tree):
        printprogress(_tree.GetEntriesFast(),num)
        # Now you have acess to the leaves/branches of each entry in the tree, e.g.

        for gp in range(evt.genmu_Nmuons):
            h_genmu_pt.Fill(evt.genmu_pt[gp])
            h_genmu_eta.Fill(evt.genmu_eta[gp])
            h_genmu_phi.Fill(evt.genmu_phi[gp])
            h_genmu_dxy.Fill(evt.genmu_dxy[gp])
        
        for mu in range(evt.omtfmu_Nmuons):
            glbpt  = ptvalue(evt.omtfmu_hwpt[mu])
            glbeta = etavalue(evt.omtfmu_hweta[mu])
            glbphi = phivalue(evt.omtfmu_hwphi[mu],evt.omtfmu_processor[mu])
            
            omtfmu = TLorentzVector(glbpt,glbeta,glbphi,0.1056583745)
            
            if evt.omtfmu_hwqual[mu] < 11: continue
            h_omtfmu_pt.Fill(glbpt)
            h_omtfmu_eta.Fill(glbeta)
            h_omtfmu_phi.Fill(glbphi)
            
            # reading gen muons
            match = False
            for gp in range(evt.genmu_Nmuons):
                genmu = TLorentzVector(evt.genmu_pt[gp],evt.genmu_eta[gp],evt.genmu_phi[gp],0.1056583745)

                if omtfmu.DeltaR(genmu) < 0.5 and omtfmu.Pt()>25.: 
                    match = True
                    ## found match, break loop
                    break
                
            heff_omtfVsgenmu_pt .Fill(match,evt.genmu_pt[gp] )
            heff_omtfVsgenmu_eta.Fill(match,evt.genmu_eta[gp])
            heff_omtfVsgenmu_phi.Fill(match,evt.genmu_phi[gp])
            heff_omtfVsgenmu_dxy.Fill(match,evt.genmu_dxy[gp])

            
    ## NOW save all the histograms inside a root file for future post-processing
    _ofile = TFile(OUTPUTFILENAME,"RECREATE")
    _ofile.cd()
    h_genmu_pt  .Write()
    h_genmu_eta .Write()
    h_genmu_phi .Write()
    h_genmu_dxy .Write()

    h_omtfmu_pt  .Write()
    h_omtfmu_eta .Write()
    h_omtfmu_phi .Write()

    heff_omtfVsgenmu_pt  .Write()
    heff_omtfVsgenmu_eta .Write()
    heff_omtfVsgenmu_dxy .Write()
    heff_omtfVsgenmu_phi .Write()

    _ofile.Write()


def drawHisto(histo,outpath):
    c1 = TCanvas("c1","c1",700,700)
    c1.cd()
    
    histo.Draw()
    gPad.Update()
    if "eff" in histo.GetName(): 
        graph = histo.GetPaintedGraph()
        graph.SetMinimum(0.)
        graph.SetMaximum(1.1)
        gPad.Update()

    latex = ROOT.TLatex()
    latex.SetTextFont(42)
    latex.SetTextAlign(31)
    latex.SetTextSize(0.04)
    latex.SetNDC(True)
    latexCMS = ROOT.TLatex()
    latexCMS.SetTextFont(61)
    latexCMS.SetTextSize(0.055)
    latexCMS.SetNDC(True)
    latexCMSExtra = ROOT.TLatex()
    latexCMSExtra.SetTextFont(52)
    latexCMSExtra.SetTextSize(0.03)
    latexCMSExtra.SetNDC(True)
    
    latex.DrawLatex(0.95, 0.96, "(14 TeV)")
    cmsExtra = "Simulation" #splitline{Simulation}{Preliminary}"
    latexCMS.DrawLatex(0.19,0.88,"CMS")
    yLabelPos = 0.84
    latexCMSExtra.DrawLatex(0.19,yLabelPos,"%s"%(cmsExtra))
    
    ROOT.gPad.Update()

    saveas = histo.GetName()
    c1.SaveAs(outpath+saveas+".png")
    c1.SaveAs(outpath+saveas+".pdf")
    c1.SaveAs(outpath+saveas+".root")
    c1.SaveAs(outpath+saveas+".C")
    
    c1.Close()

def makeplots(rootfile,outdir): 
    os.system("cp %s %s/%s" %(rootfile,outdir,rootfile))
    _file = TFile(rootfile)     
    _file.cd()
    
    style = setTDRStyle()
    ROOT.gStyle.SetTitleYOffset(1.45)
    ROOT.gStyle.SetTitleXOffset(1.45)
    ROOT.gStyle.SetOptFit(0)
    ROOT.gStyle.SetStatX(.9)
    ROOT.gStyle.SetStatY(.9)

    dirList = gDirectory.GetListOfKeys()
    for k1 in dirList: 
        h1 = k1.ReadObj()
        if h1.InheritsFrom("TH1") or h1.InheritsFrom("TEfficiency"):
            drawHisto(h1,outdir)
   
    
    
        
        
        
        
        
    
#### ========= MAIN =======================
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(usage="readtree.py [options]",description="",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("-i", "--ifile", dest="inputFileName", help='Input filename',required=True)
    parser.add_argument("-t", dest="treename",default="L1MuGlobalNtupleMaker/mytree", help='Tree name')
    parser.add_argument("-o","--ofile",dest="outputFileName", default="outplots.root", help='Output filename')
    parser.add_argument("-odir", dest="outdir", default="plots/", help='Output folder')
    args = parser.parse_args()

    INPUTFILENAME  = args.inputFileName
    OUTPUTFILENAME = args.outputFileName   
    
    print "Reading tree..."
    readtree(args.treename) 

    print "Now plotting everything"
    if not os.path.exists(args.outdir):
        os.mkdir(args.outdir)
        print "cp ~folguera/public/utils/index.php %s/" %args.outdir
        os.system("cp ~folguera/public/utils/index.php %s/" %args.outdir)
    makeplots(args.outputFileName,args.outdir)
    
    

