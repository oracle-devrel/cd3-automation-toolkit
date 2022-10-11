#!/bin/bash

#Create Required Directories
mkdir ~/.oci

sudo yum-config-manager --enable ol7_developer_EPEL
sudo yum-config-manager --enable ol7_developer

sudo yum -y install scl-utils
sudo yum -y install centos-release-scl

sudo yum -y install rh-python38


echo "source scl_source enable rh-python38" >> /cd3user/.bashrc
source /cd3user/.bashrc
pip3 install --user --upgrade pip
pip3 install --user oci
pip3 install --user oci-cli
pip3 install --user pycryptodomex==3.10.1
pip3 install --user regex
pip3 install --user pandas==1.1.5
pip3 install --user openpyxl==3.0.5
pip3 install --user xlrd==1.2.0
pip3 install --user xlsxwriter==1.3.7
pip3 install --user wget
pip3 install --user requests
pip3 install --user netaddr
pip3 install --user cfgparse
pip3 install --user ipaddress
pip3 install --user Jinja2
pip3 install --user simplejson
echo "export PYTHONPATH=${PYTHONPATH}:/root/.local/lib/python3.8/site-packages/:/cd3user/.local/lib/python3.8/site-packages/:/opt/rh/rh-python38/root/usr/lib/python3.8/site-packages/" >> /cd3user/.bashrc
source /cd3user/.bashrc


yes | sudo rpm -iUvh https://yum.oracle.com/repo/OracleLinux/OL7/developer/x86_64/getPackage/terraform-1.3.0-1.el7.x86_64.rpm