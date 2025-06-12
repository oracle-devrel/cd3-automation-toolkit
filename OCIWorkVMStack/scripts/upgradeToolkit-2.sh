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
  sudo chmod 777 /tmp/unique_dirs
  # copy all the tfvars to destination path and store directories to unique_dirs file
  sudo find . -type f -name "*.auto.tfvars" -exec bash -c '
  dest="$1/$2"
  dest_dir_on_vm=$(dirname "$dest")
  if [ -d "$dest_dir_on_vm" ]; then
    sudo cp "$2" "$dest"
    echo $dest_dir_on_vm >> /tmp/unique_dirs
  fi
  ' -- "$dest_dir" {} \;
  # remove duplicate lines from unique_dirs file
  sort -u /tmp/unique_dirs -o /tmp/unique_dirs
  echo "processing all directories with tfvars files"
  # process each line from unique_dirs file

# Read file into an array
mapfile -t dirs < /tmp/unique_dirs

for dir in "${dirs[@]}"; do
  # Skip empty lines and lines starting with "data"
  [[ -z "$dir" || "$dir" == data* ]] && continue

  echo "Processing $dir"

  source_dir=$(echo "$dir" | sed "s/$version/tenancies/g")
  source_dir_on_vm=$(echo "$dir" | sed "s/${version}/${current_version}/g")

  # Run Terraform in source container
  sudo podman exec -i "$current_name" bash -c "
    cd \"$source_dir\" || exit 1
    terraform init
    terraform state pull > source_tfstate
    terraform state list > resources_list
  "

  echo "Moving to new container"

  dest_dir=$(echo "$dir" | sed "s/$version/tenancies/g")
  echo "Dest dir: $dest_dir"

  # Copy state files from source VM directory
  sudo cp "$source_dir_on_vm/source_tfstate" "$dir/" || { echo "Failed to copy source_tfstate"; continue; }
  sudo cp "$source_dir_on_vm/resources_list" "$dir/" || { echo "Failed to copy resources_list"; continue; }
  sudo chown -R "$username:$username" "/$username/$version"

  # Run Terraform in destination container
  sudo podman exec -i "$name" bash -c "
    cd \"$dest_dir\" || exit 1
    terraform init
    terraform state pull > dest_tfstate
    while IFS= read -r r_import || [[ -n \"\$r_import\" ]]; do
      [[ -z \"\$r_import\" || \"\$r_import\" =~ ^# || \"\$r_import\" == data* ]] && continue
      terraform state mv --state source_tfstate --state-out dest_tfstate \"\$r_import\" \"\$r_import\"
    done < resources_list
    echo 'Pushing to state'
    terraform state push dest_tfstate
  "
  current_region=$(basename "$(dirname "$dir")")
  SRC_FILE="$source_dir_on_vm/variables_$current_region.tf"
  DEST_FILE="$dir/variables_$current_region.tf"
  #START_MARKER="variable \"instance_ssh_keys\""
  #END_MARKER="#instance_ssh_keys_END#"
  START_MARKER="#START_compartment_ocids#"
  END_MARKER="#compartment_ocids_END#"

  # Extract block (including markers) from source
  BLOCK=$(sudo sed -n "/$START_MARKER/,/$END_MARKER/p" "$SRC_FILE")

  # Escape special characters for safe insertion
  ESCAPED_BLOCK=$(printf '%s\n' "$BLOCK" | sed 's/[&/\]/\\&/g')

  # Use awk to delete the block in DEST and insert new content
  sudo awk -v start="$START_MARKER" -v end="$END_MARKER" -v block="$ESCAPED_BLOCK" '
  BEGIN {
      split(block, newblock, "\n")
      inblock = 0
  }
  {
      if ($0 ~ start) {
          inblock = 1
          for (i in newblock) print newblock[i]
      } else if ($0 ~ end && inblock) {
          inblock = 0
          next
      } else if (!inblock) {
          print
      }
  }
  ' "$DEST_FILE" > "/tmp/var.tmp" && sudo cp "/tmp/var.tmp" "$DEST_FILE"

  echo "Updated '$DEST_FILE' in-place with content from '$SRC_FILE'."
  echo "Done processing $dir"
done

done