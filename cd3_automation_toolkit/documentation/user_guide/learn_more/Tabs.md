## Compartments Tab
Use this Tab to create compartments in the OCI tenancy. On choosing "Identity" in the SetUpOCI menu will allow to create compartments in the OCI tenancy.

Output terraform file generated:  \<outdir>/\<region>/\<prefix>_compartments.auto.tfvars where \<region> directory is the home region.

Once terraform apply is done, you can view the resources under Identity -> Compartments in OCI console.

On re-running the same option you will find the previously existing files being backed up under directory →   \<outdir>/\<region>/backup_compartments/\<Date>-\<Month>-\<Time>.

**Notes:**

Automation Tool Kit generates the TF Configuration files for all the compartments in the tenancy. If some compartment was already existing in OCI then on Terraform Apply, the user will see logs which indicate creation of that compartment - this can be ignored as Terraform will only modify the existing Compartments (with additional information, if there are any eg description) and not create a new/duplicate one.
If you have been given admin access to only one compartment in a tenancy (rather than full admin access) - then you should create the sub-compartments from OCI console, run fetch_compartments_to_variablesTF.py script and then proceed with execution of further objects.

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

