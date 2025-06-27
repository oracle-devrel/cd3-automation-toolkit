#!/bin/bash

start=$(date +%s.%N)
username=cd3user
NOW=$( date '+%F_%H-%M-%S' )
logfile="/tmp/upgradeToolkit-2.log_"$NOW

# Redirect all output to log file
export LOG_FILE=$logfile
exec 3>&1
exec > "$logfile" 2>&1
echo "redirecting all logs to $LOG_FILE" >&3

stop_exec () {
if [[ $? -ne 0 ]] ; then
   echo "Error encountered in CD3 Automation Toolkit Container Setup. Please do setup Manually"
   exit 1
fi
}

function copy_data_from_variables_file() {

  #echo -e "\nCopying data for $START_MARKER and $END_MARKER from $SRC_FILE into $DEST_FILE "
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
}


sudo git clone https://github.com/oracle-devrel/cd3-automation-toolkit.git -b testUpgrade-container /tmp/temp
#Get version from latest tag
git config --global color.ui false
git config --global --add safe.directory /tmp/temp
cd /tmp/temp
version=$(git describe --tags)
version=${version:0:9}
sudo rm -rf /tmp/temp
stop_exec

name="cd3_toolkit_"$version


#################### Run createTenancyConfig.py for new version and create Prefixes ################
#sudo read -p "Enter Current Version to be upgraded: " current_version > /dev/tty
echo -n "Enter Current Version to be upgraded: " >&3
read current_version < /dev/tty
current_name="cd3_toolkit_"$current_version

if [ ! -d "/$userdir/$current_version" ] && sudo podman container exists "$current_name"; then
  echo -e "Valid Version. Proceeding further...\n"
else
  echo "Invalid Version. Exiting!!!"
  exit 1
fi

#sudo read -p "Enter comma separated prefix names to be upgraded: " current_prefixes > /dev/tty
echo -n "Enter comma separated prefix names to be upgraded: " >&3
read current_prefixes < /dev/tty

# Setting IFS (input field separator) value as ","
IFS=','

# Reading the split string into array
read -ra arr <<< "$current_prefixes"

# Print each value of the array by using the loop

