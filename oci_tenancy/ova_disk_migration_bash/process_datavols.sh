#!/usr/bin/bash 

#CUSTOM_IMGAE_OCID=$1
#vm_dir=$2
#customimage_display_name=$3
ova_full_string="$1"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
set -a
. $SCRIPT_DIR/env_variables
set +a

from_parent=0
if [ -z "$1" ];then
        echo -e "The script looks to be running in standalone mode\n" 2>&1 |tee $vm_dir/log
	echo -e "Enter full string of ova as per the csv file to process the data disks\n" 2>&1 |tee $vm_dir/log
	read ova_full_string
else
        from_parent=1

fi

vm_name=`echo -e "$ova_full_string" |cut -d "," -f2`
input_type=`echo -e "$ova_full_string" |cut -d "," -f1`
echo $input_type|egrep "\.vmdk$" &> /dev/null && { vm_dir=`dirname $input_type`; boot_disk=`basename $input_type` ; }
echo $input_type|egrep "\.ova$" &> /dev/null && vm_dir=$OVA_PROCESS_DIR/$vm_name
[ -d $input_type ] && vm_dir=$input_type
CUSTOM_IMGAE_OCID=`cat $vm_dir/ocids |grep custom_image_ocid|cut -d" " -f3`
customimage_display_name=`cat $vm_dir/ocids |grep customimage_display_name|cut -d" " -f3`
BLOCK_VOL_AD=`echo -e "$ova_full_string" |cut -d "," -f7`
INSTANCE_COMPARTMENT_ID=`echo -e "$ova_full_string" |cut -d "," -f6`

echo "$INSTANCE_COMPARTMENT_ID"|grep ^ocid &> /dev/null
retval=$?
if [[ $retval -ne 0 ]];then
        echo -e "compartment_id in input file is not ocids. Trying to fetch its ocid"
        INSTANCE_COMPARTMENT_ID_TMP=`oci iam compartment list --all --compartment-id-in-subtree true|grep -w -B4 \"$INSTANCE_COMPARTMENT_ID\"|grep -w id|cut -d":" -f2`
        INSTANCE_COMPARTMENT_ID=`echo -e "$INSTANCE_COMPARTMENT_ID_TMP" |sed -e 's/^ "//' -e 's/",$//'`
        echo -e "Instance compartment ID is : "$INSTANCE_COMPARTMENT_ID"" >> $vm_dir/log
        echo $INSTANCE_COMPARTMENT_ID|grep ^ocid &>/dev/null && echo "Successfully fetched ocid of compartment" >>$vm_dir/log || { echo "Couldn't find ocid of compartment.Please mention ocid of compartment in input csv and resume script from process_datavols.sh"  >>$vm_dir/log; exit 1 ; }
fi



disk_number=0
raw_convert(){
for item in "${array[@]}"
   do
        #First take each disk and do qemu convert
        disk_raw=`echo $item |sed -e 's/vmdk/raw/g'`
	
        echo -e "Converting $item to $disk_raw\n">>$vm_dir/log
	echo -e "To check if convert process is running, please run 'ps -ef|grep qemu|grep <vm_name>' in other terminal \n" >>$vm_dir/log
	cd $vm_dir
        qemu-img convert -f vmdk -O raw $item $disk_raw &> /dev/null
	retval=$?
	if [ $retval -eq 0 ];then
		echo -e "Qemu conversion is successful for disk $item\n" >>$vm_dir/log
	else
		echo -e "Qemu conversion is failed for disk $item . Exiting\n" >>$vm_dir/log
		exit 1
	fi
	
	#Checking if disk is M/G/T	
	disk_string_withsize=`ls -lh $disk_raw| awk '{print $5}'`
	size_measure="${disk_string_withsize: -1}"
        disk_raw_size=`ls -lh $disk_raw| awk '{print $5}'| sed 's/.$//'`
	disk_raw_size=${disk_raw_size%.*}
	if [[ $size_measure == "M" ]];then
  	      	echo -e "disk $disk_raw is in megabytes. Disk size should be mimimum 50G in oci\n" >>$vm_dir/log
        	disk_raw_size=50
	elif [[ $size_measure == "G" ]];then
        	echo -e "disk $disk_raw is  in Gigabytes. Checking if its minimum 50G\n" >>$vm_dir/log
		if [ $disk_raw_size -lt 50 ];then
			echo -e "Disk size should  be mimimum 50G in oci\n" >>$vm_dir/log
                	disk_raw_size=50
        	fi
	elif [[ $size_measure == "T" ]];then
        	echo -e "disk $disk_raw is in Terabytes\n" >>$vm_dir/log
        	disk_raw_size=$((disk_raw_size * 1000))
	else
        	echo -e "Couldn't find size. Exiting"
        	exit 1
	fi
	
	disk_number=$disk_number+1
        block_volume_create $disk_raw_size $item
  done
}


