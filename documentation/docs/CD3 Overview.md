
# **CD3 Automation Toolkit**  
<img width="25%" height="30%"  alt="CD3 Logo" src= "/images/CD3-logo.png"> 
---

The CD3 toolkit reads input data in the form of CD3 Excel sheet and generates Terraform files which can be used to provision the resources in OCI instead of handling the task through the OCI console manually. The toolkit also reverse engineers the components in OCI back to the Excel sheet and Terraform configuration. The toolkit can be used throughout the lifecycle of tenancy to continuously create or modify existing resources. The generated Terraform code can be used by the OCI Resource Manager or can be integrated into organization's existing devops CI/CD ecosystem.

<br>

<iframe width="100%" height="500" src="https://www.youtube.com/embed/watch?v=TSNu0pUHYsE&list=PLPIzp-E1msrbJ3WawXVhzimQnLw5iafcp&index=1">
</iframe>


:fontawesome-brands-youtube:{ style="color: #EE0F0F" } [CD3 Automation Toolkit Explained in 1 minute](https://www.youtube.com/watch?v=TSNu0pUHYsE&list=PLPIzp-E1msrbJ3WawXVhzimQnLw5iafcp&index=1) – :octicons-clock-24:

<br>

<div class="grid cards" markdown >

-   :material-clock-fast:{ .lg .middle } __Getting Started__

    ---
    [Introduction](#Introduction)<br>
    [What's new in this release](#What's_new_in_this_release)<br>
    [Toolkit Supported OCI Services](#)<br>
    [Excel Templates](#)<br>

-   :material-hammer-screwdriver:{ .lg .middle } __Deploying CD3__

    ---
    [Prerequisites](#Prerequisites)<br>
    [Launch the container](#Launch the container)<br>
    [Connect container to OCI tenancy](#)<br>

-   :material-monitor-screenshot:{ .lg .middle } __Toolkit Execution with CLI__

    ---
    [Overview](#)<br>
    [Create resources in OCI using CLI (Greenfield Workflow)](#)<br>
    [Create Network resources-CLI](#)<br>
    [Create Compute Instances-CLI](#)<br>
    [OPA integration](#)<br>
    [Export Resources from OCI using CLI (Non-Greenfield Workflow)](#)<br>
    [Export Network resources-CLI](#)<br>
    [Export Compute Instances-CLI](#)<br>

-   :material-lightbulb-auto:{ .lg .middle } __Toolkit Execution with Jenkins__

    ---

    [Prerequisites](#)<br>
    [Overview](#)<br>
    [Create resources in OCI using Jenkins(Greenfield Workflow))](#)<br>
    [Create Network resources-Jenkins](#)<br>
    [Create compute Instances/OKE/SDDC/Database-Jenkins](#)<br>
    [Provision multiple services together-Jenkins](#)<br>
    [Export Resources from OCI using Jenkins(Non-Greenfield Workflow)](#)<br>
    [Synchronize Changes between CLI and Jenkins](#)<br>   
    

-   :material-feather:{ .lg .middle } __Beyond the basics__

    ---
    [Grouping generated Terraform files](#Introduction)<br>
    [OCI Resource Manager Upload](#What's_new_in_this_release)<br>
    [Support for Additional Attributes](#)<br>
    [Additional CIS Compliance Features](#)<br>
    [CD3 Validators](#)<br>
    [Migrate jobs to User's Jenkins environment](#)<br>
    [Remote Management of Terraform State](#)<br>

-   :material-information:{ .lg .middle } __Known Behaviour__

    ---
    [Expected Behaviour of CD3](#)<br>
    [FAQs](#)<br>

-  :material-school:{ .lg .middle } __Videos & Tutorials__

    ---
    [Automation Toolkit Learning Videos](#)<br>
    [Tutorials](#)<br>
</div>