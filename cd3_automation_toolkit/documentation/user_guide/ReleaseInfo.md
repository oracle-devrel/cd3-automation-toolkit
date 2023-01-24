## Release-Info

### Automation Toolkit Release v10 & Docker Image Release v6.0

#### Date - Jan 13th, 2023

This is a major release with below updates:

1. Support for new services - OKE and SCH. New tab for 'OKE' is included in CD3-CIS-template.xlsx. New tab for 'ServiceConnectors' is added to CD3-CIS-ManagementServices-template.xlsx.
2. Added the script to fetch regions subscribed to the tenancy. This will be executed automatically every time setUpOCI is executed.
3. Introduced a new option in setUpOCI menu called 'CD3 Services' to execute 'Fetch Compartments' and 'Fetch Protocols Scripts.
4. Modified the setUpOCI workflow to prompt the user to execute 'Fetch Compartments' script in case it has not been executed previously.
5. Bug fixes wrt Instances, DB Systems


### Automation Toolkit Release v9.2.1 & Docker Image Release v5.2.1

#### Date - Nov 30th, 2022

This is a minor release with below updates:

1. Sample terraform import command included as part of output tfvars file for each OCI resource managed by Toolkit.
2. Split Export of Network options to chose export of different components separately eg Major Objects, Subnets, NSGs etc.
3. Include support for Marketplace Images for Instances.
4. Few bug fixes/enhancements wrt export of Instances/NSGs, making null values for NSGs/Instances optional in tfvars

## Previous Versions released before making it available on GitHub

### Automation Toolkit Release v9.2 & Docker Image Release v5.2

#### Date - Oct 10th, 2022

This is a major release with existing services converted into terraform modules and also bug fixes.

1. Terraform modules for FSS and ADB(Modified the input sheet for ADB to include more features)
2. Included new service - Network Load Balancers
3. Enhanced Tags sheet to include Default Tags for Multiple Compartments.
4. Enhanced CD3 Validator for FSS, NSGs column for each tab.
5. Included CIS compliance checker script as part of setUpOCI Menu option
6. Cleanup of variables_<region>.tf file
7. Updated CD3 templates in example folder with latest CIS data
8. Bug fixes wrt multiple services like Instances, Notifications etc
9. Introduced documentation folder containing terraform and toolkit user guide in outdir of each customer
 
### Automation Toolkit Release v9.1 & Docker Image Release v5.1

#### Date - Jun 13th, 2022

This is a major release with existing services converted into terraform modules and also bug fixes.

1. Terraform Modules for Instances, Block Volumes, Tags, CIS features, LBaas.
2. Introduced new columns for PV encryption in Instances/Block Volumes.
3. Introduced new columns for Min/Max bandwidth for flexible shapes load balancers, reserved public IP. Support for OCI certificate management certificates for Listeners, BackendSets.
4. Removed support for subnet_name_attach_cidr parameter from CD3 excel's 'VCN Info' sheet.
5. Bug fixes

### Automation Toolkit Release v9.0.2 & Docker Image Release v5.0.2

#### Date - April 29, 2022

This is a minor release with bug fixes related to Networking and Identity Policies.


### Automation Toolkit Release v9.0.1 & Docker Image Release v5.0.1

#### Date - April 9, 2022

This is a minor release.

1. Bug fix for data after END tag in DRGRouteRulesinOCI sheet.
2. Bug fix for tenancies having both DRGv1 and DRGv2
3. Bug fix for VCN Flow Log output
4. Bug fix for NSG ICMP rules not having only ICMP type
5. Modified output template files to adjust the spacing


### Automation Toolkit Release v9.0 & Docker Image Release v5.0

#### Date - March 21, 2022

This is a major release.

1. Terraform output files in modules format for IAM, Network, Database(DBSystems and Exa) and Management Services(Events, Notifications) components.
2. Added support for Alarms with output files as terraform modules.
3. Updated the excel sheet templates as per latest CIS compliance for IAM compartments, groups, policies, events, notifications and alarms.
4. Added support for multiple VCN CIDRs in VCNs sheet.
5. Added support for same VCN names across regions.
6. Added export for Dedicated VM Hosts and Database tabs as terraform flat files
7. Modified Database tabs to include new features.
8. Restructured the code directories and setUpOCI menu options.
9. Added drop downs in the excel sheet columns to make excel filling easier.
10. Updated OCI_regions to include all regions
11. Deprecation of OCSWorkVM.

