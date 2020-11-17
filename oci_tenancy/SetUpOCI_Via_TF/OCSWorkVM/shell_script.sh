#!/bin/bash

#Create Required Directories
mkdir ~/.oci
mkdir -p /root/ocswork/keys
mkdir -p /root/ocswork/downloads
mkdir -p /root/ocswork/git_oci
mkdir -p /root/ocswork/git_ocic2oci
mkdir -p /root/ocswork/ocic2oci_work

sudo yum -y install scl-utils
sudo yum -y install rh-python36
sudo yum -y install gcc
#scl enable rh-python36 bash
sudo echo "source scl_source enable rh-python36" >> /root/.bashrc
source /root/.bashrc
sudo yum -y groupinstall 'Development Tools'
#pip3 install --upgrade pip
pip3 install oci
pip3 install oci-cli
pip3 install pycrypto
pip3 install regex
pip3 install pandas
pip3 install openpyxl
pip3 install xlrd
pip3 install xlsxwriter
pip3 install puttykeys
pip3 install netaddr
pip3 install cfgparse
pip3 install ipaddr
pip3 install ipaddress
pip3 install paramiko
pip3 install Jinja2
pip3 install simplejson
sudo echo "export PYTHONPATH=${PYTHONPATH}:/opt/rh/rh-python36/root/usr/lib/python3.6/site-packages/" >> /root/.bashrc
source /root/.bashrc

## Needed for conversion from putty ppk to openssh
sudo yum install -y putty

#Install Required Packages
#sudo yum -y install python-pip
#pip install pip==9.0.3
#pip install oci
#pip install oci-cli
#pip install pandas
#pip install xlrd
#pip install in_place


sudo yum -y install git
#sudo yum --showduplicates list terraform #TF RHEL packages list
#uncomment for 0.13v/latest version of terraform
#sudo yum -y install terraform
sudo yum -y install terraform-0.12.28-1.el7
sudo yum -y install expect
sudo yum -y install telnet

sudo yum -y install ansible
cd /root/ocswork/downloads
git clone https://github.com/oracle/oci-ansible-modules.git
cd oci-ansible-modules
./install.py

sudo yum -y install java
sudo yum -y install wget

#Copy MarkUp Safe to appropriate location; Jinja2 and Ansible requires it
sudo cp -R /opt/rh/rh-python36/root/usr/lib64/python3.6/site-packages/MarkupSafe-1.1.1.dist-info /opt/rh/rh-python36/root/usr/lib/python3.6/site-packages/
sudo cp -R /opt/rh/rh-python36/root/usr/lib64/python3.6/site-packages/markupsafe /opt/rh/rh-python36/root/usr/lib/python3.6/site-packages/

#sudo yum -y install python36 python36-setuptools graphviz
#sudo easy_install-3.6 pip

#Copy files to respective locations and do required configurations
mv /home/opc/config ~/.oci
mv /home/opc/oci_api_key.pem /root/ocswork/keys
chown root:root ~/.oci/config
chown root:root /root/ocswork/keys/oci_api_key.pem
chmod 400 ~/.oci/config
chmod 400 /root/ocswork/keys/oci_api_key.pem
sed -i 's#key_file.*#key_file=/root/ocswork/keys/oci_api_key.pem#' ~/.oci/config


