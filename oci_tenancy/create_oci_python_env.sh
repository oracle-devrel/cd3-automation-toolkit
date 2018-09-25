#!/bin/bash

yum install qemu-img
yum install python27
scl enable python27 'python --version'
wget https://bootstrap.pypa.io/get-pip.py
chmod +x get-pip.py
./get-pip.py

pip install oci

if [ -e "~/.oci/config" ]; then
	mkdir -p ~/.oci
echo "Example config file written to ~/.oci/config"
echo "
[DEFAULT]
user=<USER_OCID>
fingerprint=<key_file_finger_print>
key_file=<path to api private key .pem file>
tenancy=<tenancy-ocid>
region=us-ashburn-1
stage_instance_name=OCI-Stage
stage_instance_ocid=<Stage Instance OCID>
local_staging_dir=/u01
compartment_id=<compartment_id>
" > ~/.oci/config

else
	echo "File exists "
fi

####
# docs here: https://docs.us-phoenix-1.oraclecloud.com/Content/API/Concepts/sdkconfig.htm
#####################

