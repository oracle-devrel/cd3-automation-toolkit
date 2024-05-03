<h2> Export and Replicate OCI Infrastructure across tenancies </h2>

ISVs or System Integrators often encounter a typical situation of replicating OCI infrastructure in one tenancy/compartment/region to another tenancy/compartment/region. It takes few days to months to replicate the whole infrastructure manually.

This document provides detailed steps for efficiently using the CD3 toolkit with CLI to onboard the customer to their new environment within minutes. 

There are **two ways** to do this: 

1. Export infrastructure from source environment to the CD3 toolkit and the exported **Excel file** is used as an input to create the same infrastructure in target environment.
2. Export infrastructure from source environment to the CD3 toolkit and the generated resources **auto.tfvars** files are copied to the service specific directories in target container. Generate the plan and execute terraform apply. 

For both the ways, set up **2 new CD3 containers** and connect them to Source Tenancy and Target Tenancy each using steps mentioned in the [install-cd3 document](https://oracle-devrel.github.io/cd3-automation-toolkit/install-cd3/). 

> ✅ **Note:** Same process should be used to replicate Infrastructure resources from one Compartment/Region to another Compartment/Region within the same Tenancy.

!!! Important
    Ensure to have required service limits in the target environment before replicating.

<img width="1486" alt="replication_workflow" src="../images/isv_workflow.png">


After the containers are successfully connected to the source and target tenancies, follow the below steps for replication. This document uses the names **source** and **target** for tenancy specific folder and files within source tenancy container and target tenancy container respectively. 
<br>

## Method 1: Using the Excel sheet of source tenancy

**Task1: Export resources from Source tenancy**

1. Download [CD3-Blank-template.xlsx](https://github.com/oracle-devrel/cd3-automation-toolkit/blob/main/cd3_automation_toolkit/example/CD3-Blank-template.xlsx), rename it to **source_template.xlsx** and place it in the ```/cd3user/tenancies/source/``` folder inside the source tenancy container. 
2. Open the *setUpOCI.properties* file. 
      ```
      vi /cd3user/tenancies/source/source_setUpOCI.properties
      ```
   Under **cd3_file** parameter, add the path to **source_template.xlsx**:```/cd3user/tenancies/source/source_template.xlsx```. Set the **workflow_type** to ```export_resources``` and save the file.
 
       <img alt="setUpOCI.properties" src="../images/isv_setupociproperties.png">

3.  Navigate to *cd3_automation_toolkit* folder and execute the setUpOCI.py script:
   ```
   cd /cd3user/oci_tools/cd3_automation_toolkit/
   python setUpOCI.py /cd3user/tenancies/source/source_setUpOCI.properties
   ```
     
     <img alt="export setupocimenu" src="../images/isv_export_setupocimenu.png">

 
4. For the prompt asking to specify region, provide the region in the source tenancy from where the resources have to exported. To export from multiple regions, provide comma separated region values. Eg: ```ashburn,phoenix``` . Leave empty to export from all regions.
5. Select required resource options and sub-options from the **setUpOCI** menu. Select the compartment from which these resources have to be exported. Provide comma separated compartment names to export from multiple compartments. Leave empty to export from all compartments.
6. The **source_template.xlsx** is now populated with the exported resources data.
   > ℹ️ **Note:** The generated shell scripts with terraform import commands need not be executed.

<br>

**Task2: Create resources in Target tenancy**

1. In the **source_template.xlsx**, make required changes to match region or other parameters in the target tenancy and rename the Excel file to **target_template.xlsx**. 
   > ℹ️ **Note:** Remove any Oracle-tags from the resource tabs in **source_template.xlsx**. If custom tags are required, replicate them first to the target environment and then proceed with other tagged resources.
2. Switch to the target container. Place **target_template.xlsx** under the ```/cd3user/tenancies/target/``` folder . 
3. Open the *setUpOCI.properties* file.

      ```
      vi /cd3user/tenancies/target/target_setUpOCI.properties
      ```

      Under **cd3_file** parameter, add the path to the **target_template.xlsx**: ```/cd3user/tenancies/target/target_template.xlsx```. Set the **workflow_type** to ```create_resources``` and save the file.

       <img alt="setUpOCI.properties" src="../images/isv_setupociproperties_create.png">
  
    > ℹ️ **Note:**

    > ▶ For replicating Network resources, switch to the source container, copy the **obj_names.safe** file located at ```/cd3user/tenancies/source/terraform_files/<region_dir>/network/``` and paste it under the same location within the target tenancy container: ```/cd3user/tenancies/target/terraform_files/<region_dir>/network/```. 

    > ▶ If any changes are done to 'VCN name'/'DRG name'/'DRG RT name attached to VCN' in the target_template, update the corresponding **obj_names.safe** file as well.     

 4. Execute the setUpOCI.py script:
   ```
   cd /cd3user/oci_tools/cd3_automation_toolkit/
   python setUpOCI.py /cd3user/tenancies/target/target_setUpOCI.properties
   ```
5. From the output menu, select the required resource options and sub-options to generate the respective tfvars.

     <img alt="create setupocimenu" src="../images/isv_create_setupocimenu.png">

6. Navigate to ```/cd3user/tenancies/target/terraform_files/<region_dir>/<service_directory/``` for all required services. Execute the below terraform commands in sequence from each of the service directories to create the resources in target OCI tenancy.

      ```
         terraform init

         terraform plan

         terraform apply
      ```


## Method 2: Using the tfvars of source tenancy


**Task1: Export resources from Source tenancy**:

1. Download [CD3-Blank-template.xlsx](https://github.com/oracle-devrel/cd3-automation-toolkit/blob/main/cd3_automation_toolkit/example/CD3-Blank-template.xlsx), rename it to **source_template.xlsx** and place it in the ```/cd3user/tenancies/source/``` folder inside the source tenancy container. 
2. Open the *setUpOCI.properties* file. 

    ```vi /cd3user/tenancies/source/source_setUpOCI.properties```.

      Under the **cd3_file** parameter, add the path to **source_template.xlsx**: ```/cd3user/tenancies/source/source_template.xlsx```. Set the **workflow_type** to ```export_resources``` and save the file.

       <img alt="setUpOCI.properties" src="../images/isv_setupociproperties.png">

3. Execute the setUpOCI.py script:
   ```
   cd /cd3user/oci_tools/cd3_automation_toolkit/
   python setUpOCI.py /cd3user/tenancies/source/source_setUpOCI.properties
   ```
4. For the prompt asking to specify region, provide the region in the source tenancy from where the resources have to exported. To export from multiple regions, provide  comma separated region values. Eg: ```ashburn,phoenix```. Leave empty to export from all regions.
5. Select required options from the setUpOCI menu. Select the compartments from which these resources have to be exported. Provide comma separated compartment names to export from multiple compartments. Leave empty to export from all compartments.
   > ℹ️ **Note:** The generated shell scripts with terraform import commands need not be executed.
6. Navigate to each of the required service folders under the region directory:

      ```
      cd /cd3user/tenancies/source/terraform_files/<region_dir>/
      ```
   Copy the generated *.auto.tfvars from each service folder.

<br>

**Task2: Create resources in Target tenancy**:

1. In the target tenancy container, navigate to ```/cd3user/tenancies/target/terraform_files/<region_dir>/```. Paste the above copied source tfvars files to the respective service folders in each of the regions.
2. In the tfvars files, make any parameter value changes if required for the target tenancy. Make use of 'sed' commands for multiple changes.

    > ℹ️ **Note:** Ensure to remove any Oracle-tags from the tfvars files. If custom tags are required, first replicate them to the target environment and then proceed with other tagged resources.

3. Execute the below commands in sequence from each of the service directories to create the resources in target OCI tenancy.

      ```
         terraform init

         terraform plan

         terraform apply
      ```

4. The target tenancy resources can also be exported to the CD3 Excel template for further management. 

<br>

This is how the CD3 toolkit enables ISVs or any individual users to achieve effortless, error-free replication of OCI infrastructure across tenancies/compartments. This approach ensures consistent infrastructure across your deployments. 


