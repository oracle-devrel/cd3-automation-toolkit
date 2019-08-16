import configparser
import argparse
import oci
import re
import subprocess
import time
import os
import paramiko
import shutil
from paramiko import SSHClient
import puttykeys
from string import ascii_lowercase
from itertools import count as letter_count

parser = argparse.ArgumentParser(description="Creates OCS Work related components")
parser.add_argument("propsfile",help="Full Path of properties file. eg ocswork.properties")

args = parser.parse_args()
config = configparser.RawConfigParser()
config.read(args.propsfile)

#Read Config file Variables
try:
    input_config_file=config.get('Default','python_config_file').strip()
    input_ocs_compartment_name=config.get('Default','ocs_compartment_name').strip()
    input_vm_compartment_name=config.get('Default','vm_compartment_name').strip()
    input_ntk_compartment_name=config.get('Default','ntk_compartment_name').strip()
    input_regions = config.get('Default', 'regions').strip()
    input_ssh_key1=config.get('Default','ssh_key1').strip()
    input_ssh_key2=config.get('Default', 'ssh_key2').strip()
    input_ssh_key3=config.get('Default', 'ssh_key3').strip()
    input_ocic_username=config.get('Default','ocic_username').strip()
    input_ocic_password=config.get('Default','ocic_password').strip()
    input_ocic_rest_endpoint=config.get('Default','ocic_rest_endpoint').strip()
    input_ocic_identity_domain=config.get('Default','ocic_identity_domain').strip()
    input_ocic_compute_endpoint=config.get('Default','ocic_compute_endpoint').strip()
    input_git_username=config.get('Default','git_username').strip()
    input_git_password=config.get('Default','git_password').strip()
    input_vcn_name=config.get('Default','ocs_vcn_name').strip()
    input_vcn_cidr=config.get('Default','ocs_vcn_cidr').strip()
    input_igw_name=config.get('Default','ocs_igw_name').strip()
    input_lpg_to_orig_name=config.get('Default','ocs_lpg_to_orig_name').strip()
    input_lpg_to_mirror_name = config.get('Default', 'ocs_lpg_to_mirror_name').strip()
    input_lpg_to_rsync_name = config.get('Default', 'ocs_lpg_to_rsync_name').strip()
    input_subnet_name=config.get('Default','ocs_subnet_name').strip()
    input_subnet_cidr=config.get('Default','ocs_subnet_cidr').strip()
    input_ad_name=config.get('Default','ocs_input_ad').strip()
    input_vm_name=config.get('Default','ocs_vm_name').strip()
    input_vm_shape=config.get('Default','ocs_vm_shape').strip()
    input_image_id=config.get('Default','ocs_vm_source_image_ocid').strip()
    input_user_data_file=config.get('Default','ocs_user_data_file').strip()
    input_pvt_key_file=config.get('Default','pvt_key_file').strip()
    input_shell_script=config.get('Default','shell_script_name')

    input_configure_panda = config.get('Default', 'configure_panda').strip()
    input_configure_koala = config.get('Default', 'configure_koala').strip()
    input_configure_git_oci = config.get('Default', 'configure_git_oci').strip()
    input_configure_git_ocictooci = config.get('Default', 'configure_git_ocictooci').strip()

    input_ocic_ip_network_for_panda = config.get('Default','ocic_ip_network_for_panda').strip()
    input_ocic_vnicset_for_panda = config.get('Default','ocic_vnicset_for_panda').strip()
    input_ocic_tf_prefix_for_panda = config.get('Default','ocic_tf_prefix_for_panda').strip()
    input_ocic_panda_storage_volume_size = int(config.get('Default','ocic_panda_storage_volume_size').strip())
    input_ocic_panda_storage_volume_disks = int(config.get('Default','ocic_panda_storage_volume_disks').strip())
    input_ocic_panda_storage_pvlv_name = config.get('Default','ocic_panda_storage_pvlv_name').strip()

    input_create_vm = config.get('Default','create_vm').strip()
    input_cleanup = config.get('Default','cleanup').strip()

except Exception as e:
    print(e)
    print('Check if all property values exist and try again..exiting...`    ')
    exit()

if input_ocic_panda_storage_volume_size > 2048:
    print ("Storage volume in OCIC cannot be greater than 2Tb. Setting to 1.5T ")
    input_ocic_panda_storage_volume_size = 1536
