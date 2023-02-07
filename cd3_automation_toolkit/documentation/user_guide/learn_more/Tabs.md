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

Use this Tab to create groups in the OCI tenancy. On choosing "Identity" in the SetUpOCI menu will allow to create groups in the OCI tenancy.

Automation toolkit supports creation and export of Dynamic Groups as well.
  
Output terraform file generated:  \<outdir>/\<region>/\<prefix>_groups.auto.tfvars under where \<region> directory is the home region.

Once terraform apply is done, you can view the resources under Identity -> Groups in OCI console.

On re-running the same option you will find the previously existing files being backed up under directory →   \<outdir>/\<region>/backup_groups/\<Date>-\<Month>-\<Time>.

## Policies Tab

Use this Tab to create policies in the OCI tenancy. On choosing "Identity" in the SetUpOCI menu will allow to create policies in the OCI tenancy.

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

   a. Based on the values entered in columns  ‘configure SGW route’, ‘configure NGW route’, ‘configure IGW route’, 'configure Onprem route' and 'configure VCNPeering route'  in Subnets sheet; if the value entered is ‘y’, it will create a route for the object in that subnet eg if ‘configure IGW’ in Subnets sheet is ‘y’ then it will read parameter ‘igw_destination’ in VCN Info tab and create a rule in the subnet with destination object as IGW of the VCN and destination CIDR as value of igw_destnation field. If comma separated values are entered in the igw_destination in VCN Info tab then the tool creates route rule for each destination cidr for IGW in that subnet.Tool works similarly for ‘configure NGW’ in Subnets tab and ‘ngw_destination’ in VCN Info tab. For SGW, route rule is added either 'all services' or object storage in that region.

   b.  For a hub spoke model, tool automatically creates route tables attached with the DRG and each LPG in the hub VCN peered with spoke VCN.
     ‘onprem_destinations’ in VCN Info tab specifies the On Prem Network CIDRs.

3. The below Default Security Rules are created:

   a.  Egress rule allowing all protocols for 0.0.0.0/0 is opened.

   b.  Ingress rule allowing all protocols for subnet CIDR is opened. This is to allow communication between VMs with in the same subnet.

4. Default Security List of the VCN is attached to the subnet if ‘add_default_seclist’ parameter in Subnets tab is set to ‘y’.

5. Components- IGW, NGW, DRG, SGW, LPGs and NSGs are created in same compartment as the VCN.

6. VCN names need to be unique for the same region. Automation ToolKit does not support duplicate values at the moment. However you can have same VCN names across different regions.
      

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

## DedicatedVMHosts Tab

Fill up the details in **'DedicatedVMHosts'** sheet and follow the options below.

On choosing **"Compute"** in the SetUpOCI menu and **"Add/Modify/Delete Dedicated VM Hosts"** submenu will allow to launch your VM on a dedicated host.



Output terraform file generated: <outdir>\<region>\<prefix>_dedicatedvmhosts.auto.tfvars.

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

On choosing **"Storage"** in the SetUpOCI menu and **"Add/Modify/Delete Block Volumes/Block Backup Policy"** submenu will allow to create block volumes in OCI Tenancy.

On completion of execution, you will be able to find the output terraform file generated at : 

-→  \<outdir>/\<region>/\<prefix>_blockvolumes.auto.tfvars

-→  \<outdir>/\<region>/\<prefix>_block-backup-policy.auto.tfvars  under  appropriate \<region> directory.

Once terraform apply is done, you can view the resources under Block Storage -> Block Volumes  in OCI console.

On re-running the option to create Block Volumes you will find the previously existing files being backed up under directory:

  \<outdir>/\<region>/backup_blockvolumes/\<Date>-\<Month>-\<Time>   and   \<outdir>/\<region>/backup_BlockBackupPolicy/\<Date>-\<Month>-\<Time>.


## FSS Tab

On choosing **"Storage"** in the SetUpOCI menu and **"Add/Modify/Delete File Systems"** submenu will allow to create file system storage on OCI tenancy.

Note:   Freeform and Defined Tags - If specified, applies to FSS object only and not to other components like Mount Target.

Once this is complete you will find the generated output terraform files in location :

---> \<outdir>/\<region>/\<prefix>_fss.auto.tfvars


Once terraform apply is done, you can view the resources under File Storage → File Systems for the region.

On re-running the same option you will find the previously existing files being backed up under directory →   \<outdir>/\<region>/backup_FSS/\<Date>-\<Month>-\<Time>.


## Load Balancers

Automation Tool Kit allows you to create Load Balancers. Components that you can create using the Tool Kit includes:

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

## LB-Hostname-Certs Tab

Once this is complete you will find the generated output terraform files in location :

---> \<outdir>/\<region>/\<prefix>_lb-hostname-certs.auto.tfvars

under \<region> directory.

Once terraform apply is done, you can view the resources under Networking → Load Balancers for the region.

On re-running the same option you will find the previously existing files being backed up under directory →   \<outdir>/\<region>/backup_LB-Hostname-Certs/\<Date>-\<Month>-\<Time>.

## Backend Set and Backend Servers Tab

