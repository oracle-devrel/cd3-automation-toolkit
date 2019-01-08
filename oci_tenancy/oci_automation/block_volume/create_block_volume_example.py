#!/bin/python

import oci
import os
from oci.config import validate_config
from oci.core.models import CreateVolumeDetails
from oci.core.models import AttachIScsiVolumeDetails
from oci.core.compute_client import ComputeClient
from oci.core.blockstorage_client import BlockstorageClient

import datetime


config = oci.config.from_file()
# print validate_config(config)

identity = oci.identity.IdentityClient(config)
compartment_id = config["compartment_id"]

block_vol_name = "test-vol1"

### Add an if block for a default - otherwise it should come from the argv ###
ad = config["ad_1"]

### Create Block Volume

print "######################################################"
print "Creating New Volume ..."
volume = CreateVolumeDetails(availability_domain=ad, compartment_id=compartment_id, display_name=block_vol_name, size_in_gbs=50)

bsc  = BlockstorageClient(config)

new_vol_response  = bsc.create_volume(volume)

new_vol = new_vol_response.data
# print new_vol

print "Waiting for Volume to be provisioned (Available) "
print "######################################################"


get_attach_response = oci.wait_until(bsc, bsc.get_volume(new_vol.id), 'lifecycle_state', 'AVAILABLE')
print get_attach_response.data


### Get the stage host instance ###

cc = ComputeClient(config)

#stage_instance = cc.list_instances(availability_domain=ad, compartment_id=compartment_id, limit=1, display_name="Murali-Linux-Staging")

#instance = stage_instance.data[0]

stg_instance_id = config["stage_instance_ocid"]
print "Instance ID: " + stg_instance_id
print "Volume Id : " + new_vol.id


##### Attach the new volume to this instance ####

iscsi_vol = AttachIScsiVolumeDetails( instance_id=stg_instance_id, type="iscsi", volume_id=new_vol.id,use_chap=False)

vol_attach = cc.attach_volume(iscsi_vol)

# print vol_attach.data
print "######################################################"
print "Attaching Volume to Stage Machine"
get_attach_response = oci.wait_until(cc, cc.get_volume_attachment(vol_attach.data.id), 'lifecycle_state', 'ATTACHED')


vol_attach =  get_attach_response.data
