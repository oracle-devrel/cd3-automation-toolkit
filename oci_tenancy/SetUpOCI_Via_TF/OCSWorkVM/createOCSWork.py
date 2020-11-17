#!/usr/bin/python3
import configparser
import argparse
import oci
import re
import subprocess
import time
import paramiko
import shutil
from paramiko import SSHClient
import puttykeys
from pathlib import Path
import sys
import os
from datetime import datetime
import calendar

sys.path.append(os.getcwd() + "/..")
from commonTools import commonTools

parser = argparse.ArgumentParser(description="Creates OCS Work related components")
parser.add_argument("propsfile", help="Full Path of properties file. eg ocswork.properties")

args = parser.parse_args()
config = configparser.RawConfigParser()
config.read(args.propsfile)

# Read Config file Variables
try:
    input_config_file = config.get('Default', 'python_config_file').strip()
    input_ocs_compartment_name = config.get('Default', 'ocs_compartment_name').strip()
    # input_vm_compartment_name=config.get('Default','vm_compartment_name').strip()
    # input_ntk_compartment_name=config.get('Default','ntk_compartment_name').strip()
    input_ssh_key1 = config.get('Default', 'ssh_key1').strip()
    input_ssh_key2 = config.get('Default', 'ssh_key2').strip()
    input_ssh_key3 = config.get('Default', 'ssh_key3').strip()
    # input_ocic_username=config.get('Default','ocic_username').strip()
    # input_ocic_password=config.get('Default','ocic_password').strip()
    # input_ocic_identity_domain=config.get('Default','ocic_identity_domain').strip()
    # input_ocic_compute_endpoint=config.get('Default','ocic_compute_endpoint').strip()
    input_git_username = config.get('Default', 'git_username').strip()
    input_git_pvt_key_file = config.get('Default', 'git_pvt_key_file').strip()
    input_vcn_name = config.get('Default', 'ocs_vcn_name').strip()
    input_vcn_cidr = config.get('Default', 'ocs_vcn_cidr').strip()
    input_igw_name = config.get('Default', 'ocs_igw_name').strip()
    input_lpg_to_orig_name = config.get('Default', 'ocs_lpg_name').strip()
    # input_lpg_to_mirror_name = config.get('Default', 'ocs_lpg_to_mirror_name').strip()
    # input_lpg_to_rsync_name = config.get('Default', 'ocs_lpg_to_rsync_name').strip()
    input_subnet_name = config.get('Default', 'ocs_subnet_name').strip()
    input_subnet_cidr = config.get('Default', 'ocs_subnet_cidr').strip()
    input_ad_name = config.get('Default', 'ocs_input_ad').strip()
    input_vm_name = config.get('Default', 'ocs_vm_name').strip()
    input_vm_shape = config.get('Default', 'ocs_vm_shape').strip()
    input_image_id = config.get('Default', 'ocs_vm_source_image_ocid').strip()
    input_cleanup_script_file = config.get('Default', 'cleanup_script_file').strip()
    input_user_data_file = config.get('Default', 'ocs_user_data_file').strip()
    input_pvt_key_file = config.get('Default', 'pvt_key_file').strip()
    input_shell_script = config.get('Default', 'shell_script_name')

    # input_configure_panda = config.get('Default', 'configure_panda').strip()
    # input_configure_koala = config.get('Default', 'configure_koala').strip()
    # input_configure_git_oci = config.get('Default', 'configure_git_oci').strip()
    # input_configure_git_ocictooci = config.get('Default', 'configure_git_ocictooci').strip()

    # input_ocic_ip_network_for_panda = config.get('Default','ocic_ip_network_for_panda').strip()
    # input_ocic_vnicset_for_panda = config.get('Default','ocic_vnicset_for_panda').strip()
    # input_ocic_tf_prefix_for_panda = config.get('Default','ocic_tf_prefix_for_panda').strip()
    # input_ocic_panda_storage_volume_size = int(config.get('Default','ocic_panda_storage_volume_size').strip())
    # input_ocic_panda_storage_volume_disks = int(config.get('Default','ocic_panda_storage_volume_disks').strip())
    # input_ocic_panda_storage_pvlv_name = config.get('Default','ocic_panda_storage_pvlv_name').strip()

    input_create_vm = config.get('Default', 'create_vm').strip()
    input_cleanup = config.get('Default', 'cleanup').strip()
    input_run_shell_script = config.get('Default', 'run_shell_script')

except Exception as e:
    print(e)
    print('Check if property values exist and try again..exiting...`    ')
    exit()

# Put default values for properties related to OCIC to OCI when using for automation
try:
    input_vm_compartment_name = config.get('Default', 'vm_compartment_name').strip()
except Exception as e:
    input_vm_compartment_name = input_ocs_compartment_name
try:
    input_ntk_compartment_name = config.get('Default', 'ntk_compartment_name').strip()
except Exception as e:
    input_ntk_compartment_name = input_ocs_compartment_name
try:
    input_configure_panda = config.get('Default', 'configure_panda').strip()
except Exception as e:
    input_configure_panda = "0"
try:
    input_configure_koala = config.get('Default', 'configure_koala').strip()
except Exception as e:
    input_configure_koala = "0"
try:
    input_configure_git_ocictooci = config.get('Default', 'configure_git_ocictooci').strip()
except Exception as e:
    input_configure_git_ocictooci = "1"
try:
    input_configure_git_oci = config.get('Default', 'configure_git_oci').strip()
except Exception as e:
    input_configure_git_oci = "1"
try:
    input_ocic_username = config.get('Default', 'ocic_username').strip()
except Exception as e:
    input_ocic_username = ""
try:
    input_ocic_password = config.get('Default', 'ocic_password').strip()
except Exception as e:
    input_ocic_password = ""
try:
    input_ocic_identity_domain = config.get('Default', 'ocic_identity_domain').strip()
except Exception as e:
    input_ocic_identity_domain = ""
try:
    input_ocic_compute_endpoint = config.get('Default', 'ocic_compute_endpoint').strip()
