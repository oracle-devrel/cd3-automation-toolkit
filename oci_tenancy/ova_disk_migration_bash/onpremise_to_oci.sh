#!/usr/bin/bash

#Colours
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

#GLOBALS
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
set -a
. $SCRIPT_DIR/env_variables
set +a

if [ -z $OVA_PROCESS_DIR ];then
	echo -e "OVA_PROCESS_DIR is not defined. Please check $SCRIPT_DIR/env_variables and define all mandatory variables.Exiting\n".
	exit 1
fi


get_abs_filename() {
  # $1 : relative filename
  if [ -d "$(dirname "$1")" ]; then
    echo "$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
  fi
}


display_usage() {
          echo "Usage:    $0 -i <path to the input csv file>"
          echo "          -i <command seperated list of multiple OVAs> "
          echo "          -h help"
          }
ova_arg=0

  while getopts ":i:hs" opt; do
    case $opt in
  s)
	skip_prereqcheck=1	
  ;;
  i)
        ova_arg=1
        ovas="$OPTARG"
	echo -e "============================= STARTING OF THE PROGRAM EXECUTION =================================\n "

	check_if_exist_num=0
	stale_found=0	
	if [[ $skip_prereqcheck -ne 1 ]];then 	
		echo -e "Doing pre-req check. Program won't proceed if pre-req check fails\n"
		$SCRIPT_DIR/prereqcheck.sh $check_failed
		retval=$?
		[[ $retval -eq 1 ]] && exit 1
	else
		echo -e "\"-s\" flag given to skip prereqcheck. Skipping it\n"
	fi
	
	echo -e "Doing some mandatory checks\n"	

	#Check if any existing ova migration process exists
	check_if_exist=`ps -ef|grep processovafile.sh|grep -v grep |wc -l`
	if [[ $check_if_exist -ne 0 ]];then
		echo -e "\n${RED}There is already more than one ova migration process running.FYI.${NC}"
		check_if_exist_num=1
	fi
	
	if [ -d $OVA_PROCESS_DIR/control ];then
		echo "Checking if there are stale device entries under $OVA_PROCESS_DIR/control"
		disk_array=($(ls /processova/control/))
		for item in "${disk_array[@]}"
		do 
			ls /dev/oracleoci/oraclevd*|grep $item &> /dev/null
			retval=$?
			if [ $retval -eq 0 ];then 
				echo "found $item under /dev/oracleoci/"
			else 
				echo -e "${RED}couldn't find $item /dev/oracleoci/${NC}"
			stale_found=1
			fi
		done

		if [ "$stale_found" -eq 1 ];then
			if [ "$check_if_exist_num" -eq 1 ];then
				echo "As reported before, there are device node stale entries found under $OVA_PROCESS_DIR/control"
				echo "As there is another ova toolkit running , you should review carefully and clean the stale entries".
				echo "Cleaning stale entries under $OVA_PROCESS_DIR/control will make sure that device is available
				for toolkit to use when attaching block devices"
			else
				echo "As reported before, there are device node stale entries found under $OVA_PROCESS_DIR/control"
				echo "Please review and clean them so that device is available for toolkit to use when attaching block devices"
			fi
		fi
	fi
        #This code is crucial as it find which disk names are currenlty in use
        max_disks=(a b c d e f g h i j k l m n o p q r s t u v w x y z aa ab ac ad ae af)
        device_name="/dev/oracleoci/oraclevd"
        [ -d $OVA_PROCESS_DIR/control ] || mkdir -p $OVA_PROCESS_DIR/control
        echo -e "Creating existing block device names under $OVA_PROCESS_DIR/control "
                for letter in "${max_disks[@]}"
                        do
                                device_name="$device_name$letter"
                                if [ -e $device_name ];then
                                                touch $OVA_PROCESS_DIR/control/oraclevd$letter  &> /dev/null
                                                chattr +i $OVA_PROCESS_DIR/control/oraclevd$letter
                                fi
                                device_name="/dev/oracleoci/oraclevd"
                        done

	echo -e "-----------${GREEN}All checks finished${NC}-----------------\n"

	OLDIFS=$IFS
	IFS=','
	ovas=`get_abs_filename $ovas`
	num=1
	max_job=0
	[ -f "$ovas" ] & while read ova_file_name vm_name rest_all
		do
			if [[ $max_job -ge 5 ]];then
				echo -e "${RED} ITS IS NOT RECOMMENDED TO PROCESS MORE THAN 5 OVAs AT SAME TIME IN ONE MACHINE"
				echo -e "IF YOU WANT MORE OVAs TO BE PROCESSES AT ONCE, PLEASE RUN THE PROGRAM FROM DIFFERENT MACHINE. EXITING..\n"
			fi
			echo -e "$num) Processing OVA file : ${GREEN}$ova_file_name${NC}"
			num=$((num + 1))
        		[[ $ova_file_name = \#* ]] && { echo -e "Line is commented.skipping\n";continue;}
        		#ADD A CHECK TO SEE IF PATH IS FULL,RELATIVE OR SIMPLE FILENAME
			#Add a check to see if file extension is .ova
			
			if [ -z $ova_file_name ];then
				echo -e "Empty line, skipping\n"
				continue
			fi			

			if [ -d $ova_file_name ];then
				echo -e "${RED}$ova_file_name is a directory${NC}"
				echo -e "Checking if directory contains vmdk file\n"
				ls $ova_file_name|grep \.vmdk &> /dev/null || { echo "$ova_file_name doesn't contain vmdk file.exiting"; continue ; }
				echo -e "Calling child script processovafile.sh to process $ova_file_name"
				echo -e "Please check "${GREEN}$OVA_PROCESS_DIR"/"$vm_name"/log${NC} file to see OVA specific progress\n"
				full_ova_string=$ova_file_name,$vm_name,$rest_all
				max_job=$((max_job + 1 ))
				nohup $SCRIPT_DIR/processovafile.sh "$full_ova_string" "directory" &	
				echo -e "----------------------------\n "
				continue
			fi 

			
			#Checking if the ovas exists
			if [ ! -f "$ova_file_name" ];then
			  echo -e "Error: File $ova_file_name doesn't exist.Processing next file\n"
			  continue
			fi

			#There could be cases where customer uploads disks with non standard name. So we are adding an option so that user can mention boot disk name specific
			#It should be ending with vmdk for sure
			echo $ova_file_name|egrep "\.vmdk$"
			retval=$?
			if [ $retval -eq 0 ];then
				echo -e "${RED}You looks to have given boot disk as input.FYI${NC}"
				echo -e "Calling child script processovafile.sh to process $ova_file_name"
				echo -e "Please check "${GREEN}$OVA_PROCESS_DIR"/"$vm_name"/log${NC} file to see OVA specific progress\n"
				full_ova_string=$ova_file_name,$vm_name,$rest_all
				max_job=$((max_job + 1 ))
				nohup $SCRIPT_DIR/processovafile.sh "$full_ova_string" "bootdisk" &
				echo -e "----------------------------\n "
				continue
			fi	
	

			#Checking if its an OVA file
			echo $ova_file_name|egrep "\.ova$"
			retval=$?
			if [ $retval -eq 0 ];then
				echo -e "File is ending with .ova"
        			echo -e "Calling child script processovafile.sh to process $ova_file_name"
				echo -e "Please check "${GREEN}$OVA_PROCESS_DIR"/"$vm_name"/log${NC} file to see OVA specific progress\n"
				full_ova_string=$ova_file_name,$vm_name,$rest_all
				max_job=$((max_job + 1 ))
        			nohup $SCRIPT_DIR/processovafile.sh "$full_ova_string" &
				echo -e "----------------------------\n "
			else
				echo -e "File $ova_file_name is not ending with ova. Skipping the file and continue with next file. please check this manually\n"
				echo -e "----------------------------\n "
			fi

	done < $ovas


	IFS=$OLDIFS
			echo -e "====================================================================================================\n "
      ;;
  h)
        display_usage
        exit 1
      ;;
  \?)
        echo "Invalid option: -$OPTARG" >&2
        display_usage
        exit 1
;;
:)
  echo "Option -$OPTARG requires an argument. Please mention location of file" >&2
  exit 1
;;
esac
done

if [ $ova_arg -eq 0 ];then
        echo "No input file given to process. You must specify -i and parameter file"
fi


