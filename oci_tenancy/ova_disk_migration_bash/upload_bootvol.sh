#!/usr/bin/bash

#OVA_PROCESS_DIR="/processova"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
from_parent=0
ova_full_string="$1"
set -a
. $SCRIPT_DIR/env_variables
set +a

vm_name=`echo -e "$ova_full_string" |cut -d "," -f2`

input_type=`echo -e "$ova_full_string" |cut -d "," -f1`
echo $input_type|egrep "\.vmdk$" &> /dev/null && vm_dir=`dirname $input_type`
echo $input_type|egrep "\.ova$" &> /dev/null && vm_dir=$OVA_PROCESS_DIR/$vm_name
[ -d $input_type ] && vm_dir=$input_type


if [ -z "$2" ];then 
	bootdisk_obj=`cat $vm_dir/ocids |grep boot_disk_name|cut -d" " -f3`
else
	bootdisk_obj=$2
fi

if [ -z "$1" ];then
	echo -e "The script looks to be running in standalone mode\n" 2>&1 |tee $vm_dir/log
	echo -e "For standalone,script helps you to upload the object to object storage.  Please enter object file location to upload: " 2>&1 |tee $vm_dir/log
	read bootdisk_obj
	echo -e "Enter the full OVA string"
	read ova_full_string
else
	from_parent=1

fi


#Add code to check if the object exist in object storage. If yes, prompt, user and exit.

echo -e "STAGE: -------------- UPLOAD BOOT VOLUME -----------------\n" >> $vm_dir/log

echo -e "Checking if the object exist in namespace\n" >>$vm_dir/log
oci os object list  -ns $OBJECT_NS -bn $OBJECT_BUCKET_NAME|grep -w $bootdisk_obj >> /dev/null
retval=$?
if [ $retval -eq 0 ];then
	echo -e "Object $bootdisk_obj exists in the namespace. Please remove it and re-run the script.Exiting." >>$vm_dir/log
	exit 1
fi

echo -e "Uploading disk $bootdisk_obj to object storage.Program will continue once the upload is finished\n">>$vm_dir/log
/usr/bin/oci --config-file /root/.oci/config os object put -ns $OBJECT_NS -bn $OBJECT_BUCKET_NAME --file $bootdisk_obj --no-overwrite >>$vm_dir/log
retval=$?
if [ $retval -eq 0 ];then
        echo -e "Object $bootdisk_obj upload is successful" >>$vm_dir/log
fi


#This will help to run this script standalone or part of whole automation.
if [ $from_parent -eq 1 ];then
	echo -e "Adding object id of $bootdisk_obj to cleanup script cleanup.sh" >> $vm_dir/log 
	#cp $SCRIPT_DIR/cleanup.sh $vm_dir >> $vm_dir/log
	echo -e "oci os object delete -ns $OBJECT_NS -bn $OBJECT_BUCKET_NAME --object-name $bootdisk_obj --force" > $vm_dir/cleanup.sh
	chmod +x $vm_dir/cleanup.sh
	echo -e "Upload of boot disk is finished. Calling create_custom_image.sh to create a custom image using the boot disk uploaded.\n">>$vm_dir/log
	$SCRIPT_DIR/create_custom_image.sh "$ova_full_string" >>$vm_dir/log
fi
