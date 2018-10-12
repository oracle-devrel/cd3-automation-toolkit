#!/bin/python
import oci
from oci.core.models import UpdateInstanceDetails
from oci.core.compute_client import ComputeClient
import argparse

config = oci.config.from_file()
identity = oci.identity.IdentityClient(config)
compartment_id = config["compartment_id"]
cc = ComputeClient(config)

parser = argparse.ArgumentParser(description="Update displayname of existing OCI instance")
parser.add_argument("--ocid",help="ocid of existing OCI instance ",required=True)
parser.add_argument("--newname",help="display name of windows image",required=True)
args = parser.parse_args()


stg_inst_id = args.ocid
newdisplayname = args.newname
stage_inst_data = cc.get_instance(stg_inst_id).data

print('Existing Display name : ' + stage_inst_data.display_name)

print("Updating displayname {!r} in compartment {!r}".format(stage_inst_data.display_name, compartment_id))
request = UpdateInstanceDetails()
request.display_name = newdisplayname
request.defined_tags = stage_inst_data.defined_tags
request.freeform_tags = stage_inst_data.freeform_tags

response = cc.update_instance(stg_inst_id, request)

print('New Display Name ' + response.data.display_name)
