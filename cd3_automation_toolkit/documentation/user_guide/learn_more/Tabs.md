## Compartments Tab
Use this Tab to create compartments in the OCI tenancy. On choosing "Identity" in the SetUpOCI menu will allow to create compartments in the OCI tenancy.

Output terraform file generated:  \<outdir>/\<region>/\<prefix>_compartments.auto.tfvars where \<region> directory is the home region.

Once terraform apply is done, you can view the resources under Identity -> Compartments in OCI console.

On re-running the same option you will find the previously existing files being backed up under directory →   \<outdir>/\<region>/backup_compartments/\<Date>-\<Month>-\<Time>.

**NOTE -**
<blockquote>
- Automation Tool Kit generates the TF Configuration files for all the compartments in the tenancy. 
  If some compartment was already existing in OCI then on Terraform Apply, the user will see logs which indicate creation of that compartment - this can be ignored as Terraform will only modify the existing Compartments (with additional information, if there are any eg description) and not create a new/duplicate one.<br>
<br> - Terraform destroy on compartments or removing the compartments details from <b><i>*_compartments.auto.tfvars</i></b> will not delete them from OCI Console by default. Inorder to destroy them from OCI either - 
 <br> <ul>
  <li>Add an additional column - <b><i>enable_delete</i></b> to Compartments Tab of CD3 Excel sheet with the value <b>"true"</b> for the compartments that needs to be deleted on terraform destroy. Execute the toolkit menu option to Create Compartments.</li>
  <br>(OR)<br><br>
  <li>Add <b><i>enable_delete = true</i></b> parameter to each of the compartment that needs to be deleted in <b><i>*_compartments.auto.tfvars</i></b></li>
  </ul>
</blockquote>

## Groups Tab

Use this Tab to create compartments in the OCI tenancy. On choosing "Identity" in the SetUpOCI menu will allow to create groups in the OCI tenancy.

Automation toolkit supports creation and export of Dynamic Groups as well.
  
Output terraform file generated:  \<outdir>/\<region>/\<prefix>_groups.auto.tfvars under where \<region> directory is the home region.

Once terraform apply is done, you can view the resources under Identity -> Groups in OCI console.

On re-running the same option you will find the previously existing files being backed up under directory →   \<outdir>/\<region>/backup_groups/\<Date>-\<Month>-\<Time>.

## Policies Tab

Use this Tab to create compartments in the OCI tenancy. On choosing "Identity" in the SetUpOCI menu will allow to create policies in the OCI tenancy.

Output terraform files generated: \<outdir>/\<region>/\<prefix>_policies.auto.tfvars where \<region> directory is the home region.

Once terraform apply is done, you can view the resources under Identity -> Policies in OCI console.

On re-running the same option you will find the previously existing files being backed up under directory →   \<outdir>/\<region>/backup_policies/\<Date>-\<Month>-\<Time>.

## Tags Tab

Use this Tab to create tags - Namespaces, Key-Value pairs, Default and Cost Tracking Tags. On choosing "Tags" in the SetUpOCI menu will allow to create Tags in the OCI tenancy.
  
Once this is complete you will find the generated output terraform files in location :

---> \<outdir>/\<region>/\<prefix>_tags-defaults.auto.tfvars 

---> \<outdir>/\<region>/\<prefix>_tags-namespaces.auto.tfvars 

---> \<outdir>/\<region>/\<prefix>_tags-keys.auto.tfvars  

under \<region> directory.

Once terraform apply is done, you can view the resources under Governance -> Tag Namespaces for the region.

On re-running the same option you will find the previously existing files being backed up under directory →   \<outdir>/\<region>/backup_Tagging/\<Date>-\<Month>-\<Time>.

## Create Network

**Pre-requisite:**

Run the script **fetch_compartments_to_variablesTF.py**
Execute CD3 Validator, to avoid any errors during the creation of VCN objects. (Check out Support for CD3 Validator for the details)

<ins>Fetch Compartments to Varaibles TF file:</ins>

This script will fetch OCIDs of all compartments that exist in the tenancy and place them in variables_\<region>.tf directory.

Command used to execute from OCSWork VM: (Fetch Compartments) - python fetch_compartments_to_variablesTF.py /cd3user/tenancies/<customer_name>/terraform_files

For other workstations - example: laptop, specify the path of 'outdir' and path of 'config' file for Python OCI - python fetch_compartments_to_variablesTF.py \<path to outdir> --configFileName \<path to config file>

