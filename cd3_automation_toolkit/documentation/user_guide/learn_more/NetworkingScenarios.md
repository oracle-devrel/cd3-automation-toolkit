# Networking Scenarios - Greenfield Workflows

## 1. Create Network
Once the necessary identity components (Compartments, Groups, Policies) are provisioned in OCI, follow the below steps to create the Network that includes VCNs, Subnets, DHCP, DRG, Security List, Route Tables, DRG Route Tables, NSGs, etc.

1. Use the excel [CD3-SingleVCN-template](/cd3_automation_toolkit/example) and fill the required Network details in the Networking Tabs - VCNs, DRGs, VCN Info, DHCP, Subnets, NSGs tabs.

   Make appropriate changes to the template. For Eg: Update the _Region_ value to your tenancy's subscribed region where you want to create the Network.
   
   Once all the required data is filled in the Excel sheet, place it at the location _/cd3user/tenancies/<customer\_name>/_ which is also mapped to your local directory.
   
2. Edit the _setUpOCI.properties_ at location:_/cd3user/tenancies /<customer\_name>/<customer\_name>\_setUpOCI.properties_ with appropriate values. 
   - Update the _cd3file_ parameter to specify the CD3 excel sheet path.
   - Set the _non_gf_tenancy_ parameter value to _false_.
  
3. Change Directory to 'cd3_automation_toolkit' :<br>
    ```cd /cd3user/oci_tools/cd3_automation_toolkit/```
    
   and execute the _setupOCI.py_ file:
   
   ```python setUpOCI.py /cd3user/tenancies/<customer_name>/<customer_name>_setUpOCI.properties```
   
4. Choose option _'Validate CD3'_ and _'Validate Network(VCNs, Subnets, DHCP, DRGs)'_ from sub-menu to check for syntax errors in Excel sheet. Examine the log file generated at /cd3user/tenancies/<customer_name>/<customer_name>\_cd3validator.logs. If there are errors, please rectify them accordingly and proceed to step 5.

5. Choose option to _'Create Network'_ under _'Network'_ from the displayed menu. Once the execution is successful, _<customer\_name>\_compartments.auto.tfvars_ file will be generated under the folder _/cd3user/tenancies/<customer\_name>/terraform_files/<region_dir>_
    
   Navigate to the above path and execute the terraform commands:<br>
       <br>_terraform init_
       <br>_terraform plan_
       <br>_terraform apply_
   
This completes the creation of Networking components in OCI. Verify the components in console.


## 2. Export the Security and Route Rules into CD3
Once you have the Networking components created in OCI for the first time,the user may choose to add, modify or delete rules in OCI Console manually at this point. Once all the desired changes are complete, export these rules to the CD3 Excel Sheets using the following steps - 
 
***Note***: Make sure to close your Excle sheet during the export process.
            Since we are doing an export, no modifications are expected to be done to the CD3 Excel sheets.
            
1. Verify the values in _setUpOCI.properties_ at location:_/cd3user/tenancies /<customer\_name>/<customer\_name>\_setUpOCI.properties_ with appropriate values. 
   -  _cd3file_ parameter specifies the CD3 excel sheet path.
   -  _non_gf_tenancy_ parameter value is set to _false_. (for Greenfield Workflow.)
   
2. Change Directory to 'cd3_automation_toolkit' :<br>
    ```cd /cd3user/oci_tools/cd3_automation_toolkit/```
    
   and execute the _setupOCI.py_ file:
   
   ```python setUpOCI.py /cd3user/tenancies/<customer_name>/<customer_name>_setUpOCI.properties```
   
3. Choose _'Network'_ from the displayed menu. Choose one or combination of the below sub-options as per requriement:
   - Security Rules
      - Export Security Rules (From OCI into SecRulesinOCI sheet)
   - Route Rules
      - Export Route Rules (From OCI into RouteRulesinOCI sheet)
   - DRG Route Rules
      - Export DRG Route Rules (From OCI into DRGRouteRulesinOCI sheet)
 
 Once the execution is successful, RouteRulesInOCI, SecRulesInOCI, DRGRouteRulesInOCI tabs of the excel sheet will be updated according to the choice made previously.
 
 At this point, we only have our Excle sheet Tabs updated, proceed to the next step to create the Terraform Files for the same.
 
