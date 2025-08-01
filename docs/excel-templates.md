# **Excel Sheet Templates**

 CD3 Excel templates serve as the main input to the Automation Toolkit. 


!!! success "CIS Compliance"
    CD3 Excel templates are aligned with the latest CIS Foundations Benchmark for Oracle Cloud!


<b>Filling the Templates</b>

- Instructions for filling in data are provided in the blue section of each sheet (within the Excel file).<br>
- Make appropriate changes to parameter values such as Region, Compartment, etc., based on your deployment requirements.


!!! Important "Heads Up!"

    - Content after the <END\> tag in any sheet will not be processed by the toolkit.
    
    - If a row is deleted from the Excel file and the toolkit is re-run, the corresponding resource will be removed from the .tfvars file.

    - After deploying infrastructure using any of the templates, run the <a href="../other-oci-tools#cis-compliance-checker-script"><u>CIS compliance checker script</u></a> to validate compliance.

<br>

**📍 CD3 Excel templates for OCI core services:**

>Click on the **Download** button towards the right end of each page to download the respective Excel template.

|Excel Sheet  | Purpose                                                                                                                    | 
|-----------|----------------------------------------------------------------------------------------------------------------------------|
| [CD3-Blank-template.xlsx](https://github.com/oracle-devrel/cd3-automation-toolkit/blob/main/cd3_automation_toolkit/example/CD3-Blank-template.xlsx)   | 	Use this template to export existing OCI resources into CD3 and Terraform| 
| [CD3-CIS-template.xlsx](https://github.com/oracle-devrel/cd3-automation-toolkit/blob/main/cd3_automation_toolkit/example/CD3-CIS-template.xlsx)      | Pre-filled with CIS Landing Zone data for DRGv2. Use this to create core OCI resources- <br> (IAM, Tags, Networking, Instances, Load Balancers, Storage, Databases) |
|[CD3-HubSpoke-template.xlsx](https://github.com/oracle-devrel/cd3-automation-toolkit/blob/main/cd3_automation_toolkit/example/CD3-HubSpoke-template.xlsx)        | Pre-filled with data for a Hub-and-Spoke networking model. Use this to deploy core OCI resources|
|[CD3-SingleVCN-template.xlsx](https://github.com/oracle-devrel/cd3-automation-toolkit/blob/main/cd3_automation_toolkit/example/CD3-SingleVCN-template.xlsx)      | Pre-filled with data for a Single VCN networking model. Use this to deploy core OCI resources|




**📍 CD3 Excel template for OCI Network Firewall:**


|Excel Sheet  | Purpose                                                                                                                    | 
|-----------|----------------------------------------------------------------------------------------------------------------------------|
| [CD3-Network-Firewall-template.xlsx](https://github.com/oracle-devrel/cd3-automation-toolkit/blob/main/cd3_automation_toolkit/example/CD3-Firewall-template.xlsx)   | 	Sample data pre-filled for deploying OCI Network Firewall. **Use separate sheets to  deploy firewalls in different regions of the tenancy** | 




**📍 CD3 Excel template for OCI Observability and Management services:**


|Excel Sheet| Purpose                                                                                                                    | 
|-----------|----------------------------------------------------------------------------------------------------------------------------|
|[CD3-CIS-ManagementServices-template.xlsx](https://github.com/oracle-devrel/cd3-automation-toolkit/blob/main/cd3_automation_toolkit/example/CD3-CIS-ManagementServices-template.xlsx) | Pre-filled with CIS Landing Zone data. Use this to deploy Events, Alarms, Notifications, and Service Connectors|


!!! info "Templates inside the container"

    The Excel Templates can also be found under "_/cd3user/oci_tools/cd3_automation_toolkit/example/_" folder  inside the container.
