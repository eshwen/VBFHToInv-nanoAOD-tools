import argparse
from datetime import date
import os
import shutil
import sys


parser = argparse.ArgumentParser()
parser.add_argument("dataset_list", type=str, help="File containing list of datasets")
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('--data', action='store_true', help="Use this option if datasets are data")
group.add_argument('--mc',   action='store_true', help="Use this option if datasets are Monte Carlo")
args = parser.parse_args()

today = str(date.today()).replace('-', '')


def write_config(dataset, proc_era, year, dataMC, out_dir='configs_'+today):
    out_file = open( os.path.join(out_dir, proc_era+'.py'), 'w' )
    
    out_file.write("""
from CRABClient.UserUtilities import config, getUsernameFromSiteDB
from CRABAPI.RawCommand import crabCommand
import os

config = config()
config.General.requestName = '{request_name}'
config.General.transferLogs = True

config.JobType.pluginName = 'Analysis'
config.JobType.psetName = 'PSet.py'
config.JobType.scriptExe = 'crab_script_vbf_{dataMC}_{year}.sh'
config.JobType.inputFiles = ['crab_script_vbf_{dataMC}_{year}.py', os.environ['CMSSW_BASE']+'/src/PhysicsTools/NanoAODTools/scripts/haddnano.py', {json_file}] #hadd nano will not be needed once nano tools are in cmssw
config.JobType.sendPythonFolder = True

config.Data.inputDataset = '{dataset}'
#config.Data.inputDBS = 'phys03'
config.Data.inputDBS = 'global'
#config.Data.splitting = 'Automatic'
config.Data.splitting = 'EventAwareLumiBased'
config.Data.unitsPerJob = 50000
#config.Data.totalUnits = 1

config.Data.outLFNDirBase = '/store/user/ebhal/{file_out_dir}'
config.Data.publication = False
config.Site.storageSite = 'T2_UK_SGrid_Bristol'
""".format(request_name=proc_era, year=year, dataMC=dataMC, dataset=dataset, file_out_dir='CHIP_skim_bkg_test1',
    json_file=os.environ['CMSSW_BASE']+'/src/VBFHToInv/NanoAODTools/data/pileup/Cert_294927-306462_13TeV_EOY2017ReReco_Collisions17_JSON_v1.txt' if dataMC == 'data' else '')
    )
    
    out_file.close()
    
    print "CRAB config file written for {bold}{ds}{end}, stored in {bold}{dir}/{end}".format(ds=dataset, dir=out_dir, bold='\033[1m', end='\033[0m')


def main():
    """ Take in list of datasets and create CRAB config files for each """

    if not os.path.exists('configs_'+today):
        os.mkdir('configs_'+today)

    with open(args.dataset_list) as in_file:
        input_datasets = in_file.readlines()

    print "Running over datasets..."

    # Write identifier strings to use in CRAB config, then write
    for dataset in input_datasets:
        dataset = dataset.rstrip('\n')
        if args.mc:
            process = (dataset.split('_')[0] + '_' + dataset.split('_')[1]).replace('/', '')
            era = (dataset.split('/')[2]).split('_')[0]
            if '_ext' in dataset: era += '_ext' + dataset.split('_ext')[1].split('/')[0]
            proc_era = process + '_' + era
            if '/RunIISummer16NanoAOD' in dataset: year = 2016
            else: year = 2017
            write_config(dataset, proc_era, year, 'mc')

        elif args.data:
            process = dataset.split('/')[1]
            era = (dataset.split('/')[2]).split('_')[0]
            proc_era = process + '_' + era
            if 'Run2016' in dataset: year = 2016
            elif 'Run2017' in dataset: year = 2017
            else: sys.exit("Unknown data taking year in dataset. Are you sure it is data?")
            write_config(dataset, proc_era, year, 'data')


if __name__ == '__main__':
    main()