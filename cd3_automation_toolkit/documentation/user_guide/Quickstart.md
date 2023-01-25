## CD3 QUICKSTART

**After launching the Docker Container and connecting it to the OCI Tenancy, follow the below steps to quickly provision a compartment on OCI**.
1. Pick up the excel [CD3-SingleVCN-template](/cd3_automation_toolkit/example) and add in the required compartment details in specified Comaprtments tab.
   Details on how to fill the data into the excel sheet can be found in the Blue section of each sheet inside the excel file. Make appropriate changes to the template eg region. Place Excel sheet at appropriate location in your docker container.
   
2. Edit the setUpOCI.properties at location: _/cd3user/tenancies/<customer_name>/<customer_name>_setUpOCI.properties with appropriate values. 
   - Provide the CD3 excel sheet path in: /cd3user/tenancies/<customer_name>/<customer_name>_setUpOCI.properties file.
   - Change the _non_gf_tenancy_ parameter_ value to _false_.
   We will be using a Greenfield workflow for this Quickstart.A Greenfield tenancy is an Empty OCI tenancy (or) any OCI tenancy where we need not to modify / use any existing resources.
   
   For more information on types of Workflows, refer to [Workflows.md](/cd3_automation_toolkit/documentation/user_guide/Workflows.md)
   
3. Change Directory to that of cd3_automation_toolkit :
    ```cd /cd3user/oci_tools/cd3_automation_toolkit/```
    
   and execute the setupOCI.py file:
   
   ```python setUpOCI.py /cd3user/tenancies/<customer_name>/<customer_name>_setUpOCI.properties```
   
 4. Once the above command is executed with the required options, <customer_name>_compartmetns.auto.tfvars file will be generated under the folder 									
    ```/cd3user/tenancies/<customer_name>/terraform_files/<Region>/```
    
   	Navigate to the above path and execute terraform commands:
   
       _terraform init_
   
       _terraform plan_
     
       _terraform apply_

   
 4. Choose _"Fetch Compartments OCIDs to variables file"_ from CD3 Services in _setUpOCI_ menu. Execute the command to fetch the details of the compartments if it already exists/created in OCI. These details will be written to the terraform variables file.
    
    </br>
    
    Please refer to [RunningAutomationToolkit](/cd3_automation_toolkit/documentation/user_guide/RunningAutomationToolkit.md) for detailed instructions and explanation of each file parameters.