### Automation Toolkit Release v8.0.3 & Docker Image Release v4.0.3

#### Date - Nov 26 , 2021

This is a minor release.

1. Bug fix for Availability Domain values while export of block volumes, FSS
2. Bug fix for DRG Route Rules export error - 'Too Many requests'
3. Bug fix for export of Tags having spaces in the values

### Automation Toolkit Release v8.0.2 & Docker Image Release v4.0.2

#### Date - Sep 30 , 2021

This is a minor release.

1. Bug fix for End Tag in NSGs tab
2. Bug fix for export of LBR hosted in two subnets in different compartments.
3. Bug fix for terraform variable name for route table names
4. Allow case insensitive for Security Rule Types/Protocols
5. Allow flexible shapes in LBR CD3

### Automation Toolkit Release v8.0 & Docker Image Release v4.0

#### Date - Jul 27 , 2021

This is a major release.

1. Support for DRGv2 - added 2 new sheets to CD3: DRGs and DRGRouteRulesinOCI
2. Backward compatible to support DRGv1
3. Updated CD3 Validator to include validation for DRGs tab
4. Optimized the code for export of objects
5. Bug fix for export of SecRules and RouteRules for all compartments
6. Updated the toolkit to support user access to a single compartment by allowing creation of sub-compartments under that only.
7. Included export of additional objects for Instances and Block Volumes
8. CD3 templates are compliant to latest CIS Landing Zone
9. Upgrade terraform version to 1.0.0
10. Please note that since this release is upgrading the terraform version so previous version's terraform state will not be compatible with the new tf files. Recommendation is to keep using old code setup for eixsting customers and new code setup for new customers. Or else export everything using new code and then import into the new terraform state

### Automation Toolkit Release v7.2 & Docker Image Release v3.2

#### Date - May 26, 2021

This is a minor release.

1. Bug fix for export of policies having newline in description eg for policies added automatically for streaming
2. Launch Linux 7.9 as OCS VM since 7.8 is not searcheable now and enable yum repos
3. Change os.cmd to function calls for SetUPOCI
4. Include CIS Features to enable cloud-guard, OSS, VCN Flow Logging
5. CD3 Validator for Identity, Networking, Instances, Block Volumes
6. Accept key value along with key var name in Instances Sheet
7. Updated CD3 Templates as per CIS

### Release v7.1.2

#### Date - Apr 12, 2021

This is a minor release.

1. Bug fix for CD3 LBR - Certs/PEM keys copied to outdir- this helps to resolve the path issue while RM upload. Export LBR also modified
2. Bug fix for Instance Export - included root compartment, AD issue and Boot Volume not found issue.
3. Removed installation of Development Tools from shell script on OCSVM.
4. Added CD3 validation for DNS Label length for VCN and Subnets

### Release v7.1.1

#### This is a minor release.

1. Bug fix for CD3 Network components validator - included check for invalid CIDR range having host bits set
2. Bug fix for Security List Rules - allow all ports for TCP/UDP
3. Removed unwanted packages from shell script - cfgparse, ipaddr, pycrypto, gcc

### Release v7.1

Date - Feb 12, 2021

Below are the highlights of this release:

1. Introduced new option in setUpOCI Menu to create RM Stack

   &nbsp; &nbsp;* When this option is chosen, it will ask for the compartment where the RM stack has to be created.
   
   &nbsp; &nbsp;* It will create stacks in the specified compartment in the home region
   
   &nbsp; &nbsp;* RM Stack names: ocswork-<prefix>-<region> where <prefix> is the prefix mentioned in setUpOCI.properties file and <region> is the regions tenancy is subscribed to.
  
   &nbsp; &nbsp;* Uploads all files in outdir to RM Stack and also uploads the tfstate file if existing.
  
   &nbsp; &nbsp;* Uses same RM Stack for multiple executions.


2. Bug fix for LBR Backend sets to allow same backend servers with different ports.

3. OCSWork VM launched with TF version 0.13.4 in sync with Resource Manager in OCI

