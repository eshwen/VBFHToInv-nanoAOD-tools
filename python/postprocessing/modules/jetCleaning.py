import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection 
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.tools import *

class JetCleaning(Module):
    def __init__(self, jetCollectionName, lepMCollectionName, lepECollectionName, photonCollectionName, outCollectionName, dR_min):
        self.jetCollectionName = jetCollectionName
        self.lepECollectionName = lepECollectionName
        self.lepMCollectionName = lepMCollectionName
        self.photonCollectionName = photonCollectionName
        self.outCollectionName = outCollectionName
        self.dR_min = dR_min
        pass
    def beginJob(self):
        pass
    def endJob(self):
        pass
    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        self.out.branch(self.outCollectionName+"_pt", "F", lenVar ="n"+self.outCollectionName);
        self.out.branch(self.outCollectionName+"_eta", "F", lenVar ="n"+self.outCollectionName);
        self.out.branch(self.outCollectionName+"_phi", "F", lenVar ="n"+self.outCollectionName);
        self.out.branch(self.outCollectionName+"_mass", "F", lenVar ="n"+self.outCollectionName);

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass
    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
        jets = Collection(event, self.jetCollectionName)
        muons = Collection(event, self.lepMCollectionName)
        electrons = Collection(event, self.lepECollectionName)
        photons = Collection(event, self.photonCollectionName)
        cleanJets_pt = []
        cleanJets_eta = []
        cleanJets_phi = []
        cleanJets_mass = []

        for jet in jets:
  	   test = True
           for muon in muons:
	      if (deltaR(jet.eta, jet.phi, muon.eta, muon.phi)< self.dR_min):
                 test =False 
           for electron in electrons:
              if (deltaR(jet.eta, jet.phi, electron.eta, electron.phi)< self.dR_min):
                 test =False
           for photon in photons:
              if (deltaR(jet.eta, jet.phi, photon.eta, photon.phi)< self.dR_min):
                 test =False
           if test:
             cleanJets_pt.append(jet.pt)
             cleanJets_eta.append(jet.eta)
             cleanJets_phi.append(jet.phi)
             cleanJets_mass.append(jet.mass) 
        
        self.out.fillBranch(self.outCollectionName+"_pt", cleanJets_pt)
        self.out.fillBranch(self.outCollectionName+"_eta", cleanJets_eta)
	self.out.fillBranch(self.outCollectionName+"_phi", cleanJets_phi)
        self.out.fillBranch(self.outCollectionName+"_mass", cleanJets_mass)
        return True


# define modules using the syntax 'name = lambda : constructor' to avoid having them loaded when not needed

JetCleaningConstructor = lambda : JetCleaning(jetCollectionName= "Jet", lepMCollectionName = 'Muon', lepECollectionName = 'Electron', photonCollectionName = 'Photon', outCollectionName = "CleanJet", dR_min = 0.4) 
 