To create network objects like VCN, subnets etc in OCI; VCNs, VCN Info, Subnets and DHCP tabs of CD3 are required to be configured.

## a. VCNs Tab

**Note:**

1. Please mention value for column 'Hub/Spoke/Peer/None' in VCNs tab as None for utilizing DRGv2 functionality (where DRG is directly attached to all VCNs and hub/spoke model is not required)

2. Declare the DRG for the VCN in 'DRG Required' column of VCNs tab and then declare the attachment in DRGs tab also. Toolkit verifies the declaration in VCNs tab and then creates the DRG while reading the DRGs tab.

## b. DRGs Tab

**Note:**

1. Only VCN attachements are supported via CD3 as of now for DRGv2. Please create attachments for RPC, VC and IPSec via OCI console.
2. Network export will also export only VCN attachments to CD3 excel sheet as of now.
3. You can create a Route Table for DRG which is not attached to any attachment by keeping 'Attached To' column in DRGs tab empty.
4. You can create an Import Route Distribution which is attached to some Route Table in DRG.

## c. VCN Info tab

This is an important tab and contains general information about networking to be setup.

## d. DHCP tab
This contains information about DHCP options to be created for each VCN.

## e. Subnets tab

**Notes:**

1. Name of the VCNs, subnets etc are all case sensitive. Specify the same names in all required places. Avoid trailing spaces for a resource Name.

2. Default Route Rules created are :

a.   Based on the values entered in columns  ‘configure SGW route’, ‘configure NGW route’, ‘configure IGW route’, 'configure Onprem route' and 'configure VCNPeering route'  in Subnets sheet; if the value entered is ‘y’, it will create a route for the object in that subnet
      eg if ‘configure IGW’ in Subnets sheet is ‘y’ then it will read parameter ‘igw_destination’ in VCN Info tab and create a rule in the subnet with destination object as IGW of the VCN and destination CIDR as value of igw_destnation field.
      If comma separated values are entered in the igw_destination in VCN Info tab then the tool creates route rule for each destination cidr for IGW in that subnet.
      Tool works similarly for ‘configure NGW’ in Subnets tab and ‘ngw_destination’ in VCN Info tab. For SGW, route rule is added either 'all services' or object storage in that region.

b.  For a hub spoke model, tool automatically creates route tables attached with the DRG and each LPG in the hub VCN peered with spoke VCN.
     ‘onprem_destinations’ in VCN Info tab specifies the On Prem Network CIDRs.

3. The below Default Security Rules are created:

a. Egress rule allowing all protocols for 0.0.0.0/0 is opened.

b. Ingress rule allowing all protocols for subnet CIDR is opened. This is to allow communication between VMs with in the same subnet.

4. Default Security List of the VCN is attached to the subnet if ‘add_default_seclist’ parameter in Subnets tab is set to ‘y’.

5. Components- IGW, NGW, DRG, SGW and LPGs are created in same compartment as the VCN.

6. VCN names need to be unique across the region. Automation ToolKit does not support duplicate values at the moment.
      

Output terraform files are generated under \<outdir>/\<region> directory.

Once terraform apply is done, you can view the resources under Networking -> Virtual Cloud Networks in OCI console.

Output files generated:

| File name | Description |
| --- | --- |
| \<prefix>_major-objects.auto.tfvars | Contains TF for all VCNs and components- IGW, NGW, SGW, DRG, LPGs.|
| \<prefix>_custom-dhcp.auto.tfvars	|Contains TF for all DHCP options for all VCNs.|
| <br>\<prefix>_routetables.auto.tfvars<br>\<prefix>_default-routetables.auto.tfvars<br>\<prefix>_drg-routetables.auto.tfvars<br>\<prefix>_drg-distributions.auto.tfvars<br>\<prefix>_drg-data.auto.tfvars</br></br></br></br></br> | <br>Separate file for each route table name is created.<br>Contains TF for route rules in each route table.</br></br> |
| <br>\<prefix>_seclists.auto.tfvars<br>\<prefix>_default-seclists.auto.tfvars</br></br> | <br>Separate file for each security list name is created.<br>Contains TF for security rules in each security list. |
|\<prefix>_subnets.auto.tfvars|	Contains TF for all subnets for all VCNs.|
|\<prefix>_default-dhcp.auto.tfvars	|Contains TF for default DHCP options of each VCN in each region |
|<br>\<prefix>_nsgs.auto.tfvars<br>\<prefix>_nsg-rules.auto.tfvars</br></br>| Contains TF for NSGs in each region |


## Export and Modify Rules

