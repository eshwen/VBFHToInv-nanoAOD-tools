#!/usr/bin/env python
import os
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import * 
from VBFHToInv.NanoAODTools.postprocessing.VBFHToInvModules import *

#this takes care of converting the input files from CRAB
from PhysicsTools.NanoAODTools.postprocessing.framework.crabhelper import inputFiles,runsAndLumis

modules = [ TriggerSelectionConstructor(),
            JetCleaningConstructor(),
            MetCleaningConstructor(),
            jecUncert_2016{block}_data(), ] # BCD is a kwarg replacement field, replaced in crab_cfg_creator with a proper value

p = PostProcessor('.', inputFiles(), modules=modules, provenance=True, fwkJobReport=True, jsonInput='Cert_271036-284044_13TeV_23Sep2016ReReco_Collisions16_JSON.txt')
p.run()

print "DONE"
os.system("ls -lR")

