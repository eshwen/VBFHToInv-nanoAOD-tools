#!/usr/bin/env python
import os
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor
import VBFHToInv.NanoAODTools.postprocessing.VBFHToInvModules as vbf

#this takes care of converting the input files from CRAB
from PhysicsTools.NanoAODTools.postprocessing.framework.crabhelper import inputFiles,runsAndLumis

modules = [ 
    vbf.TriggerSelectionConstructor(),
    vbf.MetFilters2016Constructor(),
    vbf.JetCleaningConstructor(), # currently, this includes MET cleaning, dijet variables and jetMETMinDPhi
    vbf.puWeight2016(),
    vbf.btagSF2016(),
    vbf.jetmetUncertainties2016(),
    vbf.jecUncert_2016_MC(),
    ]

p = PostProcessor(".", inputFiles(), modules=modules, provenance=True, fwkJobReport=True)
p.run()

print "DONE"
os.system("ls -lR")