You can export existing security rules and route rules in OCI. On choosing **"Network"** in the SetUpOCI menu and **"Export existing secrules and RouteRules to CD3"** and **"Export existing DRG Routerules to CD3**" submenu will allow to export existing security and route rules.

On choosing this option, you will get a prompt to enter the Compartment Name for which you want to export the rules. When left blank, rules will be exported for all Compartments in the tenancy.

Exported rules are written to 'SecRulesinOCI', ‘RouteRulesinOCI’ and 'DRGRouteRulesinOCI' tab of the cd3 excel. 

**DO NOT** open your CD3 file during the export process.

This option is useful when you want to present the CD3 to the customer as the Actual Representation of OCI console.(i.e provide the contents of OCI in the CD3 excel)

**<ins>Modify Rules</ins>**

On choosing **"Network"** in the SetUpOCI menu and **"Modify SecRules"** and **"modify RouteRules"** and **"Modify DRG RouteRules"** submenu will allow to modify existing route rules and security rules in OCI tenancy.

**SecRulesinOCI tab** – The tool reads this sheet and deletes(backs up to the backup directory) all existing security rules in OCI and replace them with the contents of this Tab.

**RouteRulesinOCI tab** – The tool reads this sheet and deletes(backs up to the backup directory) all existing route rules in OCI and replace them with the contents of this Tab.

**DRGRouteRulesinOCI tab** – The tool reads this sheet and deletes(backs up to the backup directory) all existing DRG route rules in OCI and replace them with the contents of this Tab.


## Modify Network

<ins>Modify Network</ins>

Using this option, one can add/remove/update a subnet, a DHCP option or a VCN or DRG to your existing network.

Use this option if you have modified any route rules or security rules else you can still continue using Create Network option for any changes.

On choosing **"Network"** in the SetUpOCI menu and **"Modify Network - Add/Remove/Modify any network object; updates TF files with changes; this option should be used after modification have been done to SecRules or RouteRules"** submenu allow to modify network objects in OCI Tenancy.

## DedicatedVMHosts Tab

Fill up the details in **'DedicatedVMHosts'** sheet and follow the options below.

On choosing **"Compute"** in the SetUpOCI menu and **"Add/Modify/Delete Dedicated VM Hosts"** submenu will allow to launch your VM on a dedicated host.



Output terraform file generated: \<outdir>/\<region>/dedicated_vm_hosts.tf under \<region> directory.

Once terraform apply is done, you can view the resources under Compute -> Dedicated Virtual Machine Hosts for the region.

If you want to update or add new dedicated VM hosts, update the 'DedicatedVMHosts' tab in cd3 and rerun using setUpOCI.

On re-running the same option you will find the previously existing files being backed up under directory →   \<outdir>/\<region>/backup_dedicatedvmhosts/\<Date>-\<Month>-\<Time>.

## Instances Tab


<ins>CD3 Tab Specifications:</ins>

1. "Display Name" column is case sensitive. Specified value will be the display name of Instance in OCI console.

2. Optional columns can also be left blank - like Fault Domain, IP Address. They will take default values when left empty.

3. Leave columns: Backup Policy, NSGs, DedicatedVMHost blank if instance doesn't need to be part of any of these. Instances can be made a part of Backup Policy and NSGs later by choosing appropriate option in setUpOCI menu.

4. For column SSH Key Var Name accepts SSH key value directly or the name of variable decalred in variables.tf containing the key value. Make sure to have an entry in variables_\<region>.tf file with the name you enter in SSH Key Var Name field of the Excel sheet and put the value as SSK key value.
Ex: If you enter the SSH Key Var Name as ocs_public, make an entry in variables_\<region>.tf file as shown below:

  
variable "\<value entered in SSH Key Var Name field of Excel sheet>"; here it will be as below:
  
    variable  'ocs_public'  {
    default = "<paste your public key here>"
    }

The value accepts multiple keys seperated by \n


6. Enter subnet name column value as: \<vcn-name>_\<subnet-name>

7. Source Details column of the excel sheet accepts both image and boot volume as the source for instance to be launched.
Format - 

image::\<variable containing ocid of image> or
bootVolume::\<variable containing ocid of boot volume>

Make sure to have an entry in variables_\<region>.tf file for the value you enter in Source Details field of the Excel sheet.
Ex: If you enter the Source Details as image::Linux, make an entry in variables_\<region>.tf file as shown below:

variable "\<value entered in Source Details field of Excel sheet>"; here it will be:

    variable 'Linux' {
    default = "<ocid of the image/bootVolume to launch the instance from>"
    }

