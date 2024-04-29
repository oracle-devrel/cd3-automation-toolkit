<h2> Export and Replicate OCI Infrastructure across tenancies </h2>

ISVs or System Integrators often encounter a typical situation of replicating OCI infrastructure in one tenancy/compartment to another tenancy/compartment. It takes few days to months to replicate the whole infrastructure manually.

This document provides detailed steps for efficiently using the CD3 toolkit to onboard the customer to their new environment within minutes.

There are **two ways** to do this: 

1. Export infrastructure from source environment to the CD3 toolkit and the exported **Excel file** is used as an input to create the same infrastructure in target environment.
2. Export infrastructure from source environment to the CD3 toolkit and the generated resources **auto.tfvars** files are copied to the service specific directories in target container. Generate the plan and execute terraform apply. 

For both the ways, set up 2 CD3 containers and connect them to Source Tenancy and Target Tenancy each using steps mentioned in https://oracle-devrel.github.io/cd3-automation-toolkit/install-cd3/. 

>Note: - Same process should be used to replicate Infra resources from one Compartment to another within the same Tenancy.

<img width="1486" alt="replication_workflow" src="../images/isv_workflow.png">


## Method 1: Using the Excel sheet of source tenancy

<h3> Identity Components </h3>

**Task 1:**

1. Download [CD3-Blank-template](https://github.com/oracle-devrel/cd3-automation-toolkit/blob/main/cd3_automation_toolkit/example/CD3-Blank-template.xlsx) and place it in any location inside the source tenancy container. Copy the path and place it under the **cd3_file** parameter in  
```/cd3user/tenancies /<customer_name>/<customer_name>_setUpOCI.properties``` file. 
2. Set the **workflow_type** to **export_resources**.
3. Navigate to ```cd /cd3user/oci_tools/cd3_automation_toolkit/```
   and execute  
   ```
   python setUpOCI.py /cd3user/tenancies/<customer_name>/<customer_name>_setUpOCI.properties
   ```
4. Provide comma separated “region” values if resources have to be exported from specific regions. If no region value is provided, the toolkit will export resources from all regions.
5. Select **1.Export Identity** from the setUpOCI menu and the required sub-options. Select the compartment from which these resources have to be exported. 
6. The input Excel file is now populated with the exported resources data.
   >Note: There is no need to execute the generated shell scripts containing the terraform import commands.


**Task2:**

1. In the exported Excel file, make appropriate changes to Identity tabs to match region name or other parameters for the target tenancy.
2. Copy the updated Excel file to any location within the container connected to target environment. Add this path under the  **cd3_file** parameter in  
```/cd3user/tenancies /<customer_name>/<customer_name>_setUpOCI.properties``` file. 
3. Set the **workflow_type** to **create_resources**.
4. Navigate to ```cd /cd3user/oci_tools/cd3_automation_toolkit/```
   and execute  
   ```
   python setUpOCI.py /cd3user/tenancies/<customer_name>/<customer_name>_setUpOCI.properties
   ```
5. Select **1.Identity** in setUpOCI main options and the required sub-options.
6. Navigate to ```/cd3user/tenancies/<customer_name>/terraform_files/<region_dir>/identity/``` directory of home region in target tenancy container. Execute terraform init, plan and apply. This will create the identity components in target OCI environment.


<h3> Network Components </h3>

**Task1:**

1. Download [CD3-Blank-template](https://github.com/oracle-devrel/cd3-automation-toolkit/blob/main/cd3_automation_toolkit/example/CD3-Blank-template.xlsx) and place it in any location inside the source tenancy container. Copy the path and place it under the **cd3_file** parameter in  
```/cd3user/tenancies /<customer_name>/<customer_name>_setUpOCI.properties``` file.
2. Set the **workflow_type** to **export_resources**.
3. Navigate to ```cd /cd3user/oci_tools/cd3_automation_toolkit/```                
   and execute  
   ```
   python setUpOCI.py /cd3user/tenancies/<customer_name>/<customer_name>_setUpOCI.properties
   ```
4. Provide comma separated “region” values if resources have to be exported from specific regions. If no region value is provided, the toolkit will export resources from all regions.
5. Select **3.Export Network** from the setUpOCI menu and the sub-option: **Export all Network Components** . Select the compartment from which these resources have to be exported. 
6. This will export the Network data into Excel template Networking tabs and also create **obj_names.safe** file under  ```/cd3user/tenancies/<customer_name>/terraform_files/<region_dir>/network/``` directory of each region.

     >Note:There is no need to execute the generated shell script containing the terraform import commands.

**Task2:**

1. In the exported Excel file, make appropriate changes to the Network tabs to match region name or other parameters for the target tenancy. 
   >Note:If VCN name needs to be changed for target tenancy, it has to be changed in 'VCN Name' column of VCNs, SubentsVLANs, DHCP, SecRulesinOCI, RouteRulesinOCI tabs and 'Attached To' column of DRGs tab.
2. Copy this updated Excel file to any location within target tenancy container and add its path under the **cd3_file** parameter in 
 ```/cd3user/tenancies /<customer_name>/<customer_name>_setUpOCI.properties``` file. Set the **workflow_type** to **create_resources**.
3. In the source tenancy container, navigate to ```/cd3user/tenancies/<customer_name>/terraform_files/<region_dir>/network/``` , copy **obj_names.safe** file under the same location in target tenancy container. Make sure to navigate to the required region directory in the target tenancy container.
   >Note: If any changes are done to VCN name/DRG name/DRG RT name attached to VCN in the Excel, make sure to update corresponding obj_names.safe file as well.
4. Navigate to ```cd /cd3user/oci_tools/cd3_automation_toolkit/```
   and execute  
   ```
   python setUpOCI.py /cd3user/tenancies/<customer_name>/<customer_name>_setUpOCI.properties
   ```
5. Select **3.Network** in setUpOCI main options and the required sub-options.
6. If NSGs or VLANs have to be replicated, select **3.Network**-->**Network Security Groups** , **Add/Modify/Delete VLANs**. select **Add/Modify/Delete NSGs (Reads NSGs sheet)** from the NSG sub-options.
6. Navigate to ```/cd3user/tenancies/<customer_name>/terraform_files/<region_dir>/network/``` directory in target tenancy container. Execute terraform init, plan and apply. This will create the Network components in target OCI environment.
7. For NSG and VLANs, execute terraform init, plan and apply from ```/cd3user/tenancies/<customer_name>/terraform_files/<region_dir>/nsg/``` and ```/cd3user/tenancies/<customer_name>/terraform_files/<region_dir>/vlan/``` directories respectively of each region in target tenancy container. This will create NSGs and VLANs in target OCI environment.
8. For RPC, execute terraform init, plan and apply from ```/cd3user/tenancies/<customer_name>/terraform_files/global/rpc``` directory in target tenancy container. This will create RPCs between regions in target OCI environment.

<h5> Use the same process to replicate any other CD3 supported resources in OCI </h5>


## Method 2: Using the terraform code of source tenancy

<h3> All OCI Components </h3>

**Task1**:

1. Download [CD3-Blank-template](https://github.com/oracle-devrel/cd3-automation-toolkit/blob/main/cd3_automation_toolkit/example/CD3-Blank-template.xlsx) and place it in any location inside the source tenancy container. Copy the path and place it under the **cd3_file** parameter in  
```/cd3user/tenancies /<customer_name>/<customer_name>_setUpOCI.properties``` file.
2. Set the **workflow_type** to **export_resources**.
3. Navigate to ```cd /cd3user/oci_tools/cd3_automation_toolkit/```
   and execute  
   ```
   python setUpOCI.py /cd3user/tenancies/<customer_name>/<customer_name>_setUpOCI.properties
   ```
4. Provide comma separated “region” values if resources have to be exported from specific regions. If no region value is provided, the toolkit will export resources from all regions.
5. Select required options from the setUpOCI menu. Select the compartment from which these resources have to be exported. 
   >Note:There is no need to execute the generated shell script containing the terraform import commands.
6. Navigate to each of the required service folders under ```/cd3user/tenancies/<customer_name>/terraform_files/<region_dir>/```. Copy the generated *.auto.tfvars from each service folder.

**Task2:**

1. In the target tenancy container, navigate to ```/cd3user/tenancies/<customer_name>/terraform_files/<region_dir>/```. Paste the above copied files to the respective service folders in each of the regions.
2. Ensure that necessary adjustments are made in tfvars, such as modifying names etc.,. For multiple replacements, use **sed** commands.
3. Execute terraform init, plan and apply from each of the service directories. This will create these resources in target OCI environment.
4. To get the target tenancy data into a Excel template, follow the initial steps listed in **Task1** of this section (Method2) and execute the toolkit to export the created components from target tenancy. 