if(input_ntk_compartment_name=='' or input_vm_compartment_name=='' or input_ocs_compartment_name==''):
    print("Compartment names cannot be null. Exiting...")
    exit()
if(input_ssh_key1==''):
    print("ssh_key1 cannot be left blank. Exiting...")
    exit()
if(input_regions==''):
    print("regions cannot be left blank. Exiting...")
    exit()
if os.path.isfile(input_pvt_key_file)==False:
        print("input private key file corresponding to ssh_key1 does not exist. Exiting....")
        exit()

if(input_vcn_name==''):
    input_vcn_name='OCS_VCN'
if(input_igw_name==''):
    input_igw_name='igw'
if(input_lpg_to_orig_name==''):
    input_lpg_to_orig_name='lpg'
if(input_subnet_name==''):
    input_subnet_name='OCS_Subnet'
if(input_vcn_cidr==''):
    input_vcn_cidr='10.10.0.0/16'
if(input_subnet_cidr==''):
    input_subnet_cidr='10.10.1.0/24'
if(input_ad_name==''):
    input_ad_name='ad_1'
if(input_vm_name==''):
    input_vm_name = 'OCS_VM'
if(input_vm_shape==''):
    input_vm_shape='VM.Standard2.4'
if(input_user_data_file==''):
    input_user_data_file='cloud_init_script'
if(input_shell_script==''):
    input_shell_script='shell_script.sh'


#Read Python config file
python_config = oci.config.from_file(file_location=input_config_file)#,profile_name=input_region_name)


network_client = oci.core.VirtualNetworkClient(python_config)
identity_client = oci.identity.IdentityClient(python_config)
compute_client = oci.core.ComputeClient(python_config)
regions=input_regions.split(",")
region_dict = {'ashburn':'us-ashburn-1','phoenix':'us-phoenix-1','london':'uk-london-1','frankfurt':'eu-frankfurt-1','toronto':'ca-toronto-1','tokyo':'ap-tokyo-1','seoul':'ap-seoul-1','mumbai':'ap-mumbai-1'}

def write_file(file_name,file_data):
    f=open(file_name,"w+")
    f.write(file_data)
    f.close()

#del_config_file = input_config_file
del_config_file = "config_for_delete"

def append_file(file_name,file_data):
    f = open(file_name, "a+")
    f.write(file_data)
    f.write("\n")
    f.close()

def updatePropsFile(file_name,key, update_value):
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
       # if("OCS" in compartment_desc):
        #    print('Waiting till OCS compartment becomes ACTIVE...')
         #   oci.wait_until(identity_client, identity_client.get_compartment(compartment_ocid), 'lifecycle_state','ACTIVE')
    except oci.exceptions.ServiceError as e:
        error_msg = "Compartment '" + compartment_name + "' already exists"
        if (e.message == error_msg):
            print('This compartment already exists')
            for compartment in paginate(identity_client.list_compartments, compartment_id=tenancy_id):
                if compartment_name == identity_client.name:
                    compartment_ocid = compartment.id
                    break

        elif ("home region" in e.message):
            print ("Home Region " + e.message)
            new_config = python_config
            message = e.message
            if ("IAD" in message):
                new_config.__setitem__("region",region_dict['ashburn'])
            if ("PHX" in message):
                new_config.__setitem__("region", region_dict['phoenix'])
            if ("YYZ" in message):
                new_config.__setitem__("region", region_dict['toronto'])
            if ("FRA" in message):
                new_config.__setitem__("region", region_dict['frankfurt'])
            if ("LHR" in message):
                new_config.__setitem__("region", region_dict['london'])
            if ("BOM" in message):
                new_config.__setitem__("region", region_dict['mumbai'])
            if ("ICN" in message):
                new_config.__setitem__("region", region_dict['seoul'])
            if ("NRT" in message):
                new_config.__setitem__("region", region_dict['tokyo'])

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
            print (e.message)
            compartment_ocid = "-1"
    return compartment_ocid


#Fetch AD names
print('Fetching AD names from tenancy and writing to config file if doesnt exist')
tenancy_id = python_config['tenancy']
conf_file = open(input_config_file,"a")
i = 1
for ad in paginate(identity_client.list_availability_domains,compartment_id = tenancy_id):
	ad_name = "ad_" + str(i)
	if not ad_name in python_config:
		conf_file.write("ad_" + str(i) + "=" + ad.name + "\n")
	i = i + 1