except Exception as e:
    input_ocic_compute_endpoint = ""
try:
    input_lpg_to_mirror_name = config.get('Default', 'ocs_lpg_to_mirror_name').strip()
except Exception as e:
    input_lpg_to_mirror_name = ""
try:
    input_lpg_to_rsync_name = config.get('Default', 'ocs_lpg_to_rsync_name').strip()
except Exception as e:
    input_lpg_to_rsync_name = ""
try:
    input_ocic_ip_network_for_panda = config.get('Default', 'ocic_ip_network_for_panda').strip()
except Exception as e:
    input_ocic_ip_network_for_panda = ""
try:
    input_ocic_vnicset_for_panda = config.get('Default', 'ocic_vnicset_for_panda').strip()
except Exception as e:
    input_ocic_vnicset_for_panda = ""
try:
    input_ocic_tf_prefix_for_panda = config.get('Default', 'ocic_tf_prefix_for_panda').strip()
except Exception as e:
    input_ocic_tf_prefix_for_panda = ""
try:
    input_ocic_panda_storage_volume_size = int(config.get('Default', 'ocic_panda_storage_volume_size').strip())
except Exception as e:
    input_ocic_panda_storage_volume_size = int("1536")
try:
    input_ocic_panda_storage_volume_disks = int(config.get('Default', 'ocic_panda_storage_volume_disks').strip())
except Exception as e:
    input_ocic_panda_storage_volume_disks = ""
try:
    input_ocic_panda_storage_pvlv_name = config.get('Default', 'ocic_panda_storage_pvlv_name').strip()
except Exception as e:
    input_ocic_panda_storage_pvlv_name = ""

if input_ocic_panda_storage_volume_size > 2048:
    print("Storage volume in OCIC cannot be greater than 2Tb. Setting to 1.5T ")
    input_ocic_panda_storage_volume_size = 1536
if (input_ntk_compartment_name == '' or input_vm_compartment_name == '' or input_ocs_compartment_name == ''):
    print("Compartment names cannot be null. Exiting...")
    exit()
if (input_ssh_key1 == ''):
    print("ssh_key1 cannot be left blank. Exiting...")
    exit()
if (input_cleanup_script_file == ''):
    print("cleanup_script_file cannot be empty. Please specify file name which will be used by cleanup script later. Exiting...")
    exit()

if os.path.isfile(input_pvt_key_file) == False:
    print("input private key file corresponding to ssh_key1 does not exist at the specified path. Exiting....")
    exit()

if os.path.isfile(input_git_pvt_key_file) == False:
    print("input private key file for GIT does not exist at the specified path. Exiting....")
    exit()

if (input_vcn_name == ''):
    input_vcn_name = 'OCS_VCN'
if (input_igw_name == ''):
    input_igw_name = 'igw'
if (input_lpg_to_orig_name == ''):
    input_lpg_to_orig_name = 'lpg'
if (input_subnet_name == ''):
    input_subnet_name = 'OCS_Subnet'
if (input_vcn_cidr == ''):
    input_vcn_cidr = '10.10.0.0/16'
if (input_subnet_cidr == ''):
    input_subnet_cidr = '10.10.1.0/24'
if (input_ad_name == ''):
    input_ad_name = 'ad_1'
if (input_vm_name == ''):
    input_vm_name = 'OCS_VM'
if (input_vm_shape == ''):
    input_vm_shape = 'VM.Standard2.4'
if (input_user_data_file == ''):
    input_user_data_file = 'cloud_init_script'
if (input_shell_script == ''):
    input_shell_script = 'shell_script.sh'

# Read Python config file
python_config = oci.config.from_file(file_location=input_config_file)  # ,profile_name=input_region_name)

network_client = oci.core.VirtualNetworkClient(python_config)
identity_client = oci.identity.IdentityClient(python_config)
compute_client = oci.core.ComputeClient(python_config)

ct = commonTools()
regions = []
regionsubscriptions = identity_client.list_region_subscriptions(tenancy_id=python_config['tenancy'])
for rs in regionsubscriptions.data:
    for k, v in ct.region_dict.items():
        if (rs.region_name == v):
            regions.append(k)


def write_file(file_name, file_data):
    file_to_open = tmp_folder / file_name
    f = open(file_to_open, "w+")
    f.write(file_data)
    f.close()


del_config_file = input_cleanup_script_file
# Report Error when cleanup _script_file already exists and is not empty.
if (os.path.exists(del_config_file) and os.stat(del_config_file).st_size != 0):
    # x = datetime.datetime.now()
    # date = x.strftime("%f").strip()
    print('cleanup_script_file ' + del_config_file + " already exists and is not empty. Make sure to provide a new file name..Exiting")
    exit()
    # shutil.move(del_config_file,del_config_file+"_"+date)


def append_file(file_name, file_data):
    f = open(file_name, "a+")
    f.write(file_data)
    f.write("\n")
    f.close()


def updatePropsFile(file_name, key, update_value):
    parser = configparser.ConfigParser()
    parser.read(file_name)
    parser.set('DEFAULT', key, update_value)

    with open(file_name, 'w+') as file:
        parser.write(file)


def paginate(operation, *args, **kwargs):
    while True:
        response = operation(*args, **kwargs)
        for value in response.data:
            yield value
        kwargs["page"] = response.next_page
        if not response.has_next_page:
            break

