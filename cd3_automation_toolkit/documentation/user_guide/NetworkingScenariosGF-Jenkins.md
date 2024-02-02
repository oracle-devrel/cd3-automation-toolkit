# Executing Networking Scenarios using toolkit via Jenkins

## Managing Network for Greenfield Workflow
- [Create Network](#create-network)
- [Modify Network](#modify-network)
- [Modify Security Rules, Route Rules and DRG Route Rules](#modify-security-rules-route-rules-and-drg-route-rules)
- [Sync manual changes done in OCI of Security Rules, Route Rules and DRG Route Rules with CD3 Excel Sheet and Terraform](#sync-manual-changes-done-in-oci-of-security-rules-route-rules-and-drg-route-rules-with-cd3-excel-sheet-and-terraform)
- [Add/Modify/Delete NSGs](#addmodifydelete-nsgs)
- [Add/Modify/Delete VLANs](#addmodifydelete-vlans)
- [Remote Peering Connections](#rpcs)


**NOTE-**

### Create Network
Creation of Networking components using Automation Toolkit involves four simple steps.
 - Add the networking resource details to appropriate Excel Sheets.
 - Running the setUpOCI pipeline in the toolkit to generate auto.tfvars.
 - Executing terraform pipeline to provision the resources in OCI.
 - Exporting the automatically generated Security Rules and Route Rules by the toolkit to CD3 Excel Sheet.
 
Below are the steps in detail to create Network that includes VCNs, Subnets, DHCP, DRG, Security List, Route Tables, DRG Route Tables, NSGs, etc.

1. Choose appropriate excel sheet from [Excel Templates](/cd3_automation_toolkit/documentation/user_guide/RunningAutomationToolkit.md#excel-sheet-templates) and fill the required Network details in the Networking Tabs - VCNs, DRGs, VCN Info, DHCP, Subnets, NSGs tabs.
   
2. Execute the _setupOCI_ pipeline with _Workflow_ as _Create Resources in OCI(Greenfield Workflow)_
   
3. Choose option _'Validate CD3'_ and then _'Validate Networks'_ to check for syntax errors in Excel sheet. Examine the log file generated at _/cd3user/tenancies/<customer\_name>/<customer\_name>\_cd3validator.log_. If there are errors, please rectify them accordingly and proceed to the next step.

4. Choose _'Create Network'_ under _'Network'_ from the displayed options. Click on Build.
   
<img width="347" alt="Screenshot 2024-02-02 at 7 46 37 AM" src="https://github.com/oracle-devrel/cd3-automation-toolkit/assets/103508105/c16f8d7b-dd8d-484d-b873-f5ad36facfa9">

6. It will show different stages of execution of _setUpOCI_ pipeline and also launch the _terraform-apply_ pipeline for 'network'.
7. Click on Proceed for 'Get Approval' stage of the terraform pipeline.
       
   This completes the creation of Networking components in OCI. Verify the components in console. However the details of the default security lists and default route tables may not be available in the CD3 Excel sheet yet. Inorder to export that data please follow the below steps:

8. Execute the _setupOCI.py_ pipeline with _Workflow_ as _Create Resources in OCI(Greenfield Workflow)_
9. Choose _'Network'_ from the displayed options. Choose below sub-options: (Make sure to choose all the three optionsfor the first time)
   - Security Rules
      - Export Security Rules (From OCI into SecRulesinOCI sheet)
   - Route Rules
      - Export Route Rules (From OCI into RouteRulesinOCI sheet)
   - DRG Route Rules
      - Export DRG Route Rules (From OCI into DRGRouteRulesinOCI sheet)
    Click on Build.
        
  <img width="604" alt="Screenshot 2024-02-02 at 7 45 16 AM" src="https://github.com/oracle-devrel/cd3-automation-toolkit/assets/103508105/6d142aa0-7549-4306-a51f-77552d32c2bd">


This completes the steps for Creating the Network in OCI and exporting the default rules to the CD3 Excel Sheet using the Automation Toolkit.

<br>[Go back to Networking Scenarios](#networking-scenarios)
### Modify Network 
Modifying the Networking components using Automation Toolkit involves three simple steps.
 - Add/modify the details of networking components like the VCNs, Subnets, DHCP and DRG in Excel Sheet.
 - Running the the setUpOCI pipeline in the toolkit to generate auto.tfvars.
 - Executing Terraform pipeline to provision/modify the resources in OCI.

 ***Note***: Follow [these steps](#3-modify-security-rules-route-rules-and-drg-route-rules) to modify Security Rules, Route Rules and DRG Route Rules

_Steps in detail_:
1. Modify your excel sheet to update required data in the Tabs - VCNs, DRGs, VCN Info, DHCP and Subnets.
2. Execute the _setupOCI.py_ pipeline with _Workflow_ as _Create Resources in OCI(Greenfield Workflow)_
3. To Validate the CD3 excel Tabs - Choose option _'Validate CD3'_ and _'Validate Networks'_ from sub-menu to check for syntax errors in Excel sheet. Examine the log file generated at _/cd3user/tenancies/<customer\_name>/<customer\_name>\_cd3validator.logs_. If there are errors, please rectify them accordingly and proceed to the next step.
4. Choose option to _'Modify Network'_ under _'Network'_ from the displayed options. Once the execution is successful, multiple .tfvars related to networking like _<customer\_name>\_major-objects.auto.tfvars_ and more will be generated under the folder _/cd3user/tenancies/<customer\_name>/terraform_files/<region_dir>/<service_dir>_. Existing files will move into respective backup folders.
    
   **Note-**: Make sure to export Sec Rules, Route Rules, DRG Route Rules to CD3 Excel Sheet before executing this option.

6. It will show different stages of execution of _setUpOCI_ pipeline and also launch the _terraform-apply_ pipeline for 'network'.
7. Click on Proceed for 'Get Approval' stage of the terraform pipeline.
   
This completes the modification of Networking components in OCI. Verify the components in console.

<br>[Go back to Networking Scenarios](#networking-scenarios)
### Modify Security Rules, Route Rules and DRG Route Rules

Follow the below steps to add, update or delete the following components:
- Security Lists and Security Rules
- Route Table and Route Rules
- DRG Route Table and DRG Route Rules

1. Modify your excel sheet to update required data in the Tabs - RouteRulesInOCI, SecRulesInOCI, DRGRouteRulesInOCI tabs.

2. Execute the _setupOCI.py_ pipeline with _Workflow_ as _Create Resources in OCI(Greenfield Workflow)_
   
3. Choose _'Network'_ from the displayed options. Choose below sub-options:
   - Security Rules
      - Add/Modify/Delete Security Rules (Reads SecRulesinOCI sheet)
   - Route Rules
      - Add/Modify/Delete Route Rules (Reads RouteRulesinOCI sheet)
   - DRG Route Rules
      - Add/Modify/Delete DRG Route Rules (Reads DRGRouteRulesinOCI sheet)

   Once the execution is successful, _<customer\_name>\_seclists.auto.tfvars_, _<customer\_name>\_routetables.auto.tfvars_ and _<customer\_name>\_drg-routetables.auto.tfvars_ file will be generated under the folder _/cd3user/tenancies/<customer\_name>/terraform_files/<region_dir>_. Existing files will move into respective backup folders.

   **NOTE**: This will create TF for only those Security Lists and Route Tables in VCNs which are part of cd3 and skip any VCNs that have been created outside of cd3 execution.

4. It will show different stages of execution of _setUpOCI_ pipeline and also launch the _terraform-apply_ pipeline for 'network'.
5. Click on Proceed for 'Get Approval' stage of the terraform pipeline.
   
   This completes the modification of Security Rules, Route Rules and DRG Route Rules in OCI. Verify the components in console.<br>

<br>[Go back to Networking Scenarios](#networking-scenarios)
### Sync manual changes done in OCI of Security Rules, Route Rules and DRG Route Rules with CD3 Excel Sheet and Terraform
Follow the below process to export the rules to the same CD3 Excel Sheet as the one used to Create Network, and to sync the Terraform files with OCI whenever an user adds, modifies or deletes rules in OCI Console manually.

**NOTE**: Make sure to close your Excel sheet during the export process.
                       
1. Execute the _setupOCI.py_ pipeline with _Workflow_ as _Create Resources in OCI(Greenfield Workflow)_
   
2. Choose _'Network'_ from the displayed menu. Choose below sub-options:
   - Security Rules
      - Export Security Rules (From OCI into SecRulesinOCI sheet)
      - Add/Modify/Delete Security Rules (Reads SecRulesinOCI sheet)
   - Route Rules
      - Export Route Rules (From OCI into RouteRulesinOCI sheet)
      - Add/Modify/Delete Route Rules (Reads RouteRulesinOCI sheet)
   - DRG Route Rules
      - Export DRG Route Rules (From OCI into DRGRouteRulesinOCI sheet)
      - Add/Modify/Delete DRG Route Rules (Reads DRGRouteRulesinOCI sheet)
 
    Once the execution is successful, 'RouteRulesInOCI', 'SecRulesInOCI', 'DRGRouteRulesInOCI' tabs of the excel sheet will be updated with the rules exported from OCI. And _<customer\_name>\_seclists.auto.tfvars_,  _<customer\_name>\routetables.auto.tfvars_ and  _<customer\_name>\drg-routetables.auto.tfvars_ file will be generated under the folder _/cd3user/tenancies/<customer\_name>/terraform_files/<region_dir>/<service_dir>_
    
 4. It will show different stages of execution of _setUpOCI_ pipeline and also launch the _terraform-apply_ pipeline for 'network'.
 5. Click on Proceed for 'Get Approval' stage of the terraform pipeline.
   
   This completes the export of Security Rules, Route Rules and DRG Route Rules from OCI. Terraform plan/apply should be in sync with OCI.
    
<br>[Go back to Networking Scenarios](#networking-scenarios)
### Add/Modify/Delete NSGs
Follow the below steps to update NSGs.

1. Modify your excel sheet to update required data in the Tabs - NSGs.
   
2. Execute the _setupOCI.py_ pipeline with _Workflow_ as _Create Resources in OCI(Greenfield Workflow)_
   
3. Choose _'Network'_ from the displayed menu. Choose below sub-option:
   - Network Security Groups
      - Add/Modify/Delete NSGs (Reads NSGs sheet)
    
     Once the execution is successful,  _<customer\_name>\_nsgs.auto.tfvars_ will be generated under the folder _/cd3user/tenancies/<customer\_name>/terraform_files/<region_dir>/<service_dir>_. Existing files will move into respective backup folders.
    
4. It will show different stages of execution of _setUpOCI_ pipeline and also launch the _terraform-apply_ pipeline for 'nsg'.
5. Click on Proceed for 'Get Approval' stage of the terraform pipeline.
   
This completes the modification of NSGs in OCI. Verify the components in console.

<br>[Go back to Networking Scenarios](#networking-scenarios)

### Add/Modify/Delete VLANs
Follow the below steps to update VLANs.

1.  Modify your excel sheet to update required data in the Tabs - SubnetsVLANs.
2.  Make sure that the RouteRulesinOCI sheet and corresponing terraform is in synch with route rules in OCI console. If not, please follow procedure specified in [Sync manual changes done in OCI of Security Rules, Route Rules and DRG Route Rules with CD3 Excel Sheet and Terraform](#sync-manual-changes-done-in-oci-of-security-rules-route-rules-and-drg-route-rules-with-cd3-excel-sheet-and-terraform) 
   
3. Execute the _setupOCI.py_ pipeline with _Workflow_ as _Create Resources in OCI(Greenfield Workflow)_
4. Choose _'Network'_ from the displayed menu. Choose below sub-option:
   - Add/Modify/Delete VLANs (Reads SubnetsVLANs sheet)
    
     Once the execution is successful,  _<customer\_name>\_vlans.auto.tfvars_ will be generated under the folder _/cd3user/tenancies/<customer\_name>/terraform_files/<region_dir>/<service_dir>_. Existing files will move into respective backup folders.  _<customer\_name>\routetables.auto.tfvars_ file will also be updated with the route table information specified for each VLAN.
    
4. It will show different stages of execution of _setUpOCI_ pipeline and also launch the _terraform-apply_ pipeline for 'vlan' and 'network'.
5. Click on Proceed for 'Get Approval' stage of the terraform pipeline.
  
6.  Again make sure to export the Route Rules in OCI into excel and terraform. Please follow procedure specified in [Sync manual changes done in OCI of Security Rules, Route Rules and DRG Route Rules with CD3 Excel Sheet and Terraform](#sync-manual-changes-done-in-oci-of-security-rules-route-rules-and-drg-route-rules-with-cd3-excel-sheet-and-terraform) 

This completes the modification of VLANs in OCI. Verify the components in console.

### RPCs
Remote VCN peering is the process of connecting two VCNs in different regions (but the same tenancy). The peering allows the VCNs' resources to communicate using private IP addresses without routing the traffic over the internet or through your on-premises network.
 
   - Modify your excel sheet to update required data in the Tabs - DRGs.
   - The source and target RPC details to be entered in DRG sheet for establishing a connection. Please check the example in excel file for reference.
   - Make sure that the DRGRouteRulesinOCI sheet and corresponding to terraform is in synch with DRG route rules in OCI console. If not, please follow procedure specified in [Sync manual changes done in OCI of Security Rules, Route Rules and DRG Route Rules with CD3 Excel Sheet and Terraform](#sync-manual-changes-done-in-oci-of-security-rules-route-rules-and-drg-route-rules-with-cd3-excel-sheet-and-terraform)
   - Global directory which is inside the customer outdir will have all RPC related files and scripts.
   - The RPC resources(modules,provider configurations etc) are generated dynamically for the tenancy and can work along only with CD3 automation toolkit.
   - Choose option 'Network' and then 'Customer Connectivity' for creating RPC in GreenField workflow.
   - Output files are created under _/cd3user/tenancies/<customer\_name>/terraform_files/global/rpc_ directory

<br>[Go back to Networking Scenarios](#networking-scenarios)
<br><br>
<div align='center'>

| <a href="/cd3_automation_toolkit/documentation/user_guide/learn_more/OPAForCompliance.md">:arrow_backward: Prev</a> | <a href="/cd3_automation_toolkit/documentation/user_guide/ComputeGF.md">Next :arrow_forward:</a> |
| :---- | -------: |
  
</div>
