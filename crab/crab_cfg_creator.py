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


def write_config(dataset, proc_era, year, dataMC, out_dir=config_out_dir):
    """ Copy extra files required for CRAB and write config file for dataset """
    # Supplementary files required for CRAB
    suppl = {'PSet': 'PSet.py',
             'crab_sh': 'crab_script_vbf_{dataMC}_{year}.sh'.format(dataMC=dataMC, year=year),
             'crab_py': 'crab_script_vbf_{dataMC}_{year}.py'.format(dataMC=dataMC, year=year),
    }

    # Get run block for data. Currently required because JEC uncertainties module splits run blocks
    if dataMC == 'data':
        run_block = get_run_block(proc_era)
        
    # Copy files to output dir for self-containment and logging
    for key, val in suppl.iteritems():
        if 'crab' in key and dataMC == 'data':
            with open(val, 'r') as in_file:
                old_str = in_file.read()
            new_str = old_str.format(block=run_block)
            val = val.replace('.', run_block+'.') # dirty way to append run_block onto files
            suppl[key] = val # update dictionary so new file is used
            with open( os.path.join(out_dir, val), 'w') as out_file:
                out_file.write(new_str)
                continue
        shutil.copy(val, out_dir)

    if year == 2016:
        json_file = os.path.join(os.environ['CMSSW_BASE'], 'src/VBFHToInv/NanoAODTools/data/pileup/Cert_271036-284044_13TeV_23Sep2016ReReco_Collisions16_JSON.txt')
    elif year == 2017:
        json_file = os.path.join(os.environ['CMSSW_BASE'], 'src/VBFHToInv/NanoAODTools/data/pileup/Cert_294927-306462_13TeV_EOY2017ReReco_Collisions17_JSON_v1.txt')

    # Write config file
    out_file = open( os.path.join(out_dir, proc_era+'.py'), 'w' )    
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
config.Data.splitting = 'EventAwareLumiBased'
config.Data.unitsPerJob = 50000
#config.Data.totalUnits = 1

config.Data.outLFNDirBase = '/store/user/ebhal/{file_out_dir}'
config.Data.publication = False
config.Site.storageSite = 'T2_UK_SGrid_Bristol'
""".format(request_name=proc_era, PSet=suppl['PSet'], crab_sh=suppl['crab_sh'], crab_py=suppl['crab_py'],
           dataset=dataset, file_out_dir='CHIP_skim_bkg_test1', json='{}'.format(json_file) if dataMC == 'data' else '')
    )
    out_file.close()
    
    print "CRAB config file written for {bold}{ds}{end}, stored in {bold}{dir}/{end}".format(ds=dataset, dir=os.path.relpath(out_dir), bold='\033[1m', end='\033[0m')
    

def get_run_block(proc_era):
    """ Get run block for data. Currently required because JEC uncertainties module splits run blocks """
    run_block = proc_era.split('-')[0]
    # JEC uncertainties grouped for 2016BCD
    if any(i in proc_era for i in ['2016B', '2016C', '2016D']):
        run_block = 'BCD'
    # JEC uncertainties grouped for 2016EF
    elif any(i in proc_era for i in ['2016E', '2016F']):
        run_block = 'EF'
    # All other JEC uncertainties are split by run block, so just take last character
    else:
        run_block = run_block[-1]
    return run_block


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
            era = dataset.split('/')[2]
            proc_era = process + '_' + era
            if 'Run2016' in dataset: year = 2016
            elif 'Run2017' in dataset: year = 2017
            else: sys.exit("Unknown data taking year in dataset. Are you sure it is data?")
            write_config(dataset, proc_era, year, 'data')


if __name__ == '__main__':
    main()
