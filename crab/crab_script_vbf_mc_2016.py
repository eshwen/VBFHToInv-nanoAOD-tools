#!/usr/bin/env python
import os
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor
from VBFHToInv.NanoAODTools.postprocessing.VBFHToInvModules import *

#this takes care of converting the input files from CRAB
from PhysicsTools.NanoAODTools.postprocessing.framework.crabhelper import inputFiles,runsAndLumis

modules = [ TriggerSelectionConstructor(),
            JetCleaningConstructor(), 
            MetCleaningConstructor(),
            #puWeight2016(), <-- need to figure out and define import in VBFHToInvModules.py
            btagSF2016(),
            jetmetUncertainties2016All() ]

p = PostProcessor(".", inputFiles(), modules=modules, provenance=True, fwkJobReport=True)
p.run()

print "DONE"
os.system("ls -lR")