Use the tab **BackendSet-BackendServer** of CD3 Excel to create the following components of Load Balancer:

- Backend Sets
- Backend Servers


Once this is complete you will find the generated output terraform files in location :

---> \<outdir>/\<region>/\<prefix>_backendset-backendserver.auto.tfvars

under \<region> directory.

Once terraform apply is done, you can view the resources under Networking→Load Balancers for the region.

On re-running the same option you will find the previously existing files being backed up under directory →   \<outdir>/\<region>/backup_BackendSet-BackendServer/\<Date>-\<Month>-\<Time>.

## RuleSet Tab

Use the tab **RuleSet** of CD3 Excel to create the following components of Load Balancer:

- Rule Sets
- RuleSet 

Once this is complete you will find the generated output terraform files in location :

---> \<outdir>/\<region>/\<prefix>_ruleset.auto.tfvars

under \<region> directory.

Once terraform apply is done, you can view the resources under Networking→Load Balancers for the region.

On re-running the same option you will find the previously existing files being backed up under directory →   \<outdir>/\<region>/backup_RuleSet/\<Date>-\<Month>-\<Time>.

## Path Route Set Tab

Use the tab **PathRouteSet** of CD3 Excel to create the following components of Load Balancer:

- Path Route Sets
- PathRouteSet:

Once this is complete you will find the generated output terraform files in location :

---> \<outdir>/\<region>/\<prefix>_pathrouteset.auto.tfvars

under \<region> directory.

Once terraform apply is done, you can view the resources under Networking→Load Balancers for the region.

On re-running the same option you will find the previously existing files being backed up under directory →   \<outdir>/\<region>/backup_PathRouteSet/\<Date>-\<Month>-\<Time>.

## LB Listeners Tab

Use the tab **LB-Listener** of CD3 Excel to create the following components of Load Balancer:

- Path Route Sets
- LB-Listener:

Once this is complete you will find the generated output terraform files in location :

---> \<outdir>/\<region>/\<prefix>_lb-listener.auto.tfvars

under \<region> directory.

Once terraform apply is done, you can view the resources under Networking→Load Balancers for the region.

On re-running the same option you will find the previously existing files being backed up under directory →   \<outdir>/\<region>/backup_LB-Listener/\<Date>-\<Month>-\<Time>.

## DBSystems-VM-BM Tab

This helps you to create DB Systems hosted on Virtual Machine and Bare Metal. This can be configured based on the shape chosen in the tab.

On choosing **"Database"** in the SetUpOCI menu and **"Add/Modify/Delete Virtual Machine or Bare Metal DB Systems"** submenu will allow to create DB Systems hosted on Virtual Machine and Bare Metal.

Output terraform file generated: 

\<outdir>/\<region>/\<prefix>_dbsystem-vm-bm.auto.tfvars under where \<region> directory is the region specified for the DB System.



Once terraform apply is done, you can view the resources under **Bare Metal, VM, and Exadata-> DB Systems** in OCI console.

On re-running the same option you will find the previously existing files being backed up under directory →   \<outdir>/\<region>/backup_dbsystems-vm-bm/\<Date>-\<Month>-\<Time>.

## ExaCS

You can create ExaCS in OCI by utilizing Exa-Infra and Exa-VM Cluster tabs in CD3 excel sheet.

On choosing **"Database"** in the SetUpOCI menu and **"Add/Modify/Delete EXA Infra and EXA VM Clusters"** submenu will allow to create ExaCS in OCI tenancy.


Output terraform file generated: 

\<outdir>/\<region>/\<prefix>_exa-infra.auto.tfvars under where \<region> directory is the region hosting the Exa Infra.

\<outdir>/\<region>/\<prefix>_exa-vmclusters.auto.tfvars under where \<region> directory is the region hosting the Exa VM Clusters.


Once terraform apply is done, you can view the resources under Bare Metal, VM, and Exadata-> Exadata Infrastructure and Exadara VM Clusters in OCI console.


On re-running the same option you will find the previously existing files being backed up under directory →   \<outdir>/\<region>/backup_exa-infra/\<Date>-\<Month>-\<Time>

and \<outdir>/\<region>/backup_exa-vmclusters/\<Date>-\<Month>-\<Time>


## ADB Tab

Use this Tab to create Autonomous Database Warehouse or Autonomous Database Transaction Processing in the OCI tenancy.

On choosing **"Database"** in the SetUpOCI menu and **"Add/Modify/Delete ADBs"** submenu will allow to create Autonomous Database Warehouse or Autonomous Database Transaction Processing in the OCI tenancy.


Output terraform file generated:  \<outdir>/\<region>/<prefix>_adb.auto.tfvars under where \<region> directory.

Once terraform apply is done, you can view the resources under **Oracle Database -> Autonomous Database** in OCI console.

On re-running the same option you will find the previously existing files being backed up under directory →   \<outdir>/\<region>/backup_adb/\<Date>-\<Month>-\<Time>

**NOTE -**
<blockquote>
  - Currently toolkit supports ADB creation in Shared Infra only,
  </blockquote>

## Notifications Tab

