#!/bin/bash

start=$(date +%s.%N)
username=cd3user
NOW=$( date '+%F_%H-%M-%S' )
logfile="/tmp/upgradeToolkit-2.log_"$NOW

stop_exec () {
if [[ $? -ne 0 ]] ; then
   echo $? >> $logfile 2>&1
   echo "Error encountered in CD3 Automation Toolkit Container Setup. Please do setup Manually" >> $logfile 2>&1
   exit 1
fi
}

sudo git clone https://github.com/oracle-devrel/cd3-automation-toolkit.git -b testUpgrade-container /tmp/temp
#Get version from latest tag
git config --global --add safe.directory /tmp/temp
cd /tmp/temp
version=$(git describe --tags)
version=${version:0:9}
sudo rm -rf /tmp/temp
stop_exec

name="cd3_toolkit_"$version


#################### Run createTenancyConfig.py for new version and create Prefixes ################
read -p "Enter Current Version to be upgraded: " current_version
echo $current_version
current_name="cd3_toolkit_"$current_version

read -p "Enter comma seperated prefix names to be ungraded: " current_prefixes
echo $current_prefixes

# Setting IFS (input field separator) value as ","
IFS=','

# Reading the split string into array
read -ra arr <<< "$current_prefixes"

# Print each value of the array by using the loop

echo "Python script execution will start now" >> $logfile 2>&1
for prefix in "${arr[@]}";
do
  sudo mkdir -p /$username/$version/$prefix/.config_files
  sudo cp /$username/$current_version/$prefix/.config_files/* /$username/$version/$prefix/.config_files
  sudo chown -R $username:$username /$username/$version
  sudo chown -R $username:$username /$username/$current_version
  echo "Running createTenancyConfig.py for prefix: $prefix"
  sudo podman exec -it $name bash -c "cd /${username}/oci_tools/cd3_automation_toolkit/user-scripts; python createTenancyConfig.py /${username}/tenancies/${prefix}/.config_files/${prefix}_tenancyconfig.properties --upgradeToolkit True"
  echo "createTenancyConfig.py ended for prefix: $prefix"

  #echo "Running Fetch Compartments for prefix: $prefix"
  #sudo podman exec -it $name bash -c "cd /${username}/oci_tools/cd3_automation_toolkit; python setupOCI.py /${username}/tenancies/${prefix}/${prefix}_setUpOCI.properties "

  echo "Copying tfvars for prefix: $prefix from $current_version to $version and running terraform plan"

  dest_dir=/${username}/${version}/${prefix}/terraform_files
  cd /${username}/${current_version}/${prefix}/terraform_files
  sudo find . -type f -name "*.auto.tfvars" -exec bash -c '
  dest="$1/$2"
  dest_dir_on_vm=$(dirname "$dest")
  if [ -d "$dest_dir_on_vm" ]; then
    cp "$2" "$dest"

    source_dir=$(echo "$dest_dir_on_vm" |sed 's/${version}/tenancies/g')
    source_dir_on_vm=$(echo "$dest_dir_on_vm" |sed 's/${version}/${current_version}/g')
    echo "------------------------------------------------"
    echo "Pulling terraform state for $source_dir on $3"
    echo "------------------------------------------------"
    sudo podman exec -it $3 bash -c "cd $source_dir; terraform init; terraform state pull > terraform.tfstate"

    cp "$source_dir_on_vm"/terraform.tfstate "$dest_dir_on_vm"/terraform.tfstate

    dest_dir=$(echo "$dest_dir_on_vm " |sed 's/${version}/tenancies/g')
    echo "------------------------------------------------"
    echo "Pushing terraform state and running plan for $dest_dir on $4"
    echo "------------------------------------------------"
    sudo podman exec -it $4 bash -c "cd $dest_dir; terraform init; terraform state push terraform.tfstate"
    sudo podman exec -it $4 bash -c "cd $dest_dir; terraform plan"
  fi
' -- "$dest_dir" {} "$current_name" "$name" \;

done

