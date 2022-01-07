#!/usr/bin/bash

#vm_dir=$1
ova_full_string="$1"
#CUSTOM_IMGAE_OCID=$3
OLDIFS=$IFS
IFS=','

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
set -a
. $SCRIPT_DIR/env_variables
set +a


if [ -z "$1" ];then
        echo -e "The script looks to be running in standalone mode\n" 2>&1
        echo -e "For standalone,script helps you to create terraform file for instance along with data attachments: " 2>&1 
	echo -e "Please enter full ova string in format(ova_file_name,display_name,shape,subnet_id,private_ip,compartment_id,availability_domain,fault_domain,launch_mode,os_type,os_versio)" 2>&1
	read ova_full_string
else
        from_parent=1

fi

vm_name=`echo -e "$ova_full_string" |cut -d "," -f2`
input_type=`echo -e "$ova_full_string" |cut -d "," -f1`
echo $input_type|egrep "\.vmdk$" &> /dev/null && vm_dir=`dirname $input_type`
echo $input_type|egrep "\.ova$" &> /dev/null && vm_dir=$OVA_PROCESS_DIR/$vm_name
[ -d $input_type ] && vm_dir=$input_type

#Checking if $vm_dir/ocids exists
if [ ! -f $vm_dir/ocids ];then
    	echo -e "File $vm_dir/ocids doesn't exist. This script is created to generate terraform for VMs as per the ova toolkit program only.\n" >> $vm_dir/log
	echo -e "As part of ova toolkit automation, it expects OVA to be extracted to a directory and the ocids are already created in previous stages already" >> $vm_dir/log
        exit 1
fi

CUSTOM_IMGAE_OCID=`cat $vm_dir/ocids |grep custom_image_ocid|cut -d" " -f3`

#VM instance creation
ova_file_name=`echo -e "$ova_full_string" |cut -d "," -f1`
display_name=`echo -e "$ova_full_string" |cut -d "," -f2`
shape=`echo -e "$ova_full_string" |cut -d "," -f3`
subnet_id=`echo -e "$ova_full_string" |cut -d "," -f4`
private_ip=`echo -e "$ova_full_string" |cut -d "," -f5`
compartment_id=`echo -e "$ova_full_string" |cut -d "," -f6`
availability_domain=`echo -e "$ova_full_string" |cut -d "," -f7`
fault_domain=`echo -e "$ova_full_string" |cut -d "," -f8`
disk_attachment_type=`echo -e "$ova_full_string" |cut -d "," -f12`
[ -z $disk_attachment_type ] && disk_attachment_type="iscsi"

nsg_string=`echo -e "$ova_full_string" |cut -d "(" -f2|sed -e 's/)$//'`
if [ -z "$nsg_string" ];then
	echo -e "No NSGs given in input file" >> $vm_dir/log
elif [[ -z `echo $nsg_string|grep ^ocid` ]];then
	 nsg_string="nsg_ids                = [\"\${lookup(var.nsgs,\"$nsg_string\")}\"]"

else
	#nsg_num=`echo ${#nsg_array[@]}` 
	#x=0;while [[ $x -lt $nsg_num ]];do temp_array="$temp_array,`echo ${nsg_array[$x]}\,`";x=$(( x + 1 ));done	
	
	nsg_string="nsg_ids                = [`echo -e "$nsg_string"|sed -e 's/^/"/' -e 's/,/","/g' -e 's/$/"/'`]"
fi


#Check if subnet is ocid or name
echo $subnet_id|grep ^ocid &> /dev/null
retval=$?
if [[ $retval -ne 0 ]];then
	echo -e "subnet_id in input file is not ocids. Assuming its name and adding variable declaration in terraform" >> $vm_dir/log
#	echo -e "Trying to fetch ocid from oci"  >> $vm_dir/log
	subnet_id="\${lookup(var.subnets,\"$subnet_id\")}"
	
fi

#Check if compartment is ocid or name
echo $compartment_id|grep ^ocid &> /dev/null
retval=$?
if [[ $retval -ne 0 ]];then
        echo -e "compartment_id in input file is not ocids. Assuming its name and adding variable declaration in terraform" >> $vm_dir/log
	compartment_id="\${lookup(var.compartments,\"$compartment_id\")}"

fi

#Check if AD is ocid or name
#temp_ad=`echo ${availability_domain,,}`
#if [[ $temp_ad == "ad1" ]] || [[ $temp_ad == "ad2" ]] || [[ $temp_ad == "ad3" ]];then echo -e "AD in input file is  Name not ocid" >> $vm_dir/log;availability_domain="\${lookup(var.ads,\"$availability_domain\")}"; else echo "AD is ocids" >> $vm_dir/log; fi

#Check if FD is ocid or name
#temp_fd=`echo ${fault_domain,,}`
#if [[ $temp_fd == "fd1" ]] || [[ $temp_fd == "fd2" ]] || [[ $temp_fd == "fd3" ]];then echo -e "FD in input file is variable" >> $vm_dir/log;fault_domain="\${lookup(var.fds,\"$fault_domain\")}"; else echo "FD is complete name and not variable" >> $vm_dir/log; fi


        	instance_variable="resource \""oci_core_instance"\" \""ova_$vm_name"\" {\n\tavailability_domain = \""$availability_domain"\"
\n\tfault_domain = \""$fault_domain"\"\n\tcompartment_id = \""$compartment_id"\"\n\tdisplay_name = \""$display_name"\"\n\tshape = \""$shape"\"\n\tsource_details {\n\t\tsource_type = \""image"\"\n\t\tsource_id = $CUSTOM_IMGAE_OCID\n\t}\n\n\tcreate_vnic_details {\n\t\tsubnet_id = \""$subnet_id"\"\n\t\tassign_public_ip = \""false"\"\n\t\tdisplay_name = \"""$display_name"_VNIC01"\"\n\t\thostname_label = \""$display_name"\"\n\t\tprivate_ip = \""$private_ip"\"\n\t\tskip_source_dest_check = \"false\"\n\t\t\n\t\t"$nsg_string"\n\t\t\n\t}\n\n}"
       		echo -e "$instance_variable" > $vm_dir/$vm_name.tf


#Data disk attachment


IFS=' '

disk_num=1
while read disk_name equal disk_id
do
        echo "$disk_id" |grep volume > /dev/null
        retval=$?
        if [ $retval -eq 0 ];then
                disk_attachment_variable="\nresource \""oci_core_volume_attachment"\" \"""$vm_name"-disk"$disk_num"_volume_attachment"\" { \n\t
#Required\n\tinstance_id = \""$\{oci_core_instance.ova_"$vm_name".id\}"\"\n\tattachment_type = \"$disk_attachment_type\"\n\tvolume_id = "$disk_id"\n\t}\n"
                        echo -e $disk_attachment_variable >> $vm_dir/$vm_name.tf
                        disk_num=$((disk_num + 1))

        fi
done < $vm_dir/ocids

echo -e "Terraform file $vm_dir/$vm_name.tf is generated. Copy the tf file and do \"terraform plan\" and if no error, you can apply which will create instance and attach all disks\n" >> $vm_dir/log
echo -e "-------------------------- ALL DONE -----------------------------" >> $vm_dir/log

IFS=$OLDIFS
