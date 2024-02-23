# CD3 Automation Toolkit

[![License: UPL](https://img.shields.io/badge/license-UPL-green)](https://img.shields.io/badge/license-UPL-green) [![Quality gate](https://sonarcloud.io/api/project_badges/quality_gate?project=oracle-devrel_cd3-automation-toolkit)](https://sonarcloud.io/dashboard?id=oracle-devrel_cd3-automation-toolkit)

<br>

## Introduction


The CD3 toolkit reads input data in the form of CD3 Excel sheet and generates Terraform files which can be used to provision the resources in OCI instead of handling the task through the OCI console manually. The toolkit also reverse engineers the components in OCI back to the Excel sheet and Terraform configuration. The toolkit can be used throughout the lifecycle of tenancy to continuously create or modify existing resources. The generated Terraform code can be used by the OCI Resource Manager or can be integrated into organization's existing devops CI/CD ecosystem.


<br>

## 📌 OCI Services Currently Supported by Automation Toolkit

| OCI Services | Details |
| --------- | ----------- |
| [IAM/Identity](/cd3_automation_toolkit/documentation/user_guide/learn_more/CD3ExcelTabs.md#iamidentity) | Compartments, Groups, Dynamic Groups, Policies, Users, Network Sources |
| [Governance](/cd3_automation_toolkit/documentation/user_guide/learn_more/CD3ExcelTabs.md#governance) | Tags (Namespaces, Tag Keys, Defined Tags, Default Tags, Cost Tracking) |
| [Network](/cd3_automation_toolkit/documentation/user_guide/learn_more/CD3ExcelTabs.md#network) | VCNs, Subnets, VLANs, DRGs, IGWs, NGWs, LPGs, Route Tables, DRG Route, Tables, Security Lists, Network Security Groups, Remote Peering Connections, Application Load Balancer, Network Load Balancers |
| [DNS Management](/cd3_automation_toolkit/documentation/user_guide/learn_more/CD3ExcelTabs.md#private-dns)                                       | Private DNS - Views, Zones, rrsets/records and Resolvers  |
| [Compute](/cd3_automation_toolkit/documentation/user_guide/learn_more/CD3ExcelTabs.md#compute) | Instances supporting Market Place Images, Remote Exec, Cloud-Init scripts, Dedicated VM Hosts |
| [Storage](/cd3_automation_toolkit/documentation/user_guide/learn_more/CD3ExcelTabs.md#storage) | FSS, Block and Boot Volumes, Backup Policies, Object Storage Buckets and logging for write events |
| [Database](/cd3_automation_toolkit/documentation/user_guide/learn_more/CD3ExcelTabs.md#database) | Exa Infra, ExaCS, DB Systems VM and BM, ATP, ADW |
| [Management Services](/cd3_automation_toolkit/documentation/user_guide/learn_more/CD3ExcelTabs.md#management-services) | Events, Notifications, Alarms, Service Connector Hub (SCH) |
| [Developer Services](/cd3_automation_toolkit/documentation/user_guide/learn_more/CD3ExcelTabs.md#developer-services) | Resource Manager, Oracle Kubernetes Engine (OKE) |
| [Logging Services](/cd3_automation_toolkit/documentation/user_guide/learn_more/CD3ExcelTabs.md#logging-Services) | VCN Flow Logs, LBaaS access and error Logs, OSS Buckets write Logs |
| [SDDCs ](/cd3_automation_toolkit/documentation/user_guide/learn_more/CD3ExcelTabs.md#sddcs-tab) | Oracle Cloud VMWare Solutions (Single Cluster is supported as of now. Multi-cluster support will be included in the upcoming release) |
| [CIS Landing Zone Compliance](/cd3_automation_toolkit/documentation/user_guide/learn_more/CISFeatures.md#additional-cis-compliance-features) | Download and Execute CIS Compliance Check Script, Cloud Guard, Key Vault, Budget |
[Policy Enforcement](/cd3_automation_toolkit/documentation/user_guide/learn_more/OPAForCompliance.md) | OPA - Open Policy Agent |



<br>

## 🔄 High level workflow


<img width="1018" alt="Screenshot 2024-02-06 at 1 11 21 PM" src="https://github.com/oracle-devrel/cd3-automation-toolkit/assets/103508105/f989efee-45cc-413b-a706-e1bfe7f2a8fc">

<br>


First, The Excel file is input to the CD3 Automation toolkit using either CLI or Jenkins.  

>Note: 📖 Detailed documentations and videos are provided for both options. Please check the left panel for navigation.

Based on the workflow selected (create/export), the toolkit processes the next steps.


**Create resources:**

- The input Excel file is processed by the toolkit and terraform *auto.tfvars files are generated for all those reosurces. 

- The generated terraform files can be used to deploy resources in OCI by generating a terraform plan and approving the plan for apply. 

**Export resources**

- The input Excel (preferably the Blank template) is processed by the toolkit and resources are exported to CD3 Excel template. 

- The toolkit then generates *auto.tfvars from the exported data in Excel file and also generates shell scripts with terraform import commands for all the reosurces.

- The shell scripts have to be executed in order to have the updated state file to manage the resources further.

<br>

Please refer to the **"GETTING-STARTED"** sections in the navigation panel to start your journey with the toolkit. Happy Automation!!

