#!/bin/python

import oci
from oci.core.compute_client import ComputeClient
from oci.object_storage import ObjectStorageClient
from oci.object_storage.models import CreateBucketDetails


config = oci.config.from_file()
compartment_id = config["compartment_id"]
ad = config["ad_1"]


obs = oci.object_storage.ObjectStorageClient(config)

namespace = obs.get_namespace().data
src_bucket = "NewCo_10_24Generic"
dest_bucket = "NewCoGeneric"

resp = obs.list_objects(namespace,src_bucket)

print resp.data.objects