echo "Python script execution will start now"
for prefix in "${arr[@]}";
do
  if [ ! -d "/$username/$current_version/$prefix" ]; then
    echo "Invalid Prefix $prefix. Continuing with next!!!"
    continue
  fi

  sudo mkdir -p /$username/$version/$prefix/.config_files
  sudo cp /$username/$current_version/$prefix/.config_files/* /$username/$version/$prefix/.config_files
  sudo chown -R $username:$username /$username/$version
  sudo chown -R $username:$username /$username/$current_version
  echo "--------------------------------------------------"
  echo -e "\nRunning createTenancyConfig.py for prefix: $prefix" >&3
  sudo podman exec -it $name bash -c "cd /${username}/oci_tools/cd3_automation_toolkit/user-scripts; python createTenancyConfig.py /${username}/tenancies/${prefix}/.config_files/${prefix}_tenancyconfig.properties --upgradeToolkit True" 2>&1 > /dev/tty
  echo "createTenancyConfig.py ended for prefix: $prefix"
  echo "--------------------------------------------------"

  echo -e "Checking GIT repo configuration for prefix $prefix  and version $current_version"
  current_git_status=$(sudo podman exec -it $current_name bash -c "cd /${username}/tenancies/${prefix}/terraform_files/; git config --global color.ui false; git status")
  echo $current_git_status

  echo -e "Checking GIT repo configuration for prefix $prefix  and version $version"
  git_status=$(sudo podman exec -it $name bash -c "cd /${username}/tenancies/${prefix}/terraform_files/; git config --global color.ui false; git status")
  echo $git_status

  text="fatal: not a git repository"

  if [[ "$current_git_status" != *"$text"* && "$git_status" != *"$text"* ]]; then
    echo "\nGIT is configured properly for both versions for prefix $prefix. Proceeding with GIT operations\n"
    git=1
  elif [[ "$current_git_status" == *"$text"* && "$git_status" == *"$text"* ]]; then
    echo "\nGIT is not configured for both versions for prefix $prefix. Proceeding without GIT operations\n"
    git=0
  else
    echo "\nGIT status not same for both versions for this prefix $prefix. Exiting!!!\n"
  fi

  echo "Copying tfvars for prefix: $prefix from $current_version to $version and running terraform plan" >&3

  dest_dir=/${username}/${version}/${prefix}/terraform_files
  if [ "$git" == 1 ]; then
    echo -e "\nPulling from git main"
    sudo podman exec -it "$current_name" bash -c "
    cd /${username}/tenancies/${prefix}/terraform_files/ || exit 1
    git remote get-url origin
    git_url=\$(git remote get-url origin)
    echo \"Cloning from: \$git_url\"
    git clone \"\$git_url\" ../main_repo
    cd ../main_repo || exit 1
    git checkout main
    git pull origin main
    "
    src=main_repo
  else
    src=terraform_files
  fi
  cd /${username}/${current_version}/${prefix}/${src}
  echo "Source Dir: $PWD" >&3
  
  # initialize temp unique_dir file
  > /tmp/unique_dirs
  sudo chmod 777 /tmp/unique_dirs
  # copy all the tfvars to destination path and store directories to unique_dirs file
  sudo find . -type f -name "*.auto.tfvars" -exec bash -c '
  dest="$1/$2"
  echo $2
  dest_dir_on_vm=$(dirname "$dest")
  if [ -d "$dest_dir_on_vm" ]; then
    sudo cp "$2" "$dest"
    echo $dest_dir_on_vm
    echo $dest_dir_on_vm >> /tmp/unique_dirs
  fi
  ' -- "$dest_dir" {} \;
  # remove duplicate lines from unique_dirs file
  sort -u /tmp/unique_dirs -o /tmp/unique_dirs
  echo "--------------------------------------------------"
  echo "Processing all directories one by one found with tfvars files"
  # process each line from unique_dirs file
 # if [ "$git" == 1 ]; then
 #   echo -e "\ncheckout develop back in source dir"
 #   sudo podman exec -it $current_name bash -c "cd /${username}/tenancies/${prefix}/terraform_files/; git checkout develop;git config --global color.ui true"
 # fi

  # Read file into an array
  mapfile -t dirs < /tmp/unique_dirs

  for dir in "${dirs[@]}"; do
    # Skip empty lines and lines starting with "data"
    [[ -z "$dir" || "$dir" == data* ]] && continue

    echo -e "\nProcessing $dir --->"

    source_dir=$(echo "$dir" | sed "s/$version/tenancies/g")
    source_dir=$(echo "$source_dir" | sed "s/terraform_files/$src/g")
    echo "Source dir: $source_dir"
    source_dir_on_vm=$(echo "$dir" | sed "s/${version}/${current_version}/g")
    source_dir_on_vm=$(echo "$source_dir_on_vm" | sed "s/terraform_files/$src/g")
    # Run Terraform in source container
    sudo podman exec -i "$current_name" bash -c "
      cd \"$source_dir\" || exit 1
      export TF_CLI_ARGS=-no-color
      terraform init
      terraform state pull > source_tfstate
      terraform state list > resources_list
    "

    echo -e "\nMoving to new version container\n"

    dest_dir=$(echo "$dir" | sed "s/$version/tenancies/g")
    echo "Dest dir: $dest_dir"

    # Copy state files from source VM directory
    sudo mv "$source_dir_on_vm/source_tfstate" "$dir/" || { echo "Failed to copy source_tfstate"; continue; }
    sudo mv "$source_dir_on_vm/resources_list" "$dir/" || { echo "Failed to copy resources_list"; continue; }
    sudo chown -R "$username:$username" "/$username/$version"

    # Run Terraform in destination container
    sudo podman exec -i "$name" bash -c "
      cd \"$dest_dir\" || exit 1
      export TF_CLI_ARGS=-no-color
      terraform init
      terraform state pull > dest_tfstate
      while IFS= read -r r_import || [[ -n \"\$r_import\" ]]; do
        [[ -z \"\$r_import\" || \"\$r_import\" =~ ^# || \"\$r_import\" == data* ]] && continue
        terraform state mv --state source_tfstate --state-out dest_tfstate \"\$r_import\" \"\$r_import\"
      done < resources_list
      echo -e '\nPushing to state'
      terraform state push dest_tfstate
      rm -rf dest_tfstate* source_tfstate* resources_list
    "

    echo -e '\nCopying contents of variables_<region>.tf file'
    IFS='/' read -ra parts <<< "$dir"
    current_region="${parts[-2]}"
    if [ "$current_region" = "." ]; then
      current_region="${parts[-1]}"
    fi

    SRC_FILE="$source_dir_on_vm/variables_$current_region.tf"
    DEST_FILE="$dir/variables_$current_region.tf"

    START_MARKER="#START_compartment_ocids#"
    END_MARKER="#compartment_ocids_END#"
    copy_data_from_variables_file

    START_MARKER="#START_instance_source_ocids#"
    END_MARKER="#instance_source_ocids_END#"
    copy_data_from_variables_file

    START_MARKER="#START_instance_ssh_keys#"
    END_MARKER="#instance_ssh_keys_END#"
    copy_data_from_variables_file

    START_MARKER="#START_blockvolume_source_ocids#"
    END_MARKER="#blockvolume_source_ocids_END#"
    copy_data_from_variables_file

    START_MARKER="#START_fss_source_snapshot_ocids#"
    END_MARKER="#fss_source_snapshot_ocids_END#"
    copy_data_from_variables_file

    START_MARKER="#START_oke_source_ocids#"
    END_MARKER="#oke_source_ocids_END#"
    copy_data_from_variables_file

    START_MARKER="#START_oke_ssh_keys#"
    END_MARKER="#oke_ssh_keys_END#"
    copy_data_from_variables_file

    START_MARKER="#START_sddc_ssh_keys#"
    END_MARKER="#sddc_ssh_keys_END#"
    copy_data_from_variables_file

    START_MARKER="#START_exacs_ssh_keys#"
    END_MARKER="#exacs_ssh_keys_END#"
    copy_data_from_variables_file

    START_MARKER="#START_dbsystem_ssh_keys#"
    END_MARKER="#dbsystem_ssh_keys_END#"
    copy_data_from_variables_file

    echo -e "\nUpdated '$DEST_FILE' in-place with content from '$SRC_FILE'"

    echo "Done processing $dir"
    echo "--------------------------------------------------"
  done
  echo "Done Configuring prefix $prefix" >&3
  if [ "$git" == 1 ]; then
    echo -e "\nPushing local files to GIT Repo"
    sudo podman exec -it $name bash -c "cd /${username}/tenancies/${prefix}/terraform_files/; git config --global color.ui false;git add .; git commit -m 'Push from upgrade script to new version GIT Repo'; git push --set-upstream origin develop; git checkout main; git pull origin main; git merge develop; git push origin main; git checkout develop;git config --global color.ui true"
  fi
  echo "--------------------------------------------------" >&3

done
sed -i 's/\r//g' $LOG_FILE
