#!/bin/python


import argparse
import sys
import oci
import datetime
from datetime import timedelta
import logging

parser = argparse.ArgumentParser(description="Takes in a csv file mentioning sec rules to be added for the subnet. See update_seclist-example.csv for format under example folder. It will then take backup of all existing sec list files and create new one with modified rules; Required Arguements: propsfile, outdir and secrulesfile")
parser.add_argument("--env", help="Env to delete snapshot for: Dev | QA | DR" , required=True)
parser.add_argument("--retentionDays", help="No of days to retain snapshot" , required=True)
parser.add_argument("--configFileName", help="Config file name" , required=False)

logger=logging.getLogger("removeSnapshot")
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logFile=logging.FileHandler("/fss_backup/logs/removeSnapshot.log")
logFile.setFormatter(formatter)
logger.addHandler(logFile)

if len(sys.argv)==1:
        parser.print_help()
        sys.exit(1)

args = parser.parse_args()

configFileName = args.configFileName
env = args.env
retentionDays=args.retentionDays

if args.configFileName is not None:
    configFileName = args.configFileName
    config = oci.config.from_file(file_location=configFileName)
else:
    config = oci.config.from_file()

logger.info("-------------Start removeSnapshot Execution for env "+env+"----------------")

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

    retaindays=int(retentionDays)
    now = datetime.datetime.today()
    retaindays_ago=now-timedelta(days=retaindays)

    for fss in all_fss.data:
        if(env=='Dev'):
            if('dev' in fss.display_name):
                fss_id=fss.id
                snapshots=fss_client.list_snapshots(fss_id)
                for snapshot in snapshots.data:
                    snapshot_createTime=snapshot.time_created
                    snapshot_createTime=snapshot_createTime.replace(tzinfo=None)
                    snapshot_id=snapshot.id
                    snapshot_name=snapshot.name

                    if(snapshot_createTime < retaindays_ago):
                        logger.info("removing snapshot "+snapshot_name)
                        fss_client.delete_snapshot(snapshot_id)
        if(env=='QA'):
            if('qa' in fss.display_name):
                fss_id=fss.id
                snapshots=fss_client.list_snapshots(fss_id)
                for snapshot in snapshots.data:
                    snapshot_createTime=snapshot.time_created
                    snapshot_createTime=snapshot_createTime.replace(tzinfo=None)
                    snapshot_id=snapshot.id
                    snapshot_name=snapshot.name

                    if(snapshot_createTime < retaindays_ago):
                        logger.info("removing snapshot "+snapshot_name)
                        fss_client.delete_snapshot(snapshot_id)
        if (env == 'DR'):
            if ('dr' in fss.display_name):
                fss_id=fss.id
                snapshots=fss_client.list_snapshots(fss_id)
                for snapshot in snapshots.data:
                    snapshot_createTime=snapshot.time_created
                    snapshot_createTime=snapshot_createTime.replace(tzinfo=None)
                    snapshot_id=snapshot.id
                    snapshot_name=snapshot.name

                    if(snapshot_createTime < retaindays_ago):
                        logger.info("removing snapshot "+snapshot_name)
                        fss_client.delete_snapshot(snapshot_id)
except Exception as e:
    logger.error("Error occured during execution "+ str(e))

logger.info("-------------End removeSnapshot Execution for env "+env+"----------------")