#!/bin/bash
#
#
#              Property of Oracle Corp - Oracle Consulting Services
#                 Do not copy or distribute unpublished work
#                             All Rights Reserved
##################################################################################
# Customer acknowledges that the software script(s) are not a
# generally available standard Oracle Corp product and that it is a
# fundamental condition of supply of the software script(s) to
# Customer that Customer accepts the same "as is" and without
# warranty of any kind.  No support services of any kind are
# available for the software script(s) and Oracle Corp does not represent
# to Customer that:
#
# (i)   operation of any of the software script(s) shall be
#       uninterrupted or error free, or
#
# (ii)  functions contained in the software script(s) shall operate
#       in the combinations which may be selected for use by
#       Customer or meet Customer's requirements, or
#
# (iii) that upgraded versions of the software script(s) will be
#       issued.
#
# If Customer wishes to have the software script(s) modified, or
# otherwise requires support, Oracle Corp may provide the same by means of
# a separate consulting agreement priced on a time and materials
# basis.
#
#################################################################################
# Author:   Matt Fifer
# Date:     May 5, 2019
# Version:  2.2
#
# Synopsis: ocireport-summary.sh
#
# Developed using OCI CLI Version 2.4.40
# Env:
# Python 2.7.5
# Oracle Linux 7.4
#
# Inputs: 
# Output: Log file Report and configuration files in `pwd`/logs directory
#
# Note1: The get_compartments module must be min module run.
# The get_compute_instance_map module must be run in addition for compute instance mapping  modules:
# This is because they generate min configuration files that other modules depend upon.
#
# Note2: Warning: cleanup_files will find matching temp files and remove from $LOGDIR
#
# Note3:
# Assumptions: 
# 1. OCI CLI is installed on the host running this script.
# 2. User running script has access to compartments and objects in compartments
# 3. This script is not dependent on oci-utils:
#    https://docs.cloud.oracle.com/iaas/Content/Compute/References/ociutilities.htm
# 
# Known Issues: 
#
# Issue: Determining OCID for Boot Drive for Windows based Compute Instances.
# Using 'oci compute instance get --instance-id <computeinst-id> | grep boot-volume-id..' 
# Did not return the boot volume id as it did for Linux OS based Compute Instances.
#
# Workaround: Used listing and filter for all boot volumes in compartment/AD for VM.
# 'oci compute boot-volume-attachment list --compartment-id <compartment-ocid> --availability-domain <ad-name>'
# Then inspected output for compute instance OCID (instance-id) associated (boot-volume-id)
#
# Potential Suggested Further Enhancements: 
# 1. Confirmation check of configuration ocid mappings.
#
# Usage Maintenance will be required as new features are incorporated into OCI CLI
# This may result in new metadata to be added for objects,
# thus potentially providing unexpected object mappings and resultant config files output from this script.  
#
#
# You MUST Supply options to run report
# Valid Options are:
#
# -c run report and get configs for OCI Compute Instances
# -d run report and get configs for OCI Database Systems
# -n run report and get configs for select OCI Network Objects
# -s run report and get configs for select OCI Storage Objects
# -a run report and get configs for OCI Objects in Tenancy
# -h print Usage Message for current options
#
#################################################################################
# Change history (most recent last)
#
# Version       When            Who             Comments
# -------       ----            ---             --------
# 1.0.0         14 Jan 2019     Matt Fifer      Initial Draft of script
# 1.0.1         17 Jan 2019     Matt Fifer      Added mappings, report region (oci cli user config)
# 1.0.2         18 Jan 2019     Matt Fifer      Added boot mappings, updated header
# 1.0.3         18 Jan 2019     Matt Fifer      Added block volume mappings
# 1.0.4         18 Jan 2019     Matt Fifer      Added FSS  mappings
# 1.0.5         23 Jan 2019     Matt Fifer      Added Object Storage, Load Balancer
# 1.0.6         31 Jan 2019     Matt Fifer      Added DBSystems
# 1.0.7          1 Feb 2019     Matt Fifer      Updated: get_compute_instance_block_map, get_compute_instance_boot_map find vol orphans
# 						Added: get_vcn_map
# 1.0.8          4 Feb 2019     Matt Fifer      Updated: Ability to run with input options, dirname for logdir, configdir
# 1.0.9          8 Feb 2019     Matt Fifer      Updated: DBSystems module for node association
# 2.0           20 Mar 2019     Matt Fifer      Updated: get_lb_map and get_vcn_map modules to show public/private, fix lb report mapping where lb backend server configuration is incomplete
# 2.1           21 Mar 2019     Matt Fifer      Updated: get_lb_map LB Shape,LB subnet OCID. Updated: vcn_map IGW,SGW
# 2.2           05 May 2019     Matt Fifer      Updated: Fixed issue where compartment name ocid lifecycle-state not ACTIVE
#
#
##############################################################################
#       Variaible section of script             #
#       Used to set all global vars             #
#################################################
#
DATE=`date '+%d%b%Y-%H%M%S'`
DATEDMY=`date '+%d%b%Y'`
VERSION=2.2
CUSTNAME=ClubCorp
OCI_NAMESP=`oci os ns get | grep data | awk '{print $2}' | sed 's/"//g'`
OCI_TENANCYOCID=`grep tenancy ~/.oci/config | cut -d= -f2`

OCICLI_VER=`oci -version`
PYTHON_VER=`python --version`
OCICLI_USEROCID=`grep user ~/.oci/config | cut -d= -f2`
OCICLI_USER=`oci iam user get --user-id ${OCICLI_USEROCID} | cut -d= -f2 | grep name | awk '{print $2}' | cut -d, -f1 | sed 's/"//g'`

OCICLI_USERREGION=`grep region ~/.oci/config | cut -d= -f2`
OCI_HOMEREGION=`oci iam region-subscription list | egrep "is-home-region|region-name" | awk '{print $2}' | awk '$1 == "true," { next } { print }' | cut -d, -f1 | sed 's/"//g' | head -1`

UNIX_USER=`whoami`
UNIX_HOST=`hostname`

SCRIPTPATH=`dirname $0`

#LOG=/dev/null
LOGDIR=$SCRIPTPATH/logs
LOG=$LOGDIR/`basename $0 | awk -F. '{print $1}'`-${OCICLI_USERREGION}-${DATE}.log
CONFIGDIR=$SCRIPTPATH/configs


if [ -f /etc/oracle-release ]; then

        OS_VER=`cat /etc/oracle-release`

   elif [ -f /etc/redhat-release ]; then

        OS_VER=`cat /etc/redhat-release`

   else

        OS_VER="Unable to Determine OS Release..."
fi


if [ ! -d $LOGDIR ]; then

        mkdir -p $LOGDIR

fi

if [ ! -d $CONFIGDIR ]; then

        mkdir -p $CONFIGDIR

fi

usage() {

        echo -e "" 2>&1 | tee -a $LOG
        echo -e "\tYOU HAVE NOT PROVIDED VALID ARGMENTS FOR THE OCI SUMMARY REPORT..." 2>&1 | tee -a $LOG
        echo -e "" 2>&1 | tee -a $LOG
        echo -e "Usage: $0 -c | -d | -n | -s | -a | -h" 2>&1 | tee -a $LOG
        echo -e "Where\t-c to run report and get configs for OCI Compute Instances" 2>&1 | tee -a $LOG
        echo -e "\t-d to run report and get configs for OCI Database Systems" 2>&1 | tee -a $LOG
        echo -e "\t-n to run report and get configs for select OCI Network Objects" 2>&1 | tee -a $LOG
        echo -e "\t-s to run report and get configs for select OCI Storage Objects" 2>&1 | tee -a $LOG
        echo -e "\t-a to run report and get configs for OCI Objects in Tenancy" 2>&1 | tee -a $LOG
        echo -e "\t-h print Usage Message for current options" 2>&1 | tee -a $LOG
        echo -e "" 2>&1 | tee -a $LOG
        echo -e "\tPlease Try Again, Exiting..." 2>&1 | tee -a $LOG

}


get_subscription_regions() {

echo "----------------------------------------------------------------------------" 2>&1 | tee -a $LOG
echo "" 2>&1 | tee -a $LOG
echo "Getting OCI Namespace and list of subscribed regions for this tenancy..." 2>&1 | tee -a $LOG
echo "" 2>&1 | tee -a $LOG
echo "----------------------------------------------------------------------------" 2>&1 | tee -a $LOG

echo "" 2>&1 | tee -a $LOG
echo "The OCI Namespace for the ${CUSTNAME} Tenancy is:" $OCI_NAMESP 2>&1 | tee -a $LOG

echo "" 2>&1 | tee -a $LOG
echo "OCI Availability Domain Names for this Tenancy Region $OCICLI_USERREGION:"  2>&1 | tee -a $LOG
echo "" 2>&1 | tee -a $LOG
echo `oci iam availability-domain list | grep name | awk '{print $2}' | sed 's/"//g'` 2>&1 | tee -a $LOG
echo "" 2>&1 | tee -a $LOG

echo "" 2>&1 | tee -a $LOG
echo "The ${CUSTNAME} OCI Subscribed Regions for this tenancy are:" 2>&1 | tee -a $LOG
oci iam region-subscription list | grep region-name | awk '{print $2}' | cut -d, -f1 | sed 's/"//g' 2>&1 | tee -a $LOG

echo "" 2>&1 | tee -a $LOG
echo "The ${CUSTNAME} OCI Home Region for this tenancy is:" $OCI_HOMEREGION 2>&1 | tee -a $LOG
echo "" 2>&1 | tee -a $LOG

}

get_compartments() {

# 
# Consider adding check to show oci user running script compartment access for report gen.
# Example add option: --access-level ACCESSIBLE
# 
#
# Get Compartment Name to Compartment Instance OCID mapping 
# Format out: <Compartment Name> <Compartment OCID>
#

echo "----------------------------------------------------------------------------" 2>&1 | tee -a $LOG
echo "" 2>&1 | tee -a $LOG
echo "Getting list of compartments and associated ocids..." 2>&1 | tee -a $LOG
echo "" 2>&1 | tee -a $LOG
echo "----------------------------------------------------------------------------" 2>&1 | tee -a $LOG
echo "List of Compartment Names by Compartment OCIDs" 2>&1 | tee -a $LOG
echo "Format: <OCI Compartment Name> <OCI Compartment OCID>" 2>&1 | tee -a $LOG

oci iam compartment list --all | grep compartment.oc | awk '{print $2}' | cut -d, -f1 | sed 's/"//g' >> $LOGDIR/temp-ocidcompart-$$.out

# Filter out all compartment ocid's that are ONLY ACTIVE lifecycle state

for ocidnum in `cat $LOGDIR/temp-ocidcompart-$$.out`
do

lifecyclestate=`oci iam compartment get --compartment-id $ocidnum | grep lifecycle-state | awk '{print $2}' | cut -d, -f1 |
 sed 's/"//g'`

   if [ "$lifecyclestate" = "ACTIVE" ]; then

    echo $ocidnum >> $LOGDIR/ocidcompart-$$.out

   fi

done

rm $LOGDIR/temp-ocidcompart-$$.out

echo "" 2>&1 | tee -a $LOG

for ocidnum in `cat $LOGDIR/ocidcompart-$$.out`
do
	oci iam compartment get --compartment-id $ocidnum | grep name | awk '{print $2}' | cut -d, -f1 | sed 's/"//g' >> $LOGDIR/compartname-$$.out 2>&1 | tee -a $LOG

done

echo "" 2>&1 | tee -a $LOG
echo "Creating Compartment Name to OCID Mapping..." 2>&1 | tee -a $LOG

paste $LOGDIR/compartname-$$.out $LOGDIR/ocidcompart-$$.out > $LOGDIR/name-compart-map-$DATEDMY-cfg-$$.out

num_comparts=`cat $LOGDIR/name-compart-map-$DATEDMY-cfg-$$.out | wc -l`

echo "" 2>&1 | tee -a $LOG
echo "There are currently $num_comparts compartments in this tenancy. " 2>&1 | tee -a $LOG

echo "" 2>&1 | tee -a $LOG
echo "Summary of Mapping Compartment Names to OCIDs: " 2>&1 | tee -a $LOG
echo "" 2>&1 | tee -a $LOG

cat $LOGDIR/name-compart-map-$DATEDMY-cfg-$$.out 2>&1 | tee -a $LOG
echo "" 2>&1 | tee -a $LOG
echo "" 2>&1 | tee -a $LOG


echo "Dumping Compartment Name and Compartment OCID Mapping to file:" 2>&1 | tee -a $LOG
echo $LOGDIR/name-compart-map-$DATEDMY-cfg-$$.out 2>&1 | tee -a $LOG
echo "" 2>&1 | tee -a $LOG
echo "" 2>&1 | tee -a $LOG


}


get_compute_instance_map() {

#
# Get the List of Compute Instances by Compartment
# Generate Compute Instance OCID Mapping to Compartment and AD

echo "----------------------------------------------------------------------------" 2>&1 | tee -a $LOG
echo "" 2>&1 | tee -a $LOG
echo "Getting list of Compute Instances by compartment and Availability Domain" 2>&1 | tee -a $LOG
echo "for ${OCICLI_USERREGION}..." 2>&1 | tee -a $LOG
echo "" 2>&1 | tee -a $LOG
echo "----------------------------------------------------------------------------" 2>&1 | tee -a $LOG

#
# Get Compute Instance Name, Instance OCID and Availability Domain mapping
# Format out: <Compartment Name> <Compute Instance Name> <Compute Instance OCID> <Availability Domain Name>
#

echo "List of Compute Instances by compartment and Availability Domain" 2>&1 | tee -a $LOG
echo "Format: <Compartment Name> <Compute Instance Name> <Compute Instance OCID> <Availability Domain Name>" 2>&1 | tee -a $LOG


for ocidcpartnum in `cat $LOGDIR/ocidcompart-$$.out`
do
	CPARTNAME=`oci iam compartment get --compartment-id $ocidcpartnum | grep name | awk '{print $2}' | cut -d, -f1 | sed 's/"//g'`

	oci compute instance list --compartment-id $ocidcpartnum --all | grep instance.oc  | awk '{print $2}' | cut -d, -f1 | sed 's/"//g' > $LOGDIR/ocidcompute-$CPARTNAME-$$.out
	for ocidcompute in `cat $LOGDIR/ocidcompute-$CPARTNAME-$$.out`
	do
		INSTANCE_NAME=`oci compute instance get --instance-id $ocidcompute | grep display-name | awk '{print $2}' | cut -d, -f1 | sed 's/"//g'`
		AVAILDOMAIN=`oci compute instance get --instance-id $ocidcompute | grep availability-domain | awk '{print $2}' | cut -d, -f1 | sed 's/"//g'`

		echo -en "$CPARTNAME $INSTANCE_NAME $ocidcompute $AVAILDOMAIN\n" >> $LOGDIR/$OCICLI_USERREGION-name-compute-map-$DATEDMY-cfg-$$.out
		
	done

done

num_compute=`cat $LOGDIR/$OCICLI_USERREGION-name-compute-map-$DATEDMY-cfg-$$.out | wc -l`

echo "" 2>&1 | tee -a $LOG
echo "There are currently $num_compute compute instances in the $OCICLI_USERREGION region. " 2>&1 | tee -a $LOG

	echo "" 2>&1 | tee -a $LOG
	cat $LOGDIR/$OCICLI_USERREGION-name-compute-map-$DATEDMY-cfg-$$.out 2>&1 | tee -a $LOG
	echo "" 2>&1 | tee -a $LOG
	echo "" 2>&1 | tee -a $LOG


echo "Dumping Compartment Name, Compute Instance Name/OCID, and AD Name mapping to file:" 2>&1 | tee -a $LOG
echo $LOGDIR/$OCICLI_USERREGION-name-compute-map-$DATEDMY-cfg-$$.out 2>&1 | tee -a $LOG
echo "" 2>&1 | tee -a $LOG
echo "" 2>&1 | tee -a $LOG

}

get_compute_instance_boot_map() {

# Generate Compute Instance OCID Mapping to BootVol OCID
#
# Note:
# Preferred method leveraging 'oci compute instance get --instance-id <computeinst-id> | grep boot-volume-id..'
# did not provide boot volume id for Windows OS based compute instances.
# Instead used (not pref): 'oci compute boot-volume-attachment list --compartment-id <compart-id> --availability-domain <ad-name>' 

echo "----------------------------------------------------------------------------" 2>&1 | tee -a $LOG
echo "" 2>&1 | tee -a $LOG
echo "Getting list of Compute Instance OCIDs and Boot Volume OCIDs" 2>&1 | tee -a $LOG
echo "for ${OCICLI_USERREGION}..." 2>&1 | tee -a $LOG
echo "" 2>&1 | tee -a $LOG
echo "----------------------------------------------------------------------------" 2>&1 | tee -a $LOG

#
# Get Compute Instance OCID mapping to Boot Volumes
#
# BACKUP NOTES
# oci bv boot-volume-backup create --boot-volume-id  <boot-volume-id> --display-name <name-can-be-based-on-computeinst-name> --type <FULL|INCREMENTAL>
# oci bv boot-volume-backup list --compartment-id <compartment-ocid> --boot-volume-id  <boot-volume-id>
# OCI CLI Reference: https://docs.cloud.oracle.com/iaas/tools/oci-cli/latest/oci_cli_docs/cmdref/bv/boot-volume-backup/create.html 
#
# Format out: <Compartment Name> <Compute Instance Name> <Compute Instance OCID> <Boot Volume OCID>
#

echo "List of Compute Instances by Instance OCID and Boot OCID" 2>&1 | tee -a $LOG
echo "Format: <Compartment Name> <Compute Instance Name> <Compute Instance OCID> <Boot Volume OCID>" 2>&1 | tee -a $LOG

	echo "" 2>&1 | tee -a $LOG
	echo "" 2>&1 | tee -a $LOG


cat $LOGDIR/$OCICLI_USERREGION-name-compute-map-$DATEDMY-cfg-$$.out | awk '{print $1,$2,$3}' > $LOGDIR/$OCICLI_USERREGION-compute-bootmap-1-$$.out

for cocid in `cat $LOGDIR/$OCICLI_USERREGION-compute-bootmap-1-$$.out | awk '{print $3}'`
do

  compartname=`grep $cocid $LOGDIR/$OCICLI_USERREGION-compute-bootmap-1-$$.out | awk '{print $1}'`
  compartid=`grep $compartname $LOGDIR/name-compart-map-$DATEDMY-cfg-$$.out | awk '{print $2}'`
  addomain=`grep $cocid $LOGDIR/$OCICLI_USERREGION-name-compute-map-$DATEDMY-cfg-$$.out | awk '{print $4}'`

  oci compute boot-volume-attachment list --compartment-id $compartid --availability-domain $addomain > $LOGDIR/$OCICLI_USERREGION-$compartname-compute-bootvol-$$.out

  bootvolid=`grep -B4 $cocid $LOGDIR/$OCICLI_USERREGION-$compartname-compute-bootvol-$$.out | grep boot-volume-id | awk '{print $2}' | cut -d, -f1 | sed 's/"//g'`

  echo $bootvolid >> $LOGDIR/$OCICLI_USERREGION-compute-bootmap-2-$$.out

done

paste $LOGDIR/$OCICLI_USERREGION-compute-bootmap-1-$$.out $LOGDIR/$OCICLI_USERREGION-compute-bootmap-2-$$.out > $LOGDIR/$OCICLI_USERREGION-compute-bootmap-$DATEDMY-cfg-$$.out

num_bootvol=`cat $LOGDIR/$OCICLI_USERREGION-compute-bootmap-$DATEDMY-cfg-$$.out | wc -l`

echo "" 2>&1 | tee -a $LOG
echo "There are currently $num_bootvol ATTACHED boot volumes to compute instances in the $OCICLI_USERREGION region. " 2>&1 | tee -a $LOG

	echo "" 2>&1 | tee -a $LOG

	cat $LOGDIR/$OCICLI_USERREGION-compute-bootmap-$DATEDMY-cfg-$$.out 2>&1 | tee -a $LOG
	echo "" 2>&1 | tee -a $LOG
	echo "" 2>&1 | tee -a $LOG

echo "Dumping Compartment Name, Compute Instance Name/OCID, and Boot Volume OCID mapping to file:" 2>&1 | tee -a $LOG
echo $LOGDIR/$OCICLI_USERREGION-compute-bootmap-$DATEDMY-cfg-$$.out 2>&1 | tee -a $LOG
echo "" 2>&1 | tee -a $LOG
echo "" 2>&1 | tee -a $LOG

#
# Get List of unattached boot volumes by compartment
# Format out: <Compartment Name> <Boot Volume Name> <Boot Volume OCID> <Availability Domain>
#


for compartname in `cat $LOGDIR/name-compart-map-$DATEDMY-cfg-$$.out | awk '{print $1}'`
do

  compartid=`grep $compartname $LOGDIR/name-compart-map-$DATEDMY-cfg-$$.out | awk '{print $2}'`

# Get a list of All Boot Volume OCIDs by Compartment and Availability Domain

  for addomain in `oci iam availability-domain list | grep name | awk '{print $2}' | sed 's/"//g'`
  do

    oci bv boot-volume list --compartment-id $compartid --availability-domain $addomain | grep bootvolume.oc | awk '{print $2}' | cut -d, -f1 | sed 's/"//g' > $LOGDIR/$OCICLI_USERREGION-allbootvolocids-temp-$$.out

    numocids=`cat $LOGDIR/$OCICLI_USERREGION-allbootvolocids-temp-$$.out | wc -l`
 
    if [ "$numocids" != "0" ]; then

# Compare All Boot OCID List with ones attached to compute instances

	for bootocid in `cat $LOGDIR/$OCICLI_USERREGION-allbootvolocids-temp-$$.out`
	do
	   
	grep $bootocid $LOGDIR/$OCICLI_USERREGION-compute-bootmap-$DATEDMY-cfg-$$.out

    	if [ "$?" == "1" ]; then
	
	# Boot OCID not found attached per boot map to compute instance list
	# Get Boot Vol OCID lifecycle-status (e.g. AVAILABLE and not PROVISIONING or TERMINATED)

	     bootvlifestate=`oci bv boot-volume get --boot-volume-id $bootocid | grep lifecycle-state | awk '{print $2}' | cut -d, -f1 | sed 's/"//g'`
    	     if [ "$bootvlifestate" == "AVAILABLE" ]; then

	      # Get the Boot Volume Display Name of the potential orphan and print all to unattached boot volume file

	  	bootvolname=`oci bv boot-volume get --boot-volume-id $bootocid | grep display-name | awk '{print $2}' | cut -d, -f1 | sed 's/"//g'`

    	  	echo -en "$compartname $bootvolname $bootocid $addomain\n" >> $LOGDIR/$OCICLI_USERREGION-unattach-bootvols-$DATEDMY-cfg-$$.out

	     fi

	fi

	done 

    fi

  done


done

echo "----------------------------------------------------------------------------" 2>&1 | tee -a $LOG
echo "List of UNATTACHED Boot Volumes within each Compartment by Boot Volume OCID" 2>&1 | tee -a $LOG
echo "Format: <Compartment Name> <Boot Volume Name> <Boot Volume OCID> <Availability Domain>" 2>&1 | tee -a $LOG

	echo "" 2>&1 | tee -a $LOG
	echo "" 2>&1 | tee -a $LOG


num_unattachbootvol=`cat $LOGDIR/$OCICLI_USERREGION-unattach-bootvols-$DATEDMY-cfg-$$.out | wc -l`

echo "" 2>&1 | tee -a $LOG
echo "There are currently $num_unattachbootvol unattached boot volumes in the $OCICLI_USERREGION region. " 2>&1 | tee -a $LOG


	echo "" 2>&1 | tee -a $LOG

	cat $LOGDIR/$OCICLI_USERREGION-unattach-bootvols-$DATEDMY-cfg-$$.out 2>&1 | tee -a $LOG
	echo "" 2>&1 | tee -a $LOG
	echo "" 2>&1 | tee -a $LOG

echo "Dumping Compartment Name, Boot Volume Name, Boot Volume OCID and Availability Domain mapping to file:" 2>&1 | tee -a $LOG

if [ "$num_unattachbootvol" == "0" ]; then

 echo "There are NO Unattached Boot Volumes in the region: " >> $LOGDIR/$OCICLI_USERREGION-unattach-bootvols-$DATEDMY-cfg-$$.out
 echo $OCICLI_USERREGION >> $LOGDIR/$OCICLI_USERREGION-unattach-bootvols-$DATEDMY-cfg-$$.out

fi

echo $LOGDIR/$OCICLI_USERREGION-unattach-bootvols-$DATEDMY-cfg-$$.out 2>&1 | tee -a $LOG
echo "" 2>&1 | tee -a $LOG
echo "" 2>&1 | tee -a $LOG


# Clean up remaining temporary compartment boot volume id file

rm $LOGDIR/$OCICLI_USERREGION-*-compute-bootvol-$$.out
rm $LOGDIR/$OCICLI_USERREGION-*temp-$$.out

}

get_compute_instance_block_map() {

# Generate Compute Instance OCID Mapping to Blockvol OCID(s)
#
# Get Compute Instance OCID mapping to Attached Block Volumes
# Format out: <Compartment Name> <Compute Instance Name> <Block Volume Name> <Block Volume OCID>
#

echo "----------------------------------------------------------------------------" 2>&1 | tee -a $LOG
echo "" 2>&1 | tee -a $LOG
echo "Getting list of Compute Instance OCIDs and Block Volume OCIDs" 2>&1 | tee -a $LOG
echo "for ${OCICLI_USERREGION}..." 2>&1 | tee -a $LOG
echo "" 2>&1 | tee -a $LOG
echo "----------------------------------------------------------------------------" 2>&1 | tee -a $LOG

echo "List of Compute Instances and Attached Block Volume Names, OCIDs" 2>&1 | tee -a $LOG
echo "Format: <Compartment Name> <Compute Instance Name> <Attached Block Volume Name> <Block Volume OCID>" 2>&1 | tee -a $LOG

	echo "" 2>&1 | tee -a $LOG

# Find attached block volumes based on compute instance OCID
# Note:
# Method of leveraging 'oci compute instance get --instance-id <computeinst-id> | grep volume-id..'
# is not available at this time as this info is not currently available with this query.
#
# BACKUP NOTES
# oci bv backup create --volume-id <volume-id> --display-name <name-can-be-based-on-vol-name> --type <FULL|INCREMENTAL>
# oci bv backup list --volume-id <volume-id>
# OCI CLI Reference: https://docs.cloud.oracle.com/iaas/tools/oci-cli/latest/oci_cli_docs/cmdref/bv/backup/create.html
#
# A full back captures all the data that changed since the volume creation.
# An incremental backup captures only the data that changed since the last backup (data modifed from the last backup).
# Backup metadata:
# "sizeInGBs": size of the volume backup was taken of whereas "uniqueSizeInGBs" : actual size of data that’s backed up.
#
# Format: <Compartment Name> <Compute Instance Name> <Attached Block Volume Name> <Block Volume OCID>


for cocid in `cat $LOGDIR/$OCICLI_USERREGION-name-compute-map-$DATEDMY-cfg-$$.out | awk '{print $3}'`
do

  computename=`grep $cocid $LOGDIR/$OCICLI_USERREGION-name-compute-map-$DATEDMY-cfg-$$.out | awk '{print $2}'`
  compartname=`grep $cocid $LOGDIR/$OCICLI_USERREGION-name-compute-map-$DATEDMY-cfg-$$.out | awk '{print $1}'`
  compartid=`grep $compartname $LOGDIR/name-compart-map-$DATEDMY-cfg-$$.out | awk '{print $2}'`
  
  oci compute volume-attachment list --compartment-id $compartid --instance-id $cocid | grep -A8 volume-id | grep volume-id | awk '{print $2}' | sed 's/"//g' > $LOGDIR/$OCICLI_USERREGION-$compartname-compute-blockvol-$$.out

# Find Display Name for each of the Volume OCIDs 
# Loop for each volumeid found to get the display name for each one

  for volocid in `cat $LOGDIR/$OCICLI_USERREGION-$compartname-compute-blockvol-$$.out`
  do
    voldisplay=`oci bv volume list --compartment-id $compartid | grep -B2 $volocid | grep display-name | awk '{print $2}' | cut -d, -f1 | sed 's/"//g'`
    echo -en "$compartname $computename $voldisplay $volocid\n" >> $LOGDIR/$OCICLI_USERREGION-compute-blockmap-$DATEDMY-cfg-$$.out

  done
  
done

num_blockvols=`cat $LOGDIR/$OCICLI_USERREGION-compute-blockmap-$DATEDMY-cfg-$$.out | wc -l`

echo "There are currently $num_blockvols block volumes attached to compute instances in the $OCICLI_USERREGION region. " 2>&1 | tee -a $LOG
echo "" 2>&1 | tee -a $LOG

  cat $LOGDIR/$OCICLI_USERREGION-compute-blockmap-$DATEDMY-cfg-$$.out 2>&1 | tee -a $LOG
  echo "" 2>&1 | tee -a $LOG
  echo "" 2>&1 | tee -a $LOG

echo "Dumping Compartment Name, Compute Instance Name, attached Block Volume Name/OCID mapping to file:" 2>&1 | tee -a $LOG
echo $LOGDIR/$OCICLI_USERREGION-compute-blockmap-$DATEDMY-cfg-$$.out 2>&1 | tee -a $LOG
echo "" 2>&1 | tee -a $LOG
echo "" 2>&1 | tee -a $LOG

#
# Get List of unattached block volumes by compartment
# Format out: <Compartment Name> <Block Volume Name> <Block Volume OCID> <Availability Domain>
#


for compartname in `cat $LOGDIR/name-compart-map-$DATEDMY-cfg-$$.out | awk '{print $1}'`
do

  compartid=`grep $compartname $LOGDIR/name-compart-map-$DATEDMY-cfg-$$.out | awk '{print $2}'`

# Get a list of All Block Volume OCIDs by Compartment and Availability Domain

  for addomain in `oci iam availability-domain list | grep name | awk '{print $2}' | sed 's/"//g'`
  do

    oci bv volume list --compartment-id $compartid --availability-domain $addomain | grep volume.oc | awk '{print $2}' | cut -d, -f1 | sed 's/"//g' > $LOGDIR/$OCICLI_USERREGION-allvolocids-temp-$$.out

    numocids=`cat $LOGDIR/$OCICLI_USERREGION-allvolocids-temp-$$.out | wc -l`
 
    if [ "$numocids" != "0" ]; then

# Compare All Block OCID List with ones attached to compute instances

	for bvolocid in `cat $LOGDIR/$OCICLI_USERREGION-allvolocids-temp-$$.out`
	do
	   
	grep $bvolocid $LOGDIR/$OCICLI_USERREGION-compute-blockmap-$DATEDMY-cfg-$$.out

    	if [ "$?" == "1" ]; then
	
	# Block Vol OCID not found attached per boot map to compute instance list
	# Get Block Vol OCID lifecycle-status (e.g. AVAILABLE and not PROVISIONING or TERMINATED)

	     bvolifestate=`oci bv volume get --volume-id $bvolocid | grep lifecycle-state | awk '{print $2}' | cut -d, -f1 | sed 's/"//g'`
    	     if [ "$bvolifestate" == "AVAILABLE" ]; then

	      # Get the Block Volume Display Name of the potential orphan and print all to unattached block volume file

	  	bvolname=`oci bv volume get --volume-id $bvolocid | grep display-name | awk '{print $2}' | cut -d, -f1 | sed 's/"//g'`

    	  	echo -en "$compartname $bvolname $bvolocid $addomain\n" >> $LOGDIR/$OCICLI_USERREGION-unattach-blockvols-$DATEDMY-cfg-$$.out

	     fi

	fi

	done 

    fi

  done


done


echo "----------------------------------------------------------------------------" 2>&1 | tee -a $LOG
echo "List of UNATTACHED Block Volumes within each Compartment by Block Volume OCID" 2>&1 | tee -a $LOG
echo "Format: <Compartment Name> <Block Volume Name> <Block Volume OCID> <Availability Domain>" 2>&1 | tee -a $LOG

	echo "" 2>&1 | tee -a $LOG
	echo "" 2>&1 | tee -a $LOG


num_unattachblockvol=`cat $LOGDIR/$OCICLI_USERREGION-unattach-blockvols-$DATEDMY-cfg-$$.out | wc -l`

echo "" 2>&1 | tee -a $LOG
echo "There are currently $num_unattachblockvol unattached block volumes in the $OCICLI_USERREGION region. " 2>&1 | tee -a $LOG


	echo "" 2>&1 | tee -a $LOG

	cat $LOGDIR/$OCICLI_USERREGION-unattach-blockvols-$DATEDMY-cfg-$$.out 2>&1 | tee -a $LOG
	echo "" 2>&1 | tee -a $LOG
	echo "" 2>&1 | tee -a $LOG

echo "Dumping Compartment Name, Block Volume Name, Block Volume OCID and Availability Domain mapping to file:" 2>&1 | tee -a $LOG

if [ "$num_unattachblockvol" == "0" ]; then

 echo "There are NO Unattached Block Volumes in the region: " >> $LOGDIR/$OCICLI_USERREGION-unattach-blockvols-$DATEDMY-cfg-$$.out
 echo $OCICLI_USERREGION >> $LOGDIR/$OCICLI_USERREGION-unattach-blockvols-$DATEDMY-cfg-$$.out

fi

echo $LOGDIR/$OCICLI_USERREGION-unattach-blockvols-$DATEDMY-cfg-$$.out 2>&1 | tee -a $LOG
echo "" 2>&1 | tee -a $LOG
echo "" 2>&1 | tee -a $LOG

#
#
#

# Clean up remaining temporary compartment boot volume id file

rm $LOGDIR/$OCICLI_USERREGION-*temp-$$.out

# Clean up remaining temporary compartment block volume id file

rm $LOGDIR/$OCICLI_USERREGION-*-compute-blockvol-$$.out

}

get_fss_map() {

echo "----------------------------------------------------------------------------" 2>&1 | tee -a $LOG
echo "" 2>&1 | tee -a $LOG
echo "Getting list of OCI FSS by compartment and Availability Domain" 2>&1 | tee -a $LOG
echo "for ${OCICLI_USERREGION}..." 2>&1 | tee -a $LOG
echo "" 2>&1 | tee -a $LOG
echo "----------------------------------------------------------------------------" 2>&1 | tee -a $LOG

#
# Get FSS Name, FSS OCID and Availability Domain mapping
# Format out: <Compartment Name> <Compartment OCID> <FSS Name> <FSS OCID> <Availability Domain Name>
#

echo "List of FSS Filesystems by compartment and Availability Domain" 2>&1 | tee -a $LOG
echo "Format: <Compartment Name> <Compartment OCID> <FSS Name> <FSS OCID> <Availability Domain Name>" 2>&1 | tee -a $LOG
echo "" 2>&1 | tee -a $LOG

# BACKUP NOTES
# oci fs snapshot create --file-system-id <id> --name <name-of-snapshot>
# oci fs snapshot list --file-system-id <id>
# OCI CLI Reference: https://docs.cloud.oracle.com/iaas/tools/oci-cli/latest/oci_cli_docs/cmdref/fs/snapshot/create.html
#
# Format: <Compartment Name> <Compartment OCID> <FSS Name> <FSS OCID> <Availability Domain Name>

# Get Availability Domains for this region

oci iam availability-domain list | grep name | awk '{print $2}' | sed 's/"//g' > $LOGDIR/$OCICLI_USERREGION-fss-ad-$$.out

for compartname in `cat $LOGDIR/name-compart-map-$DATEDMY-cfg-$$.out | awk '{print $1}'`
do

  compartid=`grep $compartname $LOGDIR/name-compart-map-$DATEDMY-cfg-$$.out | awk '{print $2}'`
  
  # Find Display Name for each of the Filesystem OCIDs 
  # Loop for each Filesystem OCID found by AD to get the corresponding display name for each one

  for fssad in `cat $LOGDIR/$OCICLI_USERREGION-fss-ad-$$.out`
  do
    # write fss info found for the given AD to temp1 file, if temp1 file empty, then continue on to next AD

    oci fs file-system list --compartment-id $compartid --availability-domain $fssad | grep filesystem.oc | awk '{print $2}' | cut -d, -f1 | sed 's/"//g' > $LOGDIR/$OCICLI_USERREGION-$compartname-fssad-temp-$$.out

    if [ -s "$LOGDIR/$OCICLI_USERREGION-$compartname-fssad-temp-$$.out" ]; then

    	# get all of the fssocids in the temp1 file and use to find associated display-name for the fssocid(s)

	for fssocid in  `cat $LOGDIR/$OCICLI_USERREGION-$compartname-fssad-temp-$$.out` 
	do

	   fssname=`oci fs file-system list --compartment-id $compartid --availability-domain $fssad | grep -B1 $fssocid | grep display-name | awk '{print $2}' | cut -d, -f1 | sed 's/"//g'`

	   echo -en "$compartname $compartid $fssname $fssocid $fssad\n" >> $LOGDIR/$OCICLI_USERREGION-fssmap-$DATEDMY-cfg-$$.out

	done

    fi


  done
  
done

num_fss=`cat $LOGDIR/$OCICLI_USERREGION-fssmap-$DATEDMY-cfg-$$.out | wc -l`

echo "There are currently $num_fss filesystems in the $OCICLI_USERREGION region. " 2>&1 | tee -a $LOG

  echo "" 2>&1 | tee -a $LOG

  cat $LOGDIR/$OCICLI_USERREGION-fssmap-$DATEDMY-cfg-$$.out 2>&1 | tee -a $LOG
  echo "" 2>&1 | tee -a $LOG
  echo "" 2>&1 | tee -a $LOG

echo "Dumping Compartment Name/OCID, FSS Name/OCID, and Availability Domain mapping to file:" 2>&1 | tee -a $LOG
echo $LOGDIR/$OCICLI_USERREGION-fssmap-$DATEDMY-cfg-$$.out 2>&1 | tee -a $LOG
echo "" 2>&1 | tee -a $LOG
echo "" 2>&1 | tee -a $LOG

# Clean up remaining temporary compartment block volume id file

rm $LOGDIR/$OCICLI_USERREGION-fss-ad-*.out
rm $LOGDIR/$OCICLI_USERREGION-*-temp-*.out


}

get_ossb_map() {

echo "----------------------------------------------------------------------------" 2>&1 | tee -a $LOG
echo "" 2>&1 | tee -a $LOG
echo "Getting list of OCI Object Storage Buckets and Tiers in namespace by compartment" 2>&1 | tee -a $LOG
echo "for ${OCICLI_USERREGION}..." 2>&1 | tee -a $LOG
echo "" 2>&1 | tee -a $LOG
echo "----------------------------------------------------------------------------" 2>&1 | tee -a $LOG

#
# OCI CLI Reference: https://docs.cloud.oracle.com/iaas/tools/oci-cli/latest/oci_cli_docs/cmdref/os/bucket.html
# Get OCI Bucket Names and Tier Types by Compartment
# Format out: <Namespace> <Compartment Name> <Compartment OCID> <Bucket Name> <Bucket Storage Tier>
#

echo "List of OCI Object Storage Buckets and Tiers in namespace by compartment" 2>&1 | tee -a $LOG
echo "Format: <Namespace> <Compartment Name> <Compartment OCID> <Bucket Name> <Bucket Storage Tier>" 2>&1 | tee -a $LOG
echo "" 2>&1 | tee -a $LOG


for compartname in `cat $LOGDIR/name-compart-map-$DATEDMY-cfg-$$.out | awk '{print $1}'`
do

  compartid=`grep $compartname $LOGDIR/name-compart-map-$DATEDMY-cfg-$$.out | awk '{print $2}'`

  oci os bucket list --namespace-name $OCI_NAMESP --compartment-id $compartid | grep "\<name\>" | awk '{print $2}' | cut -d, -f1 | sed 's/"//g' > $LOGDIR/$OCICLI_USERREGION-$compartname-ossb-temp-$$.out

  for ossb in `cat $LOGDIR/$OCICLI_USERREGION-$compartname-ossb-temp-$$.out`
  do

	stier=`oci os bucket get --bucket-name $ossb | grep storage-tier | awk '{print $2}' | cut -d, -f1 | sed 's/"//g'`

	echo -en "$OCI_NAMESP $compartname $compartid $ossb $stier\n" >> $LOGDIR/$OCICLI_USERREGION-ossb-map-$DATEDMY-cfg-$$.out

  done

done

num_ossb=`cat $LOGDIR/$OCICLI_USERREGION-ossb-map-$DATEDMY-cfg-$$.out | wc -l`

echo "There are currently $num_ossb Object Storage Buckets in the $OCICLI_USERREGION region. " 2>&1 | tee -a $LOG

  echo "" 2>&1 | tee -a $LOG

  cat $LOGDIR/$OCICLI_USERREGION-ossb-map-$DATEDMY-cfg-$$.out 2>&1 | tee -a $LOG
  echo "" 2>&1 | tee -a $LOG
  echo "" 2>&1 | tee -a $LOG

echo "Dumping Namespace, Compartment/OCID, Bucket Name, Bucket Storate Tier mapping to file:" 2>&1 | tee -a $LOG
echo $LOGDIR/$OCICLI_USERREGION-ossb-map-$DATEDMY-cfg-$$.out 2>&1 | tee -a $LOG
echo "" 2>&1 | tee -a $LOG
echo "" 2>&1 | tee -a $LOG

# Clean up remaining temporary compartment ossb files
 
rm $LOGDIR/$OCICLI_USERREGION-*-ossb-temp-$$.out


}

get_lb_map() {

echo "----------------------------------------------------------------------------" 2>&1 | tee -a $LOG
echo "" 2>&1 | tee -a $LOG
echo "Getting list of OCI Load Balancer info by compartment" 2>&1 | tee -a $LOG
echo "for ${OCICLI_USERREGION}..." 2>&1 | tee -a $LOG
echo "" 2>&1 | tee -a $LOG
echo "----------------------------------------------------------------------------" 2>&1 | tee -a $LOG

#
# OCI CLI Reference: https://docs.cloud.oracle.com/iaas/tools/oci-cli/latest/oci_cli_docs/cmdref/lb.html
# Get OCI Load Balancer OCIDs by Compartment, then find Backend Set Names and Backends info
# Format out: <compartment-name> <compartment-ocid> <display-name> <load-balancer-type> <load-balancer-id> <backend-set-name> <backend-name> 
# Where: 
# display-name is the name of the load balancer as seen in the OCI Web Console.
# shape is the LB provisioned maximum capacity (bandwidth) for ingress and egress traffic. Available shapes: 100 Mbps,400 Mbps,8000 Mbps.
# load-balancer-type is the type of load balancer (public or private) assocated with LB subnet type.
# subnet-name is the OCI subnet name where the load balancer is deployed.
# load-balancer-id is the [OCID] of the load balancer associated with the backend set and server.
# backend-set-name is the name of the backend set associated with the backend server.
# backend-name is the IP address and port of the backend server associated with the backend set name.
#

echo "List of OCI Load Balancer information by compartment" 2>&1 | tee -a $LOG
echo "Format: <compartment-name> <compartment-ocid> <display-name> <shape> <load-balancer-type> <subnet-name> <load-balancer-id> <backend-set-name> <backend-name>" 2>&1 | tee -a $LOG
echo "" 2>&1 | tee -a $LOG


for compartname in `cat $LOGDIR/name-compart-map-$DATEDMY-cfg-$$.out | awk '{print $1}'`
do

  compartid=`grep $compartname $LOGDIR/name-compart-map-$DATEDMY-cfg-$$.out | awk '{print $2}'`

# Get a list of LB OCIDs

  oci lb load-balancer list --compartment-id $compartid | grep loadbalancer.oc | awk '{print $2}' | cut -d, -f1 | sed 's/"//g' > $LOGDIR/$OCICLI_USERREGION-$compartname-lb-temp-$$.out

# Get the LB Name, Backend Set Name(s) and Backend(s)

  for lbocid in `cat $LOGDIR/$OCICLI_USERREGION-$compartname-lb-temp-$$.out`
  do

	lbname=`oci lb load-balancer get --load-balancer-id $lbocid | grep display-name | awk '{print $2}' | cut -d, -f1 | sed 's/"//g'`
	lbshape=`oci lb load-balancer get --load-balancer-id $lbocid | grep shape-name | awk '{print $2}' | cut -d, -f1 | sed 's/"//g'`
	lbtype=`oci lb load-balancer get --load-balancer-id $lbocid | grep is-public | awk '{print $2}'`
	lbsubnetocid=`oci lb load-balancer get --load-balancer-id $lbocid | grep subnet.oc | sed 's/"//g'`
	lbsubnetname=`oci network subnet get --subnet-id $lbsubnetocid | grep display | awk '{print $2}' | cut -d, -f1 | sed 's/"//g'`

	if [ "$lbtype" == "true" ]; then

	   lbptype="Public"

	   else

	   lbptype="Private"

	fi

	for bsetname in `oci lb backend-set list --load-balancer-id $lbocid | grep -B1 policy | grep "\<name\>" | awk '{print $2}' | cut -d, -f1 | sed 's/"//g'`
	do
	   oci lb backend list --load-balancer-id $lbocid --backend-set-name $bsetname | grep "\<name\>" | awk '{print $2}' | cut -d, -f1 | sed 's/"//g' > $LOGDIR/$OCICLI_USERREGION-$compartname-lb-bendlist-temp-$$.out

		# Address use-case where LB has Backend set but no backend servers defined

		if [[ -f "$LOGDIR/$OCICLI_USERREGION-$compartname-lb-bendlist-temp-$$.out" && ! -s "$LOGDIR/$OCICLI_USERREGION-$compartname-lb-bendlist-temp-$$.out" ]]; then

    			echo "NoneDefined" > $LOGDIR/$OCICLI_USERREGION-$compartname-lb-bendlist-temp-$$.out

		fi

		for bendserver in `cat $LOGDIR/$OCICLI_USERREGION-$compartname-lb-bendlist-temp-$$.out`
		do

		   echo -en "$compartname $compartid $lbname $lbshape $lbptype $lbsubnetname $lbocid $bsetname $bendserver\n" >> $LOGDIR/$OCICLI_USERREGION-lb-map-$DATEDMY-cfg-$$.out

		done
	done

  done

done

num_lb=`cat $LOGDIR/$OCICLI_USERREGION-lb-map-$DATEDMY-cfg-$$.out | awk '{print $7}' | uniq | wc -l`

echo "There are currently $num_lb Load Balancers in the $OCICLI_USERREGION region. " 2>&1 | tee -a $LOG

  echo "" 2>&1 | tee -a $LOG

  cat $LOGDIR/$OCICLI_USERREGION-lb-map-$DATEDMY-cfg-$$.out 2>&1 | tee -a $LOG
  echo "" 2>&1 | tee -a $LOG
  echo "" 2>&1 | tee -a $LOG

# Format: <compartment-name> <compartment-ocid> <display-name> <shape> <load-balancer-type> <subnet-name> <load-balancer-id> <backend-set-name> <backend-name>

echo "Dumping Compartment/OCID, Load Balancer Name, Load Balancer Type, Subnet Name, Load Balancer OCID, Backend Set Name and associated Backends mapping to file:" 2>&1 | tee -a $LOG
echo $LOGDIR/$OCICLI_USERREGION-lb-map-$DATEDMY-cfg-$$.out 2>&1 | tee -a $LOG
echo "" 2>&1 | tee -a $LOG
echo "" 2>&1 | tee -a $LOG

# Clean up remaining temporary compartment lb files
 
rm $LOGDIR/$OCICLI_USERREGION-*-lb*temp-$$.out


}

get_dbsys_map() {

echo "----------------------------------------------------------------------------" 2>&1 | tee -a $LOG
echo "" 2>&1 | tee -a $LOG
echo "Getting list of OCI Database Systems and Database info by compartment" 2>&1 | tee -a $LOG
echo "for ${OCICLI_USERREGION}..." 2>&1 | tee -a $LOG
echo "" 2>&1 | tee -a $LOG
echo "----------------------------------------------------------------------------" 2>&1 | tee -a $LOG

#
# OCI CLI Reference: https://docs.cloud.oracle.com/iaas/tools/oci-cli/latest/oci_cli_docs/cmdref/db.html
# Get OCI DB System OCIDs by Compartment, then find Database System Names, DB Names and OCIDs
# Format: <compartment name> <compartment OCID> <Shape> <DBSys-Name> <DBSys OCID> <DB Name> < PDB Name> <DB OCID> <AD>
# Where: 
# DBSys-Name is the OCI Database System Name. 
# DBSys OCID is the OCID of the OCI Database System.
# Shape is the OCI Shape of the Database System.
# DB Name is the OCI Database Name
# PDB Name is the OCI Pluggable Database (PDB) Name
# DB OCID is the OCID of the OCI Database.
# AD is the Availability Domain
#
# Note for DB Nodes, and PDB Listing..may need another mapping...


echo "List of OCI Database System information by compartment" 2>&1 | tee -a $LOG
echo "Format: <compartment name> <compartment OCID> <Shape> <DBSys-Name> <DBSys OCID> <DB Name> <PDB Name> <DB OCID> <AD>" 2>&1 | tee -a $LOG
echo "" 2>&1 | tee -a $LOG


for compartname in `cat $LOGDIR/name-compart-map-$DATEDMY-cfg-$$.out | awk '{print $1}'`
do

  compartid=`grep $compartname $LOGDIR/name-compart-map-$DATEDMY-cfg-$$.out | awk '{print $2}'`

# Get a list of DBSystem OCIDs in the compartment

   oci db system list --compartment-id $compartid | grep dbsystem.oc | awk '{print $2}' | cut -d, -f1 | sed 's/"//g' > $LOGDIR/$OCICLI_USERREGION-$compartname-dbsys-temp-$$.out

# Get the DBSys Name, NodeID/Nodename, DB Sys Shape, DB Name, DB OCIDs and Availability Domain


  for dbsysocid in `cat $LOGDIR/$OCICLI_USERREGION-$compartname-dbsys-temp-$$.out`
  do

	dbsysname=`oci db system get --db-system-id $dbsysocid | grep display-name | awk '{print $2}' | cut -d, -f1 | sed 's/"//g'`
	dbsyshape=`oci db system get --db-system-id $dbsysocid | grep shape | awk '{print $2}' | cut -d, -f1 | sed 's/"//g'`
	adomain=`oci db system get --db-system-id $dbsysocid | grep availability-domain | awk '{print $2}' | cut -d, -f1 | sed 's/"//g'`

# Get the DB NodeID(s) and Hostname(s) for the DBSys

    for dbnodeid in `oci db node list --compartment-id $compartid --db-system-id $dbsysocid | grep dbnode.oc | awk '{print $2}' | cut -d, -f1 | sed 's/"//g'` 
    do

	nodename=`oci db node get --db-node-id $dbnodeid | grep hostname | awk '{print $2}' | cut -d, -f1 | sed 's/"//g'`
	nodelifecyclestate=`oci db node get --db-node-id $dbnodeid | grep lifecycle-state | awk '{print $2}' | cut -d, -f1 | sed 's/"//g'`

	echo -en "$compartname $dbsysname $dbsysocid $nodename $dbnodeid $nodelifecyclestate\n" >> $LOGDIR/$OCICLI_USERREGION-dbsys-nodemap-$DATEDMY-cfg-$$.out



    done

        oci db database list --compartment-id  $compartid --db-system-id $dbsysocid | grep database.oc | awk '{print $2}' | cut -d, -f1 | sed 's/"//g' > $LOGDIR/$OCICLI_USERREGION-$compartname-db-temp-$$.out

     for dbocid in `cat $LOGDIR/$OCICLI_USERREGION-$compartname-db-temp-$$.out`
     do

	dbname=`oci db database get --database-id $dbocid | grep "\<db-name\>" | awk '{print $2}' | cut -d, -f1 | sed 's/"//g'`
	pdbname=`oci db database get --database-id $dbocid | grep "\<pdb-name\>" | awk '{print $2}' | cut -d, -f1 | sed 's/"//g'`

	# if pdbname returns "null" then there is not a pdb for the cdb

	if [ "$pdbname" == "null" ]; then

	   pdbname="hasnopdb"

	fi

	echo -en "$compartname $compartid $dbsyshape $dbsysname $dbsysocid $dbname $pdbname $dbocid $adomain\n" >> $LOGDIR/$OCICLI_USERREGION-dbsys-map-$DATEDMY-cfg-$$.out

     done


  done


done

num_db=`cat $LOGDIR/$OCICLI_USERREGION-dbsys-map-$DATEDMY-cfg-$$.out | wc -l`
num_pdb=`cat $LOGDIR/$OCICLI_USERREGION-dbsys-map-$DATEDMY-cfg-$$.out | grep -v hasnopdb | wc -l`

echo "There are currently $num_db Databases and $num_pdb Pluggable Databases in the $OCICLI_USERREGION region. " 2>&1 | tee -a $LOG

  echo "" 2>&1 | tee -a $LOG

  cat $LOGDIR/$OCICLI_USERREGION-dbsys-map-$DATEDMY-cfg-$$.out 2>&1 | tee -a $LOG
  echo "" 2>&1 | tee -a $LOG
  echo "" 2>&1 | tee -a $LOG

# Format: <compartment name> <compartment OCID> <Shape> <DBSys-Name> <DBSys OCID> <DB Name> <PDB Name> <DB OCID> <AD>

echo "Dumping Compartment/OCID, DatabaseSys Shape, DB Sys Name, DB Sys OCID, DB Name, PDB Name, DB OCID and Availability Domain to file:" 2>&1 | tee -a $LOG
echo $LOGDIR/$OCICLI_USERREGION-dbsys-map-$DATEDMY-cfg-$$.out 2>&1 | tee -a $LOG
echo "" 2>&1 | tee -a $LOG
echo "" 2>&1 | tee -a $LOG

echo "List of OCI Database System information by Node" 2>&1 | tee -a $LOG
echo "Format: <compartment name> <DBSys-Name> <DBSys OCID> <Nodename> <DB NodeOCID> <DB Node Lifecycle State>" 2>&1 | tee -a $LOG
echo "" 2>&1 | tee -a $LOG

num_db_hosts=`cat $LOGDIR/$OCICLI_USERREGION-dbsys-nodemap-$DATEDMY-cfg-$$.out | wc -l`

echo "There are currently $num_db_hosts Database Nodes in the $OCICLI_USERREGION region. " 2>&1 | tee -a $LOG

  echo "" 2>&1 | tee -a $LOG

cat  $LOGDIR/$OCICLI_USERREGION-dbsys-nodemap-$DATEDMY-cfg-$$.out 2>&1 | tee -a $LOG

# Format: <compartment name> <DBSys-Name> <DBSys OCID> <Nodename> <DB NodeOCID> <DB Node Lifecycle State>

echo "" 2>&1 | tee -a $LOG
echo "Dumping Compartment, DB Sys Name, DB Sys OCID, Node Name, Node OCID, and Node Lifecycle Status to file:" 2>&1 | tee -a $LOG
echo  $LOGDIR/$OCICLI_USERREGION-dbsys-nodemap-$DATEDMY-cfg-$$.out 2>&1 | tee -a $LOG
echo "" 2>&1 | tee -a $LOG


# Clean up remaining temporary compartment DB Sys/DB  files
 
rm $LOGDIR/$OCICLI_USERREGION-*-dbsys*temp-$$.out
rm $LOGDIR/$OCICLI_USERREGION-*-db*temp-$$.out


}

get_vcn_map() {

echo "----------------------------------------------------------------------------" 2>&1 | tee -a $LOG
echo "" 2>&1 | tee -a $LOG
echo "Getting list of OCI Network VCNs and Subnet info by compartment" 2>&1 | tee -a $LOG
echo "for ${OCICLI_USERREGION}..." 2>&1 | tee -a $LOG
echo "" 2>&1 | tee -a $LOG
echo "----------------------------------------------------------------------------" 2>&1 | tee -a $LOG

#
# OCI CLI Reference: https://docs.cloud.oracle.com/iaas/tools/oci-cli/latest/oci_cli_docs/cmdref/network.html
# Get OCI VCN OCIDs by Compartment, then find Subnet Names/OCIDs and Availability Domains
# Format: <compartment name> <VCN Name> <VCN CIDR> <VCN OCID> <Subnet Name> <Subnet Type> <Subnet CIDR> <Subnet OCID> <Availability Domain>

echo "List of OCI Virtual Cloud Networks and Subnets by compartment and Availability Domain" 2>&1 | tee -a $LOG
echo "Format: <compartment name> <VCN Name> <VCN CIDR> <VCN OCID> <Subnet Name> <Subnet Type> <Subnet CIDR> <Subnet OCID> <Availability Domain>" 2>&1 | tee -a $LOG
echo "" 2>&1 | tee -a $LOG


for compartname in `cat $LOGDIR/name-compart-map-$DATEDMY-cfg-$$.out | awk '{print $1}'`
do

  compartid=`grep $compartname $LOGDIR/name-compart-map-$DATEDMY-cfg-$$.out | awk '{print $2}'`

# Get a list of VCN OCIDs in the compartment

   oci network vcn list --compartment-id $compartid | grep vcn.oc | awk '{print $2}' | cut -d, -f1 | sed 's/"//g' > $LOGDIR/$OCICLI_USERREGION-$compartname-vcnocids-temp-$$.out

  for vcnocid in `cat $LOGDIR/$OCICLI_USERREGION-$compartname-vcnocids-temp-$$.out`
  do

    vcnname=`oci network vcn get --vcn-id $vcnocid | grep display-name | awk '{print $2}' | cut -d, -f1 | sed 's/"//g'`
    vcncidr=`oci network vcn get --vcn-id $vcnocid | grep cidr-block | awk '{print $2}' | cut -d, -f1 | sed 's/"//g'`

    oci network subnet list --compartment-id $compartid --vcn-id $vcnocid | grep subnet.oc | awk '{print $2}' | cut -d, -f1 | sed 's/"//g' > $LOGDIR/$OCICLI_USERREGION-$compartname-subnetocids-temp-$$.out

	for subnetocid in `cat $LOGDIR/$OCICLI_USERREGION-$compartname-subnetocids-temp-$$.out`
	do

	  subname=`oci network subnet get --subnet-id $subnetocid | grep display-name | awk '{print $2}' | cut -d, -f1 | sed 's/"//g'`
	  subtype=`oci network subnet get --subnet-id $subnetocid | grep prohibit-public-ip-on-vnic | awk '{print $2}' | cut -d, -f1`

		if [ "$subtype" == "true" ]; then

	   		subptype="Private"
	   	else
	   		subptype="Public"

		fi



	  subcidr=`oci network subnet get --subnet-id $subnetocid | grep cidr-block | awk '{print $2}' | cut -d, -f1 | sed 's/"//g'`
	  addomain=`oci network subnet get --subnet-id $subnetocid | grep availability-domain | awk '{print $2}' | cut -d, -f1 | sed 's/"//g'`

		if [ "$addomain" == "null" ]; then

	   		addomain="Regional"

		fi

	  echo -en "$compartname $vcnname $vcncidr $vcnocid $subname $subptype $subcidr $subnetocid $addomain\n" >> $LOGDIR/$OCICLI_USERREGION-vcn-map-$DATEDMY-cfg-$$.out

	done

  done

done

num_vcns=`cat $LOGDIR/$OCICLI_USERREGION-vcn-map-$DATEDMY-cfg-$$.out | awk '{print $4}' | uniq | wc -l`
num_subnets=`cat $LOGDIR/$OCICLI_USERREGION-vcn-map-$DATEDMY-cfg-$$.out | awk '{print $7}' | uniq | wc -l`
num_addomains=`cat $LOGDIR/$OCICLI_USERREGION-vcn-map-$DATEDMY-cfg-$$.out | awk '{print $9}' | sort -n | uniq | wc -l`

echo "There are currently $num_vcns Virtual Compute Network(s) and $num_subnets Subnet(s) across $num_addomains Availability Domain(s) within the $OCICLI_USERREGION region. " 2>&1 | tee -a $LOG

  echo "" 2>&1 | tee -a $LOG

  cat $LOGDIR/$OCICLI_USERREGION-vcn-map-$DATEDMY-cfg-$$.out  2>&1 | tee -a $LOG
  echo "" 2>&1 | tee -a $LOG
  echo "" 2>&1 | tee -a $LOG

# Format: <compartment name> <VCN Name> <VCN CIDR> <VCN OCID> <Subnet Name> <Subnet Type> <Subnet CIDR> <Subnet OCID> <Availability Domain>

echo "Dumping Compartment Name, VCN Name, VCN CIDR BLOCK, VCN OCID, Associated Subnet Name, Subnet Type, Subnet CIDR BLOCK, Subnet OCID and Availability Domain to file:" 2>&1 | tee -a $LOG
echo $LOGDIR/$OCICLI_USERREGION-vcn-map-$DATEDMY-cfg-$$.out 2>&1 | tee -a $LOG
echo "" 2>&1 | tee -a $LOG
echo "" 2>&1 | tee -a $LOG

echo "----------------------------------------------------------------------------" 2>&1 | tee -a $LOG
echo "" 2>&1 | tee -a $LOG
echo "Checking for Internet and Service Gateways by VCN" 2>&1 | tee -a $LOG
echo "for ${OCICLI_USERREGION}..." 2>&1 | tee -a $LOG
echo "" 2>&1 | tee -a $LOG
echo "----------------------------------------------------------------------------" 2>&1 | tee -a $LOG

#
# Get OCI VCNs by Compartment, then find Internet GW Names/OCIDs
# Format: <compartment name> <VCN Name> <Internet GW Name> <Internet GW OCID>

echo "List of OCI Virtual Cloud Networks and Internet Gateways by compartment" 2>&1 | tee -a $LOG
echo "Format: <compartment name> <VCN Name> <Internet GW Name> <Internet GW OCID>" 2>&1 | tee -a $LOG
echo "" 2>&1 | tee -a $LOG

for compartname in `cat $LOGDIR/name-compart-map-$DATEDMY-cfg-$$.out | awk '{print $1}'`
do

  compartid=`grep $compartname $LOGDIR/name-compart-map-$DATEDMY-cfg-$$.out | awk '{print $2}'`

# Get a list of VCN OCIDs in the compartment

   oci network vcn list --compartment-id $compartid | grep vcn.oc | awk '{print $2}' | cut -d, -f1 | sed 's/"//g' > $LOGDIR/$OCICLI_USERREGION-$compartname-vcnocids2-temp-$$.out

  for vcnocid in `cat $LOGDIR/$OCICLI_USERREGION-$compartname-vcnocids2-temp-$$.out`
  do
	
    vcnname=`oci network vcn get --vcn-id $vcnocid | grep display-name | awk '{print $2}' | cut -d, -f1 | sed 's/"//g'`

    igwname=`oci network internet-gateway list --compartment-id $compartid --vcn-id $vcnocid | grep display-name | awk '{print $2}' | cut -d, -f1 | sed 's/"//g'`

    igwocid=`oci network internet-gateway list --compartment-id $compartid --vcn-id $vcnocid | grep internetgateway.oc | awk '{print $2}' | cut -d, -f1 | sed 's/"//g'`

    if [ "$igwname" != "" ]; then

	  echo -en "$compartname $vcnname $igwname $igwocid\n" >> $LOGDIR/$OCICLI_USERREGION-igw-map-$DATEDMY-cfg-$$.out
    fi

  done

done

 if [[ -f "$LOGDIR/$OCICLI_USERREGION-igw-map-$DATEDMY-cfg-$$.out" && ! -s "$LOGDIR/$OCICLI_USERREGION-igw-map-$DATEDMY-cfg-$$.out" ]]; then

    echo "There are no defined Internet Gateways in the Region $OCICLI_USERREGION" 2>&1 | tee -a $LOG

 else

   num_igws=`cat $LOGDIR/$OCICLI_USERREGION-igw-map-$DATEDMY-cfg-$$.out | wc -l`

   echo "There are currently $num_igws Internet Gateway(s) within the $OCICLI_USERREGION region. " 2>&1 | tee -a $LOG
   echo "" 2>&1 | tee -a $LOG

   cat  $LOGDIR/$OCICLI_USERREGION-igw-map-$DATEDMY-cfg-$$.out 2>&1 | tee -a $LOG

# Format: <compartment name> <VCN Name> <Internet GW Name> <Internet GW OCID>
#
    echo "" 2>&1 | tee -a $LOG
    echo "" 2>&1 | tee -a $LOG
    echo "Dumping Compartment Name, VCN Name, Internet Gateway Name, IGW  OCID to file:" 2>&1 | tee -a $LOG
    echo $LOGDIR/$OCICLI_USERREGION-igw-map-$DATEDMY-cfg-$$.out 2>&1 | tee -a $LOG
    echo "" 2>&1 | tee -a $LOG
    echo "" 2>&1 | tee -a $LOG
 fi

#
# Get OCI VCNs by Compartment, then find Service GW Names/OCIDs
# Format: <compartment name> <VCN Name> <Service GW Name> <Service GW OCID>

echo "List of OCI Virtual Cloud Networks and Service Gateways by compartment" 2>&1 | tee -a $LOG
echo "Format: <compartment name> <VCN Name> <Service GW Name> <Service GW OCID>" 2>&1 | tee -a $LOG
echo "" 2>&1 | tee -a $LOG

for compartname in `cat $LOGDIR/name-compart-map-$DATEDMY-cfg-$$.out | awk '{print $1}'`
do

  compartid=`grep $compartname $LOGDIR/name-compart-map-$DATEDMY-cfg-$$.out | awk '{print $2}'`

# Get a list of VCN OCIDs in the compartment

   oci network vcn list --compartment-id $compartid | grep vcn.oc | awk '{print $2}' | cut -d, -f1 | sed 's/"//g' > $LOGDIR/$OCICLI_USERREGION-$compartname-vcnocids3-temp-$$.out

  for vcnocid in `cat $LOGDIR/$OCICLI_USERREGION-$compartname-vcnocids3-temp-$$.out`
  do
	
    vcnname=`oci network vcn get --vcn-id $vcnocid | grep display-name | awk '{print $2}' | cut -d, -f1 | sed 's/"//g'`

    sgwname=`oci network service-gateway list --compartment-id $compartid --vcn-id $vcnocid | grep display-name | awk '{print $2}' | cut -d, -f1 | sed 's/"//g'`

    sgwocid=`oci network service-gateway list --compartment-id $compartid --vcn-id $vcnocid | grep servicegateway.oc | awk '{print $2}' | cut -d, -f1 | sed 's/"//g'`

    if [ "$sgwocid" != "" ]; then

          # Valid Service Gateway Service Values are: "OCI PHX Object Storage" and/or "All PHX Services in Oracle Services Network"
          sgwsvcs=`oci network service-gateway get --service-gateway-id $sgwocid | grep service-name | cut -d: -f2`

	  echo -en "$compartname $vcnname $sgwname $sgwocid\n" >> $LOGDIR/$OCICLI_USERREGION-sgw-map-$DATEDMY-cfg-$$.out
	  echo -en "Service(s) provided by Service Gateway $sgwname are: $sgwsvcs\n" >> $LOGDIR/$OCICLI_USERREGION-sgw-svcmap-$DATEDMY-cfg-$$.out

    fi

  done

done

 if [[ -f "$LOGDIR/$OCICLI_USERREGION-sgw-map-$DATEDMY-cfg-$$.out" && ! -s "$LOGDIR/$OCICLI_USERREGION-sgw-map-$DATEDMY-cfg-$$.out" ]]; then

    echo "There are no defined Service Gateways in the Region $OCICLI_USERREGION" 2>&1 | tee -a $LOG

 else

   num_sgws=`cat $LOGDIR/$OCICLI_USERREGION-sgw-map-$DATEDMY-cfg-$$.out | wc -l`

   echo "There are currently $num_sgws Service Gateway(s) within the $OCICLI_USERREGION region. " 2>&1 | tee -a $LOG
   echo "" 2>&1 | tee -a $LOG

   cat  $LOGDIR/$OCICLI_USERREGION-sgw-map-$DATEDMY-cfg-$$.out 2>&1 | tee -a $LOG
   echo "" 2>&1 | tee -a $LOG
   cat  $LOGDIR/$OCICLI_USERREGION-sgw-svcmap-$DATEDMY-cfg-$$.out | tee -a $LOG

# Format: <compartment name> <VCN Name> <Service GW Name> <Service GW OCID>
#
    echo "" 2>&1 | tee -a $LOG
    echo "" 2>&1 | tee -a $LOG
    echo "Dumping Compartment Name, VCN Name, Service Gateway Name, SGW OCID to file:" 2>&1 | tee -a $LOG
    echo $LOGDIR/$OCICLI_USERREGION-sgw-map-$DATEDMY-cfg-$$.out 2>&1 | tee -a $LOG
    echo "" 2>&1 | tee -a $LOG
    echo "" 2>&1 | tee -a $LOG
 fi


# Clean up remaining temporary compartment VCN and Subnet OCID Files
 
rm $LOGDIR/$OCICLI_USERREGION-$compartname-vcn*-temp-$$.out
rm $LOGDIR/$OCICLI_USERREGION-$compartname-subnet*-temp-$$.out


}

cleanup_files() {


echo "----------------------------------------------------------------------------" 2>&1 | tee -a $LOG
echo "" 2>&1 | tee -a $LOG
echo "Executing Clean-up of temporary files in logdir: $LOGDIR..." 2>&1 | tee -a $LOG
echo "" 2>&1 | tee -a $LOG
echo "----------------------------------------------------------------------------" 2>&1 | tee -a $LOG


#
# Cleanup temp files from "get_compartments"
#


find $LOGDIR -type f -name "ocidcompart-*.out" -exec rm {} \; 2> /dev/null
find $LOGDIR -type f -name "compartname-*.out" -exec rm {} \; 2> /dev/null


#
# Cleanup temp files from "get_compute_instance_map"
#


find $LOGDIR -type f -name "ocidcompute-*.out" -exec rm {} \; 2> /dev/null


#
# Cleanup temp files from "get_compute_instance_boot_map"
#

find $LOGDIR -type f -name "us*compute-bootmap-1-*.out" -exec rm {} \; 2> /dev/null
find $LOGDIR -type f -name "us*compute-bootmap-2-*.out" -exec rm {} \; 2> /dev/null
find $LOGDIR -type f -name "us*compute-bootvol-*.out" -exec rm {} \; 2> /dev/null


#
# Cleanup temp files from "get_compute_instance_block_map"
#


find $LOGDIR -type f -name "us-*-compute-blockvol-$$.out" -exec rm {} \; 2> /dev/null


#
# Cleanup temp files from "get_fss_map"
#


find $LOGDIR -type f -name "us-*-fss-ad-*.out" -exec rm {} \; 2> /dev/null
find $LOGDIR -type f -name "us-*-temp-*.out" -exec rm {} \; 2> /dev/null


#
# Cleanup temp files from "get_ossb_map"
#


find $LOGDIR -type f -name "us-*-ossb-temp-$$.out" -exec rm {} \; 2> /dev/null


#
# Cleanup temp files from "get_lb_map"
#


find $LOGDIR -type f -name "us-*-lb*temp-$$.out" -exec rm {} \; 2> /dev/null


}

####
# Main Part of Script
####
#
echo "" 2>&1 | tee -a $LOG
echo "" 2>&1 | tee -a $LOG
echo "----------------------------------------------------------------------------" 2>&1 | tee -a $LOG
echo "" 2>&1 | tee -a $LOG
echo "Start of OCI Summary Report Script: `basename $0` on `date`" 2>&1 | tee -a $LOG
echo "Report is for the following Tenancy Region:" $OCICLI_USERREGION 2>&1 | tee -a $LOG
echo "" 2>&1 | tee -a $LOG
echo "`basename $0` version is:" $VERSION 2>&1 | tee -a $LOG
echo "OCI CLI version is:" $OCICLI_VER 2>&1 | tee -a $LOG
echo "PYTHON version is:" $$PYTHON_VER 2>&1 | tee -a $LOG
echo "OCI CLI User:" $OCICLI_USER 2>&1 | tee -a $LOG
echo "Unix User:" $UNIX_USER 2>&1 | tee -a $LOG
echo "Unix Hostname:" $UNIX_HOST 2>&1 | tee -a $LOG
echo "Hostname OS Version:" $OS_VER 2>&1 | tee -a $LOG
echo "" 2>&1 | tee -a $LOG

#
# Get the List of Subscribed Regions for the Tenancy
#

get_subscription_regions


#
# Get the List of Accessible Compartments
# Generate Compartment Name Mapping to OCID
# Note:
# get_compartments module should ALWAYS be run
# as other modules may depend on its output.
#

get_compartments



#
## Parse Options Provided Command Line for Report Modules and Config Files to be generated
# Valid Options are:
#
# -c run report and get configs for OCI Compute Instances
# -d run report and get configs for OCI Database Systems
# -n run report and get configs for select OCI Network Objects
# -s run report and get configs for select OCI Storage Objects
# -a run report and get configs for OCI Objects in Tenancy
# -h print Usage Message for current options
#
#


while getopts ":cdnsah" opt; do
  case ${opt} in

	# For Compute Option:
	# Provides Compute Instance OCID Mapping to Compartment and AD
	# Generates Compute Instance Mapping to BootVol
	# Generates Compute Instance Mapping to Attached BlockVols
	# (Vol Mappings require output from get_compute_instance_map)

    c ) echo "" 2>&1 | tee -a $LOG
        echo "OCI configuration Script: `basename $0` option is COMPUTE." 2>&1 | tee -a $LOG

	get_compute_instance_map
	get_compute_instance_boot_map
	get_compute_instance_block_map
	cleanup_files

        echo "" 2>&1 | tee -a $LOG
        echo "" 2>&1 | tee -a $LOG
        echo "OCI configuration Script: `basename $0` COMPUTE OPTION on `date` in $OCICLI_USERREGION is now complete..." 2>&1 | tee -a $LOG
      ;;

	#
	# Get the List of Database Systems / Databases by Compartment
	# Generate DB Sys Mapping by Compartment to Databases
	#

    d ) echo "" 2>&1 | tee -a $LOG
        echo "OCI configuration Script: `basename $0` option is DATABASE SYSTEM." 2>&1 | tee -a $LOG

	get_dbsys_map
	cleanup_files

        echo "" 2>&1 | tee -a $LOG
        echo "" 2>&1 | tee -a $LOG
        echo "OCI configuration Script: `basename $0` DATABASE SYSTEM OPTION on `date` in $OCICLI_USERREGION is now complete..." 2>&1 | tee -a $LOG
      ;;

	#
	# Get the List of Load Balancers by Compartment
	# Generate LB Instance Mapping by Compartment to Backend Set/Backends
	# Get the List of VCNs by Compartment
	# Generate VCN Network Mapping by Compartment to Subnets and ADs
	#

    n ) echo "" 2>&1 | tee -a $LOG
        echo "OCI configuration Script: `basename $0` option is NETWORK." 2>&1 | tee -a $LOG

	get_lb_map
	get_vcn_map
	cleanup_files

        echo "" 2>&1 | tee -a $LOG
        echo "" 2>&1 | tee -a $LOG
        echo "OCI configuration Script: `basename $0` NETWORK OPTION on `date` in $OCICLI_USERREGION is now complete...." 2>&1 | tee -a $LOG
      ;;

	#
	# Get the List of FSS by Compartment
	# Generate FSS Instance Mapping to Compartment
	# Get the List of Object Storage Buckets by Compartment
	#

    s ) echo "" 2>&1 | tee -a $LOG
        echo "OCI configuration Script: `basename $0` option is STORAGE." 2>&1 | tee -a $LOG

	get_fss_map
	get_ossb_map
	cleanup_files

        echo "" 2>&1 | tee -a $LOG
        echo "" 2>&1 | tee -a $LOG
        echo "OCI configuration Script: `basename $0` STORAGE OPTION on `date` in $OCICLI_USERREGION is now complete...." 2>&1 | tee -a $LOG
      ;;
    a ) echo "" 2>&1 | tee -a $LOG
	echo "OCI configuration Script: `basename $0` option is ALL." 2>&1 | tee -a $LOG

	get_compute_instance_map
	get_compute_instance_boot_map
	get_compute_instance_block_map
	get_dbsys_map
	get_fss_map
	get_ossb_map
	get_lb_map
	get_vcn_map
	cleanup_files

        echo "" 2>&1 | tee -a $LOG
        echo "" 2>&1 | tee -a $LOG
        echo "OCI configuration Script: `basename $0` ALL OPTION on `date` in $OCICLI_USERREGION is now complete...exiting." 2>&1 | tee -a $LOG
      ;;
    h ) echo "" 2>&1 | tee -a $LOG
        usage;
        exit 1
      ;;
    * ) echo "" 2>&1 | tee -a $LOG
        usage;
        exit 1
      ;;
  esac
done

# Check if any options passed, if none, print usage

if [ $OPTIND -eq 1 ]; then

  usage;
  exit 1

fi

shift $((OPTIND -1))


echo "" 2>&1 | tee -a $LOG
echo "" 2>&1 | tee -a $LOG
echo "OCI Summary Report for $CUSTNAME in $OCICLI_USERREGION is now complete...exiting." 2>&1 | tee -a $LOG
