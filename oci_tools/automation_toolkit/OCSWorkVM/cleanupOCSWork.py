import configparser
import argparse
import oci
import time
import os
import paramiko
from paramiko import SSHClient
import puttykeys


parser = argparse.ArgumentParser(description="Destroys Panda & OCS Work related components")
parser.add_argument("propsfile",help="Full Path of properties file. eg ocswork.properties")

args = parser.parse_args()
config = configparser.RawConfigParser()
config.read(args.propsfile)


#Read Config file Variables
try:
    input_config_file=config.get('Default','cleanup_script_file').strip()
    input_pvt_key_file = config.get('Default', 'pvt_key_file').strip()
    config_file = config.get('Default', 'python_config_file').strip()

except Exception as e:
    print(e)
    print('Check if all property values exist and try again..exiting...`    ')
    exit()


def write_file(file_name,file_data):
    f=open(file_name,"w+")
    f.write(file_data)
    f.close()

print("Reading OCID info for deletion from "+input_config_file+"\n")
python_config = oci.config.from_file(file_location=input_config_file)
ocs_compartment_ocid = python_config['ocs_compartment_ocid']
input_vcn_ocid = python_config['vcn_ocid']
input_igw_ocid = python_config['igw_ocid']
try:
    input_ngw_ocid = python_config['ngw_ocid']
except Exception as e:
    print(e)
try:
    input_lpg_to_orig_ocid = python_config['lpg_to_orig_ocid']
except Exception as e:
    print(e)
try:
    input_lpg_to_mirror_ocid = python_config['lpg_to_mirror_ocid']
except Exception as e:
    print(e)
try:
    input_lpg_to_rsync_ocid = python_config['lpg_to_rsync_ocid']
except Exception as e:
    print(e)
try:
    input_route_table_id = python_config['def_rt_table_ocid']
except Exception as e:
    print(e)

input_instance_ocid = python_config['ocswork_instance_ocid']
input_reserved_public_ocid=python_config['ocswork_reservedpublic_ocid']
input_public_ip = python_config['public_ip']
input_subnet_ocid = python_config['subnet_ocid']
## First create file to destroy the Panda Instance
## SSH To the VM, run terraform destroy by running terraform destroy -auto-approve

config1=configparser.RawConfigParser()
config1.read(input_config_file)

tf_destroy_script = """
#!/bin/bash
cd /root/ocswork/ocic2oci_work
n=0
    until [ $n -ge 5 ]
   do
      terraform destroy -auto-approve && break
      n=$[$n+1]
      sleep 3
   done
"""

del_file_path="tmp_for_del"
#Create tmp folder for files to be SCPd
if not os.path.exists(del_file_path):
    os.makedirs(del_file_path)

write_file(del_file_path+"\\tf_destroy.sh", tf_destroy_script)

#f = open(input_pvt_key_file, "r")
#putty_pvtkey_contents = f.read()
#f.close()
#f = open(del_file_path+"\\openSSHpvtKeyFile", "w+")
#f.write(puttykeys.ppkraw_to_openssh(putty_pvtkey_contents))
#f.close()

dont_ssh = 0

if dont_ssh == 1:

    ssh = SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    for x in range(10):
        try:
            ssh.connect(input_public_ip, username='opc', key_filename=del_file_path+"\\openSSHpvtKeyFile")
            ssh.connect(input_public_ip, username='opc', key_filename=del_file_path + "\\openSSHpvtKeyFile")
            print('Connected to VM for file transfer')
            break
        except Exception as e:
            print (e)
            print('Trying again..')
            time.sleep(2)

    destroy_file = del_file_path + "\\tf_destroy.sh"
    sftp = ssh.open_sftp()
    sftp.put(destroy_file,"/home/opc/tf_destroy.sh")
    print ("Pushed tf_destroy.sh")
    ## dos2unix
    cmd_to_execute = "dos2unix /home/opc/tf_destroy.sh /home/opc_tf_destroy.sh"

    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd_to_execute)
    ## destroy tf
    print( "Running tf_destroy.sh")
    cmd_to_execute = "chmod +x /home/opc/tf_destroy.sh; sudo -S /home/opc/tf_destroy.sh"
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd_to_execute)

    ssh_stdin.close()
    for line in ssh_stdout.read().splitlines():
        print(line)
    ssh.close()

network_client = oci.core.VirtualNetworkClient(python_config)
identity_client = oci.identity.IdentityClient(python_config)
compute_client = oci.core.ComputeClient(python_config)

## Delete VM
compute_client.terminate_instance(input_instance_ocid)
print ("Deleting Instance")
get_instance_response=oci.wait_until(compute_client,compute_client.get_instance(input_instance_ocid),'lifecycle_state', 'TERMINATED')
print (get_instance_response.data)

print("Delete the Reserved Public IP if it is the end of OCS enagagement with client or Retain it if you intend to rebuild OCSWork VM")
delete_ip = input("Delete Reserved public IP(y) or Retain(n): ")

if(delete_ip.lower()=='y'):
    print ("Deleting Reserved Public IP")
    try :
        network_client.delete_public_ip(input_reserved_public_ocid)
    except Exception as e:
        print (e)


## Remove route rules
route_rules_list=[]
update_route_details=oci.core.models.UpdateRouteTableDetails(route_rules=route_rules_list)
network_client.update_route_table(rt_id=input_route_table_id,update_route_table_details=update_route_details)


print ("Deleting IGW of VCN")
try :
    network_client.delete_internet_gateway(input_igw_ocid)
except Exception as e:
    print (e)
print ("Deleting NGW of VCN")
try :
    network_client.delete_nat_gateway(input_ngw_ocid)
except Exception as e:
    print (e)

#get_ntk_response = oci.wait_until(network_client,network_client.get_internet_gateway(input_igw_ocid),'lifecycle_state', 'TERMINATED')
print ("Deleting LPGs")

lpg_list= network_client.list_local_peering_gateways(compartment_id=ocs_compartment_ocid, vcn_id=input_vcn_ocid)
for lpg in lpg_list.data:
    lpg_ocid=lpg.id
    network_client.delete_local_peering_gateway(lpg_ocid)
    time.sleep(5)


print ("Deleting Subnet")
try:
    response = network_client.delete_subnet(input_subnet_ocid)
except Exception as e:
    print(e)
    print("Make sure to delete other VMs in same subnet..exiting without removing VCN and other network components.")
    exit()

print ("Deleting VCN")
response = network_client.delete_vcn(input_vcn_ocid)

#empty the file
f = open(input_config_file, 'r+')
f.truncate(0)

config2 = configparser.RawConfigParser()
config2.read(config_file)
config2.remove_option("DEFAULT",'ntk_compartment_ocid')
config2.remove_option("DEFAULT",'vm_compartment_ocid')
config2.remove_option("DEFAULT",'ocs_compartment_ocid')
config2.remove_option("DEFAULT",'ocs_vcn_ocid')
config2.remove_option("DEFAULT",'ocs_subnet_ocid')
config2.remove_option("DEFAULT",'ocs_lpg_to_orig_ocid')
config2.remove_option("DEFAULT",'ocs_lpg_to_mirror_ocid')
config2.remove_option("DEFAULT",'ocs_lpg_to_rsync_ocid')
config2.remove_option("DEFAULT",'ocswork_instance_ocid')

config2.remove_option("DEFAULT",'ad_1')
config2.remove_option("DEFAULT",'ad_2')
config2.remove_option("DEFAULT",'ad_3')


with open(config_file, 'w') as file:
    config2.write(file)

print("Done")
