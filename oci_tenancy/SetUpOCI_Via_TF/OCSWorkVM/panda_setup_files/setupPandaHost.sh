#!/bin/bash

echo "This must be run only after the Terraform to install and configure panda has been sucessfully run."
export PANDA_PUB_IP=`terraform output panda_pub_ip`
## now configure Panda using ansible
# Remove any errant ansible files
echo "Starting Ansible work"
rm -rf /root/.ansible/cp/*
#mv /home/opc/*.yml /root/ocswork/ocic2oci_work/
#chown root:root /root/ocswork/ocic2oci_work/*.yml
cd /root/ocswork/ocic2oci_work
cp /etc/ansible/ansible.cfg /etc/ansible/ansible.cfg.orig
sed -i 's/#host_key_checking = False/host_key_checking = False/g' /etc/ansible/ansible.cfg

rm -rf /root/.ansible/cp/*
ANSIBLE_HOST_KEY_CHECKING=False
#timeout 30  ansible-playbook -u opc --private-key /root/ocswork/keys/ssh-pvt-key-openssh.ppk -i  $PANDA_PUB_IP, lvm-setup.yml ctls_ssh_fix.yml
timeout 30  ansible-playbook -u opc --private-key /root/ocswork/keys/ssh-pvt-key-openssh.ppk -i  $PANDA_PUB_IP, ctls_ssh_fix.yml
retVal=$?

if [ $retVal -eq 124 ]; then
        echo " Ansible timed out - running again after deleting the /root/.ansible/cp/* directory "
        rm -rf /root/.ansible/cp/*
        ANSIBLE_HOST_KEY_CHECKING=False
        #timeout 30  ansible-playbook -u opc --private-key /root/ocswork/keys/ssh-pvt-key-openssh.ppk -i  $PANDA_PUB_IP, lvm-setup.yml ctls_ssh_fix.yml
        timeout 30  ansible-playbook -u opc --private-key /root/ocswork/keys/ssh-pvt-key-openssh.ppk -i  $PANDA_PUB_IP, ctls_ssh_fix.yml
fi


./createPandaInputs.py terraform.tfstate instance-export.json resources-default.json report_ocic.xlsx

#echo "Copy over the files like below"
#.echo "scp  -o StrictHostKeyChecking=no -i /root/ocswork/keys/ssh-pvt-key-openssh.ppk tmp/** opc@$PANDA_PUB_IP:/home/opc/ansible/"
#.echo "scp  -o StrictHostKeyChecking=no -i /root/ocswork/keys/ssh-pvt-key-openssh.ppk /root/ocswork/keys/oci_api_key.pem opc@$PANDA_PUB_IP:/home/opc/.oci/"
#echo "scp  -o StrictHostKeyChecking=no -i /root/ocswork/keys/ssh-pvt-key-openssh.ppk /root/ocswork/keys/ssh-pvt-key-openssh.ppk opc@$PANDA_PUB_IP:/home/opc/.ssh/host_key_rsa"


rm -rf /root/.ansible/cp/*
timeout 300   ansible-playbook -u opc --private-key /root/ocswork/keys/ssh-pvt-key-openssh.ppk -i  $PANDA_PUB_IP, copy_files_and_install_panda.yml
retVal=$?

if [ $retVal -eq 124 ]; then
        echo " Ansible timed out - running again after deleting the /root/.ansible/cp/* directory "
        rm -rf /root/.ansible/cp/*
        ANSIBLE_HOST_KEY_CHECKING=False
        timeout 300   ansible-playbook -u opc --private-key /root/ocswork/keys/ssh-pvt-key-openssh.ppk -i  $PANDA_PUB_IP, copy_files_and_install_panda.yml
fi

#### Copying rquired files for custom DNS ###
timeout 30   ansible-playbook -u opc --private-key /root/ocswork/keys/ssh-pvt-key-openssh.ppk -i  $PANDA_PUB_IP, /root/ocswork/git_ocic2oci/dns/custom_dns.yml
retVal=$?

if [ $retVal -eq 124 ]; then
        echo " Ansible timed out - running again after deleting the /root/.ansible/cp/* directory "
        rm -rf /root/.ansible/cp/*
        ANSIBLE_HOST_KEY_CHECKING=False
        timeout 30   ansible-playbook -u opc --private-key /root/ocswork/keys/ssh-pvt-key-openssh.ppk -i  $PANDA_PUB_IP, /root/ocswork/git_ocic2oci/dns/custom_dns.yml
fi


#### Copying required rsync files to Panda server ###
rm -rf /root/.ansible/cp/*
timeout 30   ansible-playbook -u opc --private-key /root/ocswork/keys/ssh-pvt-key-openssh.ppk -i  $PANDA_PUB_IP, /root/ocswork/git_ocic2oci/rsync/setup-pandaserver4rsync.yml
retVal=$?

if [ $retVal -eq 124 ]; then
        echo " Ansible timed out - running again after deleting the /root/.ansible/cp/* directory "
        rm -rf /root/.ansible/cp/*
        ANSIBLE_HOST_KEY_CHECKING=False
        timeout 30   ansible-playbook -u opc --private-key /root/ocswork/keys/ssh-pvt-key-openssh.ppk -i  $PANDA_PUB_IP, /root/ocswork/git_ocic2oci/rsync/setup-pandaserver4rsync.yml
fi

### Add panda Server IP to rsync properties file ###
echo "Adding Public IP of Panda server to rsyncserver.properties"
sed -i '/panda_server_ip=/c\panda_server_ip='"$PANDA_PUB_IP" /root/ocswork/git_ocic2oci/rsync/rsyncserver.properties


#### Installing custom packages on Panda server ###
rm -rf /root/.ansible/cp/*
timeout 30   ansible-playbook -u opc --private-key /root/ocswork/keys/ssh-pvt-key-openssh.ppk -i  $PANDA_PUB_IP, custom_package_install.yml
retVal=$?

if [ $retVal -eq 124 ]; then
        echo " Ansible timed out - running again after deleting the /root/.ansible/cp/* directory "
        rm -rf /root/.ansible/cp/*
        ANSIBLE_HOST_KEY_CHECKING=False
        timeout 30   ansible-playbook -u opc --private-key /root/ocswork/keys/ssh-pvt-key-openssh.ppk -i  $PANDA_PUB_IP, custom_package_install.yml
fi

### Setting Panda System MTU size to 1400

echo  "Setting Panda System MTU size to 1400 "
timeout 10 ssh -i /root/ocswork/keys/ssh-pvt-key-openssh.ppk opc@$PANDA_PUB_IP sudo /sbin/ip link set dev eth0 mtu 1400
timeout 10 ssh -i /root/ocswork/keys/ssh-pvt-key-openssh.ppk opc@$PANDA_PUB_IP 'echo "supersede interface-mtu 1400; "  |sudo tee -a /etc/dhcp/dhclient-eth0.conf'

echo " Login to the Panda servers and follow the instructions. Latest version of Panda has been installed for your comfort and safety."
echo " All the generated secret & host files have been copied to the /home/opc/ansible directory"
