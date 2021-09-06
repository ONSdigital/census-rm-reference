# ssdc-rm-ddl[![Build Status](https://travis-ci.com/ONSdigital/ssdc-rm-ddl.svg?branch=main)](https://travis-ci.com/ONSdigital/ssdc-rm-ddl)
Contains ground zero scripts to create all the RM database tables, as well as a script to update the DDL from the master branch of the RM components

To run:
`build_groundzero_ddl.sh`

It's very important that the DDL script to build ground zero is run, instead of manually editing the files in the `groundzero_ddl` directory, so that the database is always perfectly in sync with the code on the master branch.

If you have made changes to Action Scheduler, Case Processor, Exception Manager or the UAC-QID Service and you need to re-generate the ground zero DDL, you can specify specific branches with the following options:
- `CASE_PROCESSOR_BRANCH`
- `UAC_QID_SERVICE_BRANCH`
- `EXCEPTION_MANAGER_BRANCH`

For example, you might want to run `CASE_PROCESSOR_BRANCH=example-branch build_groundzero_ddl.sh` to get the groundzero DDL to be generated for an as-yet unmerged branch called `example-branch`.

Once you have run the the `build_groundzero_ddl.sh` script, you will be able to see any differences between the old and the new DDL in Git, and create patch script(s) accordingly.

## Patching a database
The script `patch_database.py` is used by RM to run database patches from a tagged release of this repository. This script is invoked from our pipelines and will run in a Kubernetes pod to apply any database patches from files in the tagged release version of this repository.

## Releasing this repo
When tagging a release of this repo you must update the version and and patch number in [ddl_version.sql](groundzero_ddl/ddl_version.sql) and update the current_version variable in [patch_database.py](patch_database.py)
