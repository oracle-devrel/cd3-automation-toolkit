# CD3-Automation-Toolkit

[![License: UPL](https://img.shields.io/badge/license-UPL-green)](https://img.shields.io/badge/license-UPL-green) [![Quality gate](https://sonarcloud.io/api/project_badges/quality_gate?project=oracle-devrel_cd3-automation-toolkit)](https://sonarcloud.io/dashboard?id=oracle-devrel_cd3-automation-toolkit)

## Table of Contents :bookmark:

1. [Introduction](#introduction)
2. [Pre-requisites](#pre-requisites)
3. [Launch Docker container](/cd3_automation_toolkit/documentation/user_guide/Launch_Docker_container.md)
4. [Connect container to OCI Tenancy](/cd3_automation_toolkit/documentation/user_guide/Connect_container_to_OCI_Tenancy.md)
5. [Getting Started with Automation Toolkit](/cd3_automation_toolkit/documentation/user_guide/RunningAutomationToolkit.md)
6. [Using the Automation Toolkit](/cd3_automation_toolkit/documentation/user_guide/Workflows.md)
   - [Green Field Tenancies](/cd3_automation_toolkit/documentation/user_guide/GreenField.md)
   - [Non-Green Field Tenancies](/cd3_automation_toolkit/documentation/user_guide/NonGreenField.md)
7. MUST READ...
   - [Managing Network for Green Field Tenancies](/cd3_automation_toolkit/documentation/user_guide/NetworkingScenariosGF.md)
   - [Managing Network for Non Green Field Tenancies](/cd3_automation_toolkit/documentation/user_guide/NetworkingScenariosNGF.md)
8. [Creating independent tfstate files for each resource](/cd3_automation_toolkit/documentation/user_guide/RestructuringOutDirectory.md)
9. [Expected Behaviour Of Automation Toolkit](/cd3_automation_toolkit/documentation/user_guide/KnownBehaviour.md)
10. [FAQs](/cd3_automation_toolkit/documentation/user_guide/FAQ.md)
11. Learn More...
    - CD3 Excel Information
      - [Excel Templates](/cd3_automation_toolkit/documentation/user_guide/RunningAutomationToolkit.md#excel-sheet-templates)
      - [OCI Services](/cd3_automation_toolkit/documentation/user_guide/learn_more/CD3ExcelTabs.md)
    - [CD3 Validator Features](/cd3_automation_toolkit/documentation/user_guide/learn_more/SupportForCD3Validator.md)
    - [Additional CIS Compliance Features](/cd3_automation_toolkit/documentation/user_guide/learn_more/CISFeatures.md)
    - [OCI Resource Manager Upload](/cd3_automation_toolkit/documentation/user_guide/learn_more/ResourceManagerUpload.md)
    - [Support for Additional Attributes](/cd3_automation_toolkit/documentation/user_guide/learn_more/SupportforAdditionalAttributes.md)
12. [Automation Toolkit Learning Videos](/cd3_automation_toolkit/documentation/user_guide/LearningVideos.md)

## Introduction
CD3 stands for <b>C</b>loud <b>D</b>eployment <b>D</b>esign <b>D</b>eliverable.
The CD3 Automation toolkit has been developed to help in automating the OCI resource object management. 
<br><br>
It reads input data in the form of CD3 Excel sheet and generates the terraform files which can be used to provision the resources in OCI instead of handling the task through the OCI console manually. The toolkit also reverse engineers the components in OCI back to the Excel sheet and Terraform configuration. This generated Terraform code can be used by the OCI Resource Manager or leveraged by the organisations’ CI/CD processes.
<br><br>
<kbd>
<img width="748" alt="Screenshot 2022-12-30 at 11 57 41 AM" src="https://user-images.githubusercontent.com/111430850/210614513-5d2e97a6-3c1e-4a2b-a793-3a1b6410c856.png">
</kbd>
<br>

#### OCI Services Currently Supported by CD3

| OCI Services | Details |
| --------- | ----------- |
| [IAM/Identity](/cd3_automation_toolkit/documentation/user_guide/learn_more/CD3ExcelTabs.md#iamidentity) | Compartments, Groups, Dynamic Groups, Policies |
| [Network](/cd3_automation_toolkit/documentation/user_guide/learn_more/CD3ExcelTabs.md#network) | VCNs, Subnets, DRGs, IGWs, NGWs, LPGs, Route Tables, DRG Route, Tables, Security Lists, Network Security Groups, Application Load Balancer, Network Load Balancers |
| [Governance](/cd3_automation_toolkit/documentation/user_guide/learn_more/CD3ExcelTabs.md#governance) | Tags (Namespaces, Tag Keys, Defined Tags, Default Tags, Cost Tracking) |
| [Compute](/cd3_automation_toolkit/documentation/user_guide/learn_more/CD3ExcelTabs.md#compute) | Instances – VM, BM, Dedicated VM Hosts |
| [Storage]((/cd3_automation_toolkit/documentation/user_guide/learn_more/CD3ExcelTabs.md#storage) | FSS, Block and Boot Volumes, Backup Policies |
| [Database](/cd3_automation_toolkit/documentation/user_guide/learn_more/CD3ExcelTabs.md#database) | Exa Infra, ExaCS, DB Systems VM and BM, ATP, ADW |
| [Management Services](/cd3_automation_toolkit/documentation/user_guide/learn_more/CD3ExcelTabs.md#management-services) | Events, Notifications, Alarms, Service Connector Hub (SCH) |
| [Developer Services](/cd3_automation_toolkit/documentation/user_guide/learn_more/CD3ExcelTabs.md#developer-services) | Resource Manager, Oracle Kubernetes Engine (OKE) |
| CIS Landing Zone Compliance | Download CIS Report Script, Execute CIS Report Script, VCN Flow Logs, Cloud Guard, Object Storage, Key Vault, Budget |


## Pre-requisites
* Git
* Any docker CLI compatible platform such as Docker or Rancher.
* Local Directory - A directory in your local system that will be shared with the container to hold the generated Terraform files.
* OCI Tenancy Access Requirement - 
Appropriate IAM policies must be in place for each of the resources that the user may try to create.
Minimum requirement for the user to get started is to have the ability to read to the tenancy.

[Click here](/cd3_automation_toolkit/documentation/user_guide/Launch_Docker_container.md) to get started and manage your OCI Infra!!! 

## Contributing
This project is open source.  Please submit your contributions by raising an <b>Issue</b> or through <b>Discussion topic</b> in this repository. Currently, we do not accept any pull requests. Oracle appreciates any contributions that are made by the open source community.

## License
Copyright (c) 2022 Oracle and/or its affiliates.

Licensed under the Universal Permissive License (UPL), Version 1.0.

See [LICENSE](LICENSE) for more details.

ORACLE AND ITS AFFILIATES DO NOT PROVIDE ANY WARRANTY WHATSOEVER, EXPRESS OR IMPLIED, FOR ANY SOFTWARE, MATERIAL OR CONTENT OF ANY KIND CONTAINED OR PRODUCED WITHIN THIS REPOSITORY, AND IN PARTICULAR SPECIFICALLY DISCLAIM ANY AND ALL IMPLIED WARRANTIES OF TITLE, NON-INFRINGEMENT, MERCHANTABILITY, AND FITNESS FOR A PARTICULAR PURPOSE.  FURTHERMORE, ORACLE AND ITS AFFILIATES DO NOT REPRESENT THAT ANY CUSTOMARY SECURITY REVIEW HAS BEEN PERFORMED WITH RESPECT TO ANY SOFTWARE, MATERIAL OR CONTENT CONTAINED OR PRODUCED WITHIN THIS REPOSITORY. IN ADDITION, AND WITHOUT LIMITING THE FOREGOING, THIRD PARTIES MAY HAVE POSTED SOFTWARE, MATERIAL OR CONTENT TO THIS REPOSITORY WITHOUT ANY REVIEW. USE AT YOUR OWN RISK.