def create_compartment(compartment_name,compartment_desc):
    compartment_ocid=''
    create_comp_detail = oci.identity.models.CreateCompartmentDetails(compartment_id=tenancy_id,description=compartment_desc,name=compartment_name)
    try:
        compartment = identity_client.create_compartment(create_comp_detail)
        compartment_ocid = compartment.data.id
        if ("OCS" in compartment_desc):
            time.sleep(10)
            print('Waiting till OCS compartment becomes ACTIVE...')
            oci.wait_until(identity_client, identity_client.get_compartment(compartment_ocid), 'lifecycle_state','ACTIVE')
    except oci.exceptions.ServiceError as e:
        error_msg = "Compartment '" + compartment_name + "' already exists"
        if (e.message == error_msg):
            print('This compartment already exists')
            for compartment in paginate(identity_client.list_compartments, compartment_id=tenancy_id):
                if compartment_name == identity_client.name:
                    compartment_ocid = compartment.id
                    break

        elif ("home region" in e.message):
            print("Home Region " + e.message)
            new_config = python_config
            message = e.message
            if ("IAD" in message):
                new_config.__setitem__("region", ct.region_dict['ashburn'])
            if ("PHX" in message):
                new_config.__setitem__("region", ct.region_dict['phoenix'])
            if ("YYZ" in message):
                new_config.__setitem__("region", ct.region_dict['toronto'])
            if ("FRA" in message):
                new_config.__setitem__("region", ct.region_dict['frankfurt'])
            if ("LHR" in message):
                new_config.__setitem__("region", ct.region_dict['london'])
            if ("BOM" in message):
                new_config.__setitem__("region", ct.region_dict['mumbai'])
            if ("ICN" in message):
                new_config.__setitem__("region", ct.region_dict['seoul'])
            if ("NRT" in message):
                new_config.__setitem__("region", ct.region_dict['tokyo'])

            new_id_client = oci.identity.IdentityClient(new_config)
            try:
                compartment = new_id_client.create_compartment(create_comp_detail)
                compartment_ocid = compartment.data.id
            except oci.exceptions.ServiceError as e:
                print('some error occurred while trying to create compartment; exiting...')
                print(e.message)
                compartment_ocid = "-1"
        else:
            print('some error occurred while trying to create compartment; exiting...')
            print(e.message)
            compartment_ocid = "-1"
    return compartment_ocid


# Fetch AD names
print('Fetching AD names from tenancy and writing to config file if doesnt exist')
tenancy_id = python_config['tenancy']
conf_file = open(input_config_file, "a")
i = 1
for ad in paginate(identity_client.list_availability_domains, compartment_id=tenancy_id):
    ad_name = "ad_" + str(i)
    if not ad_name in python_config:
        conf_file.write("ad_" + str(i) + "=" + ad.name + "\n")
    i = i + 1
conf_file.close()

ocs_compartment_found = 0
vm_compartment_found = 0
ntk_compartment_found = 0

for compartment in paginate(identity_client.list_compartments, compartment_id=tenancy_id, compartment_id_in_subtree=True ):
    if(compartment.name== input_ocs_compartment_name):
        ocs_compartment_found=1
        ocs_compartment_ocid=compartment.id
        updatePropsFile(input_config_file, "ocs_compartment_ocid", ocs_compartment_ocid)
    if (compartment.name == input_vm_compartment_name):
        vm_compartment_found = 1
        vm_compartment_ocid = compartment.id
        updatePropsFile(input_config_file, "vm_compartment_ocid", vm_compartment_ocid)
    if (compartment.name == input_ntk_compartment_name):
        ntk_compartment_found = 1
        ntk_compartment_ocid = compartment.id
        updatePropsFile(input_config_file, "ntk_compartment_ocid", ntk_compartment_ocid)

# Create all 3 compartments or use if already existing
if (ocs_compartment_found == 0):
    print('Creating Compartment for OCS related work: ' + input_ocs_compartment_name + ' under root compartment')
    ocs_compartment_ocid = create_compartment(input_ocs_compartment_name, "compartment for OCS related work")

    if ocs_compartment_ocid == "-1":
        print("Exiting due to compartment error : ")
        exit(-1)
    updatePropsFile(input_config_file, "ocs_compartment_ocid", ocs_compartment_ocid)
if (vm_compartment_found == 0 and input_vm_compartment_name != input_ocs_compartment_name):
    print('Creating Compartment for VMs: ' + input_vm_compartment_name + ' under root compartment')
    vm_compartment_ocid = create_compartment(input_vm_compartment_name, "compartment for VMs")
    if vm_compartment_ocid == "-1":
        print("Exiting due to compartment error : ")
        exit(-1)
    updatePropsFile(input_config_file, "vm_compartment_ocid", vm_compartment_ocid)
try:
    if (ntk_compartment_found == 0 and ntk_compartment_ocid != ocs_compartment_ocid and ntk_compartment_ocid != vm_compartment_ocid):
        print('Creating Compartment for Network components: ' + input_ntk_compartment_name + ' under root compartment')
        ntk_compartment_ocid = create_compartment(input_ntk_compartment_name, "compartment for Network components")
        if ntk_compartment_ocid == "-1":
            print("Exiting due to compartment error : ")
            exit(-1)
        updatePropsFile(input_config_file, "ntk_compartment_ocid", ntk_compartment_ocid)
except NameError as e:
    print("An error occured....Exiting!")
    exit(-1)

# Read Python config file again
python_config = oci.config.from_file(file_location=input_config_file)

# Create tmp folder for files to be SCPd
if not os.path.exists('tmp'):
    os.makedirs('tmp')
tmp_folder = Path("tmp")

#If image OICD provided is null in properties value, pick the latest image of OS Oracle Linux
if(input_image_id==''):
    for image in paginate(compute_client.list_images,compartment_id=tenancy_id,operating_system ='Oracle Linux',sort_by='TIMECREATED'):
        #print(image.display_name)
        #if ("Gen2-GPU" not in image.display_name):
        #if ("Oracle-Linux-7.8-2020.07.28-0" in image.display_name):
        if ("Gen2-GPU" not in image.display_name and "Oracle-Linux-7.8" in image.display_name):
            input_image_id = image.id
            break

# Get Region wise data
linux_image_id = {}
windows_image_id = {}
variables_data = {}
for key in ct.region_dict:
    linux_image_id.setdefault(key, '')
    windows_image_id.setdefault(key, '')
    variables_data.setdefault(key, '')

