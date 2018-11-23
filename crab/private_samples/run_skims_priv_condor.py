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

    # Absolute paths required for Condor jobs
    if not os.path.isabs(sub_out_dir):
        sub_out_dir = os.path.abspath(sub_out_dir)

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
""".format(executable=exec_file, sub_out_dir=sub_out_dir, year=year)
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
    # Make script executable
    call('chmod +x {0}'.format(exec_path), shell=True)
    return exec_path


def write_consolidation_script(output_dir, n_jobs):
    """ Write script to consolidate output files together """
    consol_path = os.path.join(output_dir, 'consolidate_files.sh')
    consol_file = open(consol_path, 'w')
    consol_file.write("""#!/bin/bash
n_files_expected={n_files}
mkdir all_output_files

for sub_dir in $(ls -d output*/); do
    cd $sub_dir
    if [ ! -r *.root ]; then
        echo "Found no output file in $sub_dir"
        echo "Resubmit with $(tput bold)condor_submit $sub_dir/condor_job.job$(tput sgr0) or $(tput bold)cd $sub_dir; ./exec.sh; cd -$(tput sgr0)"
    fi
    cd ..
done

mv output*/*.root ./all_output_files/

n_files_observed=$(ls -l ./all_output_files/*.root | wc -l)
if [ $n_files_expected -eq $n_files_observed ]; then
    echo "Number of skimmed files does not equal number of input files. Expected $n_files_expected, found $n_files_observed. Check the logs for job failures."
fi
""".format(n_files=n_jobs)
    )
    # Make script executable
    call('chmod +x {0}'.format(consol_path), shell=True)


def main():
    year = args.year
    out_dir = os.path.join( args.outdir, os.path.splitext(os.path.basename(args.file))[0] )
    if not os.path.isabs(out_dir):
        out_dir = os.path.abspath(out_dir)

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    else:
        sys.exit("Not overwriting current output dir. Please either remove the output directory or give a different location with the '--outdir' option and try again.")

    if args.file.endswith('.txt'):
        with open(args.file) as reading:
            input_files = reading.readlines()
    else:
        sys.exit("File with .txt extension required")

    n_jobs = len( filter(lambda x: x.startswith('root://'), input_files) )

    if not 'X509_USER_PROXY' in os.environ:
        sys.exit("""Because of the nuances of HTCondor, you need to initialise a proxy of your grid certificate somewhere HTCondor has access to (i.e., on /afs).
Run the following commands before attempting to execute this script again:
export X509_USER_PROXY=/afs/cern.ch/user/${USER:0:1}/${USER}/x509up_u${UID}
voms-proxy-init --voms cms --valid 168:00""")

    # Copy PSet script with replacement fields to output 
    pset_template_file = os.path.join(out_dir, 'PSet.py')
    shutil.copy('../PSet_condor.py', pset_template_file)

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
        shutil.copy('../crab_script_vbf_mc_{}.py'.format(year), sub_out_dir)
        # Fill replacement field in PSet script with necessary info and copy output string to file in subdirectory
        pset_file = open(pset_template_file, 'r')
        pset_str = pset_file.read()
        pset_str = pset_str.format(input_file=file)
        pset_out_file = open( os.path.join(sub_out_dir, 'PSet.py'), 'w')
        pset_out_file.write(pset_str)
        # Write Condor job file to execute
        job_file = write_submission_script(sub_out_dir, year)
        print "Submitting job {}/{}...".format(i+1, n_jobs)
        call('condor_submit {}'.format(job_file), shell=True)

    print "All jobs submitted. Monitor with 'condor_q $USER'"
    write_consolidation_script(out_dir, n_jobs)


if __name__ == '__main__':
    main()

# To do:
# - Try to catch errors better in consolidation script. Loop over output subdirectories, check the _condor_stderr file and look for some keywords regarding failing. If present, delete skimmed .root file (if there) and give command to resubmit Condor job.