8. Mention shape to be used in Shape column of the excel sheet. If Flex shape is to be used format is:

shape::ocpus

eg: VM.Standard.E3.Flex::5


9. Custom Policy Compartment Name : Specify the compartment name where the Custom Policy is created.

10. While export of instances, it will fetch details for only the primary VNIC attached to the instance


On choosing **"Compute"** in the SetUpOCI menu and **"Add/Modify/Delete Instances/Boot Backup Policy"** submenu will allow to launch your VM on OCI tenancy.



Output terraform file generated: \<outdir>/\<region>/\<prefix>_instances.auto.tfvars and \<outdir>/\<region>/\<prefix>_boot-backup-policy.auto.tfvars  under  appropriate \<region> directory.

Once the terraform apply is complete, view the resources under Compute -> Instances for the region.

On re-running the same option you will find the previously existing files being backed up under directory →   \<outdir>/\<region>/backup_instances/\<Date>-\<Month>-\<Time>.

## BlocksVolumes Tab

This tab in cd3 excel sheet is used when you need to create block volumes and attach the same to the instances in the OCI tenancy. 

Automation Tool Kit does not support sharing of volumes at the moment. While export of block volumes, if the block volume is attached to multiple instances, it will just fetch details about one attachment.

On choosing **"Storage"** in the SetUpOCI menu and **"Add/Modify/Delete Block Storage/Block Backup Policy"** submenu will allow to create block volumes in OCI Tenancy.

On completion of execution, you will be able to find the output terraform file generated at : 

-→  \<outdir>/\<region>/\<prefix>_blockvolume.auto.tfvars

-→  \<outdir>/\<region>/\<prefix>_block-backup-policy.auto.tfvars  under  appropriate \<region> directory.

Once terraform apply is done, you can view the resources under Block Storage -> Block Volumes  in OCI console.

On re-running the option to create Block Volumes you will find the previously existing files being backed up under directory:

  \<outdir>/\<region>/backup_blockvolumes/\<Date>-\<Month>-\<Time>   and   \<outdir>/\<region>/backup_BlockBackupPolicy/\<Date>-\<Month>-\<Time>.


## FSS Tab

On choosing **"Storage"** in the SetUpOCI menu and **"Add/Modify/Delete File Storage"** submenu will allow to create file system storage on OCI tenancy.

Note:   Freeform and Defined Tags - If specified, applies to FSS object only and not to other components like Mount Target.

Once this is complete you will find the generated output terraform files in location :

---> \<outdir>/\<region>/FSS.tf

under \<region> directory.

Once terraform apply is done, you can view the resources under File Storage → File Systems for the region.

On re-running the same option you will find the previously existing files being backed up under directory →   \<outdir>/\<region>/backup_FSS/\<Date>-\<Month>-\<Time>.


## Load Balancers

Automation Tool Kit allows you to create Load Balancers with all the features supported by Oracle. Components that you can create using the Tool Kit includes:

| Resource | Tab Name |
|---|---|
|Load Balancers<br>Hostnames<br>Cipher Suites<br>Certificates| LB-Hostname-Certs |
|Backend Sets and Backend Servers|BackendSet-BackendServer|
|Rule Set|RuleSet|
|Path Route Set|PathRouteSet|
|Listeners|LB-Listeners|

NOTE : While exporting and synching the tfstate file for LBR objects, the user may be notified that a few components will be modified on apply. In such scenarios, add the attributes that the Terraform notifies to be changed to the appropriate CD3 Tab of Load Balancer and Jinja2 Templates (as a non-default attribute) and re-run the export.

On choosing "Load Balancers" in the SetUpOCI menu will allow to create load balancers in OCI tenancy.

**Load Balancers, Hostnames , Certificates and Cipher Suites:**

Use the tab LB-Hostname-Certs of CD3 Excel to create the following components of Load Balancer:

Load Balancers
Hostnames
Cipher Suites
Certificates

Certificates, Hostnames and Cipher Suites are optional. Leave the related columns empty if they are not required.

## LB-Hostname-Certs

Once this is complete you will find the generated output terraform files in location :

---> \<outdir>/\<region>/\<prefix>_lb-hostname-certs.auto.tfvars

under \<region> directory.

Once terraform apply is done, you can view the resources under Networking → Load Balancers for the region.

On re-running the same option you will find the previously existing files being backed up under directory →   \<outdir>/\<region>/backup_LB-Hostname-Certs/\<Date>-\<Month>-\<Time>.
