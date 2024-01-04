# **Getting Started with Automation Toolkit**
CD3 Excel sheet is the main input for Automation Toolkit.

### **Excel Sheet Templates**

Below are the CD3 templates for the latest release having standardised IAM Components (compartments, groups and policies), Network Components and Events & Notifications Rules as per CIS Foundations Benchmark for Oracle Cloud.

Details on how to fill data into the excel sheet can be found in the Blue section of each sheet inside the excel file. Make appropriate changes to the templates eg region and use for deployment.

|Excel Sheet| Purpose                                                                                                                    | 
|-----------|----------------------------------------------------------------------------------------------------------------------------|
| [CD3-Blank-template.xlsx](/cd3_automation_toolkit/example)   | 	Choose this template while exporting the existing resources from OCI into the CD3 and Terraform.| 
| [CD3-CIS-template.xlsx](/cd3_automation_toolkit/example) | This template has auto-filled in data of CIS Landing Zone for DRGv2. Choose this template to create Core OCI Objects (IAM, Tags, Networking, Instances, LBR, Storage, Databases) |
|[CD3-HubSpoke-template](/cd3_automation_toolkit/example) | This template has auto-filled in data for a Hub and Spoke model of networking. Choose this template to create Core OCI Objects (IAM, Tags, Networking, Instances, LBR, Storage, Databases)|
|[CD3-SingleVCN-template](/cd3_automation_toolkit/example)| This template has auto-filled in data for a Single VCN model of networking. Choose this template to create Core OCI Objects (IAM, Tags, Networking, Instances, LBR, Storage, Databases)|
|[CD3-CIS-ManagementServices-template.xlsx](/cd3_automation_toolkit/example) | This template has auto-filled in data of CIS Landing Zone. Choose this template while creating the components of Events, Alarms, Notifications and Service Connectors|


> The Excel Templates can also be found at _/cd3user/oci_tools/cd3_automation_toolkit/example_ inside the container.
> After deploying the infra using any of the templates, please run [CIS compliance checker script](/cd3_automation_toolkit/documentation/user_guide/learn_more/CISFeatures.md#1-run-cis-compliance-checker-script))


<br><br>
<div align='center'>

| <a href="/cd3_automation_toolkit/documentation/user_guide/Connect_container_to_OCI_Tenancy.md">:arrow_backward: Prev</a> | <a href="/cd3_automation_toolkit/documentation/user_guide/Workflows.md">Next :arrow_forward:</a> |
| :---- | -------: |
  
</div>

