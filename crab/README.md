# Table of contents
1. [Running skims on nanoAOD datasets](#introduction)
2. [Setting up the environment (general)](#settingupenv)
3. [Running with CRAB (recommended for public datasets)](#runningCRAB)
    - [Setting up the CRAB configs](#settingCRABconfigs)
    - [Submitting jobs](#submittingCRABjobs)
    - [Monitoring](#monitoringCRABjobs)
4. [Extending the skims](#extendingskims)
5. [Running with HTCondor](#runningCondor)
    - [Running the skims](#runningjobsCondor)
    - [Transferring the output files](#transferringfilesCondor)
6. [To do](#todo)


# Running skims on nanoAOD datasets <a name="introduction"></a>

We run skims over the nanoAOD datasets we intend to use in the analysis. This helps reduce the overall footprint for each dataset, allowing us to store the output files at Bristol (or another "local" server), removing the I/O bottleneck when running over the files for analysis studies.



## Setting up the environment (general) <a name="settingupenv"></a>

If you're reading this, you should have already set up CMSSW, nanoAOD-tools and VBFHtoInv-nanoAOD-tools, which are required for running the skims. If not, follow the instructions in the README at https://github.com/eshwen/VBFHToInv-nanoAOD-tools, replacing instances of `vukasinmilosevic` with `eshwen` when cloning the repositories. This ensures you check out the most up-to-date version of everything that is maintained in this README. Make sure to compile the code with `scram b -j 8` initially, from the directory `CMSSW_10_2_5/src/`, and whenever you add/change C++ code.

**If you plan to run the skims only with CRAB, it shouldn't matter on which remote server you clone everything. However, if you plan to run with Condor, the code only works on lxplus at the moment.**

Then in each new session, you should run

```bash
cd <top_dir>/CMSSW_10_2_5/src
cmsenv
source /cvmfs/cms.cern.ch/crab3/crab.sh
export X509_USER_PROXY=/afs/cern.ch/user/${USER:0:1}/${USER}/x509up_u${UID} # if you plan to run skims with HTCondor
voms-proxy-init --voms cms --valid 168:00
cd VBFHToInv/NanoAODTools/crab
```

which also sets up the CRAB environment for job submission/monitoring and initialises a proxy of your grid certificate (required for interacting with the CERN LCG).

**Note: As above and in the following, in case you're unfamiliar, you should replace the contents enclosed by angle brackets by the value/expression they're implying. For example `<top_dir>` should be replaced by the top directory where you set up all the code.**



## Running with CRAB (recommended for public datasets) <a name="runningCRAB"></a>

### Setting up the CRAB configs <a name="settingCRABconfigs"></a>

The first step is to create a configuration file that can be sent to CRAB (CMS Remote Analysis Builder), which tells the grid node what to do and what files to run over. The script [crab_cfg_creator.py](crab_cfg_creator.py) does this for you. Give it a list of datasets to process, either in a plain text file (see [dataset_lists/](dataset_lists/) for inspiration) or comma-separated on the command line, and the type (data or MC). Example commands are below:

```bash
python crab_cfg_creator.py --mc /QCD_HT100to200_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAOD-PU2017_12Apr2018_94X_mc2017_realistic_v14-v2/NANOAODSIM,/QCD_HT100to200_TuneCP5_13TeV-madgraph-pythia8/RunIIFall17NanoAOD-PU2017_12Apr2018_94X_mc2017_realistic_v14_ext1-v1/NANOAODSIM
```

```bash
python crab_cfg_creator.py --data dataset_lists/data/singleMu_list_2017.txt
```

When parsing a file, the script ignores lines that start with `#` so you can select datasets to process within a file. The output configs will be in `configs_<YYYYMMDD>/`, with one config per dataset.

**Things to note**:
- In the event things don't work out-of-the-box, check the two following points before asking a developer for help.
- The output directory for the CRAB jobs is tied to your username. The script picks up your username on the machine you're running on, and the output directory requires your CERN username. If they are the same (or you're running on lxplus), there won't be a problem. But if these are different, either run on lxplus or change the line in [crab_cfg_creator.py](crab_cfg_creator.py) where the config file is written from `user=os.environ['USER']` to `user=<CERN username>`.
- The output from the CRAB jobs is written to Bristol by default, which you can see in the config from the line `config.Site.storageSite = 'T2_UK_SGrid_Bristol'`. If you don't have write access for Bristol or want to send the output somewhere else, you can change this line either in [crab_cfg_creator.py](crab_cfg_creator.py) or in the config after running the script.


### Submitting jobs <a name="submittingCRABjobs"></a>

Make sure you've initialised a proxy of your grid certificate and sourced the CRAB setup script as detailed in one of the previous sections. It's then as simple as running

```bash
crab submit <config.py>
```

Assuming there's nothing wrong with the config or any other required files, the submission should proceed as expected. If you have many datasets to run over, it's easier to submit with a `for` loop:

```bash
for dataset in $(ls <identifier>*.py); do crab submit $dataset; done
```

where `<identifier>` is just the prefix shared by the datasets you want to submit. For example, if you have a list of datasets that start with `QCD_HT`, do

```bash
for dataset in $(ls QCD_HT*.py); do crab submit $dataset; done
```

Avoid just `ls`-ing `*.py` as it will pick up the other Python files that _aren't_ CRAB configs in that directory. It can also take a few minutes to submit a single dataset, so it's usually preferable to open a few tabs in the terminal to submit different streams of datasets.

If you're writing the output to Bristol (default), the output directory will be `/hdfs/dpm/phy.bris.ac.uk/home/cms/store/user/<user>/`.


### Monitoring <a name="monitoringCRABjobs"></a>

You can monitor the progress of a submission with

```bash
crab status <CRAB output dir>
```

where `<CRAB output dir>` is usually in the directory you submitted from, called `crab_<config>/`. It is also possible to monitor on the web, which is much more useful if you have lots of jobs running. Head to the URL http://dashb-cms-job.cern.ch/, and then type your name in the search bar to bring up a list of your jobs. To resubmit failed jobs in a submission, do

```bash
crab resubmit <CRAB output dir>
```

Note that this does not affect jobs that are currently running or have already finished. CRAB is smart like that.



## Extending the skims <a name="extendingskims"></a>

Now that you're acquainted with running everything, you can also add your own custom modules to add to the skimming stage. Whether you want to add/remove branches, apply selections, or calculate some new variables, you can write a nanoAOD-tools module to do so. The directory [VBFHToInv-nanoAOD-tools/tree/master/python/postprocessing/modules/](VBFHToInv-nanoAOD-tools/tree/master/python/postprocessing/modules) contains the custom modules we include when running the skims. You can look there for inspiration when writing your own modules. You can then either import the constructor your module in [VBFHToInvModules.py](VBFHToInv-nanoAOD-tools/tree/master/python/postprocessing/VBFHToInvModules.py) and call it in `crab_script_vbf_<blah>.py`, or import the module directly in `crab_script_vbf_<blah>.py`.



## Running with HTCondor (recommended for private datasets) <a name="runningCondor"></a>

Whilst running the skims with CRAB is ideal, it is not possible for privately-produced nanoAOD samples. Currently, we only have private samples for signal MC as public datasets aren't available. Despite these datasets already being small, they still need to be skimmed over to add the extra branches we apply at this stage and keep everything consistent with the other samples we process.

**This workflow is still being optimised and refined, so check back for updates.**


### Running the skims <a name="runningjobsCondor"></a>

All the files required are in [private_samples/](private_samples/). The input file lists are maintained in [private_samples/file_lists/](private_samples/file_lists/) in plain text. Each file contains a list of nanoAOD files with the necessary xrootd redirector prepended. A file list can then be used as an argument for the script [run_skims_priv_condor.py](private_samples/run_skims_priv_condor.py), along with a data-taking year that the dataset was emulating. To run the skims, you just need to set up your environment like in the first section, then run


```bash
python run_skims_priv_condor.py <txt file containing file list> <year>
```

Note that these are _positional_ arguments, so have to be given in that order. You can specify a specific output directory with the option `--outdir` before the positional arguments. If not, one will be created for you. An example command would be

```bash
python --outdir ./skimmed_ttH/ run_skims_priv_condor.py file_lists/ttH_2016_v1.txt 2016
```

This runs the nanoAOD post-processing module in the same way as on CRAB, but takes the file list and runs one file per job on Condor. Whilst is good for consistency, as the `crab_script_vbf_mc` scripts are being used to process the public _and_ private datasets, dealing with the output files is a bit more annoying. If everything runs correctly, in the the output directory you will see a subdirectory for each nanoAOD file that was run over which contains the skimmed file. If a job fails (i.e., there's no output root file in the subdirectory or you get errors when trying to open the root file), you can resubmit it either back to Condor or run it locally:

```bash
cd <subdir>
condor_submit condor_job.job # resubmit with Condor
./exec.sh # resubmit to run locally
```


### Transferring the output files <a name="transferringfilesCondor"></a>

The output files shouldn't take up too much storage space so it shouldn't really matter where you set up the code in the first place. Now, move these files into a separate directory so they're easier to handle in the following steps. You can run

```bash
./consolidate_files.sh
```

from your output directory, which places all the root files in `./all_output_files/`. This also does a little error checking, telling you if a root file is missing from a subdirectory (but not if a root file exists and is bad). If you're working on lxplus, you now need to copy these output files to Bristol (or whatever server you want them on). Open a new terminal tab and log into the destination server. Now run

```bash
rsync -vuz -rltD --compress-level=9 <user>@lxplus.cern.ch:"<path to output files>" <destination path>
```

When specifying `"<path to output files>"`, making sure you remove any trailing slashes at the end (i.e., use `"test"` instead of `"test/"`). An example command would be

```bash
rsync -vuz -rltD --compress-level=9 ebhal@lxplus.cern.ch:"/afs/cern.ch/work/e/ebhal/nanoAOD_tools/CMSSW_10_2_5/src/VBFHToInv/NanoAODTools/crab/output_ZH" /storage/eb16003/
```

If you're transferring the files to Bristol, you can only do so to the low-storage partitions of soolin (like `/users/`, `/storage/`, or `/six/`). But we want them on `/hdfs/` which is meant for "big data". Due to the nature of `/hdfs/`, we need to use hadoop commands instead of usual file system ones. You can read more about this at https://hadoop.apache.org/docs/current/hadoop-project-dist/hadoop-common/FileSystemShell.html. For now, you only need to know how to create directories and copy files over.

To create a directory on `/hdfs`, use

```bash
hadoop fs -mkdir <directory>
```

The directory you specify must be the absolute path on `/hdfs`, minus the "`/hdfs`" part. For example, I have a path `/hdfs/user/eb16003/CHIP/`. Now I want to create a directory called `CHIP_skim_mc_v4/` below it. My command would be

```bash
hadoop fs -mkdir /user/eb16003/CHIP/CHIP_skim_mc_v4
```

**Notice the leading slash in the path.** You also can't create directories recursively, only one layer at a time. And since `/hdfs` usually contains a lot of data for many people's analyses, write permissions are restricted. Only write stuff to your `/hdfs/user/<user>` directory or a common place we've all agreed on. If you don't have a `/hdfs/user/<user>` directory, ask Winnie Lacesso or Luke Kreczko to set one up for you.

Now that you have the output directory on `/hdfs` set up, it's time to copy the files. If you're copying files from one part of `/hdfs` to another, you can use `hadoop fs -cp`. But since we're copying from another partition, we use `hadoop fs -copyFromLocal`. You're command should be

```bash
hadoop fs -copyFromLocal <path to skimmed files>/*.root <absolute path on /hdfs minus the "/hdfs">
```

An example command would be

```bash
hadoop fs -copyFromLocal /storage/eb16003/output_ZH/*.root /user/eb16003/CHIP/CHIP_skim_mc_v4/ZH/
```

Then let someone know where the new files are so we can build file lists and run the analysis chain.


## To do <a name="todo"></a>

- Tidy up this README, making it more readable and concise