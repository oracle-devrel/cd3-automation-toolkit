import configparser
import argparse
import oci
import subprocess
import os

def create_volume(block_storage, compartment_id, ad, display_name, size):
    print "Creating volume with Size: " + str(size) + " with Name" + display_name
    result = block_storage.create_volume(
        oci.core.models.CreateVolumeDetails(
            compartment_id=compartment_id,
            availability_domain=ad,
            display_name=display_name,
            size_in_gbs=size
        )
    )
    volume = oci.wait_until(
        block_storage,
        block_storage.get_volume(result.data.id),
        'lifecycle_state',
        'AVAILABLE'
    ).data
    print('Created Volume: {}'.format(display_name))

    return volume.id

def attach_volume():
    print "Attaching volume to the instance"
    volume_attachment_response = compute_client.attach_volume(
        oci.core.models.AttachParavirtualizedVolumeDetails(
            device='/dev/oracleoci/oraclevdx',
            display_name='NFSVolAttached',
            instance_id=instance_ocid,
            volume_id=volume_attach
        )
    )
    volume_attached = oci.wait_until(
        compute_client,
        compute_client.get_volume_attachment(volume_attachment_response.data.id),
        'lifecycle_state',
        'ATTACHED'
    )
    print (volume_attached.data)
    return volume_attached
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Creates a NFS Server")
    parser.add_argument("propsfile", help="Full Path of properties file eg nfsserver.properties")

    args = parser.parse_args()
    config = configparser.RawConfigParser()
    config.read(args.propsfile)
    input_config = ""
    nfs_local_path = config.get('Default', 'yml_nfs_config_file')
    exports_local_path = config.get('Default', 'j2_exports_file')
    #print(public_ip, nfs_local_path)


    # Read Config file Variables
    try:
        input_config_file = config.get('Default', 'python_config_file').strip()
        display_name = config.get('Default', 'display_name').strip()
        size = int(config.get('Default', 'size').encode('ascii','ignore'))
        yml_file = config.get('Default','yml_nfs_config_file')
        j2_exports_file = config.get('Default','j2_exports_file')

        #print (ocs_work_server_ocid, input_config_file, ad, display_name, size)

    except Exception as e:
        print("Please make sure that all properties are defined in the properties file. Exiting...")
        print e.__doc__
        exit()

        # Read Python config_demo_rsync file
    python_config = oci.config.from_file(file_location=input_config_file)  # ,profile_name=input_region_name)


    #ad = python_config['ad']
    #print (ad)
    compartment_id = python_config['vm_compartment_ocid']
    instance_ocid = python_config.get('ocswork_instance_ocid')
    #print (compartment_id)
    network_client = oci.core.VirtualNetworkClient(python_config)
    identity_client = oci.identity.IdentityClient(python_config)
    compute_client = oci.core.ComputeClient(python_config)
    block_storage = oci.core.BlockstorageClient(python_config)

    response = compute_client.get_instance(instance_ocid)
    instance = response.data
    ad = instance.availability_domain

    volume_attach = create_volume(block_storage, compartment_id, ad, display_name, size)
    attach_volume()

    cwd = os.getcwd()
    command = "/bin/ansible-playbook " + cwd + "/" + yml_file

    os.system(command)

   # output=subprocess.Popen((command),stdout=subprocess.PIPE).stdout

    #print output
    #utput.close()

