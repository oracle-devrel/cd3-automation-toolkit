# Networking Scenarios 

## Greenfield Tenancies

**NOTE-**
Before you start with Network Creation, make sure you have run 'Fetch Compartments OCIDs to variables file'.

### 1. Create Network
Follow the below steps to create Network that includes VCNs, Subnets, DHCP, DRG, Security List, Route Tables, DRG Route Tables, NSGs, etc.

1. Choose appropriate excel sheet from [Excel Templates](/cd3_automation_toolkit/documentation/user_guide/Essentials_of_Automation_Toolkit.md#excel-sheet-templates) and fill the required Network details in the Networking Tabs - VCNs, DRGs, VCN Info, DHCP, Subnets, NSGs tabs.
   
2. Execute the _setupOCI.py_ file with _non_gf_tenancy_ parameter value to _false_:
   
   ```python setUpOCI.py /cd3user/tenancies/<customer_name>/<customer_name>_setUpOCI.properties```
   
3. Choose option _'Validate CD3'_ and then _'Validate Network(VCNs, Subnets, DHCP, DRGs)'_ to check for syntax errors in Excel sheet. Examine the log file generated at _/cd3user/tenancies/<customer\_name>/<customer\_name>\_cd3validator.log_. If there are errors, please rectify them accordingly and proceed to the next step.

4. Choose option to _'Create Network'_ under _'Network'_ from the displayed menu. Once the execution is successful, multiple .tfvars related to networking like _<customer\_name>\_major-objects.auto.tfvars_ and more will be generated under the folder _/cd3user/tenancies/<customer\_name>/terraform_files/<region_dir>_
    
5. Navigate to the above path and execute the terraform commands:<br>
       <br>_terraform init_
       <br>_terraform plan_
       <br>_terraform apply_
   
This completes the creation of Networking components in OCI. Verify the components in console. 
### 2. Use an existing DRG in OCI while creating the network
In some scenarios, a DRG has already been created in the tenancy and rest of the Network components still need to be created. In such cases, generate the networking related tfvars using same process mentioned above till Step 4.

For Step5, Navigate to the outdir path and execute the terraform commands:<br>
       <br>_terraform init_
       <br>_terraform import "module.drgs[\"&lt;&lt;drgs terraform variable name&gt;&gt;\"].oci_core_drg.drg"_
       <br>&nbsp;&nbsp;→ This will Import the DRG into your state file.       
       _terraform plan_
       <br>&nbsp;&nbsp;→ Terraform Plan will indicate to add all the other components except DRG.
       <br>_terraform apply_

### 3. Export the Security, Route Rules and DRG Route Rules into CD3 Excel Sheet
Once you have the Networking components created in OCI for the first time, export the rules to the CD3 Excel Sheet using the following steps: 
 
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
    
**NOTE-**: The user may also choose to add, modify or delete rules in OCI Console manually at any point of time. Once all the desired changes are complete wrt rules, repeat the above process to sync the Terraform files with OCI.

### 4. Add, Update, Delete Security Rules, Route Rules and DRG Route Rules

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
   
   This completes the modification of Security Rules, Route Rules and DRG Route Rules in OCI. Verify the components in console.

### 5. Modify Network

Follow the below steps to add a new or modify the existing Networking components - VCNs, Subnets, DHCP and DRG.

1.  Modify your excel sheet to update required data in the Tabs - VCNs, DRGs, VCN Info, DHCP and Subnets.
   
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

### 6. Add/Modify/Delete NSGs
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

## Non-Greenfield Tenancies
**NOTE-**
Before you start with Network Export, make sure you have run 'Fetch Compartments OCIDs to variables file'.

### 1. Export Network

Follow the below steps to export the Networking components that includes VCNs, Subnets, DHCP, DRG, Security List, Route Tables, DRG Route Tables, NSGs, etc to CD3 Excel Sheet and create the Terraform state.

1. Use the [CD3-Blank-Template.xlsx](/cd3_automation_toolkit/example) to export the networking resources into the Tabs - VCNs, DRGs, VCN Info, DHCP, Subnets, NSGs, RouteRulesInOCI, SecRulesInOCI,DRGRouteRulesInOCI tabs.
   
2. Execute the _setupOCI.py_ file with _non_gf_tenancy_ parameter value to _true_:
   
   ```python setUpOCI.py /cd3user/tenancies/<customer_name>/<customer_name>_setUpOCI.properties```
   
3. Choose one of the below available sub-options from _'Export Network'_ of the main menu. 
   - Export all Network Components
   - Export Network components for VCNs, DRGs and DRGRouteRulesinOCI Tabs
   - Export Network components for DHCP Tab
   - Export Network components for SecRulesinOCI Tab
   - Export Network components for RouteRulesinOCI Tab
   - Export Network components for Subnets Tab
   - Export Network components for NSGs Tab
   
   Once the execution is successful, networking related .tfvars files and .sh files containing import statements will be generated under the folder _/cd3user/tenancies/<customer\_name>/terraform_files/<region_dir>_
    
   Navigate to the above path and execute the terraform commands:<br>
       <br>_terraform init_
       <br>_Execute the shell scirpts of networking components_
       <br>_terraform plan_
       <br>&nbsp;&nbsp;→ Terraform Plan must show that all the components are in sync.
   
This completes the export of Networking components from OCI.

**Sample of CD3 Excel after export:**
<br>(DO NOT Modify the highlighted columns)

VCNs tab:
![image](https://user-images.githubusercontent.com/115973871/214372501-65e68d60-bedd-4df9-bf84-a2316d0f6c62.png)

Subnets tab:
![image](https://user-images.githubusercontent.com/115973871/214372535-69714cbc-1980-4dd5-ae52-e20441903d8a.png)

### 2. Add a new or modify the existing networking components
1. Export the Networking components by following the steps [above](#1-export-network). (Note that here _non\_gf\_tenancy_ flag is set to true)
2. Follow the [process](#5-modify-network) to add new components such as VCN/DHCP/DRG/IGW/NGW/SGW/LPG/Subnet etc. (Note that here _non\_gf\_tenancy_ flag is set to false)

   


<br><br>
<div align='center'>

| <a href="/cd3_automation_toolkit/documentation/user_guide/Workflows.md">:arrow_backward: Prev</a> | <a href="/cd3_automation_toolkit/documentation/user_guide/QuickstartNGF.md">Next :arrow_forward:</a> |
| :---- | -------: |
  
</div>
