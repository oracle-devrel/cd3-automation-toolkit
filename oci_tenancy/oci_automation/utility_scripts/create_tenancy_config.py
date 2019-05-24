#!/bin/python
import sys
import os
import oci
from oci.identity.identity_client import IdentityClient
from oci.object_storage.object_storage_client import ObjectStorageClient
from oci.core.compute_client import ComputeClient


config = oci.config.from_file()
identity = oci.identity.IdentityClient(config)
compartment_id = config["compartment_id"]

##################################################################################
# This Script Sets up the following in the ~/.oci/config file
# 1.  Availability Domains
# 2.  Object Storage - Bucket Name - Defaults to : OCI-Toolkit-Obj-Store
# 3.  Connects to Object Storage - and if the Bucket doesn't exist - create it
# 4.  Adds "namespace" to the config file
##################################################################################


def paginate(operation, *args, **kwargs):
    while True:
        response = operation(*args, **kwargs)
        for value in response.data:
            yield value
        kwargs["page"] = response.next_page
        if not response.has_next_page:
            break



ad_list = identity.list_availability_domains(compartment_id)
home_dir = os.getenv("HOME")
conf_file = home_dir + "/.oci/config"

conf_file = open(conf_file,"a")
name = config["stage_instance_name"]
cc  = ComputeClient(config)
# stg_inst_id = config["stage_instance_ocid"]
stg_inst_id = "" 
stage_instance_ocid = "" 
# ad = config["ad_3"]
# response = cc.list_instances(compartment_id=compartment_id, display_name=name,availability_domain=ad)


##### Availability Domains #####

i = 1
for ad in paginate( identity.list_availability_domains,compartment_id = compartment_id):
	ad_name = "ad_" + str(i)
	if ad_name in config:
		print "Availability domain "  + ad_name + " already exists in config file - not writing"
	else:
		print "Adding to Conf file: " + ad_name + "="+ ad.name +"\n"
		conf_file.write("ad_" + str(i) + "=" + ad.name + "\n")
	i = i + 1


#### Stage Instance Availability Domain ####


stage_instance_ad = "" 
if "stage_instance_ad" in config:
	print "stage_instance_ad=" + config["stage_instance_ad"] + " exists in conf file, not overwriting"
	stage_instance_ad = config["stage_instance_ad"]
else:

	stage_instance_ad = cc.get_instance(stg_inst_id).data.availability_domain
	#print instance.data.availability_domain
	conf_file.write("stage_instance_ad=" + stage_instance_ad)

#### Object Storage Bucket ####

stg_object_store_bucket = "OCI-Toolkit-Obj-Store"

if "stg_object_store_bucket" in config:
	# do nothing
	print "stg_object_store_bucket=" + config["stg_object_store_bucket"] + " already exists - not writing to conf file"
	stg_object_store_bucket = config["stg_object_store_bucket"]
else:
	print "Adding to Conf file: " + stg_object_store_bucket + "="+ stg_object_store_bucket +"\n"
	conf_file.write("stg_object_store_bucket=" + stg_object_store_bucket + "\n")

object_stg_client = ObjectStorageClient(config)

namespace = "" 
if "namespace" in config:
	print "namespace=" + config["namespace"] + " exists in config file.  Not overwriting"
	namespace = config["namespace"]
else:
	namespace = object_stg_client.get_namespace().data
	print "Adding to Conf File: namespace=" + namespace + "\n"
	conf_file.write("namespace=" + namespace + "\n")



### Create the Bucket ###

## Easy test -if the bucket exists, this will simply return an error, ignore and move on.

bucket_details = oci.object_storage.models.CreateBucketDetails(name=stg_object_store_bucket,compartment_id=compartment_id)
try:
	bucket = object_stg_client.create_bucket(namespace_name=namespace,create_bucket_details=bucket_details)
	print "Creating Bucket - " + stg_object_store_bucket
#	print bucket.data
except oci.exceptions.ServiceError as e:
	if e.code == "BucketAlreadyExists":
		print "Bucket " + stg_object_store_bucket + " already exists - not creating it"
	else:
		print "############## ERRROR CREATING BUCKET #####################"
		print e.args[0]
	


###



conf_file.close()