4. CD3 templates as per CIS Standards
  
   
### Release v7.0.1

This is a minor release.

xrld package's latest release was not compatible and giving below issue with CD3:
  
<img width="452" alt="image" src="https://user-images.githubusercontent.com/122371432/214040681-4a9154ec-4f93-4786-808c-ad69189a0797.png">

It has been fixed by installing lower version of xlrd package.

pip3 install xlrd==1.2.0

It has been corrected and pushed to the master branch.
    
### Major Release v7.0

#### Date - Oct 9, 2020

1. Support for additional properties for OCI objects using Jinja2 templates
2. Support for configuring Events and Notifications
3. Support for export of Instances, block volumes, Tags, Events and Notifications etc to CD3
4. Updated Terraform Configuration Files to support the Latest Terraform Version
5. Support for Resource Manager
6. Support to create and export Dynamic Groups
7. Support to create and export Cost Tracking and Default Tags
8. Support to create and export LBR Components- Cipher Suites, Rule Set and Path Route Set
9. Support to attach or export 'Custom Backup Policy Attachments' to Block and Boot Volumes
  
### Release v6.1.1

creatOCSWork.py picks up latest Linux OCID and launches the OCSWork VM. However Linux 8 does not support many packages required by automation toolkit.

Hence modified the code to launch Linux 7.8 incase **ocs_vm_source_image_ocid** is left empty in ocswork.properties.
 
### Release v6.1

#### Date - July 31, 2020

Below are the highlights of this release:

1. Addition of Description field for Security Rules and Route Rules. Keep using same CD3 but just add new column 'RuleDescription' at the end of both the sheets - SecRulesinOCI and RouteRulesinOCI
2. New text files - OCI_Regions and OCI_Protocols have been introduced. If any new region gets supported by OCI, it can be added in OCI_Regions file. Similarly Protocol and its number mapping has been defined in OCI_Protocols file which will be used by Security Rules as well as NSG Rules.
3. Automation Toolkit will now support duplicate compartment names like OCI does. Please refer to CD3-template.xlsx under example folder for sample data.
4. Extra properties specific to OCItoOCI project have been removed from ocswork.properties and a new file ocswork_ocic.properties has been added to accomodate that.
5. Support for multiple OCSWork VMs via separate config_for_delete files. A new input parameter has been added to ocswork.properties file.
6. Support for Reserved Public IP for OCSWork VM. Reserved public IP will be assigned to OCSWork VM which you cna chose to retain also while destroying OCSWork VM.
7. 
  &nbsp; &nbsp;&nbsp; &nbsp; a. Regions property has been removed and now tenancy's subscribed regions will be fetched using API and terraform directories would &nbsp; &nbsp; &nbsp; &nbsp;&nbsp; &nbsp; be created based on that. It would be good to subscribe tenancy to all required regions before setting up OCS Work VM or else &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;create the region directory manually.
  
  &nbsp; &nbsp; &nbsp; &nbsp;b. Regions property has been removed from VCN Info tab of CD3 as well.
  
8. CD3 Validator has been introduced. This will validate Networking tabs as of now. It will check for any Null Values, CIDR overlaps etc. 
9. Support for Flex shapes for Instances. Please refer to CD3-template.xlsx under example folder for sample input data.
10. Instead of LinuxLatest and WindowsLatest, OS value in CD3 template has been changed to Linux and Windows respectively. Variable names in variables_<region>.tf has been changed accordingly. Support for LinuxLatest and WindowsLatest templates for instance will be deprecated from next release.
11. Support for Multiple Listeners for LBRs. Add new column 'ListenerName' in the CD3 sheet. Please refer to CD3-template.xlsx under example folder for sample input data.
12. Support for Multiple export options for FSS. Please refer to CD3-template.xlsx under example folder for sample input data.
13. Support for NSG export/import. Export process for non-greenfield tenancies will support export of NSGs and their import into terraform.
14. GIT repo has been moved to OCI. SSH key needs to be setup for access to the repo.
Private key is copied over to /root/.ssh folder. It is up to the developers if they want to keep the private key there for any future GIT updates or if they want to remove the key for security reasons.
  
### Release v6.0.1

#### Date - Mar 23, 2020

