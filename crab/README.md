# Running skims on nanoAOD datasets

We run skims over the nanoAOD datasets we intend to use in the analysis. This helps reduce the overall footprint for each dataset, allowing us to store the output files at Bristol (or another "local" server), removing the I/O bottleneck when running over the files for analysis studies.


## Running with CRAB (recommended for public datasets)

### Setting up the environment

If you're reading this, you should have already set up CMSSW, nanoAOD-tools and VBFHtoInv-nanoAOD-tools, which are required for running the skims. If not, follow the instructions at https://github.com/eshwen/VBFHToInv-nanoAOD-tools, replacing instances of `vukasinmilosevic` with `eshwen` when cloning the repositories. Make sure to compile the code with `scram b -j 8` initially, from the directory `CMSSW_10_2_5/src/`, and whenever you add/change C++ code. Then in each new session, you should run

```bash
cd <top_dir>/CMSSW_10_2_5/src
cmsenv
source /cvmfs/cms.cern.ch/crab3/crab.sh
voms-proxy-init --voms cms --valid 168:00
cd VBFHToInv/NanoAODTools/crab
```

which also sets up the CRAB environment for job submission/monitoring and initialises a proxy of your grid certificate (required for interacting with the CERN LCG).


### Setting up the CRAB configs

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


### Submitting jobs

Make sure you've initialised a proxy of your grid certificate and sourced the CRAB setup script as detailed in one of the previous sections. It's then as simple as running

```bash
crab submit <config.py>
```

Assuming there's nothing wrong with the config or any other required files, the submission should proceed as expected. If you have many datasets to run over, it's easier to submit with a `for` loop:

```bash
for dataset in $(ls <identifier>*.py); do crab submit $dataset; done
```

where `<identifier>` is just the prefix shared by the datasets you want to submit. Avoid just `ls`-ing `*.py` as it will pick up the other Python files that _aren't_ CRAB configs in that directory. It can also take a few minutes to submit a single dataset, so it's usually preferable to open a few tabs in the terminal to submit different streams of datasets.

If you're writing the output to Bristol (default), the output directory will be `/hdfs/dpm/phy.bris.ac.uk/home/cms/store/user/<user>/`.


### Monitoring

You can monitor the progress of a submission with

```bash
crab status <CRAB output dir>
```

where `<CRAB output dir>` is usually in the directory you submitted from, called `crab_<config>/`. It is also possible to monitor on the web, which is much more useful if you have lots of jobs running. Head to the URL http://dashb-cms-job.cern.ch/, and then type your name in the search bar to bring up a list of your jobs. To resubmit failed jobs in a submission, do

```bash
crab resubmit <CRAB output dir>
```

Note that this does not affect jobs that are currently running or have already finished. CRAB is smart like that.


### Extending the skims

Now that you're acquainted with running everything, you can also add your own custom modules to add to the skimming stage. Whether you want to add/remove branches, apply selections, or calculate some new variables, you can write a nanoAOD-tools module to do so. The directory [VBFHToInv-nanoAOD-tools/tree/master/python/postprocessing/modules/](VBFHToInv-nanoAOD-tools/tree/master/python/postprocessing/modules) contains the custom modules we include when running the skims. You can look there for inspiration when writing your own modules. You can then either import the constructor your module in [VBFHToInvModules.py](VBFHToInv-nanoAOD-tools/tree/master/python/postprocessing/VBFHToInvModules.py) and call it in `crab_script_vbf_<blah>.py`, or import the module directly in `crab_script_vbf_<blah>.py`.


## Running with HTCondor/locally (recommended for private datasets)

Whilst running the skims with CRAB is ideal, it is not possible for privately-produced nanoAOD samples. Currently, we only have private samples for signal MC as public datasets aren't available. Despite these datasets already being small, they still need to be skimmed over to add the extra branches we apply at this stage and keep everything consistent with the other samples we process.

**This workflow is a little annoying and still being refined, so check back for updates.**

### Running the skims

All the files required are in this directory (or below). The input file lists are maintained in [file_lists_priv_prod/](file_lists_priv_prod) in Python scripts. Each script contains a list of files with the necessary xrootd redirector prepended. These are then imported into [PSet.py](PSet.py). To run over a file list, make sure it's imported and then extend `process.source.fileNames` with that list. You don't need to change anything else in the script. Then, to process the files, run

```bash
python crab_script_vbf_mc_<year>.py 1
```

This runs the nanoAOD post-processing module in the same way as on CRAB, but takes the file list from [PSet.py](PSet.py) and processes it locally. While this is good for consistency, as the `crab_script` files are being used to process the public _and_ private datasets, dealing with the output files is a bit more annoying.


### Transferring the output files

You will get output files in the current directory. They shouldn't take up too much storage space so it shouldn't really matter where you set up the code in the first place. Now, move these files into a separate directory so they're easier to handle in the following steps. If you're working on lxplus, you now need to copy these output files to Bristol (or whatever server you want them on). Open a new terminal tab and log into the destination server. Now run

```bash
rsync -vuz -rltD --compress-level=9 <user>@lxplus.cern.ch:"<path to output files>" <destination path>
```

When specifying `"<path to output files>"`, making sure you remove any trailing slashes at the end (i.e., `"test"` instead of `"test/"`). An example command would be

```bash
rsync -vuz -rltD --compress-level=9 ebhal@lxplus.cern.ch:"/afs/cern.ch/work/e/ebhal/nanoAOD_tools/CMSSW_10_2_5/src/VBFHToInv/NanoAODTools/crab/output_ZH" /storage/eb16003/
```

If you're transferring the files to Bristol, you can only do so to the low-storage partitions of the server (like /users/, /storage/, or /six/). But we want them on /hdfs/ which is meant for "big data". So you need to transfer the files to `/hdfs/`, which require hadoop commands instead of usual file system ones. You can read more about this at https://hadoop.apache.org/docs/current/hadoop-project-dist/hadoop-common/FileSystemShell.html. For now, you only need to know how to create directories and copy files over.

To create a directory on `/hdfs`, use

```bash
hadoop fs -mkdir <directory>
```

The directory you specify must be the absolute path on `/hdfs`, minus the "`/hdfs`" part. For example, I have a path `/hdfs/user/eb16003/CHIP/`. Now I want to create a directory called `CHIP_skim_mc_v4/` below it. My command would be

```bash
hadoop fs -mkdir /user/eb16003/CHIP/CHIP_skim_mc_v4
```

Notice the leading slash in the path. You also can't create directories recursively, only one layer at a time. And since `/hdfs` usually contains a lot of data for many people's analyses, write permissions are restricted. Only write stuff to your `/hdfs/user/<user>` directory or a common place we've all agreed on. If you don't have a `/hdfs/user/<user>` directory, ask Winnie Lacesso or Luke Kreczko to set one up for you.

Now that you have the output directory on `/hdfs` set up, it's time to copy the files. If you're copying files from one part of `/hdfs` to another, you can use `hadoop fs -cp`. But since we're copying from another partition, we use `hadoop fs -copyFromLocal`. You're command should be

```bash
hadoop fs -copyFromLocal <path to skimmed files>/*.root <absolute path on /hdfs minus the "/hdfs">
```

An example command would be

```bash
hadoop fs -copyFromLocal /storage/eb16003/output_ZH/*.root /user/eb16003/CHIP/CHIP_skim_mc_v4/ZH/
```

Then let someone know where the new files are so we can build file lists and run the analysis chain.


## To do

- Tidy up this README, adding hyperlinks for each section (like in my SVJ one), making it more readable and concise