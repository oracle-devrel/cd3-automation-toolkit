# CD3 Automation Toolkit

[![License: UPL](https://img.shields.io/badge/license-UPL-green)](https://img.shields.io/badge/license-UPL-green) [![Quality gate](https://sonarcloud.io/api/project_badges/quality_gate?project=oracle-devrel_cd3-automation-toolkit)](https://sonarcloud.io/dashboard?id=oracle-devrel_cd3-automation-toolkit)
<ul>



[What is CD3](#cd3-automation-toolkit) &nbsp;&nbsp;•&nbsp;&nbsp; [Why CD3](#why-cd3) &nbsp;&nbsp;• &nbsp;&nbsp;[How CD3 works](#how-cd3-works)&nbsp;&nbsp; •&nbsp;&nbsp; [Who can use CD3](#👥-who-can-use-the-toolkit) &nbsp;&nbsp;• &nbsp;&nbsp; [Benefits](#💡-benefits-of-cd3) &nbsp;&nbsp;•&nbsp;&nbsp; [OCI services supported by CD3](#🔖-oci-services-currently-supported-by-automation-toolkit) &nbsp;&nbsp;•&nbsp;&nbsp; [High level workflow](#🔄-high-level-workflow) &nbsp;&nbsp;•&nbsp;&nbsp; [Kick-start](#🚀-ready-to-kick-start-your-cd3-journey) &nbsp;&nbsp;  •&nbsp;&nbsp; [Excel templates]()&nbsp;&nbsp; •  &nbsp;&nbsp; [Contributing](#⭐️-contributing) &nbsp;&nbsp;• &nbsp;&nbsp; [License](#⚠️-license)


<br>

CD3 stands for **Cloud Deployment Design Deliverable**. The CD3 Automation toolkit enables you to effortlessly Build, Export and Manage OCI (Oracle Cloud Infrastruture) resources within minutes ⚡️ .

<br>


### Why CD3?


⏳ For Enterprise infrastructures, manual resource provisioning is tedious and error-prone.

📝 While Terraform automates, filling variable values for each module can be cumbersome and requires Terraform expertise.

🔁 Manually created configs are hard to reuse for different environments or deployments .

<br>

###  How CD3 works?


(cd3logo -yet to be added)

<br>

The toolkit transforms input data from Excel files into Terraform files, enabling seamless creation of infrastructure in OCI.

**CD3 isn't just about creation!!!** ⬅️ Reverse engineer existing infrastructure back into Excel and gain complete control over your OCI resources lifecycle. 

📜 The generated Terraform code can be used by the OCI Resource Manager or can be integrated into organization's existing Devops CI/CD ecosystem.


<br>

### 👥 Who can use the toolkit??

  Anyone who wants to create or export OCI resources without much effort. 

<br>

### 💡 Benefits of CD3:


  ✅ Time savings ⏰ 
  
  ✅ Faster infrastructure provisioning 🚀
  
  ✅ Scalability 📈
  
  ✅ Operational efficiency ⚙️


<details>
  <summary><b>Click to know more benefits</b></summary>
<br>

**Secure architecture 🛡️:** CD3 toolkit helps customers deploy secure standardization across OCI tenancies by providing CIS-compliant Excel templates. It also enables native execution of the CIS Compliance Checker script against your tenancy.

**DevOps-oriented 🔄:** The toolkit facilitates integration of consistent output Terraform files in module format with any continuous integration and delivery (CI/CD) solution. The Terraform code can be reused to build similar workloads in different OCI regions and tenancies, which helps in quicker adoption of OCI.

**Platform independent 🌐:** CD3 is packaged as a container that can be hosted on any platform.
 
</details>


<br> 

### 🔖  OCI Services Currently Supported by CD3:

<br>

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


### 🔄 High level workflow
<br>

<img width="1018" alt="Screenshot 2024-02-06 at 1 11 21 PM" src="https://github.com/oracle-devrel/cd3-automation-toolkit/assets/103508105/f989efee-45cc-413b-a706-e1bfe7f2a8fc">

<br>


First, The Excel file is input to the CD3 Automation toolkit using either CLI or Jenkins.  

>Note: 📖 Detailed documentations and videos are provided for both options. 

Based on the workflow selected (create/export), the toolkit processes the next steps.


**Create resources:**

- The input Excel file is processed by the toolkit and terraform *auto.tfvars files are generated for all those reosurces. 

- The generated terraform files can be used to deploy resources in OCI by generating a terraform plan and approving the plan for apply. 

**Export resources**

- The input Excel (preferably the Blank template) is processed by the toolkit and resources are exported to CD3 Excel template. 

- The toolkit then generates *auto.tfvars from the exported data in Excel file and also generates shell scripts with terraform import commands for all the reosurces.

- The shell scripts have to be executed in order to have the updated state file to manage the resources further.

<br>

<br>

### 🚀 Ready to kick start your CD3 journey??

[CLICK HERE!!](/cd3_automation_toolkit/documentation/user_guide/prerequisites.md) to get started and manage your OCI Infra.


<br>

## ⭐️ Contributing
This project is open source.  Please submit your contributions by raising an <b>Issue</b> or through <b>Discussion topic</b> in this repository. Currently, we do not accept any pull requests. Oracle appreciates any contributions that are made by the open source community.

<br>

## ⚠️ License
Copyright (c) 2022 Oracle and/or its affiliates.

Licensed under the Universal Permissive License (UPL), Version 1.0.

See [LICENSE](LICENSE) for more details.

ORACLE AND ITS AFFILIATES DO NOT PROVIDE ANY WARRANTY WHATSOEVER, EXPRESS OR IMPLIED, FOR ANY SOFTWARE, MATERIAL OR CONTENT OF ANY KIND CONTAINED OR PRODUCED WITHIN THIS REPOSITORY, AND IN PARTICULAR SPECIFICALLY DISCLAIM ANY AND ALL IMPLIED WARRANTIES OF TITLE, NON-INFRINGEMENT, MERCHANTABILITY, AND FITNESS FOR A PARTICULAR PURPOSE.  FURTHERMORE, ORACLE AND ITS AFFILIATES DO NOT REPRESENT THAT ANY CUSTOMARY SECURITY REVIEW HAS BEEN PERFORMED WITH RESPECT TO ANY SOFTWARE, MATERIAL OR CONTENT CONTAINED OR PRODUCED WITHIN THIS REPOSITORY. IN ADDITION, AND WITHOUT LIMITING THE FOREGOING, THIRD PARTIES MAY HAVE POSTED SOFTWARE, MATERIAL OR CONTENT TO THIS REPOSITORY WITHOUT ANY REVIEW. USE AT YOUR OWN RISK.
