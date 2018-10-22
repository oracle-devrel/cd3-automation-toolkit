#!/bin/python

#Author: Murali Nagulakonda
#Oracle Consulting
#murali.nagulakonda.venkata@oracle.com


import sys
import oci
import argparse
from oci.core.compute_client import ComputeClient
from oci.core import BlockstorageClient
from oci.core.models import Volume


config = oci.config.from_file()
compartment_id = config["compartment_id"]
ad = config["ad_1"]
bsc = oci.core.BlockstorageClient(config)




pols = bsc.list_volume_backup_policies()
pol_list = {}
for pol in pols.data:
	print "Pol Name: " + pol.display_name + " OCID: " + pol.id
	pol_list[pol.display_name] = pol.id

print "Printing List"
print pol_list


	

vols = bsc.list_volumes(compartment_id=compartment_id,lifecycle_state=Volume.LIFECYCLE_STATE_AVAILABLE)


for vol in vols.data:
	print vol.display_name
	print vol.id
	pol_id = pol_list["silver"]
	print "Bronze id:  " +  pol_id
	cba = oci.core.models.CreateVolumeBackupPolicyAssignmentDetails(asset_id=vol.id,policy_id=pol_id)
	resp = bsc.create_volume_backup_policy_assignment(cba)
	print " Response for cvbp : " + str(resp.data)




