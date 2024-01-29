# CD3 Automation Toolkit

[![License: UPL](https://img.shields.io/badge/license-UPL-green)](https://img.shields.io/badge/license-UPL-green) [![Quality gate](https://sonarcloud.io/api/project_badges/quality_gate?project=oracle-devrel_cd3-automation-toolkit)](https://sonarcloud.io/dashboard?id=oracle-devrel_cd3-automation-toolkit)



<ul>

  <li> <a href= "#introduction">Introduction</a></li>

  <li> <a href = "https://github.com/oracle-devrel/cd3-automation-toolkit/releases/tag/v12.1">What's new in this release</a></li>
  <li> <a href = "/cd3_automation_toolkit/documentation/user_guide/learn_more/CD3ExcelTabs.md">Toolkit Supported OCI Services</a></li>
  <li> <a href = "/cd3_automation_toolkit/documentation/user_guide/ExcelTemplates.md">Excel Templates</a></li>
  
</ul>

### New Users

<ul>
  
  <li> <a href = "/cd3_automation_toolkit/documentation/user_guide/prerequisites.md">Prerequisites</a></li>
  <li> <a href = "/cd3_automation_toolkit/documentation/user_guide/Launch_Docker_container.md">Launch the container</a></li>
  <li> <a href = "/cd3_automation_toolkit/documentation/user_guide/Connect_container_to_OCI_Tenancy.md">Connect container to OCI Tenancy</a></li>
  
  <li> <a href="/cd3_automation_toolkit/documentation/user_guide/Workflows.md">Using the Automation Toolkit via CLI</a>
  <ul>
  <li> <a href="/cd3_automation_toolkit/documentation/user_guide/GreenField.md">Create resources in OCI (Greenfield Workflow)</a>
    <ul>
      <li> <a href="/cd3_automation_toolkit/documentation/user_guide/learn_more/OPAForCompliance.md"</a> Enforcing OPA (Open Policy Agent) policies for Terraform </li>
      <li> <a href="/cd3_automation_toolkit/documentation/user_guide/NetworkingScenariosGF.md"</a><b> Must Read :</b> Managing Network for Greenfield Workflow</li>
      <li> <a href="/cd3_automation_toolkit/documentation/user_guide/ComputeGF.md"</a><b> Must Read :</b> Managing Compute Instances for Greefield Workflow</li>
    </ul>
    </ul>
  </li>
  <ul>
  <li> <a href="/cd3_automation_toolkit/documentation/user_guide/NonGreenField.md">Export Resources from OCI (Non-Greenfield Workflow)</a>
    <ul>
      <li><a href ="/cd3_automation_toolkit/documentation/user_guide/NetworkingScenariosNGF.md"</a><b> Must Read : </b> Managing Network for Non-Greenfield Workflow</li>
       <li><a href = "/cd3_automation_toolkit/documentation/user_guide/ComputeNGF.md"</a><b>  Must Read : </b> Managing Compute Instances for Non-Greenfield Workflow </li> 
    </ul>
  </ul>
 <li> <a href="/cd3_automation_toolkit/documentation/user_guide/Workflows-jenkins.md"</a>Using the Automation Toolkit via Jenkins
    <ul> 
         <li> <a href="/cd3_automation_toolkit/documentation/user_guide/GreenField-Jenkins.md"</a>Create resources in OCI via Jenkins(Greenfield Workflow) </li>
         <li> <a href="/cd3_automation_toolkit/documentation/user_guide/GF-Jenkins.md"</a><b>  Must Read : </b> Creation of Resources - Instances/OKE/SDDC/Database </li>
         <li> <a href="/cd3_automation_toolkit/documentation/user_guide/NonGreenField-Jenkins.md"</a>Export Resources from OCI via Jenkins(Non-Greenfield Workflow) </li>       </ul>
  </li> 
  <li> <a href="/cd3_automation_toolkit/documentation/user_guide/cli_jenkins.md">Switch between CLI and Jenkins</a></li>
  <li> <a href="/cd3_automation_toolkit/documentation/user_guide/remote_state.md">Remote Management of Terraform State File</a></li>
 </ul>
 
 ### Existing Users

<ul>
 
  <li> <a href = "/cd3_automation_toolkit/documentation/user_guide/Upgrade_Toolkit.md">Steps to Upgrade Your Toolkit</a></li>
  <li> <a href = "/cd3_automation_toolkit/documentation/user_guide/Jobs_Migration.md">Migrating Jenkins Jobs</a></li>
</ul> 

### Videos...
<li> <a href = "/cd3_automation_toolkit/documentation/user_guide/LearningVideos.md">Automation Toolkit Learning Videos</a></li>
   

### Learn More...

<ul>

   <li> <a href = "/cd3_automation_toolkit/documentation/user_guide/RestructuringOutDirectory.md">Grouping of generated Terraform files</a></li>
   <li> <a href = "/cd3_automation_toolkit/documentation/user_guide/learn_more/ResourceManagerUpload.md">OCI Resource Manager Upload</a></li>
   <li> <a href = "/cd3_automation_toolkit/documentation/user_guide/learn_more/CISFeatures.md">Additional CIS Compliance Features</a></li>
   <li> <a href = "/cd3_automation_toolkit/documentation/user_guide/learn_more/SupportForCD3Validator.md">CD3 Validator Features</a></li>
 
   
   <li> <a href = "/cd3_automation_toolkit/documentation/user_guide/learn_more/SupportforAdditionalAttributes.md">Support for Additional Attributes</a></li>
   <li> <a href = "/cd3_automation_toolkit/documentation/user_guide/KnownBehaviour.md">Expected Behaviour Of Automation Toolkit</a></li>
   <li> <a href = "/cd3_automation_toolkit/documentation/user_guide/FAQ.md">FAQs</a></li>
 
</ul>
  


## Introduction
CD3 stands for <b>C</b>loud <b>D</b>eployment <b>D</b>esign <b>D</b>eliverable.
The CD3 Automation toolkit has been developed to help in automating the OCI resource object management. 
<br><br>
It reads input data in the form of CD3 Excel sheet and generates Terraform files which can be used to provision the resources in OCI instead of handling the task through the OCI console manually. The toolkit also reverse engineers the components in OCI back to the Excel sheet and Terraform configuration. The toolkit can be used throughout the lifecycle of tenancy to continuously create or modify existing resources. The generated Terraform code can be used by the OCI Resource Manager or can be integrated into organization's existing devops CI/CD ecosystem.
<br><br>
<kbd>
<img width="748" alt="Screenshot 2022-12-30 at 11 57 41 AM" src="https://user-images.githubusercontent.com/111430850/210614513-5d2e97a6-3c1e-4a2b-a793-3a1b6410c856.png">
</kbd>
<br>

#### OCI Services Currently Supported by Automation Toolkit

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


[Click here](/cd3_automation_toolkit/documentation/user_guide/prerequisites.md) to get started and manage your OCI Infra!

## Contributing
This project is open source.  Please submit your contributions by raising an <b>Issue</b> or through <b>Discussion topic</b> in this repository. Currently, we do not accept any pull requests. Oracle appreciates any contributions that are made by the open source community.

## License
Copyright (c) 2022 Oracle and/or its affiliates.

Licensed under the Universal Permissive License (UPL), Version 1.0.

See [LICENSE](LICENSE) for more details.

ORACLE AND ITS AFFILIATES DO NOT PROVIDE ANY WARRANTY WHATSOEVER, EXPRESS OR IMPLIED, FOR ANY SOFTWARE, MATERIAL OR CONTENT OF ANY KIND CONTAINED OR PRODUCED WITHIN THIS REPOSITORY, AND IN PARTICULAR SPECIFICALLY DISCLAIM ANY AND ALL IMPLIED WARRANTIES OF TITLE, NON-INFRINGEMENT, MERCHANTABILITY, AND FITNESS FOR A PARTICULAR PURPOSE.  FURTHERMORE, ORACLE AND ITS AFFILIATES DO NOT REPRESENT THAT ANY CUSTOMARY SECURITY REVIEW HAS BEEN PERFORMED WITH RESPECT TO ANY SOFTWARE, MATERIAL OR CONTENT CONTAINED OR PRODUCED WITHIN THIS REPOSITORY. IN ADDITION, AND WITHOUT LIMITING THE FOREGOING, THIRD PARTIES MAY HAVE POSTED SOFTWARE, MATERIAL OR CONTENT TO THIS REPOSITORY WITHOUT ANY REVIEW. USE AT YOUR OWN RISK.
