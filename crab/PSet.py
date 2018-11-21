#this fake PSET is needed for local test and for crab to figure the output filename
#you do not need to edit it unless you want to do a local test using a different input file than
#the one marked below
import FWCore.ParameterSet.Config as cms
from file_lists_priv_prod.WplusH_2016_v1 import WplusH_file_list
from file_lists_priv_prod.WminusH_2016_v1 import WminusH_file_list
from file_lists_priv_prod.ZH_2016_v1 import ZH_file_list
from file_lists_priv_prod.ttH_2016_v1 import ttH_file_list

process = cms.Process('NANO')
process.source = cms.Source("PoolSource", fileNames = cms.untracked.vstring(),
#	lumisToProcess=cms.untracked.VLuminosityBlockRange("254231:1-254231:24")
)

process.source.fileNames = [
	#'/eos/user/a/amagnan/datatest.root' ##you can change only this line
    #'/eos/user/a/amagnan/EWKZ2Jets_ZToLL_12Apr2018_94X_nanoAOD_test.root'
]

# Extend list of files to process with corresponding file list
process.source.fileNames.extend(ttH_file_list)

process.output = cms.OutputModule("PoolOutputModule",
                                  fileName=cms.untracked.string('tree.root') 
                                  )
process.out = cms.EndPath(process.output)

