#!/usr/bin/bash 

declare vm_dir
from_parent=0
ova_full_string="$1"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
set -a
. $SCRIPT_DIR/env_variables
set +a
notova=$2

if [ -z "$1" ];then
	echo -e "Script looks running in standalone mode\n"
	echo -e "Please pass the complete string as in same format of input file(ova_file_name,display_name,shape,subnet_id,private_ip,compartment_id,availability_domain,fault_domain,launch_mode,os_type,os_version,disk_attachment_type,(nsg ocids/names)) :   "
	read ova_full_string
	echo -e "Enter if your input is ova/bootdisk/directory" 
	read notova
else
	from_parent=1
fi

vm_name=`echo -e "$ova_full_string" |cut -d "," -f2`
ova_full_name=`echo -e "$ova_full_string" |cut -d "," -f1`

process_disks(){
#Find boot volume name

        num_boot=`ls|grep disk1.vmdk|wc -l`
        if [ $num_boot -eq 1 ];then
                boot_disk_name=`ls|grep disk1.vmdk`
                echo -e "Boot disk is $boot_disk_name">>$vm_dir/log
		echo -e "Adding boot disk name to ocids" >>$vm_dir/log
		echo "boot_disk_name = $boot_disk_name" > $vm_dir/ocids
        elif [ $num_boot -eq 0 ];then
                echo "No disk with string disk1 found. please check manually and upload the boot disk\n">>$vm_dir/log
                exit 1
        else
                echo "Looks like there are more than one disk with string disk1, please check manually and upload the boot disk\n">>$vm_dir/log
                exit 1
        fi

}


ova_extract(){
		vm_dir=$OVA_PROCESS_DIR/$vm_name
		if [ -d $vm_dir ];then
			echo -e "$vm_dir already exists. Please clean the directory and re-run the program\n"
			exit 1
		fi
                mkdir -p $vm_dir
                cd $vm_dir
		echo -e "STAGE :------------------------- EXTRACT OVA----------------------\n">$vm_dir/log
		echo -e "Extracting ova file $ova_full_name\n">>$vm_dir/log
                /usr/bin/tar -xf $ova_full_name >>$vm_dir/log
		retval=$?
		if [ $retval -ne 0 ];then
			echo "Extract of OVA failed. Please check manually. Exiting\n">>$vm_dir/log
			exit 1
		fi
		process_disks
}


if [ -z "$ova_full_string" ];then
	echo -e "no OVAs to process. Exiting"
	exit 1
fi

if [ $notova == "directory" ];then
	vm_dir=`echo -e "$ova_full_string" |cut -d "," -f1`
	cd $vm_dir
	process_disks
elif [ $notova == "bootdisk" ];then
	fullpath_boot_disk_name=`echo -e "$ova_full_string" |cut -d "," -f1`
	boot_disk_name=`basename $fullpath_boot_disk_name`
	vm_dir=`dirname $fullpath_boot_disk_name`	
	echo -e "Boot disk is $boot_disk_name">$vm_dir/log
	cd $vm_dir
	echo -e "Adding boot disk name to ocids" >>$vm_dir/log
	echo "boot_disk_name = $boot_disk_name" > $vm_dir/ocids
	
else	
	ova_extract $ova_full_string
fi

#this will check if we have $2 set. This is to allow to run this script individually . If we run individually, it won't run further scripts unless you specify second argument.
if [ $from_parent -eq 1 ];then
	echo -e "uploading $boot_disk_name to object storage\n">>$vm_dir/log
	$SCRIPT_DIR/upload_bootvol.sh "$ova_full_string" >> $vm_dir/log
fi