conf_file.close()


ocs_compartment_found=0
vm_compartment_found=0
ntk_compartment_found=0

for compartment in paginate(identity_client.list_compartments, compartment_id=tenancy_id, compartment_id_in_subtree=True ):
    if(compartment.name== input_ocs_compartment_name):
        ocs_compartment_found=1
        ocs_compartment_ocid=compartment.id
        updatePropsFile(input_config_file, "ocs_compartment_ocid", ocs_compartment_ocid)
    if(compartment.name== input_vm_compartment_name):
        vm_compartment_found=1
        vm_compartment_ocid=compartment.id
        updatePropsFile(input_config_file, "vm_compartment_ocid", vm_compartment_ocid)
    if(compartment.name== input_ntk_compartment_name):
        ntk_compartment_found=1
        ntk_compartment_ocid=compartment.id
        updatePropsFile(input_config_file, "ntk_compartment_ocid",ntk_compartment_ocid)


#Create all 3 compartments or use if already existing
if(ocs_compartment_found==0):
    print('Creating Compartment for OCS related work: ' +input_ocs_compartment_name + ' under root compartment')
    ocs_compartment_ocid = create_compartment(input_ocs_compartment_name,"compartment for OCS related work")

    if ocs_compartment_ocid == "-1":
        print ("Exiting due to compartment error : " )
        exit(-1)
    updatePropsFile(input_config_file, "ocs_compartment_ocid", ocs_compartment_ocid)
if(vm_compartment_found==0 and input_vm_compartment_name!=input_ocs_compartment_name):
    print('Creating Compartment for VMs: ' +input_vm_compartment_name + ' under root compartment')
    vm_compartment_ocid = create_compartment(input_vm_compartment_name,"compartment for VMs")
    if vm_compartment_ocid == "-1":
        print ("Exiting due to compartment error : " )
        exit(-1)
    updatePropsFile(input_config_file, "vm_compartment_ocid", vm_compartment_ocid)

if(ntk_compartment_found==0 and ntk_compartment_ocid!=ocs_compartment_ocid and ntk_compartment_ocid!=vm_compartment_ocid):
    print('Creating Compartment for Network components: ' +input_ntk_compartment_name + ' under root compartment')
    ntk_compartment_ocid = create_compartment(input_ntk_compartment_name,"compartment for Network components")
    if ntk_compartment_ocid == "-1":
        print ("Exiting due to compartment error : " )
        exit(-1)
    updatePropsFile(input_config_file, "ntk_compartment_ocid", ntk_compartment_ocid)

#Read Python config file again
python_config = oci.config.from_file(file_location=input_config_file)

#Create tmp folder for files to be SCPd
if not os.path.exists('tmp'):
    os.makedirs('tmp')

#If image OICD provided is null in properties value, pick the latest image of OS Oracle Linux
if(input_image_id==''):
    for image in paginate(compute_client.list_images,compartment_id=tenancy_id,operating_system ='Oracle Linux',sort_by='TIMECREATED'):
        if ("Gen2-GPU" not in image.display_name):
            input_image_id=image.id
            break

# Get Region wise data
linux_image_id={}
windows_image_id={}
variables_data={}
for key in region_dict:
    linux_image_id.setdefault(key,'')
    windows_image_id.setdefault(key,'')
    variables_data.setdefault(key,'')

