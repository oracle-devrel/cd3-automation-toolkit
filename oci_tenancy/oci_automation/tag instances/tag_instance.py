#!/bin/python

import oci
from oci.core.compute_client import ComputeClient


config = oci.config.from_file()
compartment_id = config["compartment_id"]
ad = config["ad_3"]

cc = ComputeClient(config)

response = cc.list_instances(availability_domain=ad, compartment_id=compartment_id, limit=1, display_name="linux-app-test")

print response.data

instance = response.data[0]

instance_id = instance.id

existingTagList = instance.defined_tags
# {"Operations": {"CostCenter": "42"}}
defined_tags = { "shs-os": {"Linux74":""}}
#defined_tags = {}
uid = oci.core.models.UpdateInstanceDetails(defined_tags = defined_tags)

#response = cc.update_instance(instance_id=instance_id,update_instance_details=uid)
print existingTagList

print("shs-os" in existingTagList)

