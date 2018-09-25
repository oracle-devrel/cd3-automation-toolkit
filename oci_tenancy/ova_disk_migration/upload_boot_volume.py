#!/bin/python
#######################################
# This script uses the OCI Python Package
# to upload a vmdk to object storage
# 

import sys
import oci
import os
import argparse
from oci.config import validate_config
from oci.object_storage import UploadManager
from oci.object_storage.models import CreateBucketDetails
from oci.object_storage.transfer.constants import MEBIBYTE

parser = argparse.ArgumentParser(description = "Upload Boot Volume to Object storage bucket as defined in the config file")
parser.add_argument("disk", help="Full path of the disk to be uploaded (including disk name).  This must be a .vmdk file")

if len(sys.argv)==1:
        parser.print_help()
        sys.exit(1)

args = parser.parse_args()


config = oci.config.from_file()
print validate_config(config)

identity = oci.identity.IdentityClient(config)
compartment_id = config["compartment_id"]


def progress_callback(bytes_uploaded):
    print("{} additional bytes uploaded".format(bytes_uploaded))


object_storage = oci.object_storage.ObjectStorageClient(config)

namespace = object_storage.get_namespace().data
bucket_name = config["stg_object_store_bucket"]

request = CreateBucketDetails()
request.compartment_id = compartment_id
request.name = bucket_name
bucket = oci.object_storage.models.Bucket(namespace=namespace,compartment_id=compartment_id,storage_tier='STANDARD',name=bucket_name)

## Full File Path
filename = args.disk
disk_name = filename.split('/')[-1]
print "Disk to be uploaded :  " + disk_name + " Full Path: " + filename + " to bucket " + bucket_name


print("Uploading new object {!r}".format(disk_name))

# upload manager will automatically use mutlipart uploads if the part size is less than the file size
part_size = 2 * MEBIBYTE  # part size (in bytes)
upload_manager = UploadManager(object_storage, allow_parallel_uploads=True, parallel_process_count=3)
response = upload_manager.upload_file(
    namespace, bucket_name, disk_name, filename,progress_callback=progress_callback)

