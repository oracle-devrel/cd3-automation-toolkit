from oci.object_storage.object_storage_client import ObjectStorageClient
from oci.object_storage.models import CreatePreauthenticatedRequestDetails
import oci
import argparse

### cleans up the multiple PARs created as a part of setupPandaInputs - especially when testing.


parser = argparse.ArgumentParser(description="Creates Panda related config files")
parser.add_argument("--oci_config_file", help="the Oci config file - defaults to ~/.oci/config")

args = parser.parse_args()


config = ""
oci_conf_file = args.oci_config_file
if oci_conf_file == None:
    config = oci.config.from_file()
else:
    config = oci.config.from_file(file_location=oci_conf_file)

compartment_id = config['compartment_id']

stg_object_store_bucket = "ocic-oci-sig"

object_stg_client = ObjectStorageClient(config)
namespace = object_stg_client.get_namespace().data

par_list_response = object_stg_client.list_preauthenticated_requests(namespace, stg_object_store_bucket)
for par in par_list_response.data:
    name = par.name
    if name == "OCIC2OIC":
        print ("Deleting Par with Par ID: " + par.id)
        object_stg_client.delete_preauthenticated_request(namespace,stg_object_store_bucket,par.id)
