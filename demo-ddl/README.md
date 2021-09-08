# demo-ddl
Contains ground zero scripts to create all the database tables

To run:
`build_groundzero_ddl.sh`

Once you have run the the `build_groundzero_ddl.sh` script, you will be able to see any differences between the old and the new DDL in Git, and create patch script(s) accordingly.

## Patching a database
The script `patch_database.py` is used by RM to run database patches from a tagged release of this repository. This script is invoked from our pipelines and will run in a Kubernetes pod to apply any database patches from files in the tagged release version of this repository.

## Releasing this repo
When tagging a release of this repo you must update the version and and patch number in [ddl_version.sql](groundzero_ddl/ddl_version.sql) and update the current_version variable in [patch_database.py](patch_database.py)
