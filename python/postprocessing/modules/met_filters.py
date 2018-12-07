import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.tools import *

class MetFilters(Module):
    def __init__(self, year, data=False):
        self.year = year
        self.data = data

        self.common_flags = [
            "Flag_goodVertices",
            "Flag_globalSuperTightHalo2016Filter",
            "Flag_HBHENoiseFilter",
            "Flag_HBHENoiseIsoFilter",
            "Flag_EcalDeadCellTriggerPrimitiveFilter",
        ]

        self.flags_2016 = [
            #"Flag_BadChargedCandidateSummer16Filter", # unsure if needed
            #"Flag_BadPFMuonSummer16Filter", # unsure if needed
        ]
        self.flags_2016.extend(self.common_flags)

        self.flags_2017 = [
            "Flag_BadPFMuonFilter",
            "Flag_BadChargedCandidateFilter",
            #"ecalBadCalibReducedMINIAODFilter", # needs to be re-run in miniAOD
        ]
        self.flags_2017.extend(self.common_flags)

        self.data_flags = [
            "Flag_eeBadScFilter", # for 2016, available for nanoAODs produced from miniAODv2 and later
        ]

        if self.year == 2016:
            self.applied_flags = self.flags_2016
        elif self.year == 2017:
            self.applied_flags = self.flags_2017
        else:
            self.applied_flags = []

        if self.data:
            self.applied_flags.extend(self.data_flags)


    def beginJob(self):
        pass
    def endJob(self):
        pass
    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass


    def analyze(self, event):        
        """process event, return True (go to next module) or False (fail, go to next event)"""
        for filter in self.applied_flags:
            filter_branch = getattr(event, filter)
            if filter_branch != 1:
                return False
        return True


MetFilters2016MC = lambda : MetFilters(year=2016)
MetFilters2017MC = lambda : MetFilters(year=2017)
MetFilters2016Data = lambda : MetFilters(year=2016, data=True)
MetFilters2017Data = lambda : MetFilters(year=2017, data=True)