new_config = python_config
for region in regions:
    region = region.strip().lower()
    new_config.__setitem__("region", ct.region_dict[region])
    cc = oci.core.ComputeClient(new_config)
    #fetch latest image ocids
    for image in paginate(cc.list_images,compartment_id=tenancy_id,operating_system ='Oracle Linux',sort_by='TIMECREATED'):
        if ("Gen2-GPU" not in image.display_name):
            linux_image_id[region] = image.id
            break
    for image in paginate(cc.list_images, compartment_id=tenancy_id, operating_system='Windows', sort_by='TIMECREATED'):
        if ("Gen2-GPU" not in image.display_name):
            windows_image_id[region] = image.id
            break

    # write variables data
    today = datetime.today()
    dt = str(today.day) + calendar.month_name[today.month] + str(today.year)


    variables_data[region] = """variable "ssh_public_key" {
            type = string
            default = \"""" + input_ssh_key1 + """"
    }
    variable "tenancy_ocid" {
            type = string
            default = \"""" + tenancy_id + """"
    }
    variable "user_ocid" {
            type = string
            default = \"""" + python_config['user'] + """"
    }
    variable "compartment_ocid" {
            type = string
            default = \"""" + vm_compartment_ocid + """"
    }
    variable "ntk_compartment_ocid" {
            type = string
            default = \"""" + ntk_compartment_ocid + """"
    }
    #Added below variable because tf file generated through Koala uses this variable for network components
    variable "compartment_id" {
            type = string
            default = \"""" + ntk_compartment_ocid + """"
    }
    variable "fingerprint" {
            type = string
            default = \"""" + python_config['fingerprint'] + """"
    }
    variable "private_key_path" {
            type = string
            default = "/root/ocswork/keys/oci_api_key.pem"
    }
    variable "region" {
            type = string
            default = \"""" + ct.region_dict[region] + """"
    }
    """
    if (windows_image_id[region] != ''):
        variables_data[region] = variables_data[region] + """
    #Example for OS value 'Windows' in Instances sheet
    variable "Windows" {
            type = string
            default = \"""" + windows_image_id[region] + """"
            description = "Latest ocid as on """ + dt + """"
    }"""
    if (linux_image_id[region] != ''):
        variables_data[region] = variables_data[region] + """
    #Example for OS value 'Linux' in Instances sheet
    variable "Linux"{
            type = string
            default = \"""" + linux_image_id[region] + """"
            description = "Latest ocid as on """ + dt + """"
    }"""
    write_file("variables_" + region + ".tf", variables_data[region])

# Writing public keys to a file
public_key_data = input_ssh_key1
if (input_ssh_key2 != ''):
    public_key_data = input_ssh_key1 + "\n" + input_ssh_key2
if (input_ssh_key3 != ''):
    public_key_data = public_key_data + "\n" + input_ssh_key3

write_file("ocs_public_keys.txt", public_key_data)

# Writing Terraform config files provider.tf and variables.tf
provider_data = """provider "oci" {
  version          = ">= 3.0.0"
  tenancy_ocid     = var.tenancy_ocid
  user_ocid        = var.user_ocid
  fingerprint      = var.fingerprint
  private_key_path = var.private_key_path
  region           = var.region
}"""
write_file("provider.tf", provider_data)

# write git expect script to download python code
if (input_configure_git_oci == "1"):
    script_data = """
    cd /root/ocswork/git_oci
    set timeout -1
    git pull ssh://idcs-1c7c880a11284a04a8f72d257e67de9f.""" + input_git_username.replace('@', '%40') + """@nac-gc39002.developer.ocp.oraclecloud.com/nac-gc39002_oci_262/oci.git
    """
    write_file("download_git_oci.sh", script_data)
if (input_configure_git_ocictooci == "1"):
    script_data = """
    cd /root/ocswork/git_ocic2oci
    set timeout -1
    git pull ssh://idcs-1c7c880a11284a04a8f72d257e67de9f.""" + input_git_username.replace('@', '%40') + """@nac-gc39002.developer.ocp.oraclecloud.com/nac-gc39002_ocic2oci_182/ocictooci.git
    """
    write_file("download_git_ocic2oci.sh", script_data)

