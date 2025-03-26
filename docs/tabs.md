## Compartments Tab

Use this Tab to create compartments in the OCI tenancy. On choosing "Identity" in the SetUpOCI menu will allow to create compartments in the OCI tenancy.

Output terraform file generated at:  ```<outdir>/<region>/<service_dir>/<prefix>_compartments.auto.tfvars``` where *<region\>* directory is the home region.

Once terraform apply is done, you can view the resources under *Identity -> Compartments* in OCI console.

On re-running the same option you will find the previously existing files being backed up under directory    ```<outdir>/<region>/<service_dir>/backup_compartments/<Date>-<Month>-<Time>```.

!!! Note

    - If some compartment specified in excel is already existing in OCI, then Terraform Apply indicates creation of that compartment - this can be ignored as Terraform will only modify the existing Compartments (with additional information, if there are any eg: description) and not create a new/duplicate one.<br>
    - Terraform destroy on compartments or removing the compartments details from <b><i>*_compartments.auto.tfvars</i></b> will not delete them from OCI Console by default. Inorder to destroy them from OCI either - 
    - Add an additional column - <b><i>enable_delete</i></b> in Compartments Tab of CD3 Excel sheet with the value <b>"true"</b> for the compartments that needs to be deleted on terraform destroy. Execute the toolkit menu option to Create Compartments.</li>
    (OR)<br>
    - Add <b><i>enable_delete = true</i></b> parameter to each of the compartment that needs to be deleted in <b><i>*_compartments.auto.tfvars</i></b></li>
  </ul>
</blockquote>



## Groups Tab

Use this Tab to create groups and dynamic Groups in the OCI tenancy. On choosing "Identity" in the SetUpOCI menu will allow to create groups/dynamic groups in the OCI tenancy.

The toolkit supports groups in IDCS, default and custom IAM domains now. 

**Note:**

1. Use this tab to assign users to different groups respectively. Mention the usernames as comma separated values under the column "Members".
2. Domain details should be mentioned in column "Domain Name" in the format of compartment@domain.
3. Entire path of the compartment can be mentioned with double column (::) separated. Format given below

    ```root::subcompartment1:subcompartment2@domain```

4. Domain Name can be left blank for group creation in IDCS and default domain.
5. Name is a mandatory field.
6. The Default Administrator groups ("Domain_Administrators", "All Domain Users", "Administrators")  are skipped while export of groups from Identity Domain tenancies.
  
Output terraform file generated at:  ```<outdir>/<region>/<service_dir>/<prefix>_groups.auto.tfvars``` where *<region\>* directory is the home region.

Once terraform apply is done, you can view the resources under *Identity -> Groups* in OCI console.

On re-running the same option you will find the previously existing files being backed up under directory →   ```<outdir>/<region>/<service_dir>/backup_groups/<Date>-<Month>-<Time>```.

