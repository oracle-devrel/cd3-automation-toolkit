#!/usr/bin/bash 

ova_full_string="$1"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
set -a
. $SCRIPT_DIR/env_variables
set +a

from_parent=0
if [ -z "$1" ];then
        echo -e "The script looks to be running in standalone mode\n" 2>&1 |tee $vm_dir/log
	echo -e "Please enter the full string of the OVA in format(ova_file_name,display_name,shape,subnet_id,private_ip,compartment_id,availability_domain,fault_domain,launch_mode,os_type,os_version)"
	read ova_full_string
else
        from_parent=1

fi


vm_name=`echo -e "$ova_full_string" |cut -d "," -f2`
input_type=`echo -e "$ova_full_string" |cut -d "," -f1`
echo $input_type|egrep "\.vmdk$" &> /dev/null && vm_dir=`dirname $input_type`
echo $input_type|egrep "\.ova$" &> /dev/null && vm_dir=$OVA_PROCESS_DIR/$vm_name
[ -d $input_type ] && vm_dir=$input_type
bootdisk_obj=`cat $vm_dir/ocids |grep boot_disk_name|cut -d" " -f3`
VM_LAUNCH_MODE=`echo -e "$ova_full_string" |cut -d "," -f9`
VM_LAUNCH_MODE=${VM_LAUNCH_MODE^^}
os_type=`echo -e "$ova_full_string" |cut -d "," -f10`
os_version=`echo -e "$ova_full_string" |cut -d "," -f11`


if [ -z "$os_version" ];then
        os_version=0
fi


##Add a check if the version is supported as per https://docs.cloud.oracle.com/iaas/Content/Compute/Tasks/importingcustomimagewindows.htm


echo -e "STAGE: ------------------------ CREATE CUSTOM IMAGE ---------------------\n">>$vm_dir/log

##ADD CODE TO CHECK WHICH REGION and change change the url accordingly.
if [ ! -z $REGION ];then
	sourceuri=https://objectstorage.us-$REGION-1.oraclecloud.com/n/$OBJECT_NS/b/$OBJECT_BUCKET_NAME/o/$bootdisk_obj
fi

#Add a check to see a custom image with same name exist and if yes, prompt user and exit
customimage_display_name=`echo $bootdisk_obj |sed -e 's/-disk1.vmdk//g'`

image_exist_check=`oci compute image list --compartment-id=$CUSTOM_IMAGE_COMPARTMENT_ID  --display-name $customimage_display_name`
if [ ! -z $image_exist_check ];then
	echo -e "There is a custom image with similar name found in the mentioned compartment. Please delete and re-run script" >>$vm_dir/log	
	exit 1
fi

#At present this oci cli has a bug due to which it doesn't accept os_version and os_type. So temperorily using oci-curl.Will update code when oci cli is working fine
#image_json=`oci compute image import from-object-uri --uri $sourceuri --compartment-id=$CUSTOM_IMAGE_COMPARTMENT_ID  --display-name $customimage_display_name --launch-mode $VM_LAUNCH_MODE`

cat >$vm_dir/config.json <<EOF
{
  "compartmentId": "$CUSTOM_IMAGE_COMPARTMENT_ID",
  "displayName": "$customimage_display_name",
  "imageSourceDetails":
    {
      "operatingSystem": "$os_type",
      "operatingSystemVersion": "$os_version",
      "sourceImageType": "VMDK",
      "sourceType": "objectStorageUri",
      "sourceUri": "$sourceuri"
    },
  "launchMode": "$VM_LAUNCH_MODE"
}
EOF

image_location="/20160918/images"

image_json=`$SCRIPT_DIR/oci-curl iaas.us-$REGION-1.oraclecloud.com post  $vm_dir/config.json $image_location`


#process above json and get display name and ocid
#image_display_name=`echo $image_json|grep -zoP '"display-name":\s*\K[^\s,]*(?=\s*,)'`
#image_ocid=`echo $image_json|grep -zoP '"id":\s*\K[^\s,]*(?=\s*,)'`
image_ocid=`echo $image_json|jq '.id'|grep -v null`
#Add code to check if above command is successful.
if [ ! -z $image_ocid ];then
        echo -e "custom image creation job is submitted. We need to wait for it to finish. Meantime, we will proceed to process data disks\n">>$vm_dir/log
else
        echo -e "looks like there is some issue with custom image creation. Please try to run it manually\n">>$vm_dir/log
	echo -e "Trying to show what output got when trying to create custom image \n $image_json\n"
        exit 1
fi


echo -e "Adding custom image id in cleanup.sh \n" >> $vm_dir/log
echo -e "oci compute image delete --image-id $image_ocid --force --wait-for-state DELETED" >> $vm_dir/cleanup.sh 

echo -e "Adding custom image id in ocids" >> $vm_dir/log
echo "custom_image_ocid = $image_ocid" >> $vm_dir/ocids

echo -e "Adding custom image display name in ocids"  >> $vm_dir/log
echo "customimage_display_name = $customimage_display_name" >> $vm_dir/ocids

#This will help to run the script in standalone mode too
if [ $from_parent -eq 1 ];then

	echo -e "STAGE: ---------------------DATA DISK PROCESSING---------------------\n">>$vm_dir/log
	$SCRIPT_DIR/process_datavols.sh "$ova_full_string" >>$vm_dir/log
fi
