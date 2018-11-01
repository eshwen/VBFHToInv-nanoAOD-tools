#!/usr/bin/env python
import os
import argparse
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor
from VBFHToInv.NanoAODTools.postprocessing.VBFHToInvModules import *

#this takes care of converting the input files from CRAB
from PhysicsTools.NanoAODTools.postprocessing.framework.crabhelper import inputFiles,runsAndLumis

modules = [ TriggerSelectionConstructor(),
            JetCleaningConstructor(), 
            MetCleaningConstructor(), 
            puWeight2017(),
            btagSF2017(),
            #jetmetUncertainties2017All(),
            jecUncert_2017_MC(), ]

p = PostProcessor(".", inputFiles(), modules=modules, provenance=True, fwkJobReport=True)
p.run()

print "DONE"
os.system("ls -lR")