# write Panda specific files
if (input_configure_panda == "1"):
    # write TF file for OCIC TF Provider
    provider_panda_data = """provider "opc" {
user            = var.user
password        = var.password
identity_domain = \"""" + input_ocic_identity_domain + """"
endpoint        = var.endpoint
}"""
    write_file("ocic-provider.tf", provider_panda_data)

    # write TF file for for OCIC TF Variables
    variables_panda_data = """
variable "user" {
        type = string
        default = \"""" + input_ocic_username + """"
}
variable "password" {
        type = string
        default = \"""" + input_ocic_password + """"
}
variable "endpoint" {
        type = string
        default = \"""" + input_ocic_compute_endpoint + """"
}
variable "domain" {
       type = string
       default = \"""" + input_ocic_identity_domain + """"
}
"""
    write_file("ocic-variables.tf", variables_panda_data)

    terraform_upgrade_expect_data = """#!/usr/bin/expect
set answer yes
cd /root/ocswork/ocic2oci_work
spawn terraform 0.12upgrade
expect "Enter a value:" {send "$answer\\r"}
sleep 20
expect eof
"""
    write_file("upgrade_terraform_expect_script.sh", terraform_upgrade_expect_data)

    # write TF file for Panda instance creation in OCIC
    tf_data = """ 
resource "opc_compute_storage_volume" "panda_boot_vol" {
  name = \"oraclemigration/""" + input_ocic_tf_prefix_for_panda + """_Panda-Boot_Vol"
  size = 1536
}

resource "opc_compute_instance" "panda_new" {
 name       = \"oraclemigration/""" + input_ocic_tf_prefix_for_panda + """_Panda-OCIC2OCI"
 label      = "Terraform Provisioned Panda-WithAPI"
 shape      = "oc3"
 image_list = "/oracle/public/OL_7.5_UEKR4_x86_64_MIGRATION"

  storage {
    volume = opc_compute_storage_volume.panda_boot_vol.name
    index  = 1
  }
   networking_info {
   index          = 0
   nat            =[opc_compute_ip_reservation.panda_new.name]
   shared_network = true
  }

  networking_info {
   index          = 1
   ip_network     = opc_compute_ip_network.panda_new.id
   shared_network = false
   vnic = \"""" + input_ocic_tf_prefix_for_panda + """_Panda-OCIC2OCI-vnic"
   """
    tf_data = tf_data + "vnic_sets = [\"" + input_ocic_vnicset_for_panda
    tf_data = tf_data + """"]

 }
 ssh_keys = [opc_compute_ssh_key.OCS-Panda-ssh-key.name]

}
resource "opc_compute_ssh_key" "OCS-Panda-ssh-key" {
 name    = \"""" + input_ocic_tf_prefix_for_panda + """_Panda-OCIC2OCI-SSHKey"
 """
    tf_data = tf_data + "key    =  \"" + input_ssh_key1 + "\""
    tf_data = tf_data + """
 enabled = true
}
resource "opc_compute_ip_reservation" "panda_new" {
  name            = \"""" + input_ocic_tf_prefix_for_panda + """_Panda-OCIC2OCI-IP-Reservation"
  parent_pool = "/oracle/public/ippool"
  permanent   = true
}

resource "opc_compute_ip_network" "panda_new" {
 name                = \"""" + input_ocic_tf_prefix_for_panda + """_Panda-OCIC2OCI--IP-Network"
 """
    tf_data = tf_data + "ip_address_prefix   = \"""" + input_ocic_ip_network_for_panda + """"
}
"""

    write_file("panda.tf", tf_data)
    ### Have to write the ansible files to create the storage disk.
    # write profile file required for opc cli
    username_full = "/Compute-" + input_ocic_identity_domain + '/' + input_ocic_username
    # config file for koala
    file_data = """{
        "global": {
        "format": "text",
        "debug-request": false
        },
        \
        "compute": {
        "user": \"""" + username_full + """",
        "endpoint": \"""" + input_ocic_compute_endpoint.replace("https://", "") + """",
        "password-file": "/root/.opc/profiles/password"
        }
        }
        """
    write_file("compute", file_data)
    write_file("password", input_ocic_password)

    script_data = """
    container=\"""" + username_full + """"
    password=\"""" + input_ocic_password + """"
    endpoint=\"""" + input_ocic_compute_endpoint + """"

    targetControllerName=`opc -p compute compute instance list \"""" + username_full + """" | grep Panda-OCIC2OCI`
    ctlsInstanceName=`opc -p compute compute instance list \"""" + username_full + """" | grep Panda-OCIC2OCI | awk -F"$container/" '{print $NF}'`

    vc_id_tmp=`opc -p compute -F vcable_id compute instance get $targetControllerName | sed -e "s/vcable_id//"`
    vc_id=${vc_id_tmp//[[:blank:]]/}

    ip_as_list=`opc -p compute compute ip-association list \"""" + username_full + """" --vcable $vc_id | sed -e "s/NAME//"`

    panda_pub_ip_tmp=`opc -p compute -F ip compute ip-association get $ip_as_list | sed -e "s/ip//"`
    panda_pub_ip=${panda_pub_ip_tmp//[[:blank:]]/}
    """
    write_file("fetch_panda_details.sh", script_data)

# write Koala specific files
if (input_configure_koala == "1"):
    username_full = "/Compute-" + input_ocic_identity_domain + '/' + input_ocic_username
    # config file for koala
    file_data = """{
    "global": {
    "format": "text",
    "debug-request": false
    },
    \
    "compute": {
    "user": \"""" + username_full + """",
    "endpoint": \"""" + input_ocic_compute_endpoint.replace("https://", "") + """"
    }
    }
    """
    write_file("default", file_data)
    # expect script to run koala discover
    script_data = """#!/usr/bin/expect
    set password """ + input_ocic_password + """
    cd /root/ocswork/ocic2oci_work
    set timeout -1
    #spawn /usr/local/bin/opcmigrate discover
    spawn /opt/rh/rh-python36/root/usr/bin/opcmigrate discover
    expect "Compute Classic Password" {send "$password\\r"}
    #sleep 60
    expect eof
    """
    write_file("discover_koala_expect.sh", script_data)

tenant_name = identity_client.get_tenancy(tenancy_id=python_config['tenancy']).data.name

