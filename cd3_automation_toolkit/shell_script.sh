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
python -m pip install --user --upgrade pip
python -m pip install --user oci
python -m pip install --user oci-cli
python -m pip install --user pycryptodomex==3.10.1
python -m pip install --user regex
python -m pip install --user pandas==1.1.5
python -m pip install --user openpyxl==3.0.5
python -m pip install --user xlrd==1.2.0
python -m pip install --user xlsxwriter==1.3.7
python -m pip install --user wget
python -m pip install --user requests
python -m pip install --user netaddr
python -m pip install --user cfgparse
python -m pip install --user ipaddress
python -m pip install --user Jinja2
python -m pip install --user simplejson
echo "export PYTHONPATH=${PYTHONPATH}:/root/.local/lib/python3.8/site-packages/:/cd3user/.local/lib/python3.8/site-packages/:/opt/rh/rh-python38/root/usr/lib/python3.8/site-packages/" >> /cd3user/.bashrc
source /cd3user/.bashrc


yes | sudo rpm -iUvh https://yum.oracle.com/repo/OracleLinux/OL7/developer/x86_64/getPackage/terraform-1.3.0-1.el7.x86_64.rpm
