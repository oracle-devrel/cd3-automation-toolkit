## CD3 Quick start - Create a Compartment

**Once the Docker container has been launched and connected to the OCI Tenancy, follow the below steps to quickly provision a compartment on OCI. Detailed instructions can be found at** [Running the Automation Toolkit](/cd3_automation_toolkit/documentation/user_guide/RunningAutomationToolkit.md) 
1. Use the excel [CD3-SingleVCN-template](/cd3_automation_toolkit/example) and fill the required Compartment details in the 'Compartments' tab.
   Make appropriate changes to the template eg: Region. 
   Place the Excel sheet at ```/cd3user/tenancies/<customer_name>/```in your Docker Container.
   
2. Edit the _setUpOCI.properties_ at location: _/cd3user/tenancies/<customer_name>/<customer_name>setUpOCI.properties_ with appropriate values. 
   - Update the _cd3file_ parameter to specify the CD3 excel sheet path.
   - Set the _non_gf_tenancy_ parameter value to _false_.
   
   We will be using a Greenfield workflow for this Quickstart. A Greenfield tenancy is an Empty OCI tenancy (or) any OCI tenancy where we need not modify / use any existing resources. For more information on types of Workflows, refer to [Automation Toolkit Workflows](/cd3_automation_toolkit/documentation/user_guide/Workflows.md)
   
3. Change Directory to that of cd3_automation_toolkit :
    ```cd /cd3user/oci_tools/cd3_automation_toolkit/```
    
   and execute the _setupOCI.py_ file:
   
   ```python setUpOCI.py /cd3user/tenancies/<customer_name>/<customer_name>_setUpOCI.properties```
   
 4. Once _setupOCI.py_ is executed with the required options, <customer_name>_compartments.auto.tfvars file will be generated under the folder 									
    ```/cd3user/tenancies/<customer_name>/terraform_files/<Region>/```
    
   	Navigate to the above path and execute the terraform commands:
   
       _terraform init_
   
       _terraform plan_
     
       _terraform apply_

   
 4. Choose _"Fetch Compartments OCIDs to variables file"_ from CD3 Services in _setUpOCI_ menu. Execute the command to fetch the details of the                 compartments if it already exists/ created in OCI. These details will be written to the terraform variables file.

