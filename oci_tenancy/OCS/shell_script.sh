#!/bin/bash

#Create Required Directories
mkdir ~/.oci
mkdir -p /root/ocswork/keys
mkdir -p /root/ocswork/downloads
mkdir -p /root/ocswork/terraform_files
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
mv /home/opc/provider.tf /root/ocswork/terraform_files
mv /home/opc/variables.tf /root/ocswork/terraform_files
chown root:root /root/ocswork/terraform_files/*

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
if [ -e /home/opc/ftmcli.properties ]
then
    echo "Panda Config START"
    cd /root/ocswork/downloads
    #wget https://objectstorage.us-ashburn-1.oraclecloud.com/p/Cj0Z_QotMh9JnGiIQGYuMDTq5h26PhrMq_Xcl0XhE94/n/intocimig/b/ctls_images/o/OCIC_OCI_Migration_List_panda_1_2_0.tar.gz
    #wget https://objectstorage.us-ashburn-1.oraclecloud.com/p/tWsO9aLhPmJhHKZzG7SPz6ToammwV26-tsg8blOf7cw/n/intocimig/b/ctls_images/o/OCIC_OCI_Migration_List_panda_1_3_0.tar.gz -O OCIC_OCI_Migration_List_panda.tar.gz
    wget https://objectstorage.us-ashburn-1.oraclecloud.com/p/bkknXW6XCyTG59y8aiH_9HK6PSUiHXwbzlsO3thtfu8/n/intocimig/b/ctls_images/o/OCIC_OCI_Migration_List_panda_1_4_0.tar.gz -O OCIC_OCI_Migration_List_panda.tar.gz

    mkdir -p /root/ocswork/ocic2oci_work
    cp /root/ocswork/git_ocic2oci/OCS/panda_setup_files/* /root/ocswork/ocic2oci_work/
    chmod +x /root/ocswork/ocic2oci_work/*.py
    chmod +x /root/ocswork/ocic2oci_work/*.sh

    cd /root/ocswork/ocic2oci_work/
    unzip ftmcli-v2.4.3.zip
    cd ftmcli-v2.4.3
    mv ftmcli.properties ftmcli.properties_ORIG
    mv /home/opc/ftmcli.properties .
    mv /root/ocswork/downloads/OCIC_OCI_Migration_List_panda.tar.gz /root/ocswork/ocic2oci_work/ftmcli-v2.4.3/
    chown root:root ftmcli.properties

    cd /home/opc
    dos2unix upload_panda_expect.sh upload_panda_expect.sh
    chmod +x upload_panda_expect.sh
    ./upload_panda_expect.sh
    sleep 10s

    ## Copy files generated using createOCSWork
    mv /home/opc/panda.tf /root/ocswork/ocic2oci_work/
    mv /home/opc/ocic-provider.tf /root/ocswork/ocic2oci_work/
    mv /home/opc/ocic-variables.tf /root/ocswork/ocic2oci_work/
    mv /home/opc/variables.yml /root/ocswork/ocic2oci_work/
    chown root:root /root/ocswork/ocic2oci_work/*.tf
    chown root:root /root/ocswork/ocic2oci_work/variables.yml

    cd /root/ocswork/ocic2oci_work
    ## The unfortunate side effect of running so many things through shell.  The kernel seems to be throwing irq messages.
    ## Sleep to see if this helps.
    sleep 3s
    terraform init
    sleep 3s

   # terraform apply -auto-approve
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

    # Don't use 1.0
    #wget https://objectstorage.us-ashburn-1.oraclecloud.com/p/E6ucg47gNtt4OWulJYmOHEgXzx1lthALaY6MeW3JoKA/n/intocimig/b/ocic-oci-test-migration/o/opcmigrate-1.0.0.zip

    cd /root/ocswork/downloads
    #wget https://objectstorage.us-ashburn-1.oraclecloud.com/p/q_WoaL7oyTQXuStOkNgaz4eKZjCf1tJCNMjqqUgd_64/n/intocimig/b/ocic-oci-test-migration/o/opcmigrate-1.1.0.zip -O opcmigrate.zip
    wget https://objectstorage.us-ashburn-1.oraclecloud.com/p/YiJ9tqrZ0IBQJzCHMK6iKh5J8M7CWDhGHlkkWlalL40/n/intocimig/b/ocic-oci-test-migration/o/opcmigrate-1.2.0.zip -O opcmigrate.zip

    mkdir -p /root/ocswork/opcmigrate
    cd /root/ocswork/downloads
    unzip opcmigrate.zip -d /root/ocswork/opcmigrate
    cd /root/ocswork/opcmigrate

    #python36 -m pip install ./opcmigrate-1.1.0_dev_20190118.232119.87-py3-none-any.whl
    #python36 -m pip install ./opcmigrate-1.1.0_20190128.221621.93-py3-none-any.whl
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
            /usr/local/bin/opcmigrate instances-export > instance-export.json
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


#Installing python36-devel and gcc for pip install
timeout 60 yum install python36-devel gcc -y

#Configuring DB specific packages in python36
echo "Installing packages for python36 required for DB migration...this would keep running in background and you can start your work"
python36 -m pip install --upgrade pip
python36 -m pip install oci
python36 -m pip install pycrypto
python36 -m pip install regex
