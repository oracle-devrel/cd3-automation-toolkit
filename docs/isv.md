<h2> Export and Replicate OCI Infrastructure across tenancies </h2>

ISVs or System Integrators often encounter a typical situation of replicating OCI infrastructure in one tenancy/compartment to another tenancy/compartment. It takes few days to months to replicate the whole infrastructure manually.

This document provides detailed steps for efficiently using the CD3 toolkit to onboard the customer to their new environment within minutes.

There are **two ways** to do this: 

1. Export infrastructure from source environment to the CD3 toolkit and the exported **Excel file** is used as an input to create the same infrastructure in target environment.
2. Export infrastructure from source environment to the CD3 toolkit and the generated resources **auto.tfvars** files are copied to the service specific directories in target container. Generate the plan and execute terraform apply. 


For both the ways, set up 2 new CD3 containers and connect them to Source Tenancy and Target Tenancy each using steps mentioned in https://oracle-devrel.github.io/cd3-automation-toolkit/install-cd3/. 

> **Note:** Same process should be used to replicate Infra resources from one Compartment to another within the same Tenancy.

!!! Important
    Ensure to have required service limits in the target environment.

<img width="1486" alt="replication_workflow" src="../images/isv_workflow.png">


## Method 1: Using the Excel sheet of source tenancy

Below are the step-by-step instructions for replicating Identity and Network resources from OCI. For the scope of this document, we have considered "source" and "target" as customer_names in the *tenancyconfig.properties* file for source container and target container respectively. Same naming convention is followed throughout the document.

<h3> Identity Components </h3>

**Task 1: Export Identity components from Source environment**