new_config=python_config
for region in regions:
    region=region.strip().lower()
    new_config.__setitem__("region",region_dict[region])
    cc = oci.core.ComputeClient(new_config)
    #fetch latest image ocids
    for image in paginate(cc.list_images,compartment_id=tenancy_id,operating_system ='Oracle Linux',sort_by='TIMECREATED'):
        if ("Gen2-GPU" not in image.display_name):
            linux_image_id[region]=image.id
            break
    for image in paginate(cc.list_images,compartment_id=tenancy_id,operating_system ='Windows',sort_by='TIMECREATED'):
        if ("Gen2-GPU" not in image.display_name):
            windows_image_id[region]=image.id
            break

    #write variables data
    variables_data[region] = """variable "ssh_public_key" {
            type = "string"
            default = \"""" + input_ssh_key1 + """"
    }
    variable "tenancy_ocid" {
            type = "string"
            default = \"""" + tenancy_id + """"
    }
    variable "user_ocid" {
            type = "string"
            default = \"""" + python_config['user'] + """"
    }
    variable "compartment_ocid" {
            type = "string"
            default = \"""" + vm_compartment_ocid + """"
    }
    variable "ntk_compartment_ocid" {
            type = "string"
            default = \"""" + ntk_compartment_ocid + """"
    }
    #Added below variable because tf file generated through Koala uses this variable for network components
    variable "compartment_id" {
            type = "string"
            default = \"""" + ntk_compartment_ocid + """"
    }
    variable "fingerprint" {
            type = "string"
            default = \"""" + python_config['fingerprint'] + """"
    }
    variable "private_key_path" {
            type = "string"
            default = "/root/ocswork/keys/oci_api_key.pem"
    }
    variable "region" {
            type = "string"
            default = \"""" + region_dict[region] + """"
    }
    """
    if (windows_image_id[region] != ''):
        variables_data[region] = variables_data[region] + """
    variable "windows_latest_ocid" {
            type = "string"
            default = \"""" + windows_image_id[region] + """"
    }"""
    if (linux_image_id[region] != ''):
        variables_data[region] = variables_data[region] + """
    variable "linux_latest_ocid"{
            type = "string"
            default = \"""" + linux_image_id[region] + """"
    }"""
    write_file("tmp\\variables_"+region+".tf", variables_data[region])

#Writing public keys to a file
public_key_data=input_ssh_key1
if(input_ssh_key2!=''):
    public_key_data=input_ssh_key1 + "\n" +input_ssh_key2
if (input_ssh_key3 != ''):
    public_key_data = public_key_data + "\n" + input_ssh_key3


write_file("tmp\ocs_public_keys.txt",public_key_data)

#Writing Terraform config files provider.tf and variables.tf
provider_data="""provider "oci" {
  version          = ">= 3.0.0"
  tenancy_ocid     = "${var.tenancy_ocid}"
  user_ocid        = "${var.user_ocid}"
  fingerprint      = "${var.fingerprint}"
  private_key_path = "${var.private_key_path}"
  region           = "${var.region}"
}"""
write_file("tmp\provider.tf",provider_data)

#write git expect script to download python code
if (input_configure_git_oci=="1"):
    script_data="""#!/usr/bin/expect
    set password """+input_git_password+"""
    cd /root/ocswork/git_oci
    spawn git pull  https://"""+input_git_username.replace('@','%40')+"""@developer.em2.oraclecloud.com/developer14539-usoraocips16001/s/developer14539-usoraocips16001_oci_9900/scm/oci.git
    expect "Password for 'https://"""+input_git_username+"""@developer.em2.oraclecloud.com':" {send "$password\\r"}
    sleep 60
    expect eof
    """
    write_file("tmp\\download_git_expect1.sh",script_data)
if (input_configure_git_ocictooci == "1"):
    script_data="""#!/usr/bin/expect
    set password """+input_git_password+"""
    cd /root/ocswork/git_ocic2oci
    spawn git pull https://"""+input_git_username.replace('@','%40')+"""@developer.em2.oraclecloud.com/developer14539-usoraocips16001/s/developer14539-usoraocips16001_ocictooci_10075/scm/ocictooci.git
    expect "Password for 'https://"""+input_git_username+"""@developer.em2.oraclecloud.com':" {send "$password\\r"}
    sleep 30
    expect eof
    """
    write_file("tmp\\download_git_expect2.sh",script_data)