!!! Important

    Check point no: **11** in the [Known Behaviour](./knownbehaviour.md#terraform-behavior) section for details on Terraform's behavior when exporting normal and dynamic groups.



## Policies Tab
Use this Tab to create policies in the OCI tenancy. On choosing "Identity" in the SetUpOCI menu will allow to create policies in the OCI tenancy.

Output terraform files generated at: ```<outdir>/<region>/<service_dir>/<prefix>_policies.auto.tfvars``` where *<region\>* directory is the home region.

Once terraform apply is done, you can view the resources under *Identity -> Policies* in OCI console.

On re-running the same option you will find the previously existing files being backed up under directory →   ```<outdir>/<region>/<service_dir>/backup_policies/<Date>-<Month>-<Time>```.


## Users Tab

Use this Tab to create local users in the OCI tenancy. On choosing "Identity" in the SetUpOCI menu and "Add/Modify/Delete Users" submenu will allow to create users in the OCI tenancy.

The toolkit supports users in IDCS, default and custom IAM domains now. 

**Note:**

1. Domain details should be mentioned in column "Domain Name" in the format of compartment@domain.
2. Entire path of the compartment can be mentioned with double column (::) separated. Format given below

      ```root::subcompartment1:subcompartment2@domain```

3. Domain Name can be left blank for group creation in IDCS and default domain.
4. User Name, Family Name and User Email are mandatory fields for IAM domains.
5. User Name and Description are mandatory fields for IDCS. User Email is optional.
6. Mention the capabilities which needs to be enabled under "Enable Capabilities" column and the rest will be disabled. Currently terraform doesn't support Database Passwords and Oauth 2.0 Client Credentials in IDCS, so by default those will be enabled.

Output terraform file generated: ```<outdir>/<region>/<service_dir>/<prefix>_users.auto.tfvars``` where *<region\>* directory is the home region.
  
Once terraform apply is done, you can view the resources under *Identity & Security -> Users* in OCI console.
  
On re-running the same option you will find the previously existing files being backed up under directory → ```<outdir>/<region>/<service_dir>/backup_users/<Date>-<Month>-<Time>```.


   
## Network Sources Tab
  
Use this Tab to create Network Source in the OCI tenancy. On choosing "Identity" in the SetUpOCI menu and "Add/Modify/Delete Network Sources" submenu will allow to create Network Sources in the OCI tenancy.
  
Output terraform file generated: ```<outdir>/<region>/<service_dir>/<prefix>_networksources.auto.tfvars``` where *<region\>* directory is the home region.
  
Once terraform apply is done, you can view the resources under *Identity & Security -> Network Sources* in OCI console.
  
On re-running the same option you will find the previously existing files being backed up under directory → ```<outdir>/<region>/<service_dir>/backup_networksources/<Date>-<Month>-<Time>```.

Note - Network Source creation/updation is supported only in the home region.  
    

## Tags Tab

Use this Tab to create tags - Namespaces, Key-Value pairs, Default and Cost Tracking Tags. On choosing "Tags" in the SetUpOCI menu will allow to create Tags in the OCI tenancy.
  
Once this is complete you will find the generated output terraform files in below locations :

```
 <outdir>/<region>/<service_dir>/<prefix>_tags-defaults.auto.tfvars

 <outdir>/<region>/<service_dir>/<prefix>_tags-namespaces.auto.tfvars

 <outdir>/<region>/<service_dir>/<prefix>_tags-keys.auto.tfvars 

```
under *<region\>* directory.

Once terraform apply is done, you can view the resources under *Governance -> Tag Namespaces* for the region.

On re-running the same option you will find the previously existing files being backed up under directory →   ```<outdir>/<region>/<service_dir>/backup_Tagging/<Date>-<Month>-<Time>```.

## a. VCNs Tab

**Note:**

1. Mention value for column 'Hub/Spoke/Peer/None' in VCNs tab as None for utilising DRGv2 functionality (where DRG is directly attached to all VCNs and hub/spoke model is not required)

2. Declare the DRG for the VCN in 'DRG Required' column of VCNs tab and then declare the attachment in DRGs tab also. Toolkit verifies the declaration in VCNs tab and then creates the DRG while reading the DRGs tab.

## b. DRGs Tab

**Note:**

1. Only VCN and RPC attachments are supported via CD3 as of now for DRGv2. Create attachments for VC and IPSec via OCI console.
2. Network export will also export only VCN and RPC attachments to CD3 excel sheet as of now.
3. Create a Route Table for DRG which is not attached to any attachment by keeping 'Attached To' column in DRGs tab empty.
4. Create an Import Route Distribution which is attached to some Route Table in DRG.

## c. VCN Info tab

This is an important tab and contains general information about networking to be setup.

## d. DHCP tab
This contains information about DHCP options to be created for each VCN.

## e. SubnetsVLANs tab

**Notes:**

1. Name of the VCNs, subnets etc are all case-sensitive. Specify the same names in all required places. Avoid trailing spaces for a resource Name.
2. A subnet or a vlan will be created based on the column - 'Subnet or VLAN'. When VLAN is specified, vlan tag can also be specified with sytanx as ```VLAN::<vlan_tag>```
3. Column NSGs is read only for type VLAN.
4. Columns - DHCP Option Name, Seclist Names, Add Default Seclist and DNS Label are applicable only for type Subnet.
5. Default Route Rules created are :

    <b>a.</b> Based on the values entered in columns ‘configure SGW route’, ‘configure NGW route’, ‘configure IGW route’, 'configure Onprem route' and 'configure VCNPeering route'  in Subnets sheet; if the value entered is ‘y’, it will create a route for the object in that subnet.
    
      Eg if ‘configure IGW’ in Subnets sheet is ‘y’ then it will read parameter ‘igw_destination’ in VCN Info tab and create a rule in the subnet with destination object as IGW of the VCN and destination CIDR as value of igw_destnation field.
        
      If comma separated values are entered in the igw_destination in VCN Info tab then the tool creates route rule for each destination cidr for IGW in that subnet.Tool works similarly for ‘configure NGW’ in Subnets tab and ‘ngw_destination’ in VCN Info tab. For SGW, route rule is added either 'all services' or object storage in that region.

    <b>b.</b>  For a hub spoke model, tool automatically creates route tables attached with the DRG and each LPG in the hub VCN peered with spoke VCN.
     ‘onprem_destinations’ in VCN Info tab specifies the On Prem Network CIDRs.

6. The below Default Security Rules are created:

      <b>a.</b>  Egress rule allowing all protocols for 0.0.0.0/0 is opened.

      <b>b.</b>  Ingress rule allowing all protocols for subnet CIDR is opened. This is to allow communication between VMs with in the same subnet.

7. Default Security List of the VCN is attached to the subnet if ‘add_default_seclist’ parameter in Subnets tab is set to ‘y’.

8. Components- IGW, NGW, DRG, SGW, LPGs and NSGs are created in same compartment as the VCN.

9. VCN names need to be unique for the same region. Automation ToolKit does not support duplicate values at the moment. However you can have same VCN names across different regions.
      

Output terraform files are generated under *<outdir\>/<region\>* directory.

Once terraform apply is done, you can view the resources under Networking -> Virtual Cloud Networks in OCI console.

Output files generated:

| File name | Description |
| --- | --- |
| <prefix\>_major-objects.auto.tfvars | Contains TF for all VCNs and components- IGW, NGW, SGW, DRG, LPGs.|
| <prefix\>_custom-dhcp.auto.tfvars	|Contains TF for all DHCP options for all VCNs.|
| <br><prefix\>_routetables.auto.tfvars<br><prefix\>_default-routetables.auto.tfvars<br><prefix\>_drg-routetables.auto.tfvars<br><prefix\>_drg-distributions.auto.tfvars<br><prefix\>_drg-data.auto.tfvars</br></br></br></br></br> | <br>Contains TF for route rules for each route table.</br></br> |
| <br><prefix\>_seclists.auto.tfvars<br><prefix\>_default-seclists.auto.tfvars</br></br> | <br>Contains TF for security rules for each security list. |
|<prefix\>_subnets.auto.tfvars|	Contains TF for all subnets for all VCNs.|
|<prefix\>_vlans.auto.tfvars|	Contains TF for all VLANs for all VCNs.|
|<prefix\>_default-dhcp.auto.tfvars	|Contains TF for default DHCP options of each VCN in each region |
|<br><prefix\>_nsgs.auto.tfvars<br><prefix\>_nsg-rules.auto.tfvars</br></br>| Contains TF for NSGs in each region |

## f. Rules
After running Create Network, export the Security Rules, Route Rules, DRG Route Rules (using create_resources (Greenfield) Workflow) into the excel sheet and then modify the respective sheet to do any further modification to the rules.

## g. NSGs
Use NSGs tab to add/modify/delete NSG rules and NSGs.


## DNS-Views-Zones-Records-Tab
Below are the details about specific columns to fill the sheet for DNS-Views-Zones-Records-Tab

1. "Compartment Name"- Compartment name for the  Views/Zones

2. "View Name"- Should be unique in a region

3. "Zone" - Zone Name under the specified view

4. "Domain" - Full domain name (including zone name)

5. "RType" -  Select the RType from the list

6. "RDATA" - Provide multi values as supported by the specified RType, separated by newline.
    <a href="https://docs.oracle.com/en-us/iaas/Content/DNS/Reference/supporteddnsresource.htm">Click here to read more about RType and RDATA. </a> 

6. "Defined Tags" - Specify the defined tag key and its value in the format - *<Namespace\>.<TagKey\>=<Value\>*  else leave it empty.
    Multiple Tag Key , Values can be specified using semi-colon (;) as the delimeter. 
    Example: Operations.CostCenter=01;Users.Name=user01

7. There must be only Single Row  for Domain and RType combination

8. Rows are duplicated in case of multiple child resources

Output terraform files are generated under *<outdir\>/<region\>* directory.

Once terraform apply is done, you can view the resources under Networking -> DNS management in OCI console
<br>

## Firewall Tabs
OCI Network Firewall can be created using [CD3-Firewall-template.xlsx](https://github.com/oracle-devrel/cd3-automation-toolkit/blob/main/cd3_automation_toolkit/example/CD3-Firewall-template.xlsx).
After the required details are filled in, choose "OCI Firewall" under the SetUpOCI menu to create the Firewall and its policy. 

It is recommended to execute the validator script for Firewall, to validate the input values before proceeding to create.

Once the toolkit execution is complete,  output terraform files are generated at :
```<outdir>/<region>/<service_dir>/<prefix>_firewall*.auto.tfvars```

Once terraform apply is done, you can view the resources under Identity and Security -> Network Firewalls for the region.


## DNS-Resolvers-Tab

Existing Resolvers need to be exported first before making any changes to those.
Below are the details about specific columns to fill the sheet for DNS-Resolvers-Tab

1. "Compartment Name" - Compartment name for VCN

2. "Display Name" -  Display Name is same as the VCN Name by default.

3. "Associated Private Views" - Format: *<view_compartment\>@<view_name\>*. Multiple views are seperated by newline in the same cell(\n is not supported).

4. "Endpoint Display Name" - Provide endpoint display name, new row need to be created for each endpoint in a resolver. Duplicate Names are not allowed for a single resolver.

5. "Endpoint Type:IP Address" - Format Type:IP, Type could be Forwarding or Listening. IP can be left as null if not predefined.

6. "Endpoint NSGs"- NSGs attached to the endpint.

7. "Rules" - Format: Type::Clients::Destination IP. Multiple rules are seperated by newline in the same cell(\n is not supported)(Rules are processed only for Forwarding Endpoints)

8. "Defined Tags" - Specify the defined tag key and its value in the format - *<Namespace\>.<TagKey\>=<Value\>*  else leave it empty.
   Multiple Tag Key , Values can be specified using semi colon (;) as the delimeter. 
   Example: Operations.CostCenter=01;Users.Name=user01 

9. Associated Private Views can be null/blank

Output terraform files are generated under *<outdir\>/<region\>* directory.

Once terraform apply is done, you can view the resources under Networking -> Virtual Cloud Network -> VCN Information in OCI console


## DedicatedVMHosts Tab

Fill up the details in **'DedicatedVMHosts'** sheet and follow the options below.

On choosing **"Compute"** in the SetUpOCI menu and **"Add/Modify/Delete Dedicated VM Hosts"** submenu will allow to launch your VM on a dedicated host.



Output terraform file generated: ```<outdir>/<region>/<service_dir>/<prefix>_dedicatedvmhosts.auto.tfvars```.

Once terraform apply is done, you can view the resources under *Compute -> Dedicated Virtual Machine Hosts* for the region.

If you want to update or add new dedicated VM hosts, update the 'DedicatedVMHosts' tab in cd3 and rerun using setUpOCI.

On re-running the same option you will find the previously existing files being backed up under directory →   ```<outdir>/<region>/<service_dir>/backup_dedicatedvmhosts/<Date>-<Month>-<Time>```.

## Instances Tab


<ins>CD3 Tab Specifications:</ins>

1. "Display Name" column is case sensitive. Specified value will be the display name of Instance in OCI console.

2. Optional columns can also be left blank - like Fault Domain, IP Address. They will take default values when left empty.

3. Leave columns: Backup Policy, NSGs, DedicatedVMHost blank if instance doesn't need to be part of any of these. Instances can be made a part of Backup Policy and NSGs later by choosing appropriate option in setUpOCI menu.

    >Note:
    The column "SSH Key Var Name" accepts SSH key value directly or the name of variable declared in *variables.tf* under the  **instance_ssh_keys** variable containing the key value. Make sure to have an entry in *variables_<region\>.tf* file with the name you enter in SSH Key Var Name field of the Excel sheet and put the value as SSH key value.

    >For Eg: If you enter the SSH Key Var Name as **ssh_public_key**, make an entry in *variables_<region\>.tf* file as shown below:

        
          variable  'instance_ssh_keys'  {
          type = map(any)
          default = {
          ssh_public_key = "<SSH PUB KEY STRING HERE>"
          # Use '\n' as the delimiter to add multiple ssh keys.
          # Example: ssh_public_key = "ssh-rsa AAXXX......yhdlo\nssh-rsa AAxxskj...edfwf"
          #START_instance_ssh_keys#
          # exported instance ssh keys
          #instance_ssh_keys_END#
            }
          }

4. Enter "Network Details" column value as: ```<compartment-name>@<vcn-name>::<subnet-name>```

5. Enter remote execute script(Ansible/Shell) name. Shell scripts should be named with *.sh and ansible with *.yaml or *.yml inside 'scripts' folder within the region/service dir. This feature is tested against OL8.  

6. Create a column called 'Cloud Init Script' to execute scripts (located under 'scripts' folder within the region/service dir) as part of cloud-init.   

7. Source Details column of the excel sheet accepts both image and boot volume as the source for instance to be launched.
Format - 
  ```
    image::<variable containing ocid of image> or
    bootVolume::<variable containing ocid of boot volume>
  ```

 8.  Make sure to have an entry in *variables_<region\>.tf* file for the value you enter in Source Details field of the Excel sheet.
  Ex: If you enter the Source Details as image::Linux, make an entry in *variables_<region\>.tf* file under the **instance_source_ocids** variable as shown below:


        variable 'instance_source_ocids' {
        type = map(any)
        Linux    = "<LATEST LINUX OCID HERE>"
        Windows  = "<LATEST WINDOWS OCID HERE>"
        PaloAlto = "Palo Alto Networks VM-Series Next Generation Firewall"
        #START_instance_source_ocids#
        # exported instance image ocids
        #instance_source_ocids_END#
        }

9. Mention shape to be used in Shape column of the excel sheet. If Flex shape is to be used format is:```shape::ocpus```

      eg: ```VM.Standard.E3.Flex::5```


10. Custom Policy Compartment Name : Specify the compartment name where the Custom Policy is created.

11. While export of instances, it will fetch details for only the primary VNIC attached to the instance


On choosing **"Compute"** in the SetUpOCI menu and **"Add/Modify/Delete Instances/Boot Backup Policy"** submenu will allow to launch your VM on OCI tenancy.


Output terraform file generated: ```<outdir>/<region>/<service_dir>/<prefix>_instances.auto.tfvars``` and ```<outdir>/<region>/<service_dir>/<prefix>_boot-backup-policy.auto.tfvars```  under  appropriate <region\> directory.

Once the terraform apply is complete, view the resources under *Compute -> Instances* for the region.

On re-running the same option you will find the previously existing files being backed up under directory →   ```<outdir>/<region>/<service_dir>/backup_instances/<Date>-<Month>-<Time>```.



## BlockVolumes Tab

This tab in cd3 excel sheet is used when you need to create block volumes and attach the same to the instances in the OCI tenancy. 

Automation Tool Kit does not support sharing of volumes at the moment. While export of block volumes, if the block volume is attached to multiple instances, it will just fetch details about one attachment.

On choosing **"Storage"** in the SetUpOCI menu and **"Add/Modify/Delete Block Volumes/Block Backup Policy"** submenu will allow to create block volumes in OCI Tenancy.

On completion of execution, you will be able to find the output terraform file generated at : 

  ```<outdir>/<region>/<service_dir>/<prefix>_blockvolumes.auto.tfvars```

  ```<outdir>/<region>/<service_dir>/<prefix>_block-backup-policy.auto.tfvars```  under  appropriate *<region\>* directory.

Once terraform apply is done, you can view the resources under *Block Storage -> Block Volumes*  in OCI console.

On re-running the option to create Block Volumes you will find the previously existing files being backed up under directory:

  ```<outdir>/<region>/<service_dir>/backup_blockvolumes/<Date>-<Month>-<Time>```   and   ```<outdir>/<region>/<service_dir>/backup_BlockBackupPolicy/<Date>-<Month>-<Time>```.


## FSS Tab

On choosing **"Storage"** in the SetUpOCI menu and **"Add/Modify/Delete File Systems"** submenu will allow to create file system storage on OCI tenancy.

Note:   Freeform and Defined Tags - If specified, applies to FSS object only and not to other components like Mount Target.

Once this is complete you will find the generated output terraform files in location :

  ```<outdir>/<region>/<service_dir>/<prefix>_fss.auto.tfvars```


Once terraform apply is done, you can view the resources under *File Storage → File Systems* for the region.

On re-running the same option you will find the previously existing files being backed up under directory →   ```<outdir>/<region>/<service_dir>/backup_FSS/<Date>-<Month>-<Time>```.


## Load Balancers

Automation Tool Kit allows you to create Load Balancers. Components that you can create using the Tool Kit includes:

| Resource | Tab Name |
|---|---|
|Load Balancers<br>Hostnames<br>Cipher Suites<br>Certificates| LB-Hostname-Certs |
|Backend Sets and Backend Servers|BackendSet-BackendServer|
|Rule Set|RuleSet|
|Path Route Set|PathRouteSet|
|Listeners|LB-Listeners|

  >NOTE : While exporting and synching the tfstate file for LBR objects, the user may be notified that a few components will be modified on apply. In such scenarios, add the attributes that the Terraform notifies to be changed to the appropriate CD3 Tab of Load Balancer and Jinja2 Templates (as a non-default attribute) and re-run the export.

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

 ```<outdir>/<region>/<service_dir>/<prefix>_lb-hostname-certs.auto.tfvars```


Once terraform apply is done, you can view the resources under *Networking → Load Balancers* for the region.

On re-running the same option you will find the previously existing files being backed up under directory →   ```<outdir>/<region>/<service_dir>/backup_lb-hostname-certs/<Date>-<Month>-<Time>```.

## LB-Backend Set and Backend Servers Tab

Use the tab **LB-BackendSet-BackendServer** of CD3 Excel to create the following components of Load Balancer:

- Backend Sets
- Backend Servers


Once this is complete you will find the generated output terraform files in location :

 ```<outdir>/<region>/<service_dir>/<prefix>_lb-backendset-backendserver.auto.tfvars```


Once terraform apply is done, you can view the resources under Networking→Load Balancers for the region.

On re-running the same option you will find the previously existing files being backed up under directory →   ```<outdir>/<region>/<service_dir>/backup_lb-backendset-backendserver/<Date>-<Month>-<Time>```.

## LB-RuleSet Tab

Use the tab **LB-RuleSet** of CD3 Excel to create the following components of Load Balancer:

- Rule Sets

Once this is complete you will find the generated output terraform files in location :

 ```<outdir>/<region>/<service_dir>/<prefix>_lb-ruleset.auto.tfvars```


Once terraform apply is done, you can view the resources under Networking→Load Balancers for the region.

On re-running the same option you will find the previously existing files being backed up under directory →   ```<outdir>/<region>/<service_dir>/backup_lb-ruleset/<Date>-<Month>-<Time>```.

## LB-Path Route Set Tab

Use the tab **LB-PathRouteSet** of CD3 Excel to create the following components of Load Balancer:

- Path Route Sets

Once this is complete you will find the generated output terraform files in location :

 ```<outdir>/<region>/<service_dir>/<prefix>_lb-pathrouteset.auto.tfvars```


Once terraform apply is done, you can view the resources under Networking→Load Balancers for the region.

## LB-Routing Policy Tab

Use the tab **LB-RoutingPolicy** of CD3 Excel to create the following components of Load Balancer:

- Routing Policies

Once this is complete you will find the generated output terraform files in location :

 ```<outdir>/<region>/<service_dir>/<prefix>_lb-routingpolicy.auto.tfvars```


Once terraform apply is done, you can view the resources under Networking→Load Balancers for the region.

On re-running the same option you will find the previously existing files being backed up under directory →   ```<outdir>/<region>/<service_dir>/backup_lb-routingpolicy/<Date>-<Month>-<Time>```.

## LB-Listeners Tab

Use the tab **LB-Listener** of CD3 Excel to create the following components of Load Balancer:

- LB Listener

Once this is complete you will find the generated output terraform files in location :

 ```<outdir>/<region>/<service_dir>/<prefix>_lb-listener.auto.tfvars```


Once terraform apply is done, you can view the resources under Networking→Load Balancers for the region.

On re-running the same option you will find the previously existing files being backed up under directory →   ```<outdir>/<region>/<service_dir>/backup_LB-Listener/<Date>-<Month>-<Time>```.

## DBSystems-VM-BM Tab

This helps you to create DB Systems hosted on Virtual Machine and Bare Metal. This can be configured based on the shape chosen in the tab.


>Note:
The column "SSH Key Var Name" accepts SSH key value directly or the name of variable declared in *variables.tf* under the  **dbsystem_ssh_keys** variable containing the key value. Make sure to have an entry in *variables_<region\>.tf* file with the name you enter in SSH Key Var Name field of the Excel sheet and put the value as SSH key value.

>For Eg: If you enter the SSH Key Var Name as **ssh_public_key**, make an entry in *variables_<region\>.tf* file as shown below:

    variable "dbsystem_ssh_keys" {
    type = map(any)
    default = {
    ssh_public_key = "<SSH PUB KEY STRING HERE>"
    # Use ',' as the delimiter to add multiple ssh keys.
    # Example: ssh_public_key = ["ssh-rsa AAXXX......yhdlo","ssh-rsa AAxxskj...edfwf"]
    #START_dbsystem_ssh_keys#
    # exported dbsystem ssh keys
    #dbsystem_ssh_keys_END#
       }
    }
  
On choosing **"Database"** in the SetUpOCI menu and **"Add/Modify/Delete Virtual Machine or Bare Metal DB Systems"** submenu will allow to create DB Systems hosted on Virtual Machine and Bare Metal.

Output terraform file generated: 

```<outdir>/<region>/<service_dir>/<prefix>_dbsystem-vm-bm.auto.tfvars``` under where *<region\>* directory is the region specified for the DB System.  

Once terraform apply is done, you can view the resources under **Bare Metal, VM, and Exadata-> DB Systems** in OCI console.

On re-running the same option you will find the previously existing files being backed up under directory →   ```<outdir>/<region>/<service_dir>/backup_dbsystems-vm-bm/<Date>-<Month>-<Time>```.

## ExaCS

You can create ExaCS in OCI by utilizing Exa-Infra and Exa-VM Cluster tabs in CD3 excel sheet.


>Note:
The column "SSH Key Var Name" accepts SSH key value directly or the name of variable declared in *variables.tf* under the  **exacs_ssh_keys** variable containing the key value. Make sure to have an entry in *variables_<region\>.tf* file with the name you enter in SSH Key Var Name field of the Excel sheet and put the value as SSH key value.

>For Eg: If you enter the SSH Key Var Name as **ssh_public_key**, make an entry in variables_<region\>.tf file as shown below:

      variable "exacs_ssh_keys" {
        type = map(any)
        default = {
          ssh_public_key = "<SSH PUB KEY STRING HERE>"
          # Use ',' as the delimiter to add multiple ssh keys.
          # Example: ssh_public_key = ["ssh-rsa AAXXX......yhdlo","ssh-rsa AAxxskj...edfwf"]
          #START_exacs_ssh_keys#
          # exported exacs ssh keys
          #exacs_ssh_keys_END#
        }
      }

On choosing **"Database"** in the SetUpOCI menu and **"Add/Modify/Delete EXA Infra and EXA VM Clusters"** submenu will allow to create ExaCS in OCI tenancy.

Output terraform file generated: 

```<outdir>/<region>/<service_dir>/<prefix>_exa-infra.auto.tfvars``` under where *<region\>* directory is the region hosting the Exa Infra.

```<outdir>/<region>/<service_dir>/<prefix>_exa-vmclusters.auto.tfvars``` under where *<region\>* directory is the region hosting the Exa VM Clusters.


Once terraform apply is done, you can view the resources under *Bare Metal, VM, and Exadata-> Exadata Infrastructure and Exadata VM Clusters* in OCI console.


On re-running the same option you will find the previously existing files being backed up under directory →   ```<outdir>/<region>/<service_dir>/backup_exa-infra/<Date>-<Month>-<Time>```

and ```<outdir>/<region>/<service_dir>/backup_exa-vmclusters/<Date>-<Month>-<Time>```


## ADB Tab

Use this Tab to create Autonomous Database Warehouse or Autonomous Database Transaction Processing in the OCI tenancy.

On choosing **"Database"** in the SetUpOCI menu and **"Add/Modify/Delete ADBs"** submenu will allow to create Autonomous Database Warehouse or Autonomous Database Transaction Processing in the OCI tenancy.


Output terraform file generated:  ```<outdir>/<region>/<service_dir>/<prefix>_adb.auto.tfvars``` where *<region\>* directory is the region hosting the respective ADB.

Once terraform apply is done, you can view the resources under **Oracle Database -> Autonomous Database** in OCI console.

On re-running the same option you will find the previously existing files being backed up under directory →   ```<outdir>/<region>/<service_dir>/backup_adb/<Date>-<Month>-<Time>```

**NOTE -**
<blockquote>
  - Currently toolkit supports ADB creation in Shared Infra only,
  </blockquote>

## :dolphin: MySQL Tab

`Use this Tab to create MySQL Database Systems in the OCI tenancy.`

### 💾 MySQL DB System

On choosing **"Database"** in the SetUpOCI menu and **"Add/Modify/Delete MySQL DBs"** submenu will allow to create MySQL Database Systems in the OCI tenancy.

<div class="admonition info">
<p class="admonition-title">Output File</p>
Output terraform file generated: <code>&lt;outdir&gt;/&lt;region&gt;/&lt;customer_name&gt;_mysql-dbsystems.auto.tfvars</code> where <em>&lt;region&gt;</em> directory is the region specified for the MySQL DB System.
</div>

### :clipboard: Commonly used Fields and its description
| Fields | Description |
|---|---|
|Backup policy is enabled | Specifies if automatic backups are enabled.|
|Backup policy pitr policy is enabled | Specifies if PITR is enabled or disabled |
| Backup policy Retention in days | Number of days to retain an automatic backup. |
| Backup policy window start time | The start of a 30-minute window of time in which daily, automated backups occur. This should be in the format of the "Time" portion of an RFC3339-formatted timestamp. Any second or sub-second time data will be truncated to zero. At some point in the window, the system may incur a brief service disruption as the backup is performed. |
| Crash Recovery is Enabled Data Storage (in Gbs) | Whether to run the DB System with InnoDB Redo Logs and the Double Write Buffer enabled or disabled, and whether to enable or disable syncing of the Binary Logs. |
| Database Management is Enabled | Whether to enable monitoring via the Database Management service. |
| Deletion policy automatic backup retention | Specifies if any automatic backups created for a DB System should be retained or deleted when the DB System is deleted. |
| Deletion policy final backup | Specifies whether or not a backup is taken when the DB System is deleted. REQUIRE_FINAL_BACKUP: a backup is taken if the DB System is deleted. SKIP_FINAL_BACKUP: a backup is not taken if the DB System is deleted. |
| Deletion policy is deleted protected | Specifies whether the DB System can be deleted. Set to true to prevent deletion, false (default) to allow. |
| Maintenance window start time | The start time of the maintenance window. This string is of the format: "{day-of-week} {time-of-day}". "{day-of-week}" is a case-insensitive string like "mon", "tue", &c. "{time-of-day}" is the "Time" portion of an RFC3339-formatted timestamp. Any second or sub-second time data will be truncated to zero. If you set the read replica maintenance window to "" or if not specified, the read replica is set same as the DB system maintenance window. |
| Port | The port for primary endpoint of the DB System to listen on. |
| Port_x | The TCP network port on which X Plugin listens for connections. This is the X Plugin equivalent of port. |
| Source Type | The specific source identifier. Use BACKUP for creating a new database by restoring from a backup. Use IMPORTURL for creating a new database from a URL Object Storage PAR. |
| Configuration id | The OCID of the Configuration to be used for this DB System. |


### :gear: MySQL Configurations
On choosing **`Database`** in the SetUpOCI menu and **`Add/Modify/Delete MySQL Configurations`** submenu will allow to create MySQL Database Systems in the OCI tenancy.

!!! note
    Output terraform file generated: `outdir/region/customer_name_mysql-configurations.auto.tfvars` where region directory is the region specified for the MySQL DB System.


Once terraform apply is done, you can view the resources under **Databases -> HeatWave MySQL -> DB System** in OCI console for MySQL DB System and **Databases -> HeatWave MySQL -> Configurations** for MySQL Configurations.

!!! note 
    On re-running the same option you will find the previously existing files being backed up under directory → `outdir/region/service_dir/backup_mysql/Date-Month-Time`


[Reference for OCI Mysql Configuration Variables](https://docs.oracle.com/en-us/iaas/mysql-database/doc/configuration-variables.html)

!!! Important
    - Currently Heatwave is not supported as part of CD3 deployment.


## Notifications Tab

On choosing **"Management Services"** in the SetUpOCI menu and **"Add/Modify/Delete Notification"** and **"Add/Modify/Delete Events"** submenu will allow to manage events and notifications in OCI tenancy.

Output terraform file generated: *<outdir\>/<region\>/<customer_name\>_notifications.auto.tfvars``` and *<outdir\>/<region\>/<customer_name>_events.auto.tfvars``` 

Once the terraform apply is complete, view the resources under **Application Integration-> Notifications & Application Integration-> Events** for the region in OCI Console.

Further, on re-running the same option you will find the previously existing files being backed up under directory →   ```<outdir>/<region>/<service_dir>/backup_events/<Date>-<Month>-<Time>``` or ```<outdir>/<region>/<service_dir>/backup_notifications/<Date>-<Month>-<Time>```

Note: 

- Notifications can not be configured for a particular resource OCID at the moment.
- Export of Notifications supports ONS and FAAS(will put OCID for the function in the CD3). It will skip the event export if action type is OSS.


## Alarms Tab

Use **CD3-ManagementServices-template.xlsx** under example folder of GIT as input file for creating/exporting Alarms.

On choosing **"Management Services"** in the SetUpOCI menu and **"Add/Modify/Delete Alarms"** submenu will allow to manage alarms in OCI tenancy.

Output terraform file generated: *<outdir\>/<region\>/<customer_name\>_alarms.auto.tfvars``` 

Once the terraform apply is complete, view the resources under **Observability & Management→  Monitoring → Alarms Definition** for the region in OCI Console.

Further, on re-running the same option you will find the previously existing files being backed up under directory →   ```<outdir>/<region>/<service_dir>/backup_alarms/<Date>-<Month>-<Time>```


## ServiceConnectors Tab

Use **CD3-ManagementServices-template.xlsx** under example folder of GIT as input file for creating/exporting Service connectors.

The service connector resources provisioning can be initiated by updating the corresponding excel sheet tab.

**CIS LZ recommends to create SCH to collect audit logs for all compartments, VCN Flow Logs and Object Storage Logs and send to a particular target that can be read by SIEM. CD3 SCH automation is aligned with CIZ LZ and allow the user to deploy/provision the recommended approach by filling in the suitable data in excel sheet.**

Output terraform file generated: *<outdir\>/<region\>/<customer_name\>_serviceconnectors.auto.tfvars``` 

Once the terraform apply is complete, view the resources under **service connectors window** for the region in OCI Console.

Further, on re-running the same option you will find the previously existing files being backed up under directory →  ```<outdir>/<region>/<service_dir>/backup_serviceconnectors/<Date>-<Month>-<Time>```

Note - 

- The service connector resources created via automation will not have the corresponding IAM policies between source and destination entities. It has to be created separately.
- The user will get an option to create the **IAM policy** when you click on **Edit** for the respective service connector provisioned through terraform like in below screenshot:

![image](../images/tabs-1.png)

- Also, When the target kind is **'notifications'** the value for formatted messages parameter is set to **'true'** as default. Its set to **'false'** only when the source is 'streaming'.

!!! Important

    Check point no: **9** in the [Known Behaviour](./knownbehaviour.md#terraform-behavior) section for details on Terraform's behavior when exporting service connectors.


## OKE Tab

Use this tab to create OKE components in OCI.

>Note:
The column "SSH Key Var Name" accepts SSH key value directly or the name of variable declared in *variables.tf* under the  **oke_ssh_keys** variable containing the key value. Make sure to have an entry in *variables_<region\>.tf* file with the name you enter in SSH Key Var Name field of the Excel sheet and put the value as SSH key value.

>For Eg: If you enter the SSH Key Var Name as **ssh_public_key**, make an entry in *variables_<region\>.tf* file as shown below:

    variable "oke_ssh_keys" {
    type = map(any)
    default = {
        ssh_public_key = "<SSH PUB KEY STRING HERE>"
        # Use '\n' as the delimiter to add multiple ssh keys.
        # Example: ssh_public_key = "ssh-rsa AAXXX......yhdlo\nssh-rsa AAxxskj...edfwf"
        #START_oke_ssh_keys#
        #oke_ssh_keys_END#
      }
    }

- For source details column, the format should be as below

  ```image::<variable containing ocid of image>```

  Make sure to have an entry in *variables_<region\>.tf* file for the value you enter in Source Details field of the Excel sheet.

  Eg: If you enter the Source Details as image::Linux, make an entry in *variables_<region\>.tf* file under the **oke_source_ocids** variable as shown below:

            variable "oke_source_ocids" {
              type = map(any)
              default = {
                Linux = "<OKE LINUX OCID HERE>"
                #START_oke_source_ocids#
                # exported oke image ocids
                #oke_source_ocids_END#
              }
            }
            
On choosing **"Developer Services"** in the SetUpOCI menu and **"Add/Modify/Delete OKE Cluster and Nodepools"** submenu will allow to manage oke components in OCI tenancy.

On completion of execution, you will be able to find the output terraform file generated at : 

  ```<outdir>/<region>/<service_dir>/<prefix>_oke_clusters.auto.tfvars```

  ```<outdir>/<region>/<service_dir>/<prefix>_oke_nodepools.auto.tfvars``` 


Once terraform apply is done, you can view the resources under **Developer Services -> Kubernetes Clusters (OKE)** for the region in OCI console.

On re-running the option to create oke clusters and noodepools you will find the previously existing files being backed up under directory:

```<outdir>/<region>/<service_dir>/backup_oke/<Date>-<Month>-<Time>```.


Notes:

- Current version of the toolkit support only single availability domain placement for the nodepool. So if a cluster is exported with nodepools having multiple placement configuration, the terraform plan will show changes similar to:

![image](../images/tabs-3.png)

<img src= "../images/tabs-4.png" width=50% height=50%>


To avoid this, an ignore statement as shown below is added to ignore any changes to the placement configuration in nodepool.

      ignore_changes = [node_config_details[0].placement_configs,kubernetes_version, defined_tags["Oracle-Tags.CreatedOn"], defined_tags["Oracle-Tags.CreatedBy"],node_config_details[0].defined_tags["Oracle-Tags.CreatedOn"],node_config_details[0].defined_tags["Oracle-Tags.CreatedBy"]]


**Known Observed behaviours:**

- It has been observed that the order of kubernetes labels change randomly during an export. In such situations a terraform plan detects it as a change to the kubernetes labels.
  
## VCN FLow Logs
This will enable Flow logs for all the subnets mentioned in 'SubnetsVLANs' tab of CD3 Excel sheet. Log group for each VCN is created under the same compartment as specified for VCN and all subnets are added as logs to this log group.

Below TF file is created:

| File name | Description|
|---|---|
|<customer_name\>_vcnflow-logging.auto.tfvars |TF variables file containing log group for each VCN and logs for eachsubnet in that VCN.|
  
## LBaaS Logs
This will enable LBaaS logs for all the LBs mentioned in 'LB-Hostname-Certs' tab of CD3 Excel sheet. Log group for each LBaaS is created under the same compartment as specified for LBaaS and access and error log types are added as logs to this log group.

Below TF file is created:

| File name | Description|
|---|---|
|<customer_name\>_load-balancers-logging.auto.tfvars |TF variables file containing log group for each LBaaS and its error and access logs.| 

## OSS Logs
This will enable OSS Bucket logs for all the buckets mentioned in 'Buckets' tab of CD3 Excel sheet. Log group for each bucket is created under the same compartment as specified for bucket and read and write log type is added as logs to this log group.

Below TF file is created:

| File name | Description|
|---|---|
|<customer_name\>_buckets-logging.auto.tfvars |TF variables file containing log group for each bucket and its write logs.| 

## FSS Logs
This will enable logs for all the File systems mentioned in 'FSS' tab of CD3 Excel sheet. Log group for each File system is created under the same compartment as specified for FSS and its logs are added to the log group.

Below TF file is created:

| File name | Description|
|---|---|
|<customer_name\>_nfs-logging.auto.tfvars | TF variables file containing log group for each File system and its logs.| 

## Firewall Logs

This will enable logs for the Firewalls specified in "Firewall" sheet of the Firewall template.. Log group for each Firewall is created under the same compartment as specified for Firewall and its logs are added to the log group.

Below TF file is created:

| File name | Description|
|---|---|
|<customer_name\>_fw-logging.auto.tfvars | TF variables file containing log group for each Firewall and its logs.| 

  
## SDDCs Tab
Use this tab to create OCVS in your tenancy. 

>Note:
>As of now the toolkit supports single cluster SDDC.
The column "SSH Key Var Name" accepts SSH key value directly or the name of variable declared in *variables.tf* under the  **sddc_ssh_keys** variable containing the key value. Make sure to have an entry in *variables_<region\>.tf* file with the name you enter in SSH Key Var Name field of the Excel sheet and put the value as SSH key value.

>For Eg: If you enter the SSH Key Var Name as **ssh_public_key**, make an entry in *variables_<region\>.tf* file as shown below:

    variable "sddc_ssh_keys" {
    type = map(any)
    default = {
        ssh_public_key = "<SSH PUB KEY STRING HERE>"
        # Use '\n' as the delimiter to add multiple ssh keys.
        # Example: ssh_public_key = "ssh-rsa AAXXX......yhdlo\nssh-rsa AAxxskj...edfwf"
        #START_sddc_ssh_keys#
        #sddc_ssh_keys_END#
      }
    }


Management and Workload Datastore volumes must be existing or created separately as part of **BlockVolumes** Tab.
All the Network related information for SDDCs will be provided in **SDDCs-Network** , where the vlan should be created in **SubnetsVLANs**

On choosing "Software-Defined Data Centers - OCVS" in setUpOCI menu, the toolkit will read SDDCs tab and SDDCs-Network tab. The output terraform files will be generated at :
  ```<outdir>/<region>/<service_dir>/<prefix>_sddcs.auto.tfvars``` under appropriate *<region\>* directory.

Once terraform apply is done, you can view the resources under Hybrid -> Software-Defined Data Centers in OCI console.

On re-running the option to create OCVS you will find the previously existing files being backed up under directory:

```<outdir>/<region>/<service_dir>/backup_sddcs/<Date>-<Month>-<Time>```.
  
  
## Buckets Tab
  
This tab in cd3 excel sheet is used when you need to create Object storage buckets in the OCI tenancy.

On choosing "Storage" in the SetUpOCI menu and "Add/Modify/Delete Buckets" submenu will allow to create buckets in OCI Tenancy.

On completion of execution, you will be able to find the output terraform file generated at :
  
  ```<outdir>/<region>/<service_dir>/<prefix>_buckets.auto.tfvars``` 

Once terraform apply is done, you can view the resources under Object Storage -> Buckets in OCI console.

On re-running the option to create Buckets you will find the previously existing files being backed up under directory:

```<outdir>/<region>/<service_dir>/backup_buckets/<Date>-<Month>-<Time>```.

> **_NOTE:_**  Currently the creation of buckets with indefinite retention rule is not supported, only export is supported.
  
**CD3 Tab specifications:**
  
1. The Region, Compartment Name and Bucket Name fields are mandatory.
2. **Storage Tier:** Once created, this cannot be modified unless you delete and re-create the bucket.
3. **Object Versioning:** Once enabled, this can only be suspended and cannot be disabled while modifying.
4. **Retention Rule:** To enable retention rule:
  
     4.1.   &nbsp; The versioning should be disabled.
  
     4.2.   &nbsp; Specify the value in the format ```RuleName::TimeAmount::TimeUnit::Retention Rule Lock Enabled```.Multiple rules are seperated by newline in the same cell (\n is not supported).  
  
     4.3.   &nbsp; Retention Rule Lock Enabled: The time format of the lock should be as per RFC standards. Ex: ```YYYY-MM-DDThh:mm:ssZ``` (provide the value only if you want to  have the time rule locked enabled).
  
     4.4.   &nbsp; TimeAmount: It should be number of Days/Years. Maximun value is 500.
  
     4.5.   &nbsp; TimeUnit: It should be either in DAYS and YEARS.
  
  
5.  **Replication Policy:**  To enable replication policy: 
  
     5.1.   &nbsp; There should be a policy in place to allow region object storage service to manage objects for the bucket.
  
     5.2    &nbsp; The destination bucket should be already created in the tenancy and cannot have versioning enabled.
  
     5.2.   &nbsp; The destination bucket cannot have retention rules. 
  
     5.3.   &nbsp; The format should be *PolicyName::DestinationRegion::DestinationBucketName*.
  

6.  **Lifecycle Policy Name:**  Name of the lifecycle policy. Multiple rules can be mentioned in new rows keeping all other details same.
  
7.  **Lifecycle Target and Action:**  For Multipart-uploads,  Object filters are not required and Rule Period can only be in Days.
 
  
    > **_NOTE:_**  If you have Auto-tiering mode set to Enabled, you cannot create a object lifecycle policy rule with the action set as Infrequent Access. 
  
8. **Lifecycle Rule Period:** Its a combination of TimeAmount (It should be number of Days/Years) and TimeUnit (It should be either in DAYS and YEARS). The format should be                      *TimeAmount::TimeUnit*
  
9. **Lifecyle Exclusion Patterns/Lifecycle Inclusion Patterns/Lifecycle Inclusion Prefixes:** Add the object name filter patterns here.


## Budgets Tab

The Budgets tab in CD3 Excel sheet can be used to create OCI Budgets and Budget Alert rules.

Upon executing setUpOCI.py, choose "Cost Management" from the main menu and "Budgets" from its sub-options to create Budgets/Budget Alert Rules in OCI Tenancy.

On completion of execution, you will be able to find the output terraform file generated at :
  
  ```<outdir>/<region>/<service_dir>/<prefix>_budgets.auto.tfvars``` 

Once terraform apply is done, you can view the resources under *Billing & Cost Management -> Cost Management -> Budgets* in OCI console.

On re-running the option to create Budgets, you will find the previously existing files being backed up under directory:

 ```<outdir>/<region>/<service_dir>/backup_budgets/<Date>-<Month>-<Time>```.


## Quotas Tab

The Quotas tab in CD3 Excel sheet can be used to create OCI Quota policies.

Upon executing setUpOCI.py, choose "Governance" from the main menu and "Quotas" from its sub-options to create Quota policies in OCI Tenancy.

On completion of execution, you will be able to find the output terraform file generated at :
  
  ```<outdir>/<region>/<service_dir>/<prefix>_quotas.auto.tfvars``` 

Once terraform apply is done, you can view the resources under *Governance & Administration -> Tenancy Managememt -> Quota Policies* in OCI console.

On re-running the option to create Quotas, you will find the previously existing files being backed up under directory:

 ```<outdir>/<region>/<service_dir>/backup_quotas/<Date>-<Month>-<Time>```.
  
  
## KMS Tab

The KMS tab in CD3 Excel sheet can be used to create OCI Vaults and Keys in the OCI tenancy.

Upon executing setUpOCI.py, choose "Security" from the main menu and "Add/Modify/Delete KMS (Keys/Vaults)" from its sub-options to create Keys/Vaults in OCI Tenancy.

On completion of execution, you will be able to find the output terraform file generated at :
  
  ```<outdir>/<region>/<service_dir>/<prefix>_kms.auto.tfvars``` 

Once terraform apply is done, you can view the resources under *Identity & Security -> Key Management & Secret Management* in OCI console.

On re-running the option to create KMS, you will find the previously existing files being backed up under directory:

 ```<outdir>/<region>/<service_dir>/backup_kms/<Date>-<Month>-<Time>```.


 **Toolkit currently supports:** 
 
 - Creation of **DEFAULT** or **VIRTUAL PRIVATE** vaults.

 - Replication of Default(Virtual) and Virtual Private Vaults across regions. 

!!! Important

    Check point no: **10** in [Known Behaviour](./knownbehaviour.md#terraform-behavior) for OCI Vault Replication resource terraform import behaviour. 
   
 - Creation of Master Encryption Keys (MEKs) for all the OCI supported Key shapes: AES, RSA and ECDSA.

 - Enabling Auto Rotation for the MEKs in Virtual Private Vaults.

 **Toolkit currently doesn't support:**

  - Dedicated Key Management
  
  - External Key Management

  - Private endpoints

  - Secrets 
  
## Cloud Guard

There is currently no tab for cloud guard in the CD3 excel sheet.

Upon executing setUpOCI.py, choose "Security" from the main menu and "Enable Cloud Guard" from its sub-options will enable Cloud Guard for the tenancy from specified reporting region, clones the Oracle Managed detector and responder recipes. Creates a target for root compartment with the cloned recipes.

Below TF file is created:

| File name | Description|
|---|---|
|cis-cloudguard.auto.tf |vars TF variables file for enabling cloud guard and creating target for root compartment. |

<a href="../terraform/security">Click here to view sample auto.tfvars for Security components </a> 