1. Download [CD3-Blank-template](https://github.com/oracle-devrel/cd3-automation-toolkit/blob/main/cd3_automation_toolkit/example/CD3-Blank-template.xlsx) and place it in the ```/cd3user/tenancies/source/``` folder inside the source tenancy container. 
    >  **Note:** The **/cd3user/tenancies/** folder in cd3 container is mapped to **/cd3user/mount_path/** folder in the workvm. Login to the workvm with **cd3user** to be able to copy files to the container.   

2. Open the *setUpOCI.properties* file ```vi /cd3user/tenancies/source/source_setUpOCI.properties```. Under the **cd3_file** parameter, add the path to the *CD3-Blank-template* file. Set the **workflow_type** to **export_resources** and save the file.
   
3. Navigate to ```cd /cd3user/oci_tools/cd3_automation_toolkit/```
   and execute  
   ```
   python setUpOCI.py /cd3user/tenancies/source/source_setUpOCI.properties
   ```
4. In the output, provide comma separated “region” values if resources have to be exported from specific regions. If no region value is provided, the toolkit will export resources from all regions.
5. Select **Export Identity** from the setUpOCI menu and the required sub-options. Select the compartment from which these resources have to be exported. 
6. The input Excel file is now populated with the exported resources data.
   > ℹ️ **Note:** There is no need to execute the generated shell scripts containing the terraform import commands.


**Task2: Create Identity components in Target environment**

1. In the exported Excel file, make appropriate changes to Identity tabs to match region name or other parameters for the target tenancy. 
   > ℹ️ **Note:** Ensure to remove any Oracle-tags from the Identity tabs in exported Excel file. If custom tags are required, replicate them first to the target environment and then proceed with other tagged resources.
2. Switch to the target container and copy the updated Excel file under the ```/cd3user/tenancies/target/``` folder . 
3. Open the *setUpOCI.properties* file ```vi /cd3user/tenancies/target/target_setUpOCI.properties```. Under **cd3_file** parameter, add the path to the updated Excel file. Set the **workflow_type** to **create_resources** and save the file.
4. Navigate to ```cd /cd3user/oci_tools/cd3_automation_toolkit/```
   and execute  
   ```
   python setUpOCI.py /cd3user/tenancies/target/target_setUpOCI.properties
   ```
5. From the output menu, select **Identity** under main options and the required sub-options to generate the respective tfvars files.
6. Navigate to ```/cd3user/tenancies/target/terraform_files/<region_dir>/identity/``` directory of home region (identity components are created in home region) in the target container. Execute terraform init, plan and apply. This will create the identity components in target OCI environment.


<h3> Network Components </h3>

**Task1: Export Network components from Source environment**

1. Download [CD3-Blank-template](https://github.com/oracle-devrel/cd3-automation-toolkit/blob/main/cd3_automation_toolkit/example/CD3-Blank-template.xlsx) and place it in ```/cd3user/tenancies/source/``` folder inside the source tenancy container. 
   >  **Note:** The **/cd3user/tenancies/** folder in cd3 container is mapped to **/cd3user/mount_path/** folder in the workvm.     Login to the workvm with **cd3user** to copy files to the container.
2. Open the setUpOCI.properties file ```vi /cd3user/tenancies/source/source_setUpOCI.properties```. Under the **cd3_file** parameter, add the path to the *CD3-Blank-template* file. Set the **workflow_type** to **export_resources** and save the file.
   
3. Navigate to ```cd /cd3user/oci_tools/cd3_automation_toolkit/```                
   and execute  
   ```
   python setUpOCI.py /cd3user/tenancies/source/source_setUpOCI.properties
   ```
4. In the output, provide comma separated “region” values if resources have to be exported from specific regions. If no region value is provided, the toolkit will export resources from all regions.
5. Select **Export Network** from the setUpOCI menu and the sub-option: **Export all Network Components** . Select the compartment from which these resources have to be exported. 
6. This will export the Network data into Excel template Networking tabs and also create **obj_names.safe** file under  ```/cd3user/tenancies/source/terraform_files/<region_dir>/network/``` directory of each region.

     > ℹ️ Note:There is no need to execute the generated shell scripts containing the terraform import commands.

**Task2: Create Network components in target environment**

1. In the exported Excel file, make appropriate changes to the Network tabs to match region name or other parameters for the target tenancy. 

    > **Important❗:**
    
    >  * If VCN name needs to be changed for target tenancy, it has to be changed in 'VCN Name' column of VCNs, SubentsVLANs, DHCP, SecRulesinOCI, RouteRulesinOCI tabs and 'Attached To' column of DRGs tab.  

    > * Ensure to remove any Oracle-tags from the exported Excel file. If custom tags are required, replicate them first to the target environment and then proceed with other tagged resources.
    
2. Switch to the target tenancy container and copy this updated Excel file to the ```/cd3user/tenancies/target/``` folder inside the container. 

3. Open the setUpOCI.properties file ```vi /cd3user/tenancies/target/target_setUpOCI.properties```. Under the **cd3_file** parameter, add the path to the exported Excel file. Set the **workflow_type** to **create_resources** and save the file.
3. In the source tenancy container, navigate to ```/cd3user/tenancies/source/terraform_files/<region_dir>/network/``` , copy **obj_names.safe** file and paste it under the same location in target tenancy container. Make sure to navigate to the required region directory in the target tenancy container.
   > ℹ️ **Note:** If any changes are done to VCN name/DRG name/DRG RT name attached to VCN in the Excel, make sure to update corresponding obj_names.safe file as well.
4. Navigate to ```cd /cd3user/oci_tools/cd3_automation_toolkit/```
   and execute  
   ```
   python setUpOCI.py /cd3user/tenancies/target/target_setUpOCI.properties
   ```
5. From the output, select **Network** in main options and the required sub-options to generate the respective tfvars files.
6. If NSGs or VLANs have to be replicated, select **Network**-->**Network Security Groups** , **Add/Modify/Delete VLANs**. select **Add/Modify/Delete NSGs (Reads NSGs sheet)** from the NSG sub-options.
6. Navigate to ```/cd3user/tenancies/target/terraform_files/<region_dir>/network/``` directory in target tenancy container. Execute terraform init, plan and apply. This will create the Network components in target OCI environment.
7. For NSG and VLANs, execute terraform init, plan and apply from ```/cd3user/tenancies/target/terraform_files/<region_dir>/nsg/``` and ```/cd3user/tenancies/target/terraform_files/<region_dir>/vlan/``` directories respectively of each region in target tenancy container. This will create NSGs and VLANs in the target OCI environment.
8. For RPC, execute terraform init, plan and apply from ```/cd3user/tenancies/target/terraform_files/global/rpc``` directory in target tenancy container. This will create RPCs between regions in the target OCI environment.

<h5> Use the same process to replicate any other CD3 supported resources in OCI </h5>


## Method 2: Using the terraform code of source tenancy

<h3> All OCI Components </h3>

**Task1: Export OCI resources from Source environment**:

1. Download [CD3-Blank-template](https://github.com/oracle-devrel/cd3-automation-toolkit/blob/main/cd3_automation_toolkit/example/CD3-Blank-template.xlsx) and place it in ```/cd3user/tenancies/source/``` folder inside the source tenancy container.
   >**Note:** The **/cd3user/tenancies/** folder in cd3 container is mapped to **/cd3user/mount_path/** folder in the workvm. Login to the workvm with **cd3user** to copy files to this path.

2. Open the *setUpOCI.properties* file ```vi /cd3user/tenancies/source/source_setUpOCI.properties```. Under the **cd3_file** parameter, add the path to *CD3-Blank-template* file.  Set the **workflow_type** to **export_resources** and save the file.
3. Navigate to ```cd /cd3user/oci_tools/cd3_automation_toolkit/```
   and execute  
   ```
   python setUpOCI.py /cd3user/tenancies/source/source_setUpOCI.properties
   ```
4. In the output, provide comma separated “region” values if resources have to be exported from specific regions. If no region value is provided, the toolkit will export resources from all regions.
5. Select required options from the setUpOCI menu. Select the compartment from which these resources have to be exported. 
   > ℹ️ **Note:** There is no need to execute the generated shell script containing the terraform import commands.
6. Navigate to each of the required service folders under ```/cd3user/tenancies/source/terraform_files/<region_dir>/```. Copy the generated *.auto.tfvars from each service folder.

**Task2: Creating using target container**

1. In the target tenancy container, navigate to ```/cd3user/tenancies/target/terraform_files/<region_dir>/```. Paste the above copied tfvars files to the respective service folders in each of the regions.
2. Ensure that necessary adjustments are made in tfvars, such as modifying names etc.,. If the changes are more, use **sed** commands.
   > ℹ️ **Note:** Ensure to remove any Oracle-tags from the tfvars files. If custom tags are required, first replicate them to the target environment and then proceed with other tagged resources.
3. Execute terraform init, plan and apply from each of the service directories. This will create these resources in target OCI environment.
4. To get the target tenancy data into a Excel template, follow steps 1-5 listed in **Task1** of this section (Method2) and execute the toolkit to export the created components from target tenancy. 


