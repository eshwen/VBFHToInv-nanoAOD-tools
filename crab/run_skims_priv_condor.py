#!/usr/bin/env python
import argparse
from datetime import date
import os
import shutil
from subprocess import call
import sys

today = str(date.today()).replace('-', '')

parser = argparse.ArgumentParser()
parser.add_argument("file", type=str, help="File containing list of privately-produced nanoAODs")
parser.add_argument("year", type=int, help="Data-taking year that dataset is emulating")
parser.add_argument("-o", "--outdir", type=str, default='private_skims_output_'+today, help="Output directory for storing skimmed files")
args = parser.parse_args()


def write_submission_script(sub_out_dir, year):
    """
    Write the HTCondor submission script.
    """

    exec_file = write_executable(sub_out_dir, year)

    job_path = os.path.abspath( os.path.join(sub_out_dir, 'condor_job.job') )
    job_file = open(job_path, 'w')
    job_file.write("""# HTCondor submission script
Universe   = vanilla
executable = {executable}
Log        = {sub_out_dir}/logs/condor_job.log
Output     = {sub_out_dir}/logs/condor_job.out
Error      = {sub_out_dir}/logs/condor_job.error
getenv     = True
should_transfer_files   = YES
when_to_transfer_output = ON_EXIT_OR_EVICT
use_x509userproxy = true
# Resource requests (disk storage in kB, memory in MB)
request_cpus = 1
# Disk request size determined by n_events
request_disk = 1000000
request_memory = 2000
# Max runtime (seconds)
+MaxRuntime = 7200
# Number of instances of job to run
queue 1
""".format(executable=exec_file, sub_out_dir=os.path.abspath(sub_out_dir), year=year)
    )
    job_file.close()

    # Make submission script executable
    call('chmod +x {0}'.format(job_path), shell=True)
    return job_path


def write_executable(sub_out_dir, year):
    """ 
    Write the script that is executed by the HTCondor job. Sets up the CMSSW environment properly to allow
    PYTHONPATH and other environment variables to be configured. Makes sure the commands run as they should.
    """
    exec_path = os.path.abspath( os.path.join(sub_out_dir, 'exec.sh') )
    exec_file = open(exec_path, 'w')
    exec_file.write("""#!/bin/bash
cd {CMSSW_BASE}/src
eval `scramv1 runtime -sh`
#scram b
cd {sub_out_dir}
python crab_script_vbf_mc_{year}.py 1
""".format(CMSSW_BASE=os.environ['CMSSW_BASE'], sub_out_dir=os.path.abspath(sub_out_dir), year=year)
    )
    call('chmod +x {0}'.format(exec_path), shell=True)
    return exec_path


def main():
    year = args.year
    out_dir = os.path.join( args.outdir, os.path.splitext(os.path.basename(args.file))[0] )

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    else:
        sys.exit("Not overwriting current output dir. Please either remove the output directory or give a different location with the '--outdir' option and try again.")

    if args.file.endswith('.txt'):
        with open(args.file) as reading:
            input_files = reading.readlines()
    else:
        sys.exit("File with .txt extension required")

    if not 'X509_USER_PROXY' in os.environ:
        sys.exit("""Because of the nuances of HTCondor, you need to initialise a proxy of your grid certificate somewhere HTCondor has access to (i.e., on /afs).
Run the following commands before attempting to execute this script again:
export X509_USER_PROXY=/afs/cern.ch/user/${USER:0:1}/${USER}/x509up_u${UID}
voms-proxy-init --voms cms --valid 168:00""")

    # Copy PSet script with replacement fields to output 
    pset_template_file = os.path.join(out_dir, 'PSet.py')
    shutil.copy('PSet_condor.py', pset_template_file)

    for i, file in enumerate(input_files):
        if file.startswith('#') or file.startswith('\n'):
            continue
        if not file.startswith('root://'):
            sys.exit("Files require xrootd redirector as a prepend")
        file = file.rstrip('\n')
        # Create an output subdirectory for each file/job
        sub_out_dir = os.path.join(out_dir, 'output_'+str(i))
        if not os.path.exists( os.path.join(sub_out_dir, 'logs') ):
            os.makedirs( os.path.join(sub_out_dir, 'logs') )
        else:
            print "Sub-output directory {} already exists. Overwriting...".format(sub_out_dir)
        # Copy main executable to subdirectory
        shutil.copy('crab_script_vbf_mc_{}.py'.format(year), sub_out_dir)
        # Fill replacement field in PSet script with necessary info and copy output string to file in subdirectory
        pset_file = open(pset_template_file, 'r')
        pset_str = pset_file.read()
        pset_str = pset_str.format(input_file=file)
        pset_out_file = open( os.path.join(sub_out_dir, 'PSet.py'), 'w')
        pset_out_file.write(pset_str)
        # Write Condor job file to execute
        job_file = write_submission_script(sub_out_dir, year)
        print "Submitting job {}...".format(i+1)
        call('condor_submit {}'.format(job_file), shell=True)

    print "All jobs submitted. Monitor with 'condor_q $USER'"


if __name__ == '__main__':
    main()