4. Choose _'Network'_ from the displayed menu. Choose one or combination of the below sub-options as per requriement:
   - Security Rules
      - Add/Modify/Delete Security Rules (Reads SecRulesinOCI sheet)
   - Route Rules
      - Add/Modify/Delete Route Rules (Reads RouteRulesinOCI sheet)
   - DRG Route Rules
      - Add/Modify/Delete DRG Route Rules (Reads DRGRouteRulesinOCI sheet)

   Once the execution is successful, _<customer\_name>\_compartments.auto.tfvars_ file will be generated under the folder _/cd3user/tenancies/<customer\_name>/terraform_files/<region_dir>_
    
   Navigate to the above path and execute the terraform commands:<br>
       <br>_terraform init_
       <br>_terraform plan_
       <br>_terraform apply_
   
   This completes the export of Security Rules, Route Rules and DRG Route Rules from OCI. Terraform plan/apply should be in sync with OCI.
    

## 3. Add, Update, Delete New Security Rules, Route Rules and DRG Route Rules

Follow the below steps to add, update or delete the following components:
- Security Lists and Security Rules
- Route Table and Route Rules
- DRG Route Table and DRG Route Rules

1. Modify the excel template ([Sample Templates](/cd3_automation_toolkit/example) with the required Network details in the Tabs - RouteRulesInOCI, SecRulesInOCI, DRGRouteRulesInOCI tabs.
   Once all the Excel sheet is updated, place it at the location  _/cd3user/tenancies/<customer\_name>/_ which is also mapped to your local directory.
   
2. Edit the _setUpOCI.properties_ at location:_/cd3user/tenancies /<customer\_name>/<customer\_name>\_setUpOCI.properties_ with appropriate values. 
   - Update the _cd3file_ parameter to specify the CD3 excel sheet path.
   - Set the _non_gf_tenancy_ parameter value to _false_. (for Greenfield Workflow.)
   
3. Change Directory to 'cd3_automation_toolkit' :
    ```cd /cd3user/oci_tools/cd3_automation_toolkit/```
    
   and execute the _setupOCI.py_ file:
   
   ```python setUpOCI.py /cd3user/tenancies/<customer_name>/<customer_name>_setUpOCI.properties```
   
4. Choose _'Network'_ from the displayed menu. Choose one or combination of the below sub-options as per requriement:
   - Security Rules
      - Add/Modify/Delete Security Rules (Reads SecRulesinOCI sheet)
   - Route Rules
      - Add/Modify/Delete Route Rules (Reads RouteRulesinOCI sheet)
   - DRG Route Rules
      - Add/Modify/Delete DRG Route Rules (Reads DRGRouteRulesinOCI sheet)

   Once the execution is successful, _<customer\_name>\_compartments.auto.tfvars_ file will be generated under the folder _/cd3user/tenancies/<customer\_name>/terraform_files/<region_dir>_
    
   ***Note***: This will create TF for only those Security Lists and Route Tables in VCNs which are part of cd3 and skip any VCNs that have been created outside of cd3 execution.

   Navigate to the above path and execute the terraform commands:<br>
       <br>_terraform init_
       <br>_terraform plan_
       <br>_terraform apply_
   
   This completes the modification of Security Rules, Route Rules and DRG Route Rules in OCI. Verify the components in console.
   
# Other Scenarios
## Use an existing DRG in OCI while creating the network

Follow the below steps to create a Network using an existing DRG in OCI.

1. Modify the excel template ([Sample Templates](/cd3_automation_toolkit/example) with the required Network details in the Tabs - VCNs, DRGs, VCN Info, DHCP, Subnets, etc.
   Once all the Excel sheet is updated, place it at the location _/cd3user/tenancies/<customer\_name>/_ which is also mapped to your local directory.
   
2. Edit the _setUpOCI.properties_ at location:_/cd3user/tenancies /<customer\_name>/<customer\_name>\_setUpOCI.properties_ with appropriate values. 
   - Update the _cd3file_ parameter to specify the CD3 excel sheet path.
   - Set the _non_gf_tenancy_ parameter value to _false_. (for Greenfield Workflow.)
   
3. Change Directory to 'cd3_automation_toolkit' :<br>
    ```cd /cd3user/oci_tools/cd3_automation_toolkit/```
    
   and execute the _setupOCI.py_ file:
   
   ```python setUpOCI.py /cd3user/tenancies/<customer_name>/<customer_name>_setUpOCI.properties```
   
4. Choose option _'Create Network'_ from _'Network'_ of the displayed menu. 

   Once the execution is successful, _<customer\_name>\_compartments.auto.tfvars_ file will be generated under the folder _/cd3user/tenancies/<customer\_name>/terraform_files/<region_dir>_
    
   Navigate to the above path and execute the terraform commands:<br>
       <br>_terraform init_
       <br> - Import the DRG into your state file. Execute:
       <blockquote>
       terraform import "module.drgs[\"&lt;&lt;drgs terraform variable name&gt;&gt;\"].oci_core_drg.drg" &lt;&lt;drg ocid&gt;&gt; </blockquote>
       
     <br>_terraform plan_
     <br>- Terraform Plan will indicate to add all the other components except DRG.
     
     <br>_terraform apply_
   
   This completes the creation of Networking components by using the existing DRG in OCI. Verify the components in console.

## Add a New or Modify the existing Networking components

Follow the below steps to add a new or modify the existing Networking components such as VCNs, Subnets, DHCP and DRG.

1.  Modify the excel template ([Sample Templates](/cd3_automation_toolkit/example) with the required Network details in the Tabs - VCNs, DRGs, VCN Info, DHCP and Subnets tabs.
    Once the Excel sheet is updated, place it at the location _/cd3user/tenancies/<customer\_name>/_ which is also mapped to your local directory.
   
2. Edit the _setUpOCI.properties_ at location:_/cd3user/tenancies /<customer\_name>/<customer\_name>\_setUpOCI.properties_ with appropriate values. 
   - Update the _cd3file_ parameter to specify the CD3 excel sheet path.
   - Set the _non_gf_tenancy_ parameter value to _false_. (for Greenfield Workflow.)
   
3. Change Directory to 'cd3_automation_toolkit' :<br>
    ```cd /cd3user/oci_tools/cd3_automation_toolkit/```
    
   and execute the _setupOCI.py_ file:
   
   ```python setUpOCI.py /cd3user/tenancies/<customer_name>/<customer_name>_setUpOCI.properties```
   
4. Choose option _'Validate CD3'_ and _'Validate Network(VCNs, Subnets, DHCP, DRGs)'_ from sub-menu to check for syntax errors in Excel sheet. Examine the log file generated at /cd3user/tenancies/<customer_name>/<customer_name>\_cd3validator.logs. If there are errors, please rectify them accordingly and proceed to step 5.

5. Choose option to _'Modify Network'_ under _'Network'_ from the displayed menu. Once the execution is successful, _<customer\_name>\_compartments.auto.tfvars_ file will be generated under the folder _/cd3user/tenancies/<customer\_name>/terraform_files/<region_dir>_
    
   ***Note***: Make sure to export Sec Rules, Route Rules, DRG Route Rules to CD3 Excel Sheet before executing this option.

   Navigate to the above path and execute the terraform commands:<br>
       <br>_terraform init_
       <br>_terraform plan_
       <br>_terraform apply_
   
This completes the addition of new Networking components in OCI. Verify the components in console.

***Note***: Follow the above process to add new components such as VCN/DHCP/DRG/IGW/NGW/SGW/LPG/Subnet after the export of non-greenfield tenancy for Networking.

<br><br>
<div align='center'>

| <a href="/cd3_automation_toolkit/documentation/user_guide/Workflows.md">:arrow_backward: Prev</a> | <a href="/cd3_automation_toolkit/documentation/user_guide/QuickstartNGF.md">Next :arrow_forward:</a> |
| :---- | -------: |
  
</div>


