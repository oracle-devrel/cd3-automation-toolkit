#!/usr/bin/bash 

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if [[ -z $1 ]];then
	check_failed=$1
else
	check_failed=0
fi

prereq_check(){

oci_cli_check=0

echo -e "<<--------- PRE REQ CHECK START  ----------->>\n"
echo -e "--------- OCI CLI Setup -----------"
which oci &>> /dev/null
retval=$?
if [ $retval -ne 0 ];then
	echo -e "Command oci is not available. Trying to install the same" 
	rpm -q python-pip
	retval=$?
	if [ $retval -ne 0 ];then
		sudo yum -y install python-pip &> /dev/null && echo -e "python-pip installed successfully" || echo -e "python-pip install failed.Please run \"yum install python-pip -y\" and see errors"
	fi
	
	sudo pip install oci &> /dev/null && echo -e "oci installed successfully"|| echo -e "oci package install failed . \"pip install oci\" to see errors"
	sudo pip install oci-cli &> /dev/null & echo -e "oci-cli installed successfully"|| echo -e "oci-cli package install failed .\"pip install oci-cli\" to see errors"
fi

config_file="`echo  ~`/.oci/config"

if [[ ! -f "$config_file" ]]; then
	echo -e "FAILED: No oci config file found. Creating one"
	mkdir -p ~/.oci
	echo  "[DEFAULT]
user=<USER_OCID>
fingerprint=<key_file_finger_print>
key_file=<path to api private key .pem file>
tenancy=<tenancy-ocid>
region=<region>
	" > ~/.oci/config
	
	echo -e "Created ~/.oci/config . Please fill the file with required details and re-run script. "
	check_failed=1
	oci_cli_check=1
	echo -e "Continuing with other checks"
	
else
		echo -e "oci configuration found"
		echo -e "Checking if we can query oci iam user list as a test for oci cli functionality"
		oci iam user list &> /dev/null
		retval=$?
		if [ $retval -eq 0 ];then
			echo -e "oci cli command completed successfully"
		else
			echo -e "FAILED: oci cli command failed. Please configure it properly and re-run the script"
			check_failed=1
			oci_cli_check=1
			echo -e "Continuing with other checks"
		fi
fi
		

echo -e "\n--------- Mandatory Packages check -----------"
echo -e "Checking if package qemu-img exists"
which qemu-img &>> /dev/null
retval=$?
if [ $retval -ne 0 ];then
	echo -e "qemu-img pcakage is not installed. Installing it now"
	sudo yum -y install qemu-img  &>> /dev/null
	rpm -q qemu-img &>> /dev/null
	retval=$?
	if [ $retval -eq 0 ];then
		echo -e "qemu-img is installed successfully".
	else
		echo -e "FAILED: Some issues while installing qemu-img . Please run \"yum -y install qemu-img\"  manually to see errors"
		check_failed=1
		echo -e "Continuing with other checks"
	fi
fi


echo -e "Checking if package jq exists"

which jq &>> /dev/null
retval=$?
if [ $retval -ne 0 ];then
	echo -e "jq pcakage is not installed. Installing it now" 
	sudo yum -y install jq  &>> /dev/null
	rpm -q jq &>> /dev/null
	retval=$?
	if [ $retval -eq 0 ];then
		echo -e "jq is installed successfully".
	else
		echo -e "FAILED: Some issues while installing package jq . Please run yum install jq -y manually for the errors"
		check_failed=1
		echo -e "Continuing with other checks"
	fi
fi

echo -e "\n--------- Mandatory configuration and files check -----------"


[[ -e "$SCRIPT_DIR/env_variables" ]] && echo -e "$SCRIPT_DIR/env_variables exists" || { echo -e "ERROR: $SCRIPT_DIR/env_variables missing"; check_failed=1;}
[[ -e "$SCRIPT_DIR/oci-curl" ]] && echo -e "$SCRIPT_DIR/oci-curl exists" || { echo -e "ERROR: $SCRIPT_DIR/oci-curl missing"; check_failed=1;}
[[ -e "$SCRIPT_DIR/onpremise_to_oci.sh" ]] && echo -e "$SCRIPT_DIR/onpremise_to_oci.sh exists" || { echo -e "ERROR: $SCRIPT_DIR/onpremise_to_oci.sh missing"; check_failed=1;}
[[ -e "$SCRIPT_DIR/processovafile.sh" ]] && echo -e "$SCRIPT_DIR/processovafile.sh exists" || { echo -e "ERROR: $SCRIPT_DIR/processovafile.sh missing"; check_failed=1;}
[[ -e "$SCRIPT_DIR/upload_bootvol.sh" ]] && echo -e "$SCRIPT_DIR/upload_bootvol.sh exists" || { echo -e "ERROR: $SCRIPT_DIR/upload_bootvol.sh missing";check_failed=1;}
[[ -e "$SCRIPT_DIR/create_custom_image.sh" ]] && echo -e "$SCRIPT_DIR/create_custom_image.sh exists" || { echo -e "ERROR: $SCRIPT_DIR/create_custom_image.sh missing"; check_failed=1;}
[[ -e "$SCRIPT_DIR/process_datavols.sh" ]] && echo -e "$SCRIPT_DIR/process_datavols.sh exists" || { echo -e "ERROR: $SCRIPT_DIR/process_datavols.sh missing"; check_failed=1;}
[[ -e "$SCRIPT_DIR/terraform_generate.sh" ]] && echo -e "$SCRIPT_DIR/terraform_generate.sh exists" || { echo -e "ERROR: $SCRIPT_DIR/terraform_generate.sh missing"; check_failed=1;}



if [[ -f "$SCRIPT_DIR/env_variables" ]] ;then
	CUSTOM_IMAGE_COMPARTMENT_ID=`cat "$SCRIPT_DIR/env_variables" |grep -w  ^CUSTOM_IMAGE_COMPARTMENT_ID|cut -d "=" -f2`
	STG_INSTANCE_ID=`cat "$SCRIPT_DIR/env_variables" |grep -w  ^STG_INSTANCE_ID|cut -d "=" -f2|sed -e 's/^"//' -e 's/"$//'`
	OVA_PROCESS_DIR=`cat "$SCRIPT_DIR/env_variables" |grep -w  ^OVA_PROCESS_DIR|cut -d "=" -f2`
	OBJECT_NS=`cat "$SCRIPT_DIR/env_variables" |grep -w  ^OBJECT_NS|cut -d "=" -f2`
	OBJECT_BUCKET_NAME=`cat "$SCRIPT_DIR/env_variables"| grep -w  ^OBJECT_BUCKET_NAME|cut -d "=" -f2`
	REGION=`cat "$SCRIPT_DIR/env_variables" |grep -w  ^REGION|cut -d "=" -f2`

	
	if [[ -z $CUSTOM_IMAGE_COMPARTMENT_ID ]] ;then
			echo -e "FAILED: CUSTOM_IMAGE_COMPARTMENT_ID is empty in $SCRIPT_DIR/env_variables. Cannot do object bucket specific checks"
	elif [[ -z $OBJECT_BUCKET_NAME ]];then
			echo -e "FAILED: OBJECT_BUCKET_NAME is empty in env_variables. using default value as OCI-Toolkit-Obj-Store"
			sed -i -e 's/^OBJECT_BUCKET_NAME=/OBJECT_BUCKET_NAME=OCI-Toolkit-Obj-Store/g' "$SCRIPT_DIR/env_variables"
			echo -e "Checking if object_bucket_name exist"
			eval oci os bucket list --compartment-id "$CUSTOM_IMAGE_COMPARTMENT_ID" |grep OCI-Toolkit-Obj-Store &> /dev/null
			retval=$?
			if [ $retval -eq 0 ];then
				echo -e "Object OCI-Toolkit-Obj-Store exists "
			else
				echo -e "Object OCI-Toolkit-Obj-Store doesn't exist. Creating OCI-Toolkit-Obj-Store"
				eval oci os bucket create --name OCI-Toolkit-Obj-Store --compartment-id "$CUSTOM_IMAGE_COMPARTMENT_ID"
			fi
			
	elif [[ ! -z $OBJECT_BUCKET_NAME ]];then
			echo -e "OBJECT_BUCKET_NAME is $OBJECT_BUCKET_NAME "
			echo -e "Checking if object_bucket_name exist under compartment $CUSTOM_IMAGE_COMPARTMENT_ID"
			eval oci os bucket list --compartment-id "$CUSTOM_IMAGE_COMPARTMENT_ID" |grep "$OBJECT_BUCKET_NAME" &> /dev/null
			retval=$?
			if [ $retval -eq 0 ];then
				echo -e "Object $OBJECT_BUCKET_NAME exists "
			else
				echo -e "FAILED: Object $OBJECT_BUCKET_NAME doesn't exist. Creating $OBJECT_BUCKET_NAME "
				eval oci os bucket create --name  "$OBJECT_BUCKET_NAME" --compartment-id "$CUSTOM_IMAGE_COMPARTMENT_ID"
			fi
	fi

	if [[ -z $OBJECT_NS ]];then
		echo -e "FAILED: OBJECT_NS in $SCRIPT_DIR/env_variables is empty .Trying to update it\n"
		object_ns=`eval oci os ns get --compartment-id "$CUSTOM_IMAGE_COMPARTMENT_ID"|jq .data|sed -e 's/^"//' -e 's/"$//'`
		sed -i -e 's/^OBJECT_NS=/OBJECT_NS='"$object_ns"'/g' "$SCRIPT_DIR/env_variables"
	else
		echo -e "Checking if the namspace is matching with the one in OCI"
		object_ns=`eval oci os ns get --compartment-id "$CUSTOM_IMAGE_COMPARTMENT_ID"|jq .data|sed -e 's/^"//' -e 's/"$//'`
		if [[ $object_ns == $OBJECT_NS ]];then
			echo -e "Verified that namespace $OBJECT_NS you have in $SCRIPT_DIR/env_variables is correct"
		else
			echo -e "FAILED: Namespace not matching with oci"
			check_failed=1
		fi
		
	fi
	
	
	if [[ -z $STG_INSTANCE_ID ]];then
		echo -e "FAILED: STG_INSTANCE_ID in $SCRIPT_DIR/env_variables is empty. Please fill it"
		check_failed=1
	else
		echo -e "Checking if STG_INSTANCE_ID is matching with ocid of the instance from where you are running this code"
		if [[ -e /bin/oci-metadata ]];then
			
			local_instance_id=`/bin/oci-metadata --get ID|grep OCID |sed  -e 's/^  OCID: //g'`
			if [[ $STG_INSTANCE_ID == $local_instance_id ]];then
				echo -e "STG_INSTANCE_ID is matching with local instance ocid"
			else
				echo -e "FAILED: STG_INSTANCE_ID is not matching with local instance ocid"
				echo -e "Please make sure to verify env_variable file and check STG_INSTANCE_ID. You might need to change it to $local_instance_id ." 
				check_failed=1
			fi
		else
			echo -e "/bin/oci-metadata not found and cannot do STG_INSTANCE_ID matching with local instance ID. Please do it manually"
		fi  	
	fi

	if [[ -z $OVA_PROCESS_DIR  ]];then
		echo -e "FAILED: OVA_PROCESS_DIR in $SCRIPT_DIR/env_variables is empty. Please fill it"
		check_failed=1
	else
		if [[ -d $OVA_PROCESS_DIR ]];then
			echo -e "Process Directory $OVA_PROCESS_DIR exists"
			if [ -w $OVA_PROCESS_DIR ]; then echo "$OVA_PROCESS_DIR is WRITABLE"; else echo "$OVA_PROCESS_DIR NOT WRITABLE";check_failed=1; fi
		else
			echo -e "FAILED: $OVA_PROCESS_DIR doesn't exist. Please create and mount properly"
			check_failed=1
		fi
	fi

	if [[ -z $REGION ]];then
		echo -e "FAILED: REGION in $SCRIPT_DIR/env_variables is empty. Please fill it"
		check_failed=1
	fi
	
fi	

	[[ $check_failed -eq 1 ]] && { echo -e "\n***************** One of more check failed. Please review those and correct it before proceeding ***************";return $check_failed; } || echo -e "\n***************** prereqch check  successful. Go ahead with main script execution *********************\n"


echo -e "<<--------- PRE REQ CHECK FINISHED  ----------->>"
	
	
}

prereq_check
[[ $check_failed -eq 1 ]] && exit 1 || exit 0
