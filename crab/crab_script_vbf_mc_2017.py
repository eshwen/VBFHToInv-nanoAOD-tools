#!/usr/bin/env python
import os
import argparse
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor
import VBFHToInv.NanoAODTools.postprocessing.VBFHToInvModules as vbf

#this takes care of converting the input files from CRAB
from PhysicsTools.NanoAODTools.postprocessing.framework.crabhelper import inputFiles,runsAndLumis

modules = [
    vbf.TriggerSelectionConstructor(),
    vbf.JetCleaningConstructor(), # currently, this includes MET cleaning, dijet variables and jetMETMinDPhi
    vbf.puWeight2017(),
    vbf.btagSF2017(),
    vbf.lepSFtight2017(),
    vbf.lepSFveto2017(),
    vbf.jetmetUncertainties2017(),
    vbf.jecUncert_2017_MC(),
    ]

p = PostProcessor(".", inputFiles(), modules=modules, provenance=True, fwkJobReport=True)
p.run()

print "DONE"
os.system("ls -lR")

