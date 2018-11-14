from WMCore.Configuration import Configuration
from CRABClient.UserUtilities import config, getUsernameFromSiteDB
from CRABAPI.RawCommand import crabCommand
from CRABClient.ClientExceptions import ClientException
from httplib import HTTPException
import os

config = Configuration()

# Declare dataset, then define variables to create unique identifiers for CRAB jobs
dataset = '/QCD_HT500to700_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16NanoAOD-PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2-v1/NANOAODSIM'
process = (dataset.split('_')[0] + '_' + dataset.split('_')[1]).replace('/', '')
era = (dataset.split('/')[2]).split('_')[0]
if 'Summer16NanoAOD' in dataset: year = 2016
elif 'Fall17NanoAOD' in dataset: year = 2017
crab_py_script = 'crab_script_vbf_mc_{}.py'.format(year)

config.section_("General")
config.General.requestName = process+era
config.General.transferLogs=True
config.section_("JobType")
config.JobType.pluginName = 'Analysis'
config.JobType.psetName = 'PSet.py'
config.JobType.scriptExe = 'crab_script_vbf_mc_{}.sh'.format(year)
config.JobType.inputFiles = [crab_py_script, os.environ['CMSSW_BASE']+'/src/PhysicsTools/NanoAODTools/scripts/haddnano.py'] #hadd nano will not be needed once nano tools are in cmssw
config.JobType.sendPythonFolder	 = True
config.section_("Data")
config.Data.inputDataset = dataset
#config.Data.inputDBS = 'phys03'
config.Data.inputDBS = 'global'
#config.Data.splitting = 'Automatic'
config.Data.splitting = 'EventAwareLumiBased'
config.Data.unitsPerJob = 1000
config.Data.totalUnits = 1

config.Data.outLFNDirBase = '/store/user/ebhal/CHIP_skim_test_1'
config.Data.publication = False
#config.Data.outputDatasetTag = 'NanoTestPost'
config.section_("Site")
config.Site.storageSite = "T2_UK_SGrid_Bristol"

#config.Site.storageSite = "T2_CH_CERN"
#config.section_("User")
#config.User.voGroup = 'dcms'

#try:
#    crabCommand('submit', config=config)
#except HTTPException as hte:
#    print "Failed submitting task: %s" % (hte.headers)
#except ClientException as cle:
#    print "Failed submitting task: %s" % (cle)