#write Panda specific files
if (input_configure_panda=="1"):

    #write TF file for OCIC TF Provider
    provider_panda_data = """provider "opc" {
user            = "${var.user}"
password        = "${var.password}"
identity_domain = \"""" + input_ocic_identity_domain + """"
endpoint        = "${var.endpoint}"
}"""
    write_file("tmp\\ocic-provider.tf", provider_panda_data)

    # write TF file for for OCIC TF Variables
    variables_panda_data="""
variable "user" {
        type = "string"
        default = \"""" + input_ocic_username + """"
}
variable "password" {
        type = "string"
        default = \"""" + input_ocic_password + """"
}
variable "endpoint" {
        type = "string"
        default = \"""" + input_ocic_compute_endpoint + """"
}
variable "domain" {
       type = "string"
       default = \"""" + input_ocic_identity_domain + """"
}
"""
    write_file("tmp\\ocic-variables.tf",variables_panda_data)

    terraform_upgrade_expect_data="""#!/usr/bin/expect
set answer yes
cd /root/ocswork/ocic2oci_work
spawn terraform 0.12upgrade
expect "Enter a value:" {send "$answer\\r"}
sleep 20
expect eof
"""
    write_file("tmp\\upgrade_terraform_expect_script.sh",terraform_upgrade_expect_data)

    # write TF file for Panda instance creation in OCIC
    tf_data = """ 
resource "opc_compute_storage_volume" "panda_boot_vol" {
  name = \"oraclemigration/""" + input_ocic_tf_prefix_for_panda + """_Panda-Boot_Vol"
  size = 12
}

resource "opc_compute_instance" "panda_new" {
 name       = \"oraclemigration/""" + input_ocic_tf_prefix_for_panda + """_Panda-OCIC2OCI"
 label      = "Terraform Provisioned Panda-WithAPI"
 shape      = "oc7"
 image_list = "/oracle/public/OL_7.5_UEKR4_x86_64_MIGRATION"

  storage {
    volume = "${opc_compute_storage_volume.panda_boot_vol.name}"
    index  = 1
  }
   networking_info {
   index          = 0
   nat            =["${opc_compute_ip_reservation.panda_new.name}"]
   shared_network = true
  }

  networking_info {
   index          = 1
   ip_network     = "${opc_compute_ip_network.panda_new.id}"
   shared_network = false
   vnic = \"""" + input_ocic_tf_prefix_for_panda + """_Panda-OCIC2OCI-vnic"
   """
    tf_data = tf_data + "vnic_sets = [\"" + input_ocic_vnicset_for_panda
    tf_data = tf_data + """"]
    
 }
 ssh_keys = ["${opc_compute_ssh_key.OCS-Panda-ssh-key.name}"]

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

output "panda_pub_ip" {
        value = "${opc_compute_ip_reservation.panda_new.ip}"
}

output "ctlsInstanceName" {
        value = "${opc_compute_instance.panda_new.name}/${opc_compute_instance.panda_new.id}"
}

output "container"{
        value = "/Compute-${var.domain}/${var.user}"
}

output "targetControllerName"{
        value = "/Compute-${var.domain}/${var.user}/${opc_compute_instance.panda_new.name}/${opc_compute_instance.panda_new.id}"
}

output "password" {
        value = "${var.password}"
}

output "endpoint" {
        value = "${var.endpoint}"
}

resource "opc_compute_ip_network" "panda_new" {
 name                = \"""" + input_ocic_tf_prefix_for_panda + """_Panda-OCIC2OCI--IP-Network"
 """
    tf_data = tf_data +  "ip_address_prefix   = \"" + input_ocic_ip_network_for_panda + "\" } "

### Add the storage work here
    ## Generate number to letters mapping
    letter_mapping = dict(zip(letter_count(0),ascii_lowercase))
    disk_list_for_ansible = ""
    for i in range(1,input_ocic_panda_storage_volume_disks+1):
        j=i+1
        #print ("Disk would be: /dev/xvd" + letter_mapping[j])
        if i == 1:
            disk_list_for_ansible = "/dev/xvd" + letter_mapping[j]
        else:
            disk_list_for_ansible = disk_list_for_ansible + ",/dev/xvd" + letter_mapping[j]
        tf_data = tf_data + """
    resource "opc_compute_storage_volume" "panda_disk""" + str(j) + """" {
    name = \"""" + input_ocic_tf_prefix_for_panda + """_panda_disk""" + str(j) + """"
    size = """ + str(input_ocic_panda_storage_volume_size) + """
    storage_type = "/oracle/public/storage/latency"
}
    resource "opc_compute_storage_attachment" "panda_disk""" + str(j) + """_attachment"
    {
    instance = "${opc_compute_instance.panda_new.name}"
    storage_volume = "${opc_compute_storage_volume.panda_disk""" + str(i+1) + """.name}"
    index = """ + str(j) + """
    }"""

    write_file("tmp\\panda.tf",tf_data)
    ### Have to write the ansible files to create the storage disk.
    ansible_var_data = """
volume: 
   pvs: """ + disk_list_for_ansible + """
   create_lvsize: '100%FREE'
"""
    write_file("tmp\\variables.yml",ansible_var_data)