# Creating VM
if (input_create_vm == "1"):
    ad_name = python_config[input_ad_name]
    vcn_found = 0
    igw_found = 0
    ngw_found = 0
    subnet_found = 0
    igw_ocid = ''
    ngw_ocid = ''

    # Check if VCN with same CIDR already exists and if it exists then check for other components
    default_route_table_id = ''
    for vcn in paginate(network_client.list_vcns, compartment_id=ocs_compartment_ocid):
        if (vcn.cidr_block == input_vcn_cidr):
            print("VCN with this CIDR already exists..Reusing same for OCS Work. VCN name is " + vcn.display_name)
            vcn_ocid = vcn.id
            default_route_table_id = vcn.default_route_table_id
            vcn_found = 1

            # Check if subnet also exists
            for subnet in paginate(network_client.list_subnets, compartment_id=ocs_compartment_ocid, vcn_id=vcn_ocid):
                if (subnet.cidr_block == input_subnet_cidr):
                    subnet_ocid = subnet.id
                    subnet_private = subnet.prohibit_public_ip_on_vnic
                    subnet_route_table_id = subnet.route_table_id
                    subnet_found = 1

                    if (subnet_private == True):
                        print("Subnet with this CIDR already exists..Reusing same for OCS Work. Subnet name is " + subnet.display_name + " It is private subnet. Will attach NGW to the route table")
                        #Check if NGW exists for the VCN
                        for ngw in paginate(network_client.list_nat_gateways, compartment_id=ocs_compartment_ocid,vcn_id=vcn.id):
                            ngw_ocid = ngw.id
                            print("NGW exists for this VCN")
                            ngw_found = 1
                            break
                        if (ngw_found == 0):
                            print('Creating NGW')
                            create_ngw_details = oci.core.models.CreateNatGatewayDetails(compartment_id=ocs_compartment_ocid, display_name="NGW", vcn_id=vcn_ocid)
                            ngw = network_client.create_nat_gateway(create_ngw_details)
                            ngw_ocid = ngw.data.id
                        # Create Route Rule
                        route_rule = oci.core.models.RouteRule(destination='0.0.0.0/0', destination_type='CIDR_BLOCK',
                                                               network_entity_id=ngw_ocid)
                    if (subnet_private == False):
                        print("Subnet with this CIDR already exists..Reusing same for OCS Work. Subnet name is " + subnet.display_name + " It is public subnet. Will attach IGW to the route table")
                        for igw in paginate(network_client.list_internet_gateways, compartment_id=ocs_compartment_ocid,vcn_id=vcn.id):
                            igw_ocid = igw.id
                            print("IGW exists for this VCN")
                            igw_found = 1
                            break
                        if (igw_found == 0):
                            print('Creating IGW')
                            create_igw_details = oci.core.models.CreateInternetGatewayDetails(
                                compartment_id=ocs_compartment_ocid, display_name=input_igw_name, is_enabled=True,
                                vcn_id=vcn_ocid)
                            igw = network_client.create_internet_gateway(create_igw_details)
                            igw_ocid = igw.data.id
                        # Create Route Rule
                        route_rule = oci.core.models.RouteRule(destination='0.0.0.0/0',
                                                               destination_type='CIDR_BLOCK',
                                                               network_entity_id=igw_ocid)
                    break

            break

    # Creates OCS VCN in the specified OCS compartment
    if (vcn_found == 0):
        print('Creating VCN: ' + input_vcn_name)
        # Converting vcn name to alphanumeric string
        regex = re.compile('[^a-zA-Z0-9]')
        vcn_dns = regex.sub('', input_vcn_name)
        vcn_dns_label = (vcn_dns[:15]) if len(vcn_dns) > 15 else vcn_dns

        create_vcn_details=oci.core.models.CreateVcnDetails(cidr_block=input_vcn_cidr,dns_label=vcn_dns_label,compartment_id=ocs_compartment_ocid, display_name=input_vcn_name)
        vcn=network_client.create_vcn(create_vcn_details)
        vcn_ocid=vcn.data.id

    # Creating subnet
    if (subnet_found == 0):
        subnet_private = False
        print('Creating public SUBNET: ' + input_subnet_name + ' with default route table, security list and dhcp options')
        # Converting subnet name to alphanumeric string
        regex = re.compile('[^a-zA-Z0-9]')
        subnet_dns = regex.sub('', input_subnet_name)
        subnet_dns_label = (subnet_dns[:15]) if len(subnet_dns) > 15 else subnet_dns

        create_subnet_details = oci.core.models.CreateSubnetDetails(availability_domain=ad_name,
                                                                    cidr_block=input_subnet_cidr,
                                                                    dns_label=subnet_dns_label,
                                                                    compartment_id=ocs_compartment_ocid,
                                                                    display_name=input_subnet_name, vcn_id=vcn_ocid)
        subnet = network_client.create_subnet(create_subnet_details)
        subnet_ocid = subnet.data.id
        subnet_route_table_id = subnet.data.route_table_id
        print('Creating IGW')
        create_igw_details = oci.core.models.CreateInternetGatewayDetails(
            compartment_id=ocs_compartment_ocid, display_name=input_igw_name, is_enabled=True,
            vcn_id=vcn_ocid)
        igw = network_client.create_internet_gateway(create_igw_details)
        igw_ocid = igw.data.id
        route_rule = oci.core.models.RouteRule(destination='0.0.0.0/0', destination_type='CIDR_BLOCK',
                                               network_entity_id=igw_ocid)

    # Updating route table to allow internet access along with existing rules
    subnet_rt_table = network_client.get_route_table(rt_id=subnet_route_table_id)
    existing_rules_list = subnet_rt_table.data.route_rules

    add_rule = 1
    for rule in existing_rules_list:
        if (route_rule.destination == rule.destination):
            print("Route Rule with 0.0.0.0/0 destination already exists in the route table. Not adding any new route rule now. Please verify internet access for OCS VM")
            add_rule = 0

    if (add_rule == 1):
        existing_rules_list.append(route_rule)
        update_route_details = oci.core.models.UpdateRouteTableDetails(route_rules=existing_rules_list)
        network_client.update_route_table(rt_id=subnet_route_table_id, update_route_table_details=update_route_details)

    lpg_found = 0
    print('Creating LPG')
    for lpg in paginate(network_client.list_local_peering_gateways, compartment_id=ocs_compartment_ocid, vcn_id=vcn_ocid):
        if(lpg.display_name==input_lpg_to_orig_name):
            lpg_ocid = lpg.id
            print("LPG with same name exists for this VCN..Reusing same for OCSWork")
            lpg_to_orig_ocid = lpg_ocid
            lpg_found = 1
            break
    if(lpg_found==0):
        create_lpg_details=oci.core.models.CreateLocalPeeringGatewayDetails(compartment_id=ocs_compartment_ocid, display_name=input_lpg_to_orig_name,vcn_id=vcn_ocid)
        lpg=network_client.create_local_peering_gateway(create_lpg_details)
        lpg_to_orig_ocid = lpg.data.id

    lpg_to_mirror_ocid = ''
    lpg_to_rsync_ocid = ''
    if (input_lpg_to_mirror_name != ''):
        create_lpg_details = oci.core.models.CreateLocalPeeringGatewayDetails(compartment_id=ocs_compartment_ocid,
                                                                          display_name=input_lpg_to_mirror_name, vcn_id=vcn_ocid)
        lpg = network_client.create_local_peering_gateway(create_lpg_details)
        lpg_to_mirror_ocid = lpg.data.id

    if (input_lpg_to_rsync_name != ''):
        create_lpg_details = oci.core.models.CreateLocalPeeringGatewayDetails(compartment_id=ocs_compartment_ocid,
                                                                          display_name=input_lpg_to_rsync_name, vcn_id=vcn_ocid)
        lpg = network_client.create_local_peering_gateway(create_lpg_details)
        lpg_to_rsync_ocid = lpg.data.id

    encoded_user_data = ""
    if ("darwin" in sys.platform):
        out = subprocess.Popen(["/usr/bin/base64", input_user_data_file], stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
        stdout, stderr = out.communicate()
        write_file("output.txt", stdout.decode("utf-8"))
        time.sleep(5)
    elif("win" in sys.platform):
        output=subprocess.Popen(("certutil.exe -encode "+ input_user_data_file + " tmp\\output.txt"),stdout=subprocess.PIPE).stdout
        output.close()
        time.sleep(5)

    elif ("linux" in sys.platform):
        out = subprocess.Popen(["/bin/base64", input_user_data_file], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout, stderr = out.communicate()
        write_file("output.txt", stdout.decode("utf-8"))
        time.sleep(5)

    file = tmp_folder / 'output.txt'
    f = open(file, 'r')
    for line in f:
        if not (line.__contains__("CERTIFICATE")):
            encoded_user_data = encoded_user_data + line
    f.close()

    encoded_user_data = encoded_user_data.replace('\n', '')

    print('Creating VM: ' + input_vm_name)
    multiple_ssh_keys = input_ssh_key1
    if (input_ssh_key2 != ''):
        multiple_ssh_keys = input_ssh_key1 + "\n" + input_ssh_key2
    if (input_ssh_key3 != ''):
        multiple_ssh_keys = multiple_ssh_keys + "\n" + input_ssh_key3

    create_source_details = oci.core.models.InstanceSourceViaImageDetails(source_type="image", image_id=input_image_id)
    metadata = {"ssh_authorized_keys": multiple_ssh_keys, "user_data": encoded_user_data}
    create_vnic_details = oci.core.models.CreateVnicDetails(subnet_id=subnet_ocid, assign_public_ip=False)
    launch_instance_details=oci.core.models.LaunchInstanceDetails(availability_domain=ad_name,compartment_id=ocs_compartment_ocid,
                                                                  display_name=input_vm_name,shape=input_vm_shape,
                                                                  source_details=create_source_details,metadata=metadata,
                                                                  create_vnic_details=create_vnic_details)
    instance=compute_client.launch_instance(launch_instance_details)

    # wait till Instance comes to RUNNING state
    print('Waiting for instance to come to RUNNING state...')
    new_instance=instance.data
    get_instance_response=oci.wait_until(compute_client,compute_client.get_instance(new_instance.id),'lifecycle_state', 'RUNNING')
    #Fetch public IP address of the VM
    instance_ocid=new_instance.id
    vnicAttachments =compute_client.list_vnic_attachments(compartment_id=ocs_compartment_ocid,instance_id=instance_ocid)
    for vnicAttachment in vnicAttachments.data:
        vnic_ocid = vnicAttachment.vnic_id
    vnic = network_client.get_vnic(vnic_ocid)

    ip = ''
    """public_ip=vnic.data.public_ip
    if(public_ip!=None):
        print('Public IP of VM: '+public_ip)
        ip=public_ip
    """
    private_ip = vnic.data.private_ip
    print('Private IP of VM: ' + private_ip)
    ip = private_ip

    # Attach Reserved Public IP if subnet is public subnet
    if (subnet_private == False):
        private_ip_ids = network_client.list_private_ips(vnic_id=vnic_ocid)
        for pvtipid in private_ip_ids.data:
            pvtip_ocid = pvtipid.id

    #if(ip==''):
    #    ip=private_ip
    # create Reserved Public IP
        reserved_ip_exists= False
        tenancy_public_ips = network_client. list_public_ips(scope="REGION", compartment_id=ocs_compartment_ocid, lifetime ="RESERVED")
        for tenancy_public_ip in tenancy_public_ips.data:
            if(tenancy_public_ip.display_name==input_vm_name and tenancy_public_ip.private_ip_id == None):
                reserved_ip_exists=True
                update_public_ip_details = oci.core.models.UpdatePublicIpDetails(private_ip_id=pvtip_ocid)
                public_ip_id=network_client.update_public_ip(public_ip_id =tenancy_public_ip.id, update_public_ip_details=update_public_ip_details)


        if(reserved_ip_exists==False):
            create_public_ip_details = oci.core.models.CreatePublicIpDetails(display_name=input_vm_name,compartment_id=ocs_compartment_ocid,lifetime="RESERVED", private_ip_id=pvtip_ocid)
            public_ip_id=network_client.create_public_ip(create_public_ip_details=create_public_ip_details)

        # Get public IP
        public_ip_id = public_ip_id.data
        public_ip_ocid = public_ip_id.id
        public_ip = public_ip_id.ip_address
        if (public_ip != None):
            print('Reserved Public IP of VM: ' + public_ip)
            ip = public_ip

    print("\nWriting OCID info to file: " + del_config_file + " required for cleanup script")
    # Write to config file for cleanup
    with open(input_config_file, 'r') as file:
        existing_data = file.read()
        append_file(del_config_file, existing_data)

    append_file(del_config_file, "Tenant_Name=" + tenant_name)
    append_file(del_config_file, "vcn_ocid=" + vcn_ocid)
    if (igw_ocid != ''):
        append_file(del_config_file, "igw_ocid=" + igw_ocid)
    if (ngw_ocid != ''):
        append_file(del_config_file, "ngw_ocid=" + ngw_ocid)

    append_file(del_config_file, "lpg_to_orig_ocid=" + lpg_to_orig_ocid)

    if (lpg_to_mirror_ocid != ''):
        append_file(del_config_file, "lpg_to_mirror_ocid=" + lpg_to_mirror_ocid)
    if (lpg_to_rsync_ocid != ''):
        append_file(del_config_file, "lpg_to_rsync_ocid=" + lpg_to_rsync_ocid)

    # append_file(del_config_file, "ocswork_instance_ocid=" + instance_ocid)
    updatePropsFile(del_config_file, "ocswork_instance_ocid", instance_ocid)

    if (public_ip != None):
        append_file(del_config_file, "public_ip=" + public_ip)
        append_file(del_config_file, "ocswork_reservedpublic_ocid=" + public_ip_ocid)

    append_file(del_config_file, "private_ip=" + private_ip)

    if (default_route_table_id == ''):
        default_route_table_id = subnet_route_table_id
    append_file(del_config_file, "def_rt_table_ocid=" + default_route_table_id)

    append_file(del_config_file, "subnet_ocid=" + subnet_ocid)

    append_file(del_config_file, "compartment_name=" + input_ocs_compartment_name + "\n")

    # write below details also to the config file so that it can be used later while creating the network for client
    updatePropsFile(input_config_file, "ocs_vcn_ocid", vcn_ocid)
    updatePropsFile(input_config_file, "ocs_subnet_ocid", subnet_ocid)
    updatePropsFile(input_config_file, "ocs_lpg_to_orig_ocid", lpg_to_orig_ocid)
    if (lpg_to_mirror_ocid != ''):
        updatePropsFile(input_config_file, "ocs_lpg_to_mirror_ocid", lpg_to_mirror_ocid)
    if (lpg_to_rsync_ocid != ''):
        updatePropsFile(input_config_file, "ocs_lpg_to_rsync_ocid", lpg_to_rsync_ocid)
    updatePropsFile(input_config_file, "ocswork_instance_ocid", instance_ocid)

    # scp private key and config files to VM
    print('\nCopying required files to the VM')
    time.sleep(5)

    f = open(input_pvt_key_file, "r")
    putty_pvtkey_contents = f.read()
    f.close()
    openSSHpvtKeyFile = str(tmp_folder / "openSSHpvtKeyFile")
    f = open(openSSHpvtKeyFile, "w+")
    f.write(puttykeys.ppkraw_to_openssh(putty_pvtkey_contents))
    f.close()

    ssh = SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    for x in range(10):
        try:
            ssh.connect(ip, username='opc', key_filename=openSSHpvtKeyFile)
            print('Connected to VM for file transfer')
            break
        except Exception as e:
            print(e)
            print('Trying again..')
            time.sleep(2)

    provider = str(tmp_folder / 'provider.tf')
    koala = str(tmp_folder / 'default')
    script_file = input_shell_script
    upload_git_script1 = str(tmp_folder / 'download_git_oci.sh')
    upload_git_script2 = str(tmp_folder / 'download_git_ocic2oci.sh')
    discover_koala_script = str(tmp_folder / 'discover_koala_expect.sh')
    upgrade_terraform_script = str(tmp_folder / 'upgrade_terraform_expect_script.sh')
    public_key_file = str(tmp_folder / 'ocs_public_keys.txt')

    sftp = ssh.open_sftp()
    print('Copying Python Config File..')
    sftp.put(input_config_file, '/home/opc/config')
    print('Copying private key File for OCI communication..')
    sftp.put(python_config['key_file'], '/home/opc/oci_api_key.pem')
    print('Copying private key to login to VM..')
    sftp.put(input_pvt_key_file, '/home/opc/ssh-pvt-key.ppk')
    print('Copying file containing OCS public keys..')
    sftp.put(public_key_file, '/home/opc/ocs_public_keys.txt')
    print('Copying OCI Terraform files..')
    sftp.put(provider, '/home/opc/provider.tf')
    for region in regions:
        region = region.strip().lower()
        ssh.exec_command("sudo mkdir -p /root/ocswork/terraform_files/" + region)
        file = "variables_" + region + ".tf"
        sftp.put(str(tmp_folder / file), '/home/opc/variables_' + region + '.tf')
        mv_variables_cmd = "sudo mv /home/opc/variables_" + region + ".tf /root/ocswork/terraform_files/" + region
        mv_provider_cmd = "sudo cp /home/opc/provider.tf /root/ocswork/terraform_files/" + region
        ssh.exec_command(mv_variables_cmd)
        ssh.exec_command(mv_provider_cmd)

    if (input_configure_panda == "1"):
        print('Copying generated files for Panda Server Creation..')
        sftp.put(str(tmp_folder / 'panda.tf'), '/home/opc/panda.tf')
        sftp.put(str(tmp_folder / 'ocic-provider.tf'), '/home/opc/ocic-provider.tf')
        sftp.put(str(tmp_folder / 'ocic-variables.tf'), '/home/opc/ocic-variables.tf')
        sftp.put(str(tmp_folder / 'upgrade_terraform_expect_script.sh'), '/home/opc/upgrade_terraform_expect_script.sh')
        sftp.put(str(tmp_folder / 'compute'), '/home/opc/compute')
        sftp.put(str(tmp_folder / 'password'), '/home/opc/password')
        sftp.put(str(tmp_folder / 'fetch_panda_details.sh'), '/home/opc/fetch_panda_details.sh')

    if (input_configure_koala == "1"):
        print('Copying Koala files..')
        sftp.put(koala, '/home/opc/default')
        sftp.put(discover_koala_script, '/home/opc/discover_koala_expect.sh')
    if (input_configure_git_oci == "1" or input_configure_git_ocictooci == "1"):
        print('Copying private key file for GIT..')
        sftp.put(input_git_pvt_key_file, '/home/opc/id_rsa')
    if (input_configure_git_oci == "1"):
        print('Copying OCI GIT download script file..')
        sftp.put(upload_git_script1, '/home/opc/download_git_oci.sh')
    if (input_configure_git_ocictooci == "1"):
        print('Copying OCICTOOCI GIT download script file..')
        sftp.put(upload_git_script2, '/home/opc/download_git_ocic2oci.sh')

    print('Copying shell script file to setup the VM..')

    if input_run_shell_script == "1":
        sftp.put(script_file, '/home/opc/shell_script.sh')
    else:
        sftp.put(script_file, '/home/opc/shell_script_do_not_run_auto.sh')
    sftp.close()
    print('sudo to root to view /var/log/messages to check cloud-init progress')

if input_cleanup == "1":
    shutil.rmtree('tmp')