block_volume_create(){
        echo -e "processing $disk_raw\n">>$vm_dir/log
	
	disk_to_process=$2
	disk_display_name=`echo $disk_to_process |sed -e 's/.vmdk//g'`
        #oci commands for create BV
	block_volume_json=`oci bv volume create --availability-domain $BLOCK_VOL_AD --compartment-id $INSTANCE_COMPARTMENT_ID --size-in-gbs $disk_raw_size --display-name $disk_display_name  --wait-for-state AVAILABLE`
	block_volume_uuid=`echo $block_volume_json|grep -zoP '"id":\s*\K[^\s,]*(?=\s*,)'`	
	if [ -z $block_volume_uuid ];then
		echo "There is some issues when trying to create Block volume $disk_display_name. Please check manually.Exiting"  >>$vm_dir/log
		exit 1 
	fi

	echo -e ""$disk_to_process"_uuid = $block_volume_uuid" >> $vm_dir/ocids
	 echo -e "Adding ocids of block volumes to cleanup.sh\n" >> $vm_dir/log
        echo -e "oci bv volume delete --volume-id $block_volume_uuid --force --wait-for-state TERMINATED\n" >>$vm_dir/cleanup.sh

	

	#This code is crucial as it find which disk name to be assigned for attachment
	device_name="/dev/oracleoci/oraclevd"
	max_disks=(a b c d e f g h i j k l m n o p q r s t u v w x y z aa ab ac ad ae af)
	num=0
	for x in "${max_disks[@]}"
		do
        		device_name=$device_name$x
        		disk_check_name="$OVA_PROCESS_DIR/control/oraclevd$x"
        		if [ ! -f $disk_check_name ];then
               			 echo "$disk_check_name not found. Using /dev/oracleoci/oraclevd$x to assign to new block attachment">>$vm_dir/log
				#Add  code to touch $vm_dir/oraclevdx. To handle race condition.
				echo -e "Touching $disk_check_name to avoid any race condition of two processing trying to use same disk for attachment\n" >>$vm_dir/log
				
				touch $disk_check_name 2>>$vm_dir/log
				retval=$?
				if [ $retval -eq 0 ];then
					echo -e "Successfully created $disk_check_name and proceeding with disk attachment using $disk_check_name\n" >>$vm_dir/log
					chattr +i $disk_check_name
					break
				else
					echo -e "Cannot touch $disk_check_name. trying next one\n" >>$vm_dir/log
				fi	
        		fi
        		device_name="/dev/oracleoci/oraclevd"
			if [ $num -eq 32 ];then
				#WE HAVE TO IMPROVISE THE CODE TO LOOP THROUGH SAME CODE TILL WE FIND A FREE
				echo -e "At present all 32 disks attachment slot is over. Please check and re-run the script after sometime. Make sure to run cleanup.sh\n">>$vm_dir/log
				chattr -i $disk_check_name
				rm -f $disk_check_name
				exit 1	
			fi
			num=$((num + 1))
		done
	block_volume_uuid="${block_volume_uuid%\"}"
	block_volume_uuid="${block_volume_uuid#\"}"
        #oci command for attach it to the staging server. PV and use device-name.
	echo -e "Trying to attach $item to $device_name\n" >>$vm_dir/log
	block_vol_attachment_json=`oci compute volume-attachment attach --type paravirtualized --volume-id $block_volume_uuid --instance-id $STG_INSTANCE_ID --device $device_name  --wait-for-state ATTACHED`
	retval=$?
	if [ $retval -eq 0 ];then
		echo -e "Attachment of $item to $device_name is successful\n" >>$vm_dir/log
	else
		echo -e "Attachment of $item to $device_name is failed. Please check manually and rectify, Exiting automation\n" >>$vm_dir/log
		chattr -i $disk_check_name
		rm -f $disk_check_name
		exit 1
	fi
	block_vol_attachment_uuid=`echo $block_vol_attachment_json|grep -zoP '"id":\s*\K[^\s,]*(?=\s*,)'`
	block_vol_attachment_uuid="${block_vol_attachment_uuid%\"}"
        block_vol_attachment_uuid="${block_vol_attachment_uuid#\"}"

	#Add a check by calling oci compute volume-attachment get and confirm if device name is same as $device_name"	


	if [ -e $device_name ];then
        	#dd $disk_raw to the above attached disk.
		echo "Doing dd of $disk_raw to $device_name . This might take some time based on disk size" >> $vm_dir/log
		echo -e "Please run ps -ef|grep $disk_raw |grep dd |grep -v grep to see progress" >> $vm_dir/log
		dd bs=8192 if=$disk_raw of=$device_name &>/dev/null 
		retval=$?
		if [ $retval -ne 0 ];then
			echo -e "dd process failed for disk $disk_raw . Please check manually .Exiting. Do cleanup andre-run script after fixing the issue\n" >>$vm_dir/log
			echo -e "Detaching $device_name \n" >>$vm_dir/log
			oci compute volume-attachment detach --volume-attachment-id $block_vol_attachment_uuid --wait-for-state DETACHED --force >> $vm_dir/log
			retval=$?
			if [ $retval -ne 0 ];then
 		                echo -e "Detach of disk $disk_raw from staging server failed. Please check manually.  Do cleanup and re-run script after fixing the issue\n" >>$vm_dir/log
				echo -e "You will need to manually cleanup $disk_check_name(1. Detach the disk $device_name 2. chattr -i $disk_check_name 3. rm -f $disk_check_name)" >>$vm_dir/log
                		exit 1
			fi
			chattr -i $disk_check_name
			rm -rf $disk_check_name
			exit 1
		else
			echo -e "dd process for disk $disk_raw	is successful\n" >>$vm_dir/log
		fi
	fi	
        
	#check to confirm no dd or no process accessing the disk

        #oci commands to detach attachment
	oci compute volume-attachment detach --volume-attachment-id $block_vol_attachment_uuid --wait-for-state DETACHED --force >> $vm_dir/log
	retval=$?
	if [ $retval -ne 0 ];then
		echo -e "Detach of disk $disk_raw from staging server failed. Please check manually.  Do cleanup andre-run script after fixing the issue\n" >>$vm_dir/log
		exit 1
	else
		echo -e "Detachment of $disk_raw from staging server is successful\n" >>$vm_dir/log
		chattr -i $disk_check_name
		rm -rf $disk_check_name
	fi


}

