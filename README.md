# cd3-automation-toolkit

[![License: UPL](https://img.shields.io/badge/license-UPL-green)](https://img.shields.io/badge/license-UPL-green) [![Quality gate](https://sonarcloud.io/api/project_badges/quality_gate?project=oracle-devrel_cd3-automation-toolkit)](https://sonarcloud.io/dashboard?id=oracle-devrel_cd3-automation-toolkit)

## Introduction
CD3 stands for <b>C</b>loud <b>D</b>eployment <b>D</b>esign <b>D</b>eliverable.
The CD3 Automation toolkit has been developed to help in automating the OCI resource object management. 
<br><br>
It reads input data in the form of CD3 Excel sheets and generates the terraform files instead of handling the task through the OCI console manually. The toolkit also reverse engineers the components in OCI back to the Excel sheet and Terraform configuration. This generated Terraform code can be used by the OCI Resource Manager or leveraged by the organisations’ CI/CD processes.
<br><br>
<img width="748" alt="Screenshot 2022-12-30 at 11 57 41 AM" src="https://user-images.githubusercontent.com/111430850/210614513-5d2e97a6-3c1e-4a2b-a793-3a1b6410c856.png">
<br>

#### OCI Services Currently Supported by CD3

| OCI Services | Details |
| --------- | ----------- |
| IAM | Compartments, Groups, Dynamic Groups, Policies |
| Network | VCNs, Subnets, DRGs, IGWs, NGWs, LPGs, Route Tables, DRG Route, Tables, Security Lists, Network Security Groups, Application Load Balancer, Network Load Balancers |
| Governance | Tags (Namespaces, Tag Keys, Defined Tags, Default Tags, Cost Tracking) |
| Compute | Instances – VM, BM, Dedicated VM Hosts |
| Storage | FSS, Block and Boot Volumes, Backup Policies |
| Database | Exa Infra, ExaCS, DB Systems VM and BM, ATP, ADW |
| Management Services | Events, Notifications, Alarms, Service Connector Hub (SCH) |
| Developer Services | Resource Manager, Oracle Kubernetes Engine (OKE) |
| CIS Landing Zone Compliance | Download CIS Report Script, Execute CIS Report Script, VCN Flow Logs, Cloud Guard, Object Storage, Key Vault, Budget |

`To ease the execution of toolkit, we have provided the steps to build an image which encloses the code base and its package dependencies. Follow the steps provided below to clone the repo and build the image.`
<br>

## Getting Started

### Pre-requisites
* Git
* Any docker CLI compatible platform such as Docker or Rancher.
* Local Directory - A directory in your local system that will be shared with the container to hold the generated Terraform files.
* OCI Tenancy Access Requirement - 
Appropriate IAM policies must be in place for each of the resources that the user may try to create.
Minimum requirement for the user to get started is to have the ability to read to the tenancy.


### To clone the repo
* Open your terminal and change the directory to the one where you want to download the git repo.
* Run the git clone command as shown below:<br/>
&nbsp; &nbsp; &nbsp; &nbsp; git clone https://github.com/oracle-devrel/cd3-automation-toolkit
* Once the cloning command completes successfully, the repo will replicate to the local directory. 

### To build an image

* Change directory to cd3-automation-toolkit(i.e. the cloned repo in your local).
* Run <i>"docker build --platform linux/amd64 -t cd3toolkit:${image_tag} -f Dockerfile --pull --no-cache ."</i><br/>
<br  /><b>Note</b> : ${image_tag} should be replaced with suitable tag as per your requirements/standards.
<br  />&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;The period at the end of the docker build command is required.

### To save the image (Optional)
* Run  <i>"docker save cd3toolkit:${image_tag} | gzip > cd3toolkit_${image_tag}.tar.gz"</i>


### To run the CD3 container and exec into it
* Run  <i>"docker run --platform linux/amd64 -it -d -v <directory_in_local_system_where_the_files_must_be_generated>:/cd3user/tenancies <image_name>:<image_tag>"</i>
* Run  <i>"docker ps"</i>
* Run  <i>"docker exec -it <container_id> bash"</i>
<br><br>
Follow the toolkit docs i.e. from the section <i>"Configuring the Docker Container to connect to OCI Tenancy"</i> in 
<a href="https://github.com/oracle-devrel/cd3-automation-toolkit/blob/develop/cd3_automation_toolkit/documentation/user_guide/01%20CD3%20Automation%20Toolkit%20-%20End%20to%20End%20Process.pdf">CD3 Automation Tookit - End To End Process Documentation</a>. Please download the document from Github.
<br>
<i>CD3 Quick Start template can be found at <b><a href="https://github.com/oracle-devrel/cd3-automation-toolkit/blob/develop/cd3_automation_toolkit/example/CD3-CIS-template.xlsx">CD3 CIS Template</a></b></i>
<br>
<i>CD3 Sample Excel templates can be found at <b><a href="https://github.com/oracle-devrel/cd3-automation-toolkit/tree/develop/cd3_automation_toolkit/example">Excel Templates</a> </b></i>
<br>
<br>
<b>Note</b> : <i>The above steps have been tested on Windows (Git Bash) and MacOS.</i><br/>

## Contributing
This project is open source.  Please submit your contributions by raising an <b>Issue</b> or through <b>Discussion topic</b> in this repository. Currently, we do not accept any pull requests. Oracle appreciates any contributions that are made by the open source community.

## License
Copyright (c) 2022 Oracle and/or its affiliates.

Licensed under the Universal Permissive License (UPL), Version 1.0.

See [LICENSE](LICENSE) for more details.

ORACLE AND ITS AFFILIATES DO NOT PROVIDE ANY WARRANTY WHATSOEVER, EXPRESS OR IMPLIED, FOR ANY SOFTWARE, MATERIAL OR CONTENT OF ANY KIND CONTAINED OR PRODUCED WITHIN THIS REPOSITORY, AND IN PARTICULAR SPECIFICALLY DISCLAIM ANY AND ALL IMPLIED WARRANTIES OF TITLE, NON-INFRINGEMENT, MERCHANTABILITY, AND FITNESS FOR A PARTICULAR PURPOSE.  FURTHERMORE, ORACLE AND ITS AFFILIATES DO NOT REPRESENT THAT ANY CUSTOMARY SECURITY REVIEW HAS BEEN PERFORMED WITH RESPECT TO ANY SOFTWARE, MATERIAL OR CONTENT CONTAINED OR PRODUCED WITHIN THIS REPOSITORY. IN ADDITION, AND WITHOUT LIMITING THE FOREGOING, THIRD PARTIES MAY HAVE POSTED SOFTWARE, MATERIAL OR CONTENT TO THIS REPOSITORY WITHOUT ANY REVIEW. USE AT YOUR OWN RISK. 
