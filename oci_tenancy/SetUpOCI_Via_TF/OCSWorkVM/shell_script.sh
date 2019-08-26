#!/bin/bash

#Create Required Directories
mkdir ~/.oci
mkdir -p /root/ocswork/keys
mkdir -p /root/ocswork/downloads
#mkdir -p /root/ocswork/terraform_files/ashburn
#mkdir -p /root/ocswork/terraform_files/phoenix
mkdir -p /root/ocswork/git_oci
mkdir -p /root/ocswork/git_ocic2oci
mkdir -p /root/ocswork/ocic2oci_work

## Needed for conversion from putty ppk to openssh
sudo yum install -y putty

#Install Required Packages
sudo yum -y install python-pip
#pip install pip==9.0.3
pip install oci
pip install oci-cli
pip install pandas
pip install xlrd
pip install puttykeys
pip install netaddr
pip install cfgparse
pip install in_place

#sudo yum -y install screen
sudo yum -y install git
sudo yum -y install terraform
sudo yum -y install expect


sudo yum -y install ansible
cd /root/ocswork/downloads
git clone https://github.com/oracle/oci-ansible-modules.git
cd oci-ansible-modules
./install.py

sudo yum -y install java
sudo yum -y install wget

sudo yum -y install python36 python36-setuptools graphviz
sudo easy_install-3.6 pip

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
## the download_git_expect1.sh and download_git_expect2.sh will not be created if configure_git is set to 0 in the props file.
if [ -e /home/opc/download_git_expect1.sh ]
then
    cd  /home/opc
    dos2unix download_git_expect1.sh download_git_expect1.sh
    chmod +x download_git_expect1.sh
    cd /root/ocswork/git_oci
    git init
    cd  /home/opc
    ./download_git_expect1.sh
    sleep 5s
    find /root/ocswork/git_oci -type f -iname "*.py" -exec chmod +x {} \;
fi
if [ -e /home/opc/download_git_expect2.sh ]
then
    cd /home/opc
    dos2unix download_git_expect2.sh download_git_expect2.sh
    chmod +x download_git_expect2.sh
    cd /root/ocswork/git_ocic2oci
    git init
    cd  /home/opc
    ./download_git_expect2.sh
    sleep 5s
    find /root/ocswork/git_ocic2oci -type f -iname "*.py" -exec chmod +x {} \;
fi

#Configure Panda
if [ -e /home/opc/panda.tf ]
then
    echo "Panda Config START"
    mkdir -p /root/ocswork/ocic2oci_work
    cp /root/ocswork/git_oci/oci_tenancy/SetUpOCI_Via_TF/OCSWorkVM/panda_setup_files/* /root/ocswork/ocic2oci_work/
    chmod +x /root/ocswork/ocic2oci_work/*.py
    chmod +x /root/ocswork/ocic2oci_work/*.sh

    cd /root/ocswork/ocic2oci_work/

    ## Copy files generated using createOCSWork
    mv /home/opc/panda.tf /root/ocswork/ocic2oci_work/
    mv /home/opc/ocic-provider.tf /root/ocswork/ocic2oci_work/
    mv /home/opc/ocic-variables.tf /root/ocswork/ocic2oci_work/
    mv /home/opc/variables.yml /root/ocswork/ocic2oci_work/
    mv /home/opc/upgrade_terraform_expect_script.sh /root/ocswork/ocic2oci_work/

    chown root:root /root/ocswork/ocic2oci_work/*.tf
    chown root:root /root/ocswork/ocic2oci_work/variables.yml

    cd /root/ocswork/ocic2oci_work
    ## The unfortunate side effect of running so many things through shell.  The kernel seems to be throwing irq messages.
    ## Sleep to see if this helps.
    sleep 3s
    terraform init
    sleep 3s

    dos2unix upgrade_terraform_expect_script.sh upgrade_terraform_expect_script.sh
    chmod +x upgrade_terraform_expect_script.sh
    ./upgrade_terraform_expect_script.sh

    sleep 1s
    terraform init
    sleep 1s

   ## Writing some retry logic to TF
    n=0
    until [ $n -ge 5 ]
    do
      terraform apply -auto-approve && break
      n=$[$n+1]
      sleep 3
    done
    echo "Panda Config END"
fi

#Configure Koala
if [ -e /home/opc/default ]
then
    echo "Koala Config START"

    cp /root/ocswork/ocic2oci_work/opcmigrate-1.4.0.zip /root/ocswork/downloads/opcmigrate.zip
    cd /root/ocswork/downloads
    unzip opcmigrate.zip -d /root/ocswork/opcmigrate
    cd /root/ocswork/opcmigrate

    python36 -m pip install ./opcmigrate-*.whl

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
            echo "koala discover completed..proceeding"
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
timeout 60 yum install python36-devel gcc -y

#Configuring DB specific packages in python36
echo "Installing packages for python36 required for DB migration...this would keep running in background and you can start your work"
python36 -m pip install --upgrade pip
python36 -m pip install oci
python36 -m pip install pycrypto
python36 -m pip install regex
python36 -m pip install pandas
python36 -m pip install openpyxl
python36 -m pip install xlrd
python36 -m pip install xlsxwriter

#Use Default python as python36 on OCS VM
sudo rm -f /bin/python
sudo ln -s /bin/python36 /bin/python