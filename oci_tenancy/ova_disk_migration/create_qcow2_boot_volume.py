#!/bin/python

## This Script Takes the Uploaded vmdk from Object Storage and creates an Image that can be used to launch an instance ###
#Author: Murali Nagulakonda
#Oracle Consulting
#murali.nagulakonda.venkata@oracle.com



import sys
import oci
import os
from oci.config import validate_config
from oci.object_storage import UploadManager
from oci.core.models import CreateImageDetails
from oci.object_storage.transfer.constants import MEBIBYTE
from oci.core.models import ImageSourceViaObjectStorageTupleDetails
from oci.core.compute_client import ComputeClient
import datetime
import argparse

parser = argparse.ArgumentParser(description = "Create bootvolume from uploaded vmdk in Object store")
parser.add_argument("disk", help="Name of vmdk object (disk) already uploaded to object store")

if len(sys.argv)==1:
        parser.print_help()
        sys.exit(1)

args = parser.parse_args()





config = oci.config.from_file()
print validate_config(config)

identity = oci.identity.IdentityClient(config)
compartment_id = config["compartment_id"]
compartment_id = "ocid1.compartment.oc1..aaaaaaaat3lzt4tiukor6nxfx5dc7sd6do62j6dwdt3fbkjgxotbvyh3jmca"

### Upload VMDK : /u01/odec_test_ova/odramdmap3t-disk1.vmdk ###


object_storage = oci.object_storage.ObjectStorageClient(config)

namespace = object_storage.get_namespace().data
bucket_name =  config["stg_object_store_bucket"]
object_name = args.disk
preauth_name = object_name + "-preauth"
print preauth_name

days = datetime.datetime.now()+datetime.timedelta(days=10)
#days = days.isoformat()
days = days.strftime('%Y-%m-%dT%H:%M:%SZ')

preauth_det = oci.object_storage.models.CreatePreauthenticatedRequestDetails(name=preauth_name,access_type="ObjectReadWrite",time_expires=days,object_name=object_name)
# print preauth_det

preaut_resp = object_storage.create_preauthenticated_request(namespace_name=namespace, bucket_name=bucket_name, create_preauthenticated_request_details=preauth_det)
print preaut_resp.data.access_uri
access_url =  "https://objectstorage." + config["region"] + ".oraclecloud.com" + preaut_resp.data.access_uri

#imgObjSrc = ImageSourceViaObjectStorageTupleDetails(source_image_type="VMDK",source_type="bootVolume",bucket_name=bucket_name,namespace_name=namespace,object_name=object_name)

imgObjSrc = oci.core.models.ImageSourceViaObjectStorageUriDetails (source_image_type="QCOW2",source_type="objectStorageUri",source_uri=access_url)
print imgObjSrc

createImgDet = CreateImageDetails(compartment_id=compartment_id, display_name=object_name,image_source_details=imgObjSrc,launch_mode="EMULATED")


computeClient = ComputeClient(config)

response = computeClient.create_image(createImgDet)
print response.data

# get_import_response = oci.wait_until(computeClient, response, 'lifecycle_state', 'AVAILABLE')
# print get_import_response.data


