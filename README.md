
[![License: UPL](https://img.shields.io/badge/license-UPL-green)](https://img.shields.io/badge/license-UPL-green) [![Quality gate](https://sonarcloud.io/api/project_badges/quality_gate?project=oracle-devrel_cd3-automation-toolkit)](https://sonarcloud.io/dashboard?id=oracle-devrel_cd3-automation-toolkit)

<br>

# CD3 Automation Toolkit

<br>
 
  [What's New](https://github.com/oracle-devrel/cd3-automation-toolkit/releases/tag/v2025.2.1) &nbsp;•&nbsp;[Excel Templates](https://oracle-devrel.github.io/cd3-automation-toolkit/latest/excel-templates/) &nbsp;•&nbsp;[CD3 Docs](https://oracle-devrel.github.io/cd3-automation-toolkit/)&nbsp;•&nbsp; [Watch & Learn](https://www.youtube.com/playlist?list=PLPIzp-E1msrbJ3WawXVhzimQnLw5iafcp) &nbsp;•&nbsp;[Blogs & Tutorials](https://oracle-devrel.github.io/cd3-automation-toolkit/latest/tutorials/) &nbsp;•&nbsp;[Livelabs](https://apexapps.oracle.com/pls/apex/f?p=133:180:112501098061930::::wid:3724) &nbsp;•&nbsp;[Slack Channel](https://oracle-devrel.github.io/cd3-automation-toolkit/latest/queries) 
  
<br>


CD3 stands for **Cloud Deployment Design Deliverable**. The CD3 Automation toolkit enables you to effortlessly Build, Export and Manage OCI (Oracle Cloud Infrastructure) resources by converting Excel templates to fully functional Terraform modules within minutes ⚡️⚡️ .

Additionally, the toolkit also supports seamless resource management using OCI DevOps GIT service and Jenkins Pipelines.

<br>

🚀 Click the below button to quickly launch CD3 toolkit container in Oracle Cloud and start managing your Infra as Code. 
<br>

[![Deploy_To_OCI](https://oci-resourcemanager-plugin.plugins.oci.oraclecloud.com/latest/deploy-to-oracle-cloud.svg)](https://cloud.oracle.com/resourcemanager/stacks/create?zipUrl=https://github.com/oracle-devrel/cd3-automation-toolkit/archive/refs/heads/develop.zip)

<br>

<h2>📌 Toolkit Supported OCI Services</h2>

<table>
  
  <tr>
    <td>IAM/Identity</td>
    <td>Tagging</td>
    <td>Quotas</td>
  </tr>
  <tr>
    <td>Network</td>
    <td>DNS Management</td>
    <td>Load Balancers</td>
  </tr>
  <tr>
    <td>Compute</td>
    <td>Storage</td>
    <td>Oracle, MySQL Databases</td>    
  </tr>
    <tr>
    <td>OCI Network Firewall</td>
    <td>KMS</td>
    <td>Policy Enforcement using OPA</td>  
  </tr>
  <tr>
    <td>OKE</td>
    <td>Resource Manager</td>
    <td>SDDCs</td>    
  </tr>
  <tr>
    <td>Logging Services</td>
    <td>Monitoring</td>
    <td>Budgets</td>
  </tr>
  <tr>    
    <td>Cloud Guard</td>
    <td>SHOWOCI report</td>    
    <td>CIS Compliance Report</td> 
  </tr>
</table>
</tr>
</body>

📌 The Toolkit also extends its support to <b>ADB@Azure</b>

<br>

## Why CD3?


⏳ For Enterprise infrastructures, manual resource provisioning is tedious and error-prone.

📝 Creating Terraform Code for each module/resource can be cumbersome and requires Terraform expertise.

🔁 Manually created infrastructure is hard to rebuild for different environments or regions.

<br>

##  How CD3 works?


The toolkit transforms input data from Excel files into Terraform files, enabling seamless creation of infrastructure in OCI.

**CD3 isn't just about creation!!!** ⬅️ Reverse engineer existing infrastructure back into Excel and IaC(terraform) and continue to manage your OCI resources using CD3.

📜 The generated Terraform code can be used by the OCI Resource Manager or can be integrated into organization's existing DevOps CI/CD ecosystem.

<br>

## 👥 Who can use the toolkit??

  Anyone who wants to create/modify new resources in OCI or export existing resources from OCI and manage IaC without much effort. 

<br>

## 💡 Benefits of CD3:


   ✅ Time saving ⏰ 
  
   ✅ Faster infrastructure provisioning 🚀
  
   ✅ Scalability 📈
  
   ✅ Operational efficiency ⚙️

<br>

   **There's more!!**

**Secure architecture 🛡️:** CD3 toolkit helps customers deploy secure standardization across OCI tenancies by providing CIS-compliant Excel templates. It also enables native execution of the CIS Compliance Checker script against your tenancy.

**DevOps-oriented 🔄:** The toolkit facilitates integration of consistent output Terraform files in module format with any continuous integration and delivery (CI/CD) solution. The Terraform code can be reused to build similar workloads in different OCI regions and tenancies, which helps in quicker adoption of OCI.

**Platform independent 🌐:** CD3 is packaged as a container that can be hosted on any platform.
 
<br>


## Where to get started?

[Click here](https://oracle-devrel.github.io/cd3-automation-toolkit/) to learn how to setup the toolkit and start managing your OCI Infra !!

<br>

## ⭐️ Contributing
This project is open source.  Please submit your contributions by raising an <b>Issue</b> or through <b>Discussion topic</b> in this repository. Currently, we do not accept any pull requests. Oracle appreciates any contributions that are made by the open source community.

<br>

## ⚠️ License
Copyright (c) 2024 Oracle and/or its affiliates.

Licensed under the Universal Permissive License (UPL), Version 1.0.

See [LICENSE](LICENSE.txt) for more details. 

ORACLE AND ITS AFFILIATES DO NOT PROVIDE ANY WARRANTY WHATSOEVER, EXPRESS OR IMPLIED, FOR ANY SOFTWARE, MATERIAL OR CONTENT OF ANY KIND CONTAINED OR PRODUCED WITHIN THIS REPOSITORY, AND IN PARTICULAR SPECIFICALLY DISCLAIM ANY AND ALL IMPLIED WARRANTIES OF TITLE, NON-INFRINGEMENT, MERCHANTABILITY, AND FITNESS FOR A PARTICULAR PURPOSE.  FURTHERMORE, ORACLE AND ITS AFFILIATES DO NOT REPRESENT THAT ANY CUSTOMARY SECURITY REVIEW HAS BEEN PERFORMED WITH RESPECT TO ANY SOFTWARE, MATERIAL OR CONTENT CONTAINED OR PRODUCED WITHIN THIS REPOSITORY. IN ADDITION, AND WITHOUT LIMITING THE FOREGOING, THIRD PARTIES MAY HAVE POSTED SOFTWARE, MATERIAL OR CONTENT TO THIS REPOSITORY WITHOUT ANY REVIEW. USE AT YOUR OWN RISK.