There was a bug in v6.0 where TF for Instances, FSS, LBR etc was not getting correct subnet name as created for subnets using NEtworking.

It has been corrected and pushed to the master branch.

### Major Release v6.0

Below are the highlights of this release:

1. Support for Non Green Field Tenancies. 
2. Removed common_seclist_name and seclist_per_subnet columns from Subnets Tab. Specify security lists to be created for a subnet as comma separated in seclist_names column.
3. If DNS doesn't need to be enabled for a VCN or subnet, specify 'n' in dns_label column for that VCN or Subnet.
4. Specify 'n' for route_table_name or seclist_names in Subnets tab if only Default Route Table or Default Secuirty List of VCN needs to be attached to the subnet.
5. When you are running Modify Network, if there are any route tables or security lists which are not attached to any subnet or DRG or LPG then it will display the names in output like below:
  
**ATTENTION!!! Below RouteTables are not attached to any subnet or DRG and LPG; If you want to delete any of them, remove the TF file!!!**

**ATTENTION!!! Below SecLists are not attached to any subnet; If you want to delete any of them, remove the TF file!!!**

### Release v5.0.1

There was a bug in LPGs creation/peering. Corrected that and pushed as v5.0.1

### Major Release v5.0

#### Date - Feb 7, 2020

It has many new enhancements and features added to it.

Detailed explanation about CD3 excel is at: CD3 Excel release v5.0

Below are the highlights:

1. yum utility won't break on OCS Work VM. Please use python setUpOCI.py <setUpOCI.properties> cmd and python fetch_compartments_to_variablesTF.py <outdir> cmd to execute automation.
2. Export of rules after network creation is a mandatory step. Single sheet- 'SecRulesinOCI' and 'RouteRulesinOCI' would be used to manage rules in OCI.
3. Color Coding has been added to the exported rules.
4. Support for specifying LPG names has been included. 
  
&nbsp; &nbsp; &nbsp; &nbsp; Format to specify LPG names:
  
&nbsp; &nbsp; &nbsp; &nbsp; specify either y (like for other components) - this will give default name to the LPG whch is <vcn_name>_lpg<counter> eg ProdVCN_lpg0
 or the &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; name that you want to give to the LPG.
  
5. Peering section has been removed and merged in VCNs tab. Format for specifying peering in hub_spoke_peer_none column:
  
&nbsp; &nbsp; &nbsp; &nbsp;specify hub in the column for the VCN you want to mark as hub
  
&nbsp; &nbsp; &nbsp; &nbsp;specify spoke:<hub_vcn_name> if you want to mark a VCN as spoke to hub VCN
  
&nbsp; &nbsp; &nbsp; &nbsp;specify peer:<vcn_name> if you want to establish normal peering between 2 VCNs
  
&nbsp; &nbsp; &nbsp; &nbsp;specify none if the VCN is a normal standalone VCN
  
6. you can specify SGW target for route rules in OCI. specify as either object_storage or all_services
  
When VCNs are specified in hub-spoke model, Route Tables associated with DRG and LPG get created automatically.
Inter subnet communication and egress communication from all subnets is opened via SecRules.
Initial Subnet Route rules are controlled by flags for each target in Subnets Tab.
If any change is required to be done in default sec rules or route rules, they can be modified via cd3 after exporting them.

CSV support for this version is still under progress.
  
### Major Release v4.0

> **Note** 
 >This version would require you to change your excel file and use the latest one since there is a column addition in the existing sheet.

1. Added support to add a common security List across subnets apart from just Default Security List. This is done by adding a new column in Subnets tab "common_seclist_name" which specifies name of common seclist to be created and used for each subnet
&nbsp; &nbsp;  If left blank for a particular subnet that means the common seclist doesnt not need to be assigned to that subnet.
2. Modified output files created for routes. Earlier tool used to create one TF file for all route tables. Now it would generate separate file for each Route Table like it does for Security List.
3. Introduced option to create new VCN under Update Network
4. Added Default DHCP options also to TF like for Default Security List
5. Added support to include Description for a rule in NSGs. Added new column for this
6. Modified DB Systems creation code. Separated tabs for DB system - VM, BM and Exa
7. Fixed some minor issues with existing code

