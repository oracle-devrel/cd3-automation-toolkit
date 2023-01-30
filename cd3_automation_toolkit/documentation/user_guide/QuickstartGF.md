## Quick start - Create a Compartment (Greenfield Workflow)

**Once the Docker container has been launched and connected to the OCI Tenancy, follow the below steps to quickly provision a compartment on OCI. Detailed instructions can be found at** [Running the Automation Toolkit](/cd3_automation_toolkit/documentation/user_guide/RunningAutomationToolkit.md) 
1. Use the excel [CD3-SingleVCN-template](/cd3_automation_toolkit/example) and fill the required Compartment details in the 'Compartments' tab.

   Make appropriate changes to the template. For Eg: Update the _Region_ value to your tenancy's home region.
   
   Once all the required data is filled in the Excel sheet, place it at the location _/cd3user/tenancies/<customer\_name>/_ which is also mapped to your    local directory.
   
2. Edit the _setUpOCI.properties_ at location:_/cd3user/tenancies /<customer\_name>/<customer\_name>\_setUpOCI.properties_ with appropriate values. 
   - Update the _cd3file_ parameter to specify the CD3 excel sheet path.
   - Set the _non_gf_tenancy_ parameter value to _false_. (for Greenfield Workflow.)
  
     <blockquote>For more information on types of Workflows, refer to <a href = /cd3_automation_toolkit/documentation/user_guide/Workflows.md> Automation Toolkit Workflows</a></blockquote>
   
3. Change Directory to 'cd3_automation_toolkit' :
    ```cd /cd3user/oci_tools/cd3_automation_toolkit/```
    
   and execute the _setupOCI.py_ file:
   
   ```python setUpOCI.py /cd3user/tenancies/<customer_name>/<customer_name>_setUpOCI.properties```
   
4. Choose option to create compartments under 'Identity' from the displayed menu. Once the exececution is successful, _<customer\_name>\_compartments.auto.tfvars_ file will be generated under the folder _/cd3user/tenancies/<customer\_name>/terraform_files/<region_dir>_
    
   Navigate to the above path and execute the terraform commands:<br>
       <br>_terraform init_
       <br>_terraform plan_
       <br>_terraform apply_
   
5. Choose _Fetch Compartments OCIDs to variables file_ under _CD3 Services_ in setUpOCI menu. Execute the command to fetch the details of the                 compartments if it already exists/ created in OCI. These details will be written to the terraform variables file.

6. Repeat the above process (except Step 5) to create other components in OCI.

<br><br>
<div align='center'>

| <a href="/cd3_automation_toolkit/documentation/user_guide/Workflows.md">:arrow_backward: Prev</a> | <a href="/cd3_automation_toolkit/documentation/user_guide/QuickstartNGF.md">Next :arrow_forward:</a> |
| :---- | -------: |
  
</div>
