#!/bin/bash

username=cd3user
sudo mkdir -p /$username/mount_path
logfile="/$username/mount_path/installToolkit.log"
toolkit_dir="/tmp/githubCode"
tenancyconfig_properties="$toolkit_dir/cd3_automation_toolkit/user-scripts/tenancyconfig.properties"
start=$(date +%s.%N)
sudo sh -c "echo '########################################################################' >> /etc/motd"
sudo sh -c "echo '                 Welcome to CD3 Automation Toolkit WorkVM' >> /etc/motd"
sudo sh -c "echo '########################################################################' >> /etc/motd"
sudo sh -c "echo 'Please wait for couple of minutes for container to become active if you' >> /etc/motd"
sudo sh -c "echo 'are logging in for first time to after VM Provisioning. Toolkit initial' >> /etc/motd"
sudo sh -c "echo 'setup log is present at - /cd3user/mount_path/installToolkit.log' >> /etc/motd"
sudo sh -c "echo 'To verify podman container run command: sudo podman ps -a' >> /etc/motd"
sudo sh -c "echo 'To connect to container run command: sudo podman exec -it cd3_toolkit bash' >> /etc/motd"
sudo sh -c "echo 'if you want to stop seeing these messages at login remove in /etc/motd' >> /etc/motd"
sudo sh -c "echo '###########################################################################' >> /etc/motd"

stop_exec () {
if [[ $? -ne 0 ]] ; then
   echo $? >> $logfile 2>&1
   echo "Error encountered in CD3 Automation Toolkit Container Setup. Please do setup Manually" >> $logfile 2>&1
   exit 1
fi
}

sudo systemctl stop oracle-cloud-agent.service >> $logfile 2>&1
cd /etc/yum.repos.d/
for i in $( ls *.osms-backup ); do sudo mv $i ${i%.*}; done
echo "***SELinux permissive***" >> $logfile 2>&1
sudo setenforce 0
sudo sed -c -i "s/\SELINUX=.*/SELINUX=permissive/" /etc/sysconfig/selinux

echo "***cd3user setup***" >> $logfile 2>&1
sudo useradd -u 1001 $username
sudo sh -c "echo $username ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$username"
sudo chmod 0440 /etc/sudoers.d/$username
sudo chmod 775 -R /$username
sudo chown -R $username:$username /$username
sudo usermod -aG $username opc
sudo mkdir /home/$username/.ssh
sudo chown -R $username:$username /home/$username/.ssh
sudo chmod 700 /home/$username/.ssh
sudo cp /home/opc/.ssh/authorized_keys /home/$username/.ssh/authorized_keys
sudo chown -R $username:$username /home/$username/.ssh/authorized_keys
sudo chmod 600 /home/$username/.ssh/authorized_keys

echo "***Install git***" >> $logfile 2>&1
sudo yum install -y git >> $logfile 2>&1
stop_exec

echo "***Install Podman***" >> $logfile 2>&1
echo "########################################################" >> $logfile 2>&1
osrelase=`cat /etc/oracle-release`
if [[ $osrelase == "Oracle Linux Server release 7".* ]] ; then
     sudo yum install -y podman podman-docker >> $logfile 2>&1
     stop_exec
else
    sudo yum install -y podman podman-docker >> $logfile 2>&1
    stop_exec
    sudo systemctl enable podman.service
    sudo systemctl start podman.service
    stop_exec
fi
sudo podman --version >> $logfile 2>&1

echo "***Download Toolkit***" >> $logfile 2>&1
sudo git clone https://github.com/oracle-devrel/cd3-automation-toolkit.git $toolkit_dir >> $logfile 2>&1
stop_exec

curl -H "Authorization: Bearer Oracle" -L http://169.254.169.254/opc/v2/instance/ -o /tmp/metadata.json
metadata=$(cat /tmp/metadata.json)
user_id=$(echo "$metadata" | jq -r '.metadata.current_user_ocid')
cust_name=$(echo "$metadata" | jq -r '.metadata.tenancy_name')
tenancy_id=$(echo "$metadata" | jq -r '.metadata.tenancy_ocid')
config_region=$(echo "$metadata" | jq -r '.metadata.config_region')
sudo sed -c -i "s/prefix=.*/prefix=$cust_name/" $tenancyconfig_properties
sudo sed -c -i "s/tenancy_ocid=.*/tenancy_ocid=$tenancy_id/" $tenancyconfig_properties
sudo sed -c -i "s/region=.*/region=$config_region/" $tenancyconfig_properties
sudo sed -c -i "s/user_ocid=.*/user_ocid=$user_id/" $tenancyconfig_properties

echo "***Building container image***" >> $logfile 2>&1
cd /tmp
cd githubCode
sudo podman build --platform linux/amd64 -t cd3_toolkit -f Dockerfile --pull --no-cache . >> $logfile 2>&1
stop_exec
sudo podman images >> $logfile 2>&1

echo "***Setting Up podman Container***" >> $logfile 2>&1
sudo podman run --name cd3_toolkit -it -p 8443:8443 -d -v /cd3user/mount_path:/cd3user/tenancies  cd3_toolkit bash >> $logfile 2>&1
stop_exec
sudo podman ps -a >> $logfile 2>&1
echo "Connect to Container using command - sudo podman exec -it cd3_toolkit bash " >> $logfile 2>&1

sudo systemctl start oracle-cloud-agent.service

duration_sec=$(echo "$(date +%s.%N) - $start" | bc)
duration_min=$(echo "$duration_sec%3600/60" | bc)
execution_time=`printf "%.2f seconds" $duration_sec`
echo "Script Execution Time in Seconds: $execution_time" >> $logfile 2>&1
echo "Script Execution Time in Minutes: approx $duration_min Minutes" >> $logfile 2>&1