#write Koala specific files
if (input_configure_koala=="1"):
    username_full="/Compute-" + input_ocic_identity_domain + '/' + input_ocic_username
    #config file for koala
    file_data="""{
    "global": {
    "format": "text",
    "debug-request": false
    },
    \
    "compute": {
    "user": \""""+username_full+ """",
    "endpoint": \""""+input_ocic_compute_endpoint.replace("https://","")+ """"
    }
    }
    """
    write_file("tmp\\default",file_data)
    #expect script to run koala discover
    script_data="""#!/usr/bin/expect
    set password """+input_ocic_password+"""
    cd /root/ocswork/ocic2oci_work
    spawn /usr/local/bin/opcmigrate discover
    expect "Compute Classic Password" {send "$password\\r"}
    sleep 60
    expect eof
    """
    write_file("tmp\\discover_koala_expect.sh",script_data)
#Creating VM

if(input_create_vm=="1"):
    ad_name = python_config[input_ad_name]
    vcn_found=0
    igw_found=0
    ngw_found=0
    subnet_found=0
    igw_ocid=''
    ngw_ocid=''

    #Check if VCN with same CIDR already exists and if it exists then check for other components
    default_route_table_id=''
    for vcn in paginate(network_client.list_vcns,compartment_id=ocs_compartment_ocid):
        if(vcn.cidr_block==input_vcn_cidr):
            print("VCN with this CIDR already exists..Reusing same for OCS Work. VCN name is "+vcn.display_name)
            vcn_ocid=vcn.id
            default_route_table_id=vcn.default_route_table_id
            vcn_found=1

            #Check if subnet also exists
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
                        #Create Route Rule
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

    #Creates OCS VCN in the specified OCS compartment
    if(vcn_found==0):
        print('Creating VCN: '+input_vcn_name)
        #Converting vcn name to alphanumeric string
        regex = re.compile('[^a-zA-Z0-9]')
        vcn_dns_label=regex.sub('', input_vcn_name)
        create_vcn_details=oci.core.models.CreateVcnDetails(cidr_block=input_vcn_cidr,dns_label=vcn_dns_label,compartment_id=ocs_compartment_ocid, display_name=input_vcn_name)
        vcn=network_client.create_vcn(create_vcn_details)
        vcn_ocid=vcn.data.id

    # Creating subnet
    if (subnet_found == 0):
        print('Creating public SUBNET: ' + input_subnet_name + ' with default route table, security list and dhcp options')
        # Converting subnet name to alphanumeric string
        regex = re.compile('[^a-zA-Z0-9]')
        subnet_dns_label = regex.sub('', input_subnet_name)
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

    add_rule=1
    for rule in existing_rules_list:
        if (route_rule.destination == rule.destination):
            print("Route Rule with 0.0.0.0/0 destination already exists in the route table. Not adding anything. Internet Access might not work for the VM")
            add_rule=0

    if(add_rule==1):
        existing_rules_list.append(route_rule)
        update_route_details = oci.core.models.UpdateRouteTableDetails(route_rules=existing_rules_list)
        network_client.update_route_table(rt_id=subnet_route_table_id, update_route_table_details=update_route_details)

    print('Creating LPG')
    create_lpg_details=oci.core.models.CreateLocalPeeringGatewayDetails(compartment_id=ocs_compartment_ocid, display_name=input_lpg_to_orig_name,vcn_id=vcn_ocid)
    lpg=network_client.create_local_peering_gateway(create_lpg_details)
    lpg_to_orig_ocid = lpg.data.id

    lpg_to_mirror_ocid = ''
    lpg_to_rsync_ocid = ''
    if(input_lpg_to_mirror_name!=''):
        create_lpg_details = oci.core.models.CreateLocalPeeringGatewayDetails(compartment_id=ocs_compartment_ocid,
                                                                          display_name=input_lpg_to_mirror_name, vcn_id=vcn_ocid)
        lpg = network_client.create_local_peering_gateway(create_lpg_details)
        lpg_to_mirror_ocid = lpg.data.id

    if(input_lpg_to_rsync_name!=''):
        create_lpg_details = oci.core.models.CreateLocalPeeringGatewayDetails(compartment_id=ocs_compartment_ocid,
                                                                          display_name=input_lpg_to_rsync_name, vcn_id=vcn_ocid)
        lpg = network_client.create_local_peering_gateway(create_lpg_details)
        lpg_to_rsync_ocid = lpg.data.id


    output=subprocess.Popen(("certutil.exe -encode "+ input_user_data_file + " tmp\\output.txt"),stdout=subprocess.PIPE).stdout
    output.close()
    time.sleep(5)

    encoded_user_data=""
    with open('tmp\\output.txt', 'r') as f:
        for line in f:
            if not (line.__contains__("CERTIFICATE")):
                encoded_user_data=encoded_user_data+line
    f.close()

    encoded_user_data=encoded_user_data.replace('\n','')
    print('Creating VM: '+input_vm_name)
    multiple_ssh_keys=input_ssh_key1
    if(input_ssh_key2!=''):
        multiple_ssh_keys=input_ssh_key1 + "\n" +input_ssh_key2
    if (input_ssh_key3 != ''):
        multiple_ssh_keys = multiple_ssh_keys + "\n" + input_ssh_key3

    create_source_details=oci.core.models.InstanceSourceViaImageDetails(source_type="image",image_id=input_image_id)
    metadata= {"ssh_authorized_keys" : multiple_ssh_keys, "user_data" : encoded_user_data}
    launch_instance_details=oci.core.models.LaunchInstanceDetails(availability_domain=ad_name,compartment_id=ocs_compartment_ocid,display_name=input_vm_name,shape=input_vm_shape,source_details=create_source_details,metadata=metadata,subnet_id=subnet_ocid)
    instance=compute_client.launch_instance(launch_instance_details)

    #wait till Instance comes to RUNNING state
    print('Waiting for instance to come to RUNNING state...')
    new_instance=instance.data
    get_instance_response=oci.wait_until(compute_client,compute_client.get_instance(new_instance.id),'lifecycle_state', 'RUNNING')
    #Fetch public IP address of the VM
    instance_ocid=new_instance.id
    vnicAttachments =compute_client.list_vnic_attachments(compartment_id=ocs_compartment_ocid,instance_id=instance_ocid)
    for vnicAttachment in vnicAttachments.data:
        vnic_ocid=vnicAttachment.vnic_id
    vnic=network_client.get_vnic(vnic_ocid)

    ip=''
    public_ip=vnic.data.public_ip
    if(public_ip!=None):
        print('Public IP of VM: '+public_ip)
        ip=public_ip

    private_ip = vnic.data.private_ip
    print('Private IP of VM: ' + private_ip)
    if(ip==''):
        ip=private_ip

    #Write to config file for cleanup
    with open(input_config_file, 'r') as file:
        existing_data = file.read()
        append_file(del_config_file, existing_data)

    append_file(del_config_file, "vcn_ocid=" + vcn_ocid)
    if (igw_ocid!=''):
        append_file(del_config_file, "igw_ocid=" + igw_ocid)
    if (ngw_ocid != ''):
        append_file(del_config_file, "ngw_ocid=" + ngw_ocid)

    append_file(del_config_file, "lpg_to_orig_ocid=" + lpg_to_orig_ocid)

    if (lpg_to_mirror_ocid !=''):
        append_file(del_config_file, "lpg_to_mirror_ocid=" + lpg_to_mirror_ocid)
    if (lpg_to_rsync_ocid != ''):
        append_file(del_config_file, "lpg_to_rsync_ocid=" + lpg_to_rsync_ocid)

    append_file(del_config_file, "ocswork_instance_ocid=" + instance_ocid)

    if(public_ip!=None):
        append_file(del_config_file, "public_ip=" + public_ip)

    append_file(del_config_file, "private_ip=" + private_ip)

    if (default_route_table_id == ''):
        default_route_table_id=subnet_route_table_id
        append_file(del_config_file, "def_rt_table_ocid=" + default_route_table_id)

    append_file(del_config_file, "subnet_ocid=" + subnet_ocid)

    append_file(del_config_file, "compartment_name=" + input_ocs_compartment_name + "\n")

    #write below details also to the config file so that it can be used later while creating the network for client
    updatePropsFile(input_config_file, "ocs_vcn_ocid", vcn_ocid)
    updatePropsFile(input_config_file, "ocs_subnet_ocid", subnet_ocid)
    updatePropsFile(input_config_file, "ocs_lpg_to_orig_ocid", lpg_to_orig_ocid)
    if (lpg_to_mirror_ocid != ''):
        updatePropsFile(input_config_file, "ocs_lpg_to_mirror_ocid", lpg_to_mirror_ocid)
    if (lpg_to_rsync_ocid != ''):
        updatePropsFile(input_config_file, "ocs_lpg_to_rsync_ocid", lpg_to_rsync_ocid)
    updatePropsFile(input_config_file, "ocswork_instance_ocid", instance_ocid)

    #scp private key and config files to VM
    print('Copying required files to the VM')
    time.sleep(5)

    f=open(input_pvt_key_file,"r")
    putty_pvtkey_contents = f.read()
    f.close()
    f = open("tmp\\openSSHpvtKeyFile","w+")
    f.write(puttykeys.ppkraw_to_openssh(putty_pvtkey_contents))
    f.close()

    ssh = SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    for x in range(10):
        try:
            ssh.connect(ip, username='opc', key_filename='tmp\\openSSHpvtKeyFile')
            print('Connected to VM for file transfer')
            break
        except Exception as e:
            print (e)
            print('Trying again..')
            time.sleep(2)

    provider='tmp\\provider.tf'
    koala='tmp\\default'
    script_file=input_shell_script
    upload_git_script1='tmp\\download_git_expect1.sh'
    upload_git_script2='tmp\\download_git_expect2.sh'
    discover_koala_script='tmp\\discover_koala_expect.sh'
    upgrade_terraform_script="tmp\\upgrade_terraform_expect_script.sh"
    public_key_file='tmp\\ocs_public_keys.txt'


    sftp = ssh.open_sftp()
    print('Copying Python Config File..')
    sftp.put(input_config_file, '/home/opc/config')
    print('Copying private key File for OCI communication..')
    sftp.put(python_config['key_file'], '/home/opc/oci_api_key.pem')
    print('Copying private key to login to VM..')
    sftp.put(input_pvt_key_file, '/home/opc/ssh-pvt-key.ppk')
    print('Copying file containing OCS public keys..')
    sftp.put('tmp\\ocs_public_keys.txt', '/home/opc/ocs_public_keys.txt')
    print('Copying OCI Terraform files..')
    sftp.put(provider, '/home/opc/provider.tf')
    for region in regions:
        region=region.strip().lower()
        ssh.exec_command("sudo mkdir -p /root/ocswork/terraform_files/"+region)
        file="tmp\\variables_"+region+".tf"
        sftp.put(file, '/home/opc/variables_'+region+'.tf')
        mv_variables_cmd="sudo mv /home/opc/variables_"+region+".tf /root/ocswork/terraform_files/"+region
        mv_provider_cmd = "sudo cp /home/opc/provider.tf /root/ocswork/terraform_files/" + region
        ssh.exec_command(mv_variables_cmd)
        ssh.exec_command(mv_provider_cmd)



    if(input_configure_panda=="1"):
        print('Copying generated files for Panda Server Creation..')
        sftp.put('tmp\\panda.tf','/home/opc/panda.tf')
        sftp.put('tmp\\ocic-provider.tf','/home/opc/ocic-provider.tf')
        sftp.put('tmp\\ocic-variables.tf','/home/opc/ocic-variables.tf')
        sftp.put('tmp\\upgrade_terraform_expect_script.sh', '/home/opc/upgrade_terraform_expect_script.sh')
        sftp.put('tmp\\variables.yml','/home/opc/variables.yml')
    if(input_configure_koala=="1"):
        print('Copying Koala files..')
        sftp.put(koala, '/home/opc/default')
        sftp.put(discover_koala_script, '/home/opc/discover_koala_expect.sh')
    if(input_configure_git_oci=="1"):
        print('Copying OCI GIT download script file..')
        sftp.put(upload_git_script1, '/home/opc/download_git_expect1.sh')
    if (input_configure_git_ocictooci == "1"):
        print('Copying OCICTOOCI GIT download script file..')
        sftp.put(upload_git_script2, '/home/opc/download_git_expect2.sh')

    print('Copying shell script file to setup the VM..')
    input_run_shell_script = config.get('Default','run_shell_script')
    if input_run_shell_script == "1":
        sftp.put(script_file, '/home/opc/shell_script.sh')
    else:
        sftp.put(script_file, '/home/opc/shell_script_do_not_run_auto.sh')
    sftp.close()
    print('sudo to root to view /var/log/messages to check cloud-init progress')

if input_cleanup == "1":
    shutil.rmtree('tmp')
