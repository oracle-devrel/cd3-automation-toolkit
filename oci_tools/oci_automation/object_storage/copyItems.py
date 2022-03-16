#!/bin/python

## Copies items from one bucket to another.
## If items are in a subdirectory - direct copy fails, so have to download and re-upload
## Thats what this does.

import oci

from oci.core.compute_client import ComputeClient
from oci.object_storage import ObjectStorageClient
from oci.object_storage.models import CreateBucketDetails
from oci.audit.models import AuditEvent
from oci.object_storage.models import CopyObjectDetails
from oci.object_storage import UploadManager
from oci.object_storage.transfer.constants import MEBIBYTE



config = oci.config.from_file()
compartment_id = config["compartment_id"]
ad = config["ad_1"]


obs = oci.object_storage.ObjectStorageClient(config)
def progress_callback(bytes_uploaded):
    print("{} additional bytes uploaded".format(bytes_uploaded))



namespace = obs.get_namespace().data
src_bucket = "NewCo_10_24Generic"
dest_bucket = "NewCoGeneric"

resp = obs.list_objects(namespace,src_bucket)
part_size = 2 * MEBIBYTE  # part size (in bytes)

for obj in resp.data.objects:
	obj_file =  obj.name
	print obj_file
#	cod = oci.object_storage.models.CopyObjectDetails(source_object_name=obj.name, destination_namespace=namespace, destination_bucket=dest_bucket, destination_object_name=obj.name)
#	cod.destination_region = "us-ashburn-1"
#	copy_resp = obs.copy_object(namespace, src_bucket, cod)
#	print copy_resp.data
	get_obj = obs.get_object(namespace, src_bucket, obj.name)
	with open(obj_file, 'wb') as f:
	    for chunk in get_obj.data.raw.stream(1024 * 1024, decode_content=False):
		f.write(chunk)

	f.close()
	# upload manager will automatically use mutlipart uploads if the part size is less than the file size
	upload_manager = UploadManager(obs, allow_parallel_uploads=True, parallel_process_count=3)
	response = upload_manager.upload_file(
	    namespace, dest_bucket, obj.name, obj.name,progress_callback=progress_callback)


#	exit(-1)

#resp = obs.list_objects(namespace,dest_bucket)
#print resp.data.objects