chown -R root:root /root/ocswork/terraform_files/*

# Move the pvt key to the /root/ocswork directory
mv /home/opc/ssh-pvt-key.ppk /root/ocswork/keys/ssh-pvt-key.ppk
cd /root/ocswork/keys/
puttygen /root/ocswork/keys/ssh-pvt-key.ppk -O private-openssh -o /root/ocswork/keys/ssh-pvt-key-openssh.ppk
#mv /home/opc/ssh-pvt-key-openssh.ppk /root/ocswork/keys/ssh-pvt-key-openssh.ppk
mv /home/opc/ocs_public_keys.txt /root/ocswork/keys/ocs_public_keys.txt
chown root:root /root/ocswork/keys/ssh-pvt-key-openssh.ppk
chmod 400 /root/ocswork/keys/ssh-pvt-key-openssh.ppk
chown root:root /root/ocswork/keys/ocs_public_keys.txt
chmod 400 /root/ocswork/keys/ocs_public_keys.txt

#Download GIT Repo
## the download_git_oci.sh and download_git_ocic2oci.sh will not be created if configure_git is set to 0 in the props file.
if [ -e /home/opc/download_git_oci.sh ] || [ -e /home/opc/download_git_ocic2oci.sh ]
then
  mv /home/opc/id_rsa /root/.ssh
  cd /root/.ssh
  chmod 400 id_rsa
  echo -e "Host nac-gc39002.developer.ocp.oraclecloud.com\n\tStrictHostKeyChecking no\n" >> ~/.ssh/config
fi

if [ -e /home/opc/download_git_oci.sh ]
then
    cd  /home/opc
    dos2unix download_git_oci.sh download_git_oci.sh
    chmod +x download_git_oci.sh
    cd /root/ocswork/git_oci
    git init
    cd  /home/opc
    ./download_git_oci.sh
    sleep 15s
    find /root/ocswork/git_oci -type f -iname "*.py" -exec chmod +x {} \;
    dos2unix /root/ocswork/git_oci/oci_tenancy/ova_disk_migration_bash/*.sh
fi
if [ -e /home/opc/download_git_ocic2oci.sh ]
then
    cd /home/opc
    dos2unix download_git_ocic2oci.sh download_git_ocic2oci.sh
    chmod +x download_git_ocic2oci.sh
    cd /root/ocswork/git_ocic2oci
    git init
    cd  /home/opc
    ./download_git_ocic2oci.sh
    sleep 5s
    find /root/ocswork/git_ocic2oci -type f -iname "*.py" -exec chmod +x {} \;
fi

#Configure Panda
if [ -e /home/opc/panda.tf ]
then
    echo "Panda Config START"
    mkdir -p /root/ocswork/ocic2oci_work
    mv /root/ocswork/git_oci/oci_tenancy/SetUpOCI_Via_TF/OCSWorkVM/panda_setup_files/opc-cli-18.1.2.zip /root/ocswork/downloads/
    mv /root/ocswork/git_oci/oci_tenancy/SetUpOCI_Via_TF/OCSWorkVM/panda_setup_files/* /root/ocswork/ocic2oci_work/
    chmod +x /root/ocswork/ocic2oci_work/*.py
    chmod +x /root/ocswork/ocic2oci_work/*.sh

    cd /root/ocswork/ocic2oci_work/
    ## Download older version of terraform
    #wget https://releases.hashicorp.com/terraform/0.11.14/terraform_0.11.14_linux_amd64.zip
    #sleep 2s
    #unzip terraform_0.11.14_linux_amd64.zip
    #sleep 2s
    #mv terraform terraform0.11

    ## Copy files generated using createOCSWork
    mv /home/opc/panda.tf /root/ocswork/ocic2oci_work/
    mv /home/opc/ocic-provider.tf /root/ocswork/ocic2oci_work/
    mv /home/opc/ocic-variables.tf /root/ocswork/ocic2oci_work/
    #mv /home/opc/variables.yml /root/ocswork/ocic2oci_work/
    mv /home/opc/upgrade_terraform_expect_script.sh /root/ocswork/ocic2oci_work/

    chown root:root /root/ocswork/ocic2oci_work/*.tf
    #chown root:root /root/ocswork/ocic2oci_work/variables.yml

    cd /root/ocswork/ocic2oci_work
    ## The unfortunate side effect of running so many things through shell.  The kernel seems to be throwing irq messages.
    ## Sleep to see if this helps.
    #sleep 1s
    #./terraform0.11 init
    #sleep 1s

    dos2unix upgrade_terraform_expect_script.sh upgrade_terraform_expect_script.sh
    chmod +x upgrade_terraform_expect_script.sh
    ./upgrade_terraform_expect_script.sh

    sleep 1s
    terraform init
    sleep 1s

   ## Writing some retry logic to TF
    n=0
    until [ $n -ge 3 ]
    do
      terraform apply -auto-approve && break
      n=$[$n+1]
      sleep 3
    done
    # Get Panda details using OPC CLI; this is used because there is bug in terraform while using oraclemigration for panda instance
    if [ -e /root/ocswork/downloads/opc-cli-18.1.2.zip ]
    then
      cd /root/ocswork/downloads
      unzip opc-cli-18.1.2.zip
      sleep 1
      sudo cp ./linux/opc /usr/bin
      mkdir -p /root/.opc/profiles
      mv /home/opc/compute /root/.opc/profiles
      mv /home/opc/password /root/.opc/profiles
      chown root:root /root/.opc/profiles/compute
      chown root:root /root/.opc/profiles/password
      chmod 600 /root/.opc/profiles/compute
      chmod 600 /root/.opc/profiles/password

      mv /home/opc/fetch_panda_details.sh /root/ocswork/ocic2oci_work/
      cd /root/ocswork/ocic2oci_work/
      dos2unix fetch_panda_details.sh fetch_panda_details.sh
      chmod +x fetch_panda_details.sh
      #./fetch_panda_details.sh
    fi
    echo "Panda Config END"
fi

#Configure Koala
if [ -e /home/opc/default ]
then
    echo "Koala Config START"
    mv /root/ocswork/git_oci/oci_tenancy/SetUpOCI_Via_TF/OCSWorkVM/panda_setup_files/opcmigrate-1.4.0.zip /root/ocswork/ocic2oci_work/
    cp /root/ocswork/ocic2oci_work/opcmigrate-1.4.0.zip /root/ocswork/downloads/opcmigrate.zip
    cd /root/ocswork/downloads
    unzip opcmigrate.zip -d /root/ocswork/opcmigrate
    cd /root/ocswork/opcmigrate

    pip3 install ./opcmigrate-*.whl

    mkdir -p /root/.opc/profiles
    mv /home/opc/default /root/.opc/profiles
    chown root:root /root/.opc/profiles/default
    cd /home/opc
    dos2unix discover_koala_expect.sh discover_koala_expect.sh
    chmod +x discover_koala_expect.sh
    ./discover_koala_expect.sh
    sleep 10s
    n=0
    until [ $n -ge 5 ]
    do
        if [ -e /root/ocswork/ocic2oci_work/resources-default.json ]
        then
            echo "Koala discover completed..Proceeding"
            cd /root/ocswork/ocic2oci_work
            /usr/local/bin/opcmigrate generate --with-security-rule-union -o ocic2oci_network.tf
            cp ocic2oci_network.tf /root/ocswork/terraform_files
            mv ocic2oci_network.tf ocic2oci_network.tf_Orig
            #/usr/local/bin/opcmigrate instances-export > instance-export.json
            /usr/local/bin/opcmigrate plan create --output migration-plan.json
            /usr/local/bin/opcmigrate instances-export --plan migration-plan.json --format json > instance-export.json
            /usr/local/bin/opcmigrate report
            sleep 5s
            mv *.xlsx report_ocic.xlsx
            n=$[$n+1]
            break
        else
            echo "Koala discover failed..Retrying"
            n=$[$n+1]
            sleep 3s
        fi
    done
    echo "Koala Config END"
fi

#Removing expect scripts as they contain clear text password of the user
rm -f /home/opc/download_git_expect1.sh
rm -f /home/opc/download_git_expect2.sh
rm -f /home/opc/upload_panda_expect.sh
rm -f /home/opc/discover_koala_expect.sh
rm -f /home/opc/provider.tf


#Installing python36-devel and gcc for pip install
#timeout 60 yum install python36-devel gcc -y

#Configuring DB specific packages in python36
#echo "Installing packages for python36..This would keep running in background and you can start your work"
#/usr/bin/python3 -m pip install --upgrade pip
#/usr/bin/python3 -m pip install oci
#/usr/bin/python3 -m pip install pycrypto
#/usr/bin/python3 -m pip install regex
#/usr/bin/python3 -m pip install pandas
#/usr/bin/python3 -m pip install openpyxl
#/usr/bin/python3 -m pip install xlrd
#/usr/bin/python3 -m pip install xlsxwriter

#Use Default python as python36 on OCS VM
#sudo rm -f /bin/python
#sudo ln -s /bin/python3.6 /bin/python

#sudo echo "source scl_source enable rh-python36" >> /root/.bashrc
#sudo source /root/.bashrc