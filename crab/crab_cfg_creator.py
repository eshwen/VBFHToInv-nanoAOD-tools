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
config_out_dir = os.path.join( os.getcwd(), 'configs_'+today )


class SuperDataset(object):
    """ Sets all parameters required for writing CRAB config file """
    def __init__(self, dataset):
        self.dataset = dataset
        if args.mc: self.dataMC = 'mc'
        elif args.data: self.dataMC = 'data'
        self.get_proc_era()
        self.get_year()
        self.get_job_params()
        if self.dataMC == 'data':
            self.get_run_block()
            self.get_json()

    def get_proc_era(self):
        if self.dataMC == 'data':
            process = self.dataset.split('/')[1]
            era = self.dataset.split('/')[2]
            self.proc_era = process + '_' + era
        elif self.dataMC == 'mc':
            if self.dataset.startswith('/DYJetsToLL'):
                process = (self.dataset.split('_')[0] + '_' + self.dataset.split('_')[1] + '_' + self.dataset.split('_')[2]).replace('/', '')
            else:
                process = (self.dataset.split('_')[0] + '_' + self.dataset.split('_')[1]).replace('/', '')
            era = (self.dataset.split('/')[2]).split('_')[0]
            if '_ext' in self.dataset:
                era += '_ext' + self.dataset.split('_ext')[1].split('/')[0]
            self.proc_era = process + '_' + era

    def get_year(self):
        if self.dataMC == 'data':
            if 'Run2016' in self.dataset: self.year = 2016
            elif 'Run2017' in self.dataset: self.year = 2017
            else: sys.exit("Unknown data taking year in dataset. Are you sure it is data?")
        elif self.dataMC == 'mc':
            if '/RunIISummer16NanoAOD' in self.dataset: self.year = 2016
            elif '/RunIIFall17NanoAOD' in self.dataset: self.year = 2017
            else: sys.exit("Unknown creation year in dataset. Are you sure it is valid MC?")

    def get_run_block(self):
        """ Get run block for data. Currently required because JEC uncertainties module splits run blocks """
        self.run_block = self.proc_era.split('-')[0]
        # JEC uncertainties grouped for 2016BCD
        if any(i in self.proc_era for i in ['2016B', '2016C', '2016D']):
            self.run_block = 'BCD'
        # JEC uncertainties grouped for 2016EF
        elif any(i in self.proc_era for i in ['2016E', '2016F']):
            self.run_block = 'EF'
        # All other JEC uncertainties are split by run block, so just take last character
        else:
            self.run_block = self.run_block[-1]

    def get_json(self):
        if self.year == 2016:
            self.json_file = os.path.join(os.environ['CMSSW_BASE'], 'src/VBFHToInv/NanoAODTools/data/pileup/Cert_271036-284044_13TeV_23Sep2016ReReco_Collisions16_JSON.txt')
        elif self.year == 2017:
            self.json_file = os.path.join(os.environ['CMSSW_BASE'], 'src/VBFHToInv/NanoAODTools/data/pileup/Cert_294927-306462_13TeV_EOY2017ReReco_Collisions17_JSON_v1.txt')

    def get_job_params(self):
        self.splitting = 'FileBased'
        self.unitsPerJob = 1


def write_config(sd, out_dir=config_out_dir):
    """ Copy extra files required for CRAB and write config file for dataset """
    # Supplementary files required for CRAB
    suppl = {'PSet': 'PSet.py',
             'crab_sh': 'crab_script_vbf_{dataMC}_{year}.sh'.format(dataMC=sd.dataMC, year=sd.year),
             'crab_py': 'crab_script_vbf_{dataMC}_{year}.py'.format(dataMC=sd.dataMC, year=sd.year),
    }
        
    # Copy files to output dir for self-containment and logging
    for key, val in suppl.iteritems():
        if 'crab' in key and sd.dataMC == 'data':
            with open(val, 'r') as in_file:
                old_str = in_file.read()
            new_str = old_str.format(block=sd.run_block)
            val = val.replace('.', sd.run_block+'.') # dirty way to append run_block onto files
            suppl[key] = val # update dictionary so new file is used
            with open( os.path.join(out_dir, val), 'w') as out_file:
                out_file.write(new_str)
                continue
        shutil.copy(val, out_dir)


    # Write config file
    out_file = open( os.path.join(out_dir, sd.proc_era+'.py'), 'w' )    
    out_file.write("""
from CRABClient.UserUtilities import config, getUsernameFromSiteDB
from CRABAPI.RawCommand import crabCommand
import os

config = config()
config.General.requestName = '{request_name}'
config.General.transferLogs = True

config.JobType.pluginName = 'Analysis'
config.JobType.psetName = '{PSet}'
config.JobType.scriptExe = '{crab_sh}'
config.JobType.inputFiles = ['{crab_py}', os.environ['CMSSW_BASE']+'/src/PhysicsTools/NanoAODTools/scripts/haddnano.py', {json}]
config.JobType.sendPythonFolder = True

config.Data.inputDataset = '{dataset}'
#config.Data.inputDBS = 'phys03'
config.Data.inputDBS = 'global'
#config.Data.splitting = 'Automatic'
config.Data.splitting = '{splitting}'
config.Data.unitsPerJob = {unitsPerJob}
#config.Data.totalUnits = 1

config.Data.outLFNDirBase = '/store/user/ebhal/{file_out_dir}'
config.Data.publication = False
config.Site.storageSite = 'T2_UK_SGrid_Bristol'
""".format(request_name=sd.proc_era, PSet=suppl['PSet'], crab_sh=suppl['crab_sh'], crab_py=suppl['crab_py'],
           dataset=sd.dataset, file_out_dir='CHIP_skim_bkg_test2', json='\'{}\''.format(sd.json_file) if sd.dataMC == 'data' else '',
           splitting=sd.splitting, unitsPerJob=sd.unitsPerJob
           )
    )
    out_file.close()
    
    print "CRAB config file written for {bold}{ds}{end}, stored in {bold}{dir}/{end}".format(ds=sd.dataset, dir=os.path.relpath(out_dir), bold='\033[1m', end='\033[0m')


def main():
    """ Take in list of datasets and create CRAB config files for each """

    if not os.path.exists(config_out_dir):
        os.mkdir(config_out_dir)

    with open(args.dataset_list) as in_file:
        input_datasets = in_file.readlines()

    print "Running over datasets..."

    # Write identifier strings to use in CRAB config, then write
    for dataset in input_datasets:
        if dataset.startswith('#') or dataset.startswith('\n'):
            continue
        dataset = dataset.rstrip('\n')
        super_dataset = SuperDataset(dataset)
        write_config(super_dataset)


if __name__ == '__main__':
    main()
