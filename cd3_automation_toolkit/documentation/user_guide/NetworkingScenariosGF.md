# Networking Scenarios 

## Greenfield Tenancies (Managing Network for Green Field Tenancies)
- [Create Network](#create-network)
- [Use an existing DRG in OCI while creating the network](#use-an-existing-drg-in-oci-while-creating-the-network)
- [Modify Network](#modify-network)
- [Modify Security Rules, Route Rules and DRG Route Rules](#modify-security-rules-route-rules-and-drg-route-rules)
- [Sync manual changes done in OCI of Security Rules, Route Rules and DRG Route Rules with CD3 Excel Sheet and Terraform](#sync-manual-changes-done-in-oci-of-security-rules-route-rules-and-drg-route-rules-with-cd3-excel-sheet-and-terraform)
- [Add/Modify/Delete NSGs](#addmodifydelete-nsgs)


**NOTE-**
Before you start with Network Creation, make sure you have run 'Fetch Compartments OCIDs to variables file'.

### Create Network
Creation of Networking components using Automation Toolkit involes four simple steps.
 - Add the networking resource details to appropriate Excel Sheets.
 - Running the toolkit to generate auto.tfvars.
 - Executing Terraform commands to provision the resources in OCI.
 - Exporting the automatically generated Security Rules and Route Rules by the toolkit to CD3 Excel Sheet.
 
Below are the steps in detail to create Network that includes VCNs, Subnets, DHCP, DRG, Security List, Route Tables, DRG Route Tables, NSGs, etc.

1. Choose appropriate excel sheet from [Excel Templates](/cd3_automation_toolkit/documentation/user_guide/RunningAutomationToolkit.md#excel-sheet-templates) and fill the required Network details in the Networking Tabs - VCNs, DRGs, VCN Info, DHCP, Subnets, NSGs tabs.
   
2. Execute the _setupOCI.py_ file with _non_gf_tenancy_ parameter value to _false_:
   
   ```python setUpOCI.py /cd3user/tenancies/<customer_name>/<customer_name>_setUpOCI.properties```
   
3. Choose option _'Validate CD3'_ and then _'Validate Network(VCNs, Subnets, DHCP, DRGs)'_ to check for syntax errors in Excel sheet. Examine the log file generated at _/cd3user/tenancies/<customer\_name>/<customer\_name>\_cd3validator.log_. If there are errors, please rectify them accordingly and proceed to the next step.

4. Choose option to _'Create Network'_ under _'Network'_ from the displayed menu. Once the execution is successful, multiple .tfvars related to networking like _<customer\_name>\_major-objects.auto.tfvars_ and more will be generated under the folder _/cd3user/tenancies/<customer\_name>/terraform_files/<region_dir>_
    
5. Navigate to the above path and execute the terraform commands:<br>
       <br>_terraform init_
       <br>_terraform plan_
       <br>_terraform apply_
       
   This completes the creation of Networking components in OCI. Verify the components in console. However the details of the default security lists and default route tables may not be available in the CD3 Excel sheet yet. Inorder to export that data please follow the below steps:

6. Execute the _setupOCI.py_ file with _non_gf_tenancy_ parameter value to _false_:
   
   ```python setUpOCI.py /cd3user/tenancies/<customer_name>/<customer_name>_setUpOCI.properties```
   
7. Choose _'Network'_ from the displayed menu. Choose below sub-options: (Make sure to choose all the three optionsfor the first time)
   - Security Rules
      - Export Security Rules (From OCI into SecRulesinOCI sheet)
   - Route Rules
      - Export Route Rules (From OCI into RouteRulesinOCI sheet)
   - DRG Route Rules
      - Export DRG Route Rules (From OCI into DRGRouteRulesinOCI sheet)

This completes the steps for Creating the Network in OCI and exporting the default rules to the CD3 Excel Sheet using the Automation Toolkit.

### Use an existing DRG in OCI while creating the network
In some scenarios, a DRG has already been created in the tenancy and rest of the Network components still need to be created. In such cases, generate the networking related tfvars using same process mentioned above till Step 4.

 - For Step 5, Navigate to the outdir path and execute the terraform commands:<br>
       <br>_terraform init_
       <br>_terraform import "module.drgs[\"&lt;&lt;drgs terraform variable name&gt;&gt;\"].oci_core_drg.drg" &lt;&lt;drg-ocid&gt;&gt;_
       <br>&nbsp;&nbsp;→ This will Import the DRG into your state file.       
       _terraform plan_
       <br>&nbsp;&nbsp;→ Terraform Plan will indicate to add all the other components except DRG.
       <br>_terraform apply_

   Continue executing the remaining steps (from Step 6) of [Create Network](#1-create-network).

<br>[Go back to Networking Scenarios](#greenfield-tenancies)
### Modify Network 
Modifying the Networking components using Automation Toolkit involves three simple steps.
 - Add/modify the details of networking components like the VCNs, Subnets, DHCP and DRG in Excel Sheet.
 - Running the toolkit to generate auto.tfvars.
 - Executing Terraform commands to provision/modify the resources in OCI.

 ***Note***: Follow [these steps](#3-modify-security-rules-route-rules-and-drg-route-rules) to modify Security Rules, Route Rules and DRG Route Rules

_Steps in detail_:
1. Modify your excel sheet to update required data in the Tabs - VCNs, DRGs, VCN Info, DHCP and Subnets.
   
2. Execute the _setupOCI.py_ file with _non_gf_tenancy_ parameter value to _false_:
   
   ```python setUpOCI.py /cd3user/tenancies/<customer_name>/<customer_name>_setUpOCI.properties```
   
3. To Validate the CD3 excel Tabs - Choose option _'Validate CD3'_ and _'Validate Network(VCNs, Subnets, DHCP, DRGs)'_ from sub-menu to check for syntax errors in Excel sheet. Examine the log file generated at _/cd3user/tenancies/<customer\_name>/<customer\_name>\_cd3validator.logs_. If there are errors, please rectify them accordingly and proceed to the next step.

4. Choose option to _'Modify Network'_ under _'Network'_ from the displayed menu. Once the execution is successful, multiple .tfvars related to networking like _<customer\_name>\_major-objects.auto.tfvars_ and more will be generated under the folder _/cd3user/tenancies/<customer\_name>/terraform_files/<region_dir>_. Existing files will move into respective backup folders.
    
   **Note-**: Make sure to export Sec Rules, Route Rules, DRG Route Rules to CD3 Excel Sheet before executing this option.

5. Navigate to the above path and execute the terraform commands:<br>
       <br>_terraform init_
       <br>_terraform plan_
       <br>_terraform apply_
   
This completes the modification of Networking components in OCI. Verify the components in console.

<br>[Go back to Networking Scenarios](#greenfield-tenancies)
### Modify Security Rules, Route Rules and DRG Route Rules

Follow the below steps to add, update or delete the following components:
- Security Lists and Security Rules
- Route Table and Route Rules
- DRG Route Table and DRG Route Rules

1. Modify your excel sheet to update required data in the Tabs - RouteRulesInOCI, SecRulesInOCI, DRGRouteRulesInOCI tabs.

2. Execute the _setupOCI.py_ file with _non_gf_tenancy_ parameter value to _false_:
   
   ```python setUpOCI.py /cd3user/tenancies/<customer_name>/<customer_name>_setUpOCI.properties```
   
4. Choose _'Network'_ from the displayed menu. Choose below sub-options:
   - Security Rules
      - Add/Modify/Delete Security Rules (Reads SecRulesinOCI sheet)
   - Route Rules
      - Add/Modify/Delete Route Rules (Reads RouteRulesinOCI sheet)
   - DRG Route Rules
      - Add/Modify/Delete DRG Route Rules (Reads DRGRouteRulesinOCI sheet)

   Once the execution is successful, _<customer\_name>\_seclists.auto.tfvars_, _<customer\_name>\_routetables.auto.tfvars_ and _<customer\_name>\_drg-routetables.auto.tfvars_ file will be generated under the folder _/cd3user/tenancies/<customer\_name>/terraform_files/<region_dir>_. Existing files will move into respective backup folders.

   **NOTE**: This will create TF for only those Security Lists and Route Tables in VCNs which are part of cd3 and skip any VCNs that have been created outside of cd3 execution.

      Navigate to the above path and execute the terraform commands:<br>
       <br>_terraform init_
       <br>_terraform plan_
       <br>_terraform apply_
   
   This completes the modification of Security Rules, Route Rules and DRG Route Rules in OCI. Verify the components in console.<br>

<br>[Go back to Networking Scenarios](#greenfield-tenancies)
### Sync manual changes done in OCI of Security Rules, Route Rules and DRG Route Rules with CD3 Excel Sheet and Terraform
Follow the below process to export the rules to the same CD3 Excel Sheet as the one used to Create Network, and to sync the Terraform files with OCI whenever an user adds, modifies or deletes rules in OCI Console manually.

**NOTE**: Make sure to close your Excel sheet during the export process.
                       
1. Execute the _setupOCI.py_ file with _non_gf_tenancy_ parameter value to _false_:
   
   ```python setUpOCI.py /cd3user/tenancies/<customer_name>/<customer_name>_setUpOCI.properties```
   
2. Choose _'Network'_ from the displayed menu. Choose below sub-options:
   - Security Rules
      - Export Security Rules (From OCI into SecRulesinOCI sheet)
   - Route Rules
      - Export Route Rules (From OCI into RouteRulesinOCI sheet)
   - DRG Route Rules
      - Export DRG Route Rules (From OCI into DRGRouteRulesinOCI sheet)
 
    Once the execution is successful, 'RouteRulesInOCI', 'SecRulesInOCI', 'DRGRouteRulesInOCI' tabs of the excel sheet will be updated with the rules exported from OCI. At this point, we only have our Excel sheet Tabs updated, proceed to the next step to create the Terraform Files for the same.
 
3. Choose _'Network'_ from the displayed menu. Choose below sub-options:
   - Security Rules
      - Add/Modify/Delete Security Rules (Reads SecRulesinOCI sheet)
   - Route Rules
      - Add/Modify/Delete Route Rules (Reads RouteRulesinOCI sheet)
   - DRG Route Rules
      - Add/Modify/Delete DRG Route Rules (Reads DRGRouteRulesinOCI sheet)

   Once the execution is successful, _<customer\_name>\_seclists.auto.tfvars_,  _<customer\_name>\routetables.auto.tfvars_ and  _<customer\_name>\drg-routetables.auto.tfvars_ file will be generated under the folder _/cd3user/tenancies/<customer\_name>/terraform_files/<region_dir>_
    
   Navigate to the above path and execute the terraform commands:<br>
       <br>_terraform init_
       <br>_terraform plan_
       <br>_terraform apply_
   
   This completes the export of Security Rules, Route Rules and DRG Route Rules from OCI. Terraform plan/apply should be in sync with OCI.
    
<br>[Go back to Networking Scenarios](#greenfield-tenancies)
### Add/Modify/Delete NSGs
Follow the below steps to update NSGs.

1.  Modify your excel sheet to update required data in the Tabs - NSGs.
   
2. Execute the _setupOCI.py_ file with _non_gf_tenancy_ parameter value to _false_:
   
   ```python setUpOCI.py /cd3user/tenancies/<customer_name>/<customer_name>_setUpOCI.properties```
   
3. Choose _'Network'_ from the displayed menu. Choose below sub-option:
   - Network Security Groups
      - Add/Modify/Delete NSGs (Reads NSGs sheet)
    
     Once the execution is successful,  _<customer\_name>\_nsgs.auto.tfvars_ will be generated under the folder _/cd3user/tenancies/<customer\_name>/terraform_files/<region_dir>_. Existing files will move into respective backup folders.
    
4. Navigate to the above path and execute the terraform commands:<br>
       <br>_terraform init_
       <br>_terraform plan_
       <br>_terraform apply_
   
This completes the modification of NSGs in OCI. Verify the components in console.

<br>[Go back to Networking Scenarios](#greenfield-tenancies)
<br><br>
<div align='center'>

| <a href="/cd3_automation_toolkit/documentation/user_guide/NonGreenField.md">:arrow_backward: Prev</a> | <a href="/cd3_automation_toolkit/documentation/user_guide/NetworkingScenariosNGF.md">Next :arrow_forward:</a> |
| :---- | -------: |
  
</div>
