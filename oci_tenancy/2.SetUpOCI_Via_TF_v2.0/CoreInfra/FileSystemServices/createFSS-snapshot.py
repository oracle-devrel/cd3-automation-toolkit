#!/bin/python


import argparse
import sys
import oci
import datetime
import logging


parser = argparse.ArgumentParser(description="Takes in arg mentioning Env name for FSS and creates the snapshot for all mount points in that Env")
parser.add_argument("--env", help="Env to create snapshot for: Dev | QA | DR" , required=True)
parser.add_argument("--configFileName", help="Config file name" , required=False)

logger=logging.getLogger("createSnapshot")
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logFile=logging.FileHandler("/fss_backup/logs/createSnapshot.log")
logFile.setFormatter(formatter)
logger.addHandler(logFile)

if len(sys.argv)==1:
        parser.print_help()
        sys.exit(1)

args = parser.parse_args()

configFileName = args.configFileName
env = args.env

logger.info("----------Start createSnapshot Execution for env "+env+"-----------")
if args.configFileName is not None:
    configFileName = args.configFileName
    config = oci.config.from_file(file_location=configFileName)
else:
    config = oci.config.from_file()

try:
    fss_client= oci.file_storage.FileStorageClient(config)
    compartment_ocid=''

    if(env=='Dev' or env == 'QA'):
        compartment_ocid=config.get("np_compartment_ocid")
        #compartment_ocid='ocid1.compartment.oc1..aaaaaaaayrb5yjhwxdludf3kjjga4sek3tiat5yanjr3t3pss6zpndhta7yq'
    if(env=='DR'):
        compartment_ocid = config.get("dr_compartment_ocid")
        #compartment_ocid = 'ocid1.compartment.oc1..aaaaaaaad3uuzb5s2dx2pw56xc76vc23qktmzdqw3pqa7gglwozzmbqk5jeq'
    if(env=='Prod'):
        compartment_ocid = config.get("prod_compartment_ocid")
        #compartment_ocid ='ocid1.compartment.oc1..aaaaaaaazvqlztr7akiw7mobcxzi33rupme3xbowav3yd4putoxi7ah6o4oa'

    if(compartment_ocid!=''):
        all_fss = fss_client.list_file_systems(compartment_ocid, config.get("ad_1"))

    for fss in all_fss.data:
        if(env=='Dev'):
            if('dev' in fss.display_name):
                logger.info('Creating snapshot for '+fss.display_name + ' with name snaphot_'+fss.display_name+"_"+str(datetime.date.today()))
                fss_id=fss.id
                createSnapshotDetails = oci.file_storage.models.CreateSnapshotDetails(file_system_id=fss_id,name="snapshot_"+fss.display_name+"_"+str(datetime.date.today()))
                fss_client.create_snapshot(create_snapshot_details=createSnapshotDetails)
        if(env=='QA'):
            if('qa' in fss.display_name):
                logger.info('Creating snapshot for '+fss.display_name + ' with name snaphot_'+fss.display_name+"_"+str(datetime.date.today()))
                fss_id = fss.id
                createSnapshotDetails = oci.file_storage.models.CreateSnapshotDetails(file_system_id=fss_id,name="snapshot_"+fss.display_name+"_"+str(datetime.date.today()))
                fss_client.create_snapshot(create_snapshot_details=createSnapshotDetails)
        if (env == 'DR'):
            if ('dr' in fss.display_name):
                logger.info('Creating snapshot for ' + fss.display_name + ' with name snaphot_'+fss.display_name+"_"+ str(datetime.date.today()))
                fss_id = fss.id
                createSnapshotDetails = oci.file_storage.models.CreateSnapshotDetails(file_system_id=fss_id,name="snapshot_"+fss.display_name+"_"+str(datetime.date.today()))
                fss_client.create_snapshot(create_snapshot_details=createSnapshotDetails)
        if (env == 'Prod'):
            if ('prod' in fss.display_name):
                logger.info('Creating snapshot for ' + fss.display_name + ' with name snaphot_'+fss.display_name+"_"+ str(datetime.date.today()))
                fss_id = fss.id
                createSnapshotDetails = oci.file_storage.models.CreateSnapshotDetails(file_system_id=fss_id,name="snapshot_"+fss.display_name+"_"+str(datetime.date.today()))
                fss_client.create_snapshot(create_snapshot_details=createSnapshotDetails)
except Exception as e:
    logger.error("Error occured during execution "+ str(e))

logger.info("----------End createSnapshot Execution for env "+env+"-----------")