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

  # initialize temp unique_dir file
  > /tmp/unique_dirs
  chmod 777 /tmp/unique_dirs
  # copy all the tfvars to destination path and store directories to unique_dirs file
  sudo find . -type f -name "*.auto.tfvars" -exec bash -c '
  dest="$1/$2"
  dest_dir_on_vm=$(dirname "$dest")
  if [ -d "$dest_dir_on_vm" ]; then
    cp "$2" "$dest"
    echo $dest_dir_on_vm >> /tmp/unique_dirs
  fi
  ' -- "$dest_dir" {} \;
  # remove duplicate lines from unique_dirs file
  sort -u /tmp/unique_dirs -o /tmp/unique_dirs

  # process each line from unique_dirs file
  while IFS= read -r line; do
  # Skip empty or whitespace-only lines
  [[ -z "${line// }" ]] && continue
  dir=$line
  echo "Processing: $dir"
  source_dir=$(echo "$dir" |sed "s/$version/tenancies/g")
  echo "source dir : $source_dir"
  source_dir_on_vm=$(echo "$dir" |sed "s/${version}/${current_version}/g")
  sudo podman exec -it $current_name bash -c "cd $source_dir; terraform init; terraform state pull > source_tfstate;> resources_list;terraform state list|while IFS= read -r r_export; do echo $r_export >> resources_list; echo $r_export; done"

 dest_dir=$(echo "$dir" |sed "s/$version/tenancies/g")
 sudo cp "$source_dir_on_vm"/source_tfstate "$dir"/source_tfstate
 sudo cp "$source_dir_on_vm"/resources_list "$dir"/resources_list
 sudo chown -R $username:$username /$username/$version
 echo "dest_dir : $dest_dir"
 sudo podman exec -it $name bash -c "cd $dest_dir; terraform init; terraform state pull > dest_tfstate; cat resources_list|while IFS= read -r r_import; do terraform state mv --state source_tfstate --state-out dest_tfstate \"$r_import\" \"$r_import\"; done; terraform state push dest_tfstate"
 done < "/tmp/unique_dirs"
done
