#!/bin/bash

start=$(date +%s.%N)
username=cd3user
NOW=$( date '+%F_%H-%M-%S' )
toolkit_dir="/tmp/downloadToolkit_upgrade_"$NOW

mkdir -p $toolkit_dir
logfile="/tmp/upgradeToolkit-1.log_"$NOW
# Redirect all output to log file
export LOG_FILE=$logfile
exec 3>&1
exec > "$logfile" 2>&1
echo "Redirecting all logs to $LOG_FILE" >&3

tenancyconfig_properties="$toolkit_dir/cd3_automation_toolkit/user-scripts/tenancyconfig.properties"


stop_exec () {
if [[ $? -ne 0 ]] ; then

   echo "Error encountered in CD3 Automation Toolkit Container Setup. Please do setup Manually"
   exit 1
fi
}

echo "***Download latest Toolkit***" >&3
sudo git clone https://github.com/oracle-devrel/cd3-automation-toolkit.git -b testUpgrade-container $toolkit_dir
#Get version from latest tag
git config --global --add safe.directory $toolkit_dir
cd $toolkit_dir
version=$(git describe --tags)
version=${version:0:9}
sudo mkdir /$username/$version
sudo chown -R $username:$username /$username/$version
stop_exec


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



echo "***Building container image***" >&3
name="cd3_toolkit_"$version
cd $toolkit_dir
sudo podman build --platform linux/amd64 -t $name -f Dockerfile --pull --no-cache .
stop_exec
sudo podman images


echo "***Setting Up podman Container***" >&3
sudo podman run --name $name -it -p 8444:8443 -d -v /cd3user/$version:/cd3user/tenancies  $name bash
stop_exec
sudo podman ps -a
echo "Connect to Container using command - sudo podman exec -it cd3_toolkit bash "


duration_sec=$(echo "$(date +%s.%N) - $start" | bc)
duration_min=$(echo "$duration_sec%3600/60" | bc)
execution_time=`printf "%.2f seconds" $duration_sec`
echo "Script Execution Time in Seconds: $execution_time" >&3
echo "Script Execution Time in Minutes: approx $duration_min Minutes" >&3