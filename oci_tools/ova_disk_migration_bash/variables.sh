#!/bin/bash
#===============================================================================
#
#          FILE:  variables.sh
# 
#         USAGE:  ./variables.sh 
# 
#   DESCRIPTION:  
# 
#       OPTIONS:  ---
#  REQUIREMENTS:  ---
#          BUGS:  ---
#         NOTES:  ---
#        AUTHOR:   (), 
#       COMPANY:  
#       VERSION:  1.0
#       CREATED:  11/15/2019 07:34:50 AM GMT
#      REVISION:  ---

#-------------------------------------------------------------------------------
#   AD VARIABLE PREPARATION
#-------------------------------------------------------------------------------
ad_list=`oci iam availability-domain list --all`
adstring="variable "\"ads\"" {\n\tdefault = {\n\t\t"
echo -e "### ADs ###" > variables.tf
echo -e  "$adstring" >> variables.tf
ad_num=1
while read l ; do
	adname=`echo $l | jq '.name' -r`
	echo -e "\t\tad"$ad_num" = \"${adname}\"" >> variables.tf
	ad_num=$((ad_num + 1))
done< <(jq -c '.data[]' <<< "${ad_list}")

echo -e "\t\t}\n\t}\n" >> variables.tf
#-------------------------------------------------------------------------------
#   FD VARIABLE PREPARATION
#-------------------------------------------------------------------------------
echo -e "\n### FDs ####" >> variables.tf
fdstring="variable \""fds\"" {\n\tdefault = {\n\t\tfd1 = \""FAULT-DOMAIN\-1\""\n\t\tfd2 = "\"FAULT-DOMAIN\-2\""\n\t\tfd3 = "\"FAULT-DOMAIN\-3\""\n\t\t}\n\t}"
echo -e "$fdstring\n" >> variables.tf

#-------------------------------------------------------------------------------
#   SHAPES VARIABLE PREPARATION
#-------------------------------------------------------------------------------
echo -e "\n### SHAPES ###" >> variables.tf


#===============================================================================
#   COMPARTMENT,VCN,SUBNET,NSG VARIABLE PREPARATION
#-------------------------------------------------------------------------------
echo -e "\n### COMPARTMENTS ###" >> variables.tf

comp_list=`oci iam compartment list --all --compartment-id-in-subtree true`
vcnstring="variable \"vcns\" {\n\tdefault = {\n\t\t"
subnetstring="variable \"subnets\" {\n\t\tdefault = {\n\t\t"
nsgstring="variable \"nsgs\" {\n\t\tdefault = {\n\t\t"
echo -e "variable \"compartments\" {\n\tdefault = {\n\t\t" >> variables.tf
while read i; do
        name=`echo $i | jq '.name' -r`
        id=`echo $i | jq '.id' -r`
        echo -e "\t\t${name} = \"${id}\"" >> variables.tf
	vcnlist=`oci network vcn list --all --compartment-id $id`
	while read j; do
		displayname="`echo $j | jq '."display-name"' -r`"
		vcnid=`echo $j | jq '.id' -r`
		[ -n $vcnid -o -n $displayname ] && vcnstring="$vcnstring $displayname = \"$vcnid\"\n\t\t" 
		subnetlist=`oci network subnet list --all --compartment-id $id --vcn-id $vcnid`
		while read k; do
			subnetdisplayname="`echo $k | jq '."display-name"' -r`"	
			subnetid=`echo $k | jq '.id' -r`
			[ -n $subnetid -o -n $subnetdisplayname ] && subnetstring="$subnetstring $subnetdisplayname = \"$subnetid\"\n\t\t"
		done< <(jq -c '.data[]' <<< "${subnetlist}")
	done< <(jq -c '.data[]' <<< "${vcnlist}")

	nsglist=`oci network nsg list --compartment-id $id`
	while read m; do
		nsgdisplayname="`echo $m | jq '."display-name"' -r`"
		nsgid=`echo $m | jq '.id' -r`	
		[ -n $nsgid -o -n $nsgdisplayname ] && nsgstring="$nsgstring $nsgdisplayname = \"$nsgid\"\n\t\t"
	done< <(jq -c '.data[]' <<< "${nsglist}")
	
done< <(jq -c '.data[] | select(."name" != "ManagedCompartmentForPaaS")' <<< "${comp_list}") 
echo -e "\n\t\t}\n}" >> variables.tf

echo -e "\n### VCNs ###" >> variables.tf
echo -e ""$vcnstring"\n\t\t}\n}" >> variables.tf

echo -e "\n### SUBNETS ###" >> variables.tf
echo -e "$subnetstring\n\t\t}\n}" >> variables.tf

echo -e "\n### NSGS ###" >> variables.tf
echo -e "$nsgstring\n\t\t}\n}" >> variables.tf

echo -e "variable.tf is created in `pwd`"
