## Create New Network Resources in OCI (Greenfield Workflow)

   - [Create Network](#create-network)
   - [Use an existing DRG in OCI while creating the network](#use-an-existing-drg-in-oci-while-creating-the-network)
   - [Modify Network](#modify-network)
   - [Modify Security Rules, Route Rules and DRG Route Rules](#modify-security-rules-route-rules-and-drg-route-rules)
   - [Sync manual changes done in OCI of Security Rules, Route Rules and DRG Route Rules with CD3 Excel Sheet and Terraform](#sync-manual-changes-done-in-oci-of-security-rules-route-rules-and-drg-route-rules-with-cd3-excel-sheet-and-terraform)
   - [Add/Modify/Delete NSGs](#addmodifydelete-nsgs)
   - [Add/Modify/Delete VLANs](#addmodifydelete-vlans)
   - [RPCs](#rpcs)


!!! note
    Make sure to execute "Fetch Compartments OCIDs to variables file" from CD3 Services in setUpOCI menu before starting with Network Creation.

### Create Network

Creation of Networking components using Automation Toolkit involves four simple steps.

 - Add the networking resource details to appropriate Excel Sheets.
 - Running the toolkit with 'Create Resources' workflow to generate *.auto.tfvars.
 - Executing Terraform to provision resources in OCI.
 - Exporting the automatically generated Security Rules and Route Rules by the toolkit to CD3 Excel Sheet.
!!! Important
    'Create Network' generates custom security rules and route rules in OCI along with default ones. Make sure to export them all into excel sheet after running Create Network.
 
Below are the steps in detail to create Network that includes VCNs, Subnets, DHCP, DRG, Security List, Route Tables, DRG Route Tables, NSGs, etc.

1. Choose appropriate excel sheet from [Excel Templates](excel-templates.md) and fill the required Network details in the Networking Tabs - VCNs, DRGs, VCN Info, DHCP, Subnets, NSGs tabs. <br>

2. Execute _setupOCI_ with _Create Resources_ workflow.
   
 
3. Choose option _'Validate CD3'_ and then _'Validate Networks'_ to check for syntax errors in Excel sheet. Examine the log file generated at ```/cd3user/tenancies/<prefix>/<prefix>_cd3validator.log.``` If there are errors,  rectify them accordingly and proceed to the next step. <br>

4. Choose option _'Create Network'_ under _'Network'_ from the displayed menu. Once the execution is successful, multiple .tfvars related to networking like _<customer\_name>\_major-objects.auto.tfvars_ and more will be generated under the folder ```/cd3user/tenancies/<prefix>/terraform_files/<region_dir>/<service_dir>``` <br>

5. Look at the terraform plan and apply. Running terraform apply completes the creation of Networking components in OCI. Verify the components in console. However the details of the security lists and route tables may not be available in the CD3 Excel sheet yet. In order to export that data, follow the below steps: <br>

6. Execute _setupOCI_ with _Create Resources_ workflow:
  
7. Choose _'Network'_ from the displayed menu. Choose below sub-options: (Make sure to choose all the three options for the first time)<br>
   ```Security Rules```
        <br>   - Export Security Rules (From OCI into SecRulesinOCI sheet)
	<br> - Add/Modify/Delete Route Rules (Reads SecRulesinOCI sheet)<br>
   ```Route Rules```
        <br>   - Export Route Rules (From OCI into RouteRulesinOCI sheet)
	<br> - Add/Modify/Delete Route Rules (Reads RouteRulesinOCI sheet)<br>
   ```DRG Route Rules```
        <br>   - Export DRG Route Rules (From OCI into DRGRouteRulesinOCI sheet)
	<br> - Add/Modify/Delete Route Rules (Reads DRGRouteRulesinOCI sheet)<br>

8. Executing terraform plan for network shows 'Up-to-Date' with no changes.

This completes the steps for Creating the Network in OCI and exporting the rules to the CD3 Excel Sheet using the Automation Toolkit.


### Use an existing DRG in OCI while creating the network
In some scenarios, a DRG has already been created in the tenancy and rest of the Network components still need to be created. In such cases, generate the networking related tfvars using same process mentioned above till Step 4. Use same name for DRG in DRGs tab as present in OCI console.

 - For Step 5, Navigate to the outdir path and execute the terraform commands:<br>
       ```
		terraform init
       ```
       ```
		terraform import "module.drgs[\"<<drgs terraform variable name>>\"].oci_core_drg.drg" <<drg_ocid>>
       ```
       → This will Import the DRG into the state file.       
       ```
		terraform plan
       ```
       → Terraform Plan will indicate to add all the other components except DRG.
       ```
		terraform apply
       ```

   Continue executing the remaining steps (from Step 6) of [Create Network](#create-network).

!!! Note
    When using the toolkit with Jenkins, the apply pipeline for network will need to be stopped before  running terraform import command for DRG. After terraform import cmd has been executed successfully, re-launch the apply pipeline for network folder.


### Modify Security Rules, Route Rules and DRG Route Rules

Follow the below steps to add, update or delete the following components:
- Security Lists and Security Rules
- Route Table and Route Rules
- DRG Route Table and DRG Route Rules

1. Modify the Excel sheet to update required data in the Tabs - RouteRulesInOCI, SecRulesInOCI, DRGRouteRulesInOCI tabs. <br>

2. Execute _setupOCI_ with _Create Resources_ workflow.
   
3. Choose _'Network'_ from the displayed menu. Choose below sub-options:<br>
    ```Security Rules```
      <br> - Add/Modify/Delete Security Rules (Reads SecRulesinOCI sheet)<br>
    ```Route Rules```
      <br> - Add/Modify/Delete Route Rules (Reads RouteRulesinOCI sheet)<br>
    ```DRG Route Rules```
      <br> - Add/Modify/Delete DRG Route Rules (Reads DRGRouteRulesinOCI sheet)

     Once the execution is successful, _<prefix\>_seclists.auto.tfvars_, _<prefix\>_routetables.auto.tfvars_ and _<prefix\>_drg-routetables.auto.tfvars_ file will be generated under the folder ```/cd3user/tenancies/<prefix>/terraform_files/<region_dir>.``` Existing files will move into respective backup folders.
 
    !!! note 
        This will create TF for only those Security Lists and Route Tables in VCNs which are part of cd3 and skip any VCNs that have been created outside of cd3 execution.


4. Look at the terraform plan and apply. Running terraform apply completes the modification of Security Rules, Route Rules and DRG Route Rules in OCI. Verify the components in console.<br>

### Modify Network 
Modifying the Networking components using Automation Toolkit involves three simple steps.

 - Add/modify the details of networking components like the VCNs, Subnets, DHCP and DRG in Excel Sheet.<br>
 - Running the toolkit with 'Create Resources' workflow to generate *.auto.tfvars.<br>
 - Executing Terraform to provision/modify resources in OCI.
 
 Follow [these steps](#modify-security-rules-route-rules-and-drg-route-rules) to modify Security Rules, Route Rules and DRG Route Rules.


1. Modify the Excel sheet to update required data in the Tabs - VCNs, DRGs, VCN Info, DHCP and Subnets. <br>

2. Execute _setupOCI_ with _Create Resources_ workflow.

3. To Validate the CD3 excel Tabs - choose option _'Validate CD3'_ and _'Validate Networks'_ from sub-menu to check for syntax errors in Excel sheet. Examine the log file generated at ```/cd3user/tenancies/<prefix>/<prefix>_cd3validator.logs.``` If there are errors, rectify them accordingly and proceed to the next step. <br>

4. Choose option _'Modify Network'_ under _'Network'_ from the displayed menu. Once the execution is successful, multiple .tfvars related to networking like _<prefix\>_major-objects.auto.tfvars_ and more will be generated under the folder ```/cd3user/tenancies/<prefix>/terraform_files/<region_dir>/<service_dir>```. Existing files will move into respective backup folders.<br>
   **Note-**: Make sure to export Sec Rules, Route Rules, DRG Route Rules to CD3 Excel Sheet before executing this option. <br>

5. Look at the terraform plan and apply. Running terraform apply completes the modification of Networking components in OCI. Verify the components in console.

### Sync manual changes done in OCI of Security Rules, Route Rules and DRG Route Rules with CD3 Excel Sheet and Terraform
Follow the below process to export the rules to the same CD3 Excel Sheet as the one used to Create Network, and to sync the Terraform files with OCI whenever a user adds, modifies or deletes rules in OCI Console manually.

!!! note 
      Make sure to close the Excel sheet during the export process.
                       
1. Execute _setupOCI_ with _Create Resources_ workflow.

2. Choose _'Network'_ from the displayed menu. Choose below sub-options:<br>
   ```Security Rules```
      <br> - Export Security Rules (From OCI into SecRulesinOCI sheet)<br>
   ```Route Rules```
      <br> - Export Route Rules (From OCI into RouteRulesinOCI sheet)<br>
   ```DRG Route Rules```
      <br> - Export DRG Route Rules (From OCI into DRGRouteRulesinOCI sheet)

    Once the execution is successful, 'RouteRulesInOCI', 'SecRulesInOCI', 'DRGRouteRulesInOCI' tabs of the excel sheet will be updated with the rules exported from OCI. At this point, we only have our Excel sheet Tabs updated, proceed to the next step to create the Terraform Files for the same.
 
3. Choose _'Network'_ from the displayed menu. Choose below sub-options:<br>
   ```Security Rules```
      <br> -Add/Modify/Delete Security Rules (Reads SecRulesinOCI sheet)<br>
   ```Route Rules```
      <br> - Add/Modify/Delete Route Rules (Reads RouteRulesinOCI sheet)<br>
   ```DRG Route Rules```
      <br> - Add/Modify/Delete DRG Route Rules (Reads DRGRouteRulesinOCI sheet)

     Once the execution is successful, _<prefix\>_seclists.auto.tfvars_,  _<prefix\>_routetables.auto.tfvars_ and  _<prefix\>drg-routetables.auto.tfvars_ files will be generated under the folder ```/cd3user/tenancies/<prefix>/terraform_files/<region_dir>/<service_dir>```
    
4. Look at the terraform plan and apply. Running terraform apply completes the export of Security Rules, Route Rules and DRG Route Rules from OCI. Terraform plan/apply should be in sync with OCI.
    

### Add/Modify/Delete NSGs

1.  Modify the Excel sheet to update required data in the Tabs - NSGs. <br>

2. Execute _setupOCI_ with _Create Resources_ workflow.

3. Choose _'Network'_ from the displayed menu. Choose below sub-option:<br>
   	```Network Security Groups```
      <br> - Add/Modify/Delete NSGs (Reads NSGs sheet)
    
     Once the execution is successful,  ```<prefix>_nsgs.auto.tfvars``` will be generated under the folder ```/cd3user/tenancies/<prefix>/terraform_files/<region_dir>/<service_dir>```. Existing files will move into respective backup folders.
    
4. Look at the terraform plan and apply. Running terraform apply completes the modification of NSGs in OCI. Verify the components in console.


### Add/Modify/Delete VLANs


1.  Modify the Excel sheet to update required data in the Tabs - SubnetsVLANs. <br>

2.  Make sure that the RouteRulesinOCI sheet and corresponding terraform is in synch with route rules in OCI console. If not, follow the procedure specified in [Sync manual changes done in OCI of Security Rules, Route Rules and DRG Route Rules with CD3 Excel Sheet and Terraform](#sync-manual-changes-done-in-oci-of-security-rules-route-rules-and-drg-route-rules-with-cd3-excel-sheet-and-terraform) <br>
  
3. Execute _setupOCI_ with _Create Resources_ workflow.
  
4. Choose _'Network'_ from the displayed menu. Choose below sub-option: <br>
   ```- Add/Modify/Delete VLANs (Reads SubnetsVLANs sheet)```
    
      Once the execution is successful, ```<prefix>\_vlans.auto.tfvars``` will be generated under the folder   ```/cd3user/tenancies/<prefix>/terraform_files/<region_dir>/<service_dir>.``` Existing files will move into respective backup folders.```<prefix>_routetables.auto.tfvars``` file will also be updated with the route table information specified for each VLAN.
    
5. Look at the terraform plan and apply. Run terraform apply.

6.  Again make sure to export the Route Rules in OCI into excel and terraform. Follow the procedure specified in [Sync manual changes done in OCI of Security Rules, Route Rules and DRG Route Rules with CD3 Excel Sheet and Terraform](#sync-manual-changes-done-in-oci-of-security-rules-route-rules-and-drg-route-rules-with-cd3-excel-sheet-and-terraform) 

This completes the modification of VLANs in OCI. Verify the components in console.

### RPCs
Remote VCN peering is the process of connecting two VCNs in different regions (but the same tenancy). The peering allows the VCNs' resources to communicate using private IP addresses without routing the traffic over the internet or through your on-premises network.
 
   - Modify the Excel sheet to update required data in the Tabs - DRGs.
   - The source and target RPC details to be entered in DRG sheet for establishing a connection. Check the example in excel file for reference.
   - Make sure that the DRGRouteRulesinOCI sheet and corresponding terraform is in synch with DRG route rules in OCI console. If not, follow the procedure specified in [Sync manual changes done in OCI of Security Rules, Route Rules and DRG Route Rules with CD3 Excel Sheet and Terraform](#sync-manual-changes-done-in-oci-of-security-rules-route-rules-and-drg-route-rules-with-cd3-excel-sheet-and-terraform)
   - Global directory which is inside the customer outdir will have all RPC related files and scripts.
   - The RPC resources(modules,provider configurations etc) are generated dynamically for the tenancy and can work along only with CD3 automation toolkit.
   - Choose option 'Network' and then 'Customer Connectivity' for creating RPC in create_resources (GreenField) workflow.
   - Output files are created under ```/cd3user/tenancies/<prefix>/terraform_files/global/rpc``` directory

## Export Existing Network Resources from OCI (Non-Greenfield Workflow)

 - [Export Network](#export-network)
 - [Add a new or modify the existing networking components](#add-a-new-or-modify-the-existing-networking-components)


!!! note
    Make sure to execute "Fetch Compartments OCIDs to variables file" from CD3 Services in setUpOCI menu before starting with Network Creation.

### Export Network

Follow the below steps to export the Networking components that includes VCNs, Subnets, DHCP, DRG, Security List, Route Tables, DRG Route Tables, NSGs, etc to CD3 Excel Sheet and create the Terraform state.

1. Use the [CD3-Blank-Template.xlsx](https://github.com/oracle-devrel/cd3-automation-toolkit/blob/main/cd3_automation_toolkit/example) to export the networking resources into the Tabs - VCNs, DRGs, VCN Info, DHCP, Subnets, NSGs, RouteRulesInOCI, SecRulesInOCI,DRGRouteRulesInOCI tabs. <br>
 
2. Execute _setupOCI_ with _Export Resources_ workflow.

3. Choose one of the below available sub-options from _'Export Network'_ of the main menu. 
      - Export all Network Components
      - Export Network components for VCNs/DRGs/DRGRouteRulesinOCI Tabs
      - Export Network components for DHCP Tab
      - Export Network components for SecRulesinOCI Tab
      - Export Network components for RouteRulesinOCI Tab
      - Export Network components for SubnetsVLANs Tab
      - Export Network components for NSGs Tab
   
     Once the execution is successful, networking related *.auto.tfvars files and .sh files containing import statements will be generated under the folder ```/cd3user/tenancies/<prefix>/terraform_files/<region_dir>/<service_dir>```
   
     Also,The RPC related .tfvars and .sh files containing import statements will be generated in global directory which is inside the ```/cd3user/tenancies/<prefix>/terraform_files/``` folder. 
     
4. Execute *import_commands_network_major-objects.sh* and then rest of the sh files. **These will be automatically executed while using the toolkit with Jenkins.**

!!! note
      The **oci_core_drg_attachment_management** for RPC resources will be shown as created at the end of import process, but it doesn't actually create any resources and can be safely ignored.

   <img width="870" alt="rpc" src="../images/clinetworkexport-1.png">
    


   5.Running  terraform plan must show that all the components are in sync. This completes the export of Networking components from OCI.

**Sample of CD3 Excel after export:**
<br>(DO NOT Modify the highlighted columns)

(Showing old images below)
<br>VCNs tab:
![image](../images/clinetworkexport-2.png)

Subnets tab:
![image](../images/clinetworkexport-3.png)


### Add a new or modify the existing networking components
1. Export the Networking components by following the steps [above](#export-network). (Note that here _Workflow Type_ is set to _Export Resources_)
2. Follow the [process](manage-network.md#modify-network) to add new components such as VCN/DHCP/DRG/IGW/NGW/SGW/LPG/Subnet etc. (Note that here _Workflow Type_ is set to _Create Resources_)




