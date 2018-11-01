#!/usr/bin/env python
import os
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import * 
from VBFHToInv.NanoAODTools.postprocessing.VBFHToInvModules import *

#this takes care of converting the input files from CRAB
from PhysicsTools.NanoAODTools.postprocessing.framework.crabhelper import inputFiles,runsAndLumis

modules = [ TriggerSelectionConstructor(),
            JetCleaningConstructor(),
            MetCleaningConstructor(),
            jecUncert_2017{block}_data(), ] # {block} is a kwarg replacement field, replaced in crab_cfg_creator with a proper value

p = PostProcessor('.', inputFiles(), modules=modules, provenance=True, fwkJobReport=True, jsonInput='Cert_294927-306462_13TeV_EOY2017ReReco_Collisions17_JSON_v1.txt')
p.run()

print "DONE"
os.system("ls -lR")

