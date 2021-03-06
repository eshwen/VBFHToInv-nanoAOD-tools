#Import all the modules defined in /modules
import os

#adding specific VBF variables to the trees
from VBFHToInv.NanoAODTools.postprocessing.modules.dijetVar import DiJetVariableConstructor
from VBFHToInv.NanoAODTools.postprocessing.modules.jetMetmindphi import JetMetMinDPhiConstructor
from VBFHToInv.NanoAODTools.postprocessing.modules.MetCleaning import MetCleaningConstructor
from VBFHToInv.NanoAODTools.postprocessing.modules.lepSFProducer import lepSFtight2017, lepSFveto2017
from VBFHToInv.NanoAODTools.postprocessing.modules.jetCleaning import JetCleaningConstructor
from VBFHToInv.NanoAODTools.postprocessing.modules.trigger_selection import TriggerSelectionConstructor
from VBFHToInv.NanoAODTools.postprocessing.modules.met_filters import MetFilters2016MC, MetFilters2017MC, MetFilters2016Data, MetFilters2017Data

#btagging weights - give event weight automatically based on jets discri (so all working points automatically)
from PhysicsTools.NanoAODTools.postprocessing.modules.btv.btagSFProducer import btagSF2016, btagSF2017


#pu weight - data file is hardcoded !!!
from PhysicsTools.NanoAODTools.postprocessing.modules.common.puWeightProducer import puWeightProducer
pufile_data_2016 = "{}/src/VBFHToInv/NanoAODTools/data/pileup/RerecoData2016withSysts.root".format(os.environ['CMSSW_BASE'])
pufile_data_2017 = "{}/src/VBFHToInv/NanoAODTools/data/pileup/RerecoData2017withSysts.root".format(os.environ['CMSSW_BASE'])
puWeight2016 = lambda : puWeightProducer('auto', pufile_data_2016, "pu_mc", "pileup", verbose=False)
puWeight2017 = lambda : puWeightProducer('auto', pufile_data_2017, "pu_mc", "pileup", verbose=False)

#how to change data and MC files ??
#pufile_data2017="%s/src/VBFHToInv/NanoAODTools/python/postprocessing/data/pileup/pileup_Cert_294927-306462_13TeV_PromptReco_Collisions17_withVar.root" % os.environ['CMSSW_BASE']
#pufile_mcFall17="%s/src/VBFHToInv/NanoAODTools/python/postprocessing/data/pileup/" % os.environ['CMSSW_BASE']
#puWeight2017 = lambda : puWeightProducer(pufile_mcFall17,pufile_data2017,"pu_mc","pileup",verbose=False)

#lepton SF
#from PhysicsTools.NanoAODTools.postprocessing.modules.common.lepSFProducer import lepSF

from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jetmetUncertainties import jetmetUncertainties2016, jetmetUncertainties2017

from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jecUncertainties import jecUncertProducer
jec_uncerts = [ "SubTotalPileUp",
                "SubTotalRelative",
                "SubTotalPt",
                "SubTotalScale",
                "SubTotalAbsolute",
                "SubTotalMC",
                "Total", ]
jecUncert_2016_MC = lambda : jecUncertProducer('Summer16_23Sep2016V4_MC', jec_uncerts)
jecUncert_2017_MC = lambda : jecUncertProducer('Fall17_17Nov2017_V6_MC', jec_uncerts)
# Files from 2017 data already in nanoAOD-tools, but need to copy Summer16_23Sep2016*V3_DATA*.txt from cmgtools-lite/RootTools/data/jec/
jecUncert_2016BCD_data = lambda : jecUncertProducer('Summer16_23Sep2016BCDV3_DATA', jec_uncerts)
jecUncert_2016EF_data = lambda : jecUncertProducer('Summer16_23Sep2016EFV3_DATA', jec_uncerts)
jecUncert_2016G_data = lambda : jecUncertProducer('Summer16_23Sep2016GV3_DATA', jec_uncerts)
jecUncert_2016H_data = lambda : jecUncertProducer('Summer16_23Sep2016HV3_DATA', jec_uncerts)
jecUncert_2017B_data = lambda : jecUncertProducer('Fall17_17Nov2017B_V6_DATA', jec_uncerts)
jecUncert_2017C_data = lambda : jecUncertProducer('Fall17_17Nov2017C_V6_DATA', jec_uncerts)
jecUncert_2017D_data = lambda : jecUncertProducer('Fall17_17Nov2017D_V6_DATA', jec_uncerts)
jecUncert_2017E_data = lambda : jecUncertProducer('Fall17_17Nov2017E_V6_DATA', jec_uncerts)
jecUncert_2017F_data = lambda : jecUncertProducer('Fall17_17Nov2017F_V6_DATA', jec_uncerts)

from PhysicsTools.NanoAODTools.postprocessing.modules.common.countHistogramsModule import countHistogramsModule
