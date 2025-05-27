#!/bin/bash

start=$(date +%s.%N)
username=cd3user
#sudo mkdir -p /$username/mount_path
sudo mkdir -p /$username/
NOW=$( date '+%F_%H-%M-%S' )
toolkit_dir="/tmp/downloadToolkit_"$NOW

mkdir -p $toolkit_dir
logfile="/tmp/installToolkit.log_"$NOW
tenancyconfig_properties="$toolkit_dir/cd3_automation_toolkit/user-scripts/tenancyconfig.properties"


stop_exec () {
if [[ $? -ne 0 ]] ; then
   echo $? >> $logfile 2>&1
   echo "Error encountered in CD3 Automation Toolkit Container Setup. Please do setup Manually" >> $logfile 2>&1
   exit 1
fi
}

echo "***Download Toolkit***" >> $logfile 2>&1
sudo git clone https://github.com/oracle-devrel/cd3-automation-toolkit.git -b testUpgrade $toolkit_dir
#Get version from release-Notes of code downloaded
version="v2025.1.1"
stop_exec

sudo mkdir -p /$username/$version

sudo sh -c "echo '########################################################################' >> /etc/motd"
sudo sh -c "echo '                 Welcome to CD3 Automation Toolkit WorkVM' >> /etc/motd"
sudo sh -c "echo '########################################################################' >> /etc/motd"
sudo sh -c "echo 'Please wait for couple of minutes for container to become active if you' >> /etc/motd"
sudo sh -c "echo 'are logging in for first time to after VM Provisioning. Toolkit initial' >> /etc/motd"
sudo sh -c "echo 'setup log is present at - /cd3user/"$version"/installToolkit.log' >> /etc/motd"
sudo sh -c "echo 'To verify podman container run command: sudo podman ps -a' >> /etc/motd"
sudo sh -c "echo 'To connect to container run command: sudo podman exec -it cd3_toolkit bash' >> /etc/motd"
sudo sh -c "echo 'if you want to stop seeing these messages at login remove in /etc/motd' >> /etc/motd"
sudo sh -c "echo '###########################################################################' >> /etc/motd"


sudo curl -H "Authorization: Bearer Oracle" -L http://169.254.169.254/opc/v2/instance/ -o /tmp/metadata.json
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
name="cd3_toolkit_"$version
cd $toolkit_dir
sudo podman build --platform linux/amd64 -t $name -f Dockerfile --pull --no-cache . >> $logfile 2>&1
stop_exec
sudo podman images >> $logfile 2>&1


echo "***Setting Up podman Container***" >> $logfile 2>&1
sudo podman run --name $name -it -p 8443:8443 -d -v /cd3user/$version:/cd3user/tenancies  $name bash >> $logfile 2>&1
stop_exec
sudo podman ps -a >> $logfile 2>&1
echo "Connect to Container using command - sudo podman exec -it cd3_toolkit bash " >> $logfile 2>&1


duration_sec=$(echo "$(date +%s.%N) - $start" | bc)
duration_min=$(echo "$duration_sec%3600/60" | bc)
execution_time=`printf "%.2f seconds" $duration_sec`
echo "Script Execution Time in Seconds: $execution_time" >> $logfile 2>&1
echo "Script Execution Time in Minutes: approx $duration_min Minutes" >> $logfile 2>&1



#################### Copy files and run createTenancy for new version ################
read -p "Enter Current Version to be upgraded: " current_version
echo $current_version

read -p "Enter comma seperated prefix names ro be ungraded: " current_prefixes
echo $current_prefixes

# Setting IFS (input field separator) value as ","
IFS=','

# Reading the split string into array
read -ra arr <<< "$current_prefixes"

# Print each value of the array by using the loop

echo "Running createTenancyConfig.py for input prefixes" >> $logfile 2>&1
do
  sudo mkdir -p /cd3user/$version/$prefix/.config_files
  sudo  cp /cd3user/$current_version/$prefix/.config_files/* /cd3user/$version/$prefix/.config_files
  sudo podman exec -it $name bash -c "cd /cd3user/oci_tools/cd3_automation_toolkit/user-scripts; python createTenancyConfig.py /cd3user/$version/$prefix/.config_files/${prefix}_tenancyconfig.properties --upgradeToolkit True" >> $logfile 2>&1
done