On choosing **"Management Services"** in the SetUpOCI menu and **"Add/Modify/Delete Notification"** and **"Add/Modify/Delete Events"** submenu will allow to manage events and notifications in OCI tenancy.

Output terraform file generated: \<outdir>/\<region>/\<customer_name>_notifications.auto.tfvars and \<outdir>/\<region>/\<customer_name>_events.auto.tfvars under \<region> directory.

Once the terraform apply is complete, view the resources under **Application Integration-> Notifications & Application Integration-> Events** for the region in OCI Console.

Further, on re-running the same option you will find the previously existing files being backed up under directory →   \<outdir>/\<region>/backup_events/\<Date>-\<Month>-\<Time> or \<outdir>/\<region>/backup_notifications/\<Date>-\<Month>-\<Time>

Note: 

- Notifications can not be configured for a particular resource OCID at the moment.
- Export of Notifications supports ONS and FAAS(will put OCID for the function in the CD3). It will skip the event export if action type is OSS.


## Alarms Tab

Please make sure to use **CD3-ManagementServices-template.xlsx** under example folder of GIT as input file for creating/exporting Alarms.

On choosing **"Management Services"** in the SetUpOCI menu and **"Add/Modify/Delete Alarms"** submenu will allow to manage alarms in OCI tenancy.

Output terraform file generated: \<outdir>/\<region>/\<customer_name>_alarms.auto.tfvars under \<region> directory.

Once the terraform apply is complete, view the resources under **Observability & Management→  Monitoring → Alarms Definition** for the region in OCI Console.

Further, on re-running the same option you will find the previously existing files being backed up under directory →   \<outdir>/\<region>/backup_alarms/\<Date>-\<Month>-\<Time>/


## ServiceConnectors Tab

Please make sure to use **CD3-ManagementServices-template.xlsx** under example folder of GIT as input file for creating/exporting Service connectors.

The service connector resources provisioning can be initiated by updating the corresponding excel sheet tab.

**CIS LZ recommends to create SCH to collect audit logs for all compartments, VCN Flow Logs and Object Storage Logs and send to a particular target that can be read by SIEM. CD3 SCH automation is aligned with CIZ LZ and allow the user to deploy/provision the recommended approach by filling in the suitable data in excel sheet.**

Output terraform file generated: \<outdir>/\<region>/\<customer_name>_serviceconnectors.auto.tfvars under \<region> directory.

Once the terraform apply is complete, view the resources under **service connectors window** for the region in OCI Console.

Further, on re-running the same option you will find the previously existing files being backed up under directory →   \<outdir>/\<region>/backup_serviceconnectors/\<Date>-\<Month>-\<Time>/

Note - 

- The service connector resources created via automation will not have the corresponding IAM policies between source and destination entities. It has to be created separately.
- The user will get an option to create the **IAM policy** when you click on **Edit** for the respective service connector provisioned through terraform like in below screenshot:

![image](https://user-images.githubusercontent.com/115973871/216242750-d84a79bf-5799-4e51-ba40-ca82a00d04aa.png)

- Also, When the target kind is **'notifications'** the value for formatted messages parameter is set to **'true'** as default. Its set to **'false'** only when the source is 'streaming'.


## OKE Tab

On choosing **"Developer Services"** in the SetUpOCI menu and **"Add/Modify/Delete OKE Cluster and Nodepools"** submenu will allow to manage oke components in OCI tenancy.

On completion of execution, you will be able to find the output terraform file generated at : 

-→  \<outdir>/\<region>/\<prefix>_oke_clusters.auto.tfvars

-→  \<outdir>/\<region>/\<prefix>_oke_nodepools.auto.tfvars  under  appropriate \<region> directory.

Once terraform apply is done, you can view the resources under **Developer Services -> Kubernetes Clusters (OKE)** for the region in OCI console.

On re-running the option to create oke clusters and noodepools you will find the previously existing files being backed up under directory:

\<outdir>/\<region>/backup_oke/\<Date>-\<Month>-\<Time>.


Notes:

- Current version of the toolkit support only single availability domain placement for the nodepool. So if a cluster is exported with nodepools having multiple placement configuration, the terraform plan will show changes similar to:

![image](https://user-images.githubusercontent.com/115973871/216243984-9379741e-6e40-45fb-a4b6-948ace78f7a4.png)

<img src=https://user-images.githubusercontent.com/115973871/216244050-88ad6797-1fe1-4198-9172-c3c3f33d810d.png width=50% height=50%>


To avoid this, an ignore statement as shown below is added to ignore any changes to the placement configuration in nodepool.

      ignore_changes = [node_config_details[0].placement_configs,kubernetes_version, defined_tags["Oracle-Tags.CreatedOn"], defined_tags["Oracle-Tags.CreatedBy"],node_config_details[0].defined_tags["Oracle-Tags.CreatedOn"],node_config_details[0].defined_tags["Oracle-Tags.CreatedBy"]]}


**Known Observed behaviours:**

- It has been observerd that the order of kubernetes labels change randomly during an export. In such situations a terraform plan detects it as a change to the kubernetes labels.

