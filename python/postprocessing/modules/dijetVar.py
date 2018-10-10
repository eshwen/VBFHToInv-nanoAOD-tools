import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection 
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

class DiJetVar(Module):
    def __init__(self, jetCollectionName):
        self.jetCollectionName = jetCollectionName
        pass
    def beginJob(self):
        pass
    def endJob(self):
        pass
    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        self.out.branch("leading_Mjj",  "F");
	self.out.branch("leading_dEtajj", "F");
        self.out.branch("leading_dPhijj", "F");

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass
    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
        jets = Collection(event, self.jetCollectionName)
        
        eventSum = ROOT.TLorentzVector()
        if (len(jets)>=2):
           eventSum += (jets[0].p4()+jets[1].p4())
           self.out.fillBranch("leading_Mjj",eventSum.M())
           self.out.fillBranch("leading_dPhijj", eventSum.Phi())
           self.out.fillBranch("leading_dEtajj", abs(eventSum.Eta()))
        else:
	   self.out.fillBranch("leading_Mjj",-1000)
           self.out.fillBranch("leading_dPhijj", -1000)
           self.out.fillBranch("leading_dEtajj", -1000)
        return True


# define modules using the syntax 'name = lambda : constructor' to avoid having them loaded when not needed

DiJetVariableConstructor = lambda : DiJetVar(jetCollectionName= "Jet") 
 
