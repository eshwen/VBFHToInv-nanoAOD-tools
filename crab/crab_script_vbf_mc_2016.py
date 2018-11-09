#!/usr/bin/env python
import os
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor
from VBFHToInv.NanoAODTools.postprocessing.VBFHToInvModules import *

#this takes care of converting the input files from CRAB
from PhysicsTools.NanoAODTools.postprocessing.framework.crabhelper import inputFiles,runsAndLumis

modules = [ countHistogramsModule(),
            TriggerSelectionConstructor(),
            JetCleaningConstructor(), 
            MetCleaningConstructor(),
            puWeight2016(),
            btagSF2016(),
            #jetmetUncertainties2016All(),
            jecUncert_2016_MC(), ]

p = PostProcessor(".", inputFiles(), modules=modules, provenance=True, fwkJobReport=True)
p.run()

print "DONE"
os.system("ls -lR")

