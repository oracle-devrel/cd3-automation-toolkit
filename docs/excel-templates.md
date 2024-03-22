# **Excel Sheet Templates**

CD3 Excel templates serve as the main input to the Automation Toolkit. 

The CD3 templates for the latest release as per CIS Foundations Benchmark for Oracle Cloud are listed in the tables below.

Instructions on how to fill data into the Excel sheet can be found in the Blue section of each sheet within the Excel file. Make appropriate changes to the parameter values eg: Region, Compartment etc., as required for deployment.


!!! Important

    - Anything after <END\> tag in the sheet is not processed by the toolkit. 
    
    - If a row is deleted from the Excel sheet and the toolkit is rerun, it will be removed from tfvars.
    
    - After deploying the Infrastructure using any of the templates, run [CIS compliance checker script](cisfeatures.md) to validate it.

<br>

**CD3 Excel templates for OCI core services:**


|Excel Sheet  | Purpose                                                                                                                    | 
|-----------|----------------------------------------------------------------------------------------------------------------------------|
| [CD3-Blank-template.xlsx](https://github.com/oracle-devrel/cd3-automation-toolkit/blob/main/cd3_automation_toolkit/example/CD3-Blank-template.xlsx)   | 	Choose this template while exporting the existing resources from OCI into the CD3 and Terraform.| 
| [CD3-CIS-template.xlsx](https://github.com/oracle-devrel/cd3-automation-toolkit/blob/main/cd3_automation_toolkit/example/CD3-CIS-template.xlsx)      | This template has auto-filled in data of CIS Landing Zone for DRGv2. Choose this template to create Core OCI Objects (IAM, Tags, Networking, Instances, LBR, Storage, Databases) |
|[CD3-HubSpoke-template.xlsx](https://github.com/oracle-devrel/cd3-automation-toolkit/blob/main/cd3_automation_toolkit/example/CD3-HubSpoke-template.xlsx)        | This template has auto-filled in data for a Hub and Spoke model of networking. Choose this template to create Core OCI Objects (IAM, Tags, Networking, Instances, LBR, Storage, Databases)|
|[CD3-SingleVCN-template.xlsx](https://github.com/oracle-devrel/cd3-automation-toolkit/blob/main/cd3_automation_toolkit/example/CD3-SingleVCN-template.xlsx)      | This template has auto-filled in data for a Single VCN model of networking. Choose this template to create Core OCI Objects (IAM, Tags, Networking, Instances, LBR, Storage, Databases)|


<br>

**CD3 Excel template for OCI Network Firewall:**


|Excel Sheet  | Purpose                                                                                                                    | 
|-----------|----------------------------------------------------------------------------------------------------------------------------|
| [CD3-Network-Firewall-template.xlsx](https://github.com/oracle-devrel/cd3-automation-toolkit/blob/main/cd3_automation_toolkit/example/CD3-Firewall-template.xlsx)   | 	This template has sample data for deploying Network Firewall in OCI. **Use separate sheets to deploy firewalls in separate regions of the tenancy.** | 


<br>

**CD3 Excel template for OCI Observability and Management services:**


|Excel Sheet| Purpose                                                                                                                    | 
|-----------|----------------------------------------------------------------------------------------------------------------------------|
|[CD3-CIS-ManagementServices-template.xlsx](https://github.com/oracle-devrel/cd3-automation-toolkit/blob/main/cd3_automation_toolkit/example/CD3-CIS-ManagementServices-template.xlsx) | This template has auto-filled in data of CIS Landing Zone. Choose this template while creating the components of Events, Alarms, Notifications and Service Connectors|


!!! note 

    The Excel Templates can also be found at "_/cd3user/oci_tools/cd3_automation_toolkit/example_" folder  inside the container.