#This will help to run script standalone as well
if [ ! -z "$vm_dir" ]
  then
    echo "Checking for data disks in $vm_dir ">>$vm_dir/log
    echo $input_type|egrep "\.vmdk$" &> /dev/null && array=($(ls $vm_dir|grep vmdk|grep -v $boot_disk)) || array=($(ls $vm_dir|grep vmdk|grep -v disk1))
#elif [ ! -z "$1" ];then
#	echo -e "Script is running in standalone mode\n">>$vm_dir/log
 #       IFS=', ' read -r -a array <<< "$1"
else
	echo -e "No input argument provided. Please provide command separated list disk images to process (/vm/disk1.vmdk,/vm/disk2.vmdk)">>$vm_dir/log
	exit 1

fi

#Calling functions
raw_convert array

if [ $from_parent -eq 1 ];then

	#CODE WHICH WAIT FOR CUSTOm IMAGE TO BE AVAILABLE
	echo -e "Checking if image you uploaded is AVAILABLE. Script will wait in infinite loop till its available. If you want to interrupt this, you will have to kill the script pid manually">>$vm_dir/log
	image_exist_check=`oci compute image list --compartment-id=$CUSTOM_IMAGE_COMPARTMENT_ID  --display-name $customimage_display_name |grep lifecycle-state|grep AVAILABLE`
	retval=$?
	while true
	do
		if [ $retval -eq 0 ];then
			echo  -e "The custom image state is now AVAILABLE. Exiting the inifinte loop and proceeding with terraform creation" >>$vm_dir/log
			break
		fi
	done

	#We write custom image ocid only after image is available
	#echo "custom_image_ocid = $CUSTOM_IMGAE_OCID" >> $vm_dir/ocids

	#Nowe have both custom image and data disks available. Now we can call code to generate terraform
	#Steps for creating a terraform file using the ocid of the image and also combine the input simple text or csv file.
	echo -e "STAGE :------------------- TERRAFORM CREATION -------------------------- \n">>$vm_dir/log
	$SCRIPT_DIR/terraform_generate.sh "$ova_full_string"
fi
