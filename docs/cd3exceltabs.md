
# OCI Services currently supported by Automation Toolkit

Click on the links below to know about the specifics of each tab in the excel sheet.

#### IAM/Identity

 - [Compartments](tabs.md#compartments-tab)

 - [Groups](tabs.md#groups-tab)
  
 - [Policies](tabs.md#policies-tab)

 - [Users](tabs.md#users-tab)

 - [NetworkSources](tabs.md#network-sources-tab)

<a href="../terraform/identity"> Click here to view sample auto.tfvars for the Identity components</a> 
	


#### Governance

 - [Tags](tabs.md#tags-tab)

<a href="../terraform/governance">Click here to view sample auto.tfvars for Governance components</a> 

#### Network
  
 - [VCNs](tabs.md#a-vcns-tab)
  
 - [DRGs](tabs.md#b-drgs-tab)
  
 - [VCN Info](tabs.md#c-vcn-info-tab)
  
 - [DHCP](tabs.md#d-dhcp-tab)
  
 - [SubnetsVLANs](tabs.md#e-subnetsvlans-tab)
 
 - [DRGRouteRulesinOCI](tabs.md#f-rules)

 - [SecRulesinOCI](tabs.md#f-rules)

 - [RouteRulesinOCI](tabs.md#f-rules)

 - [NSGs](tabs.md#g-nsgs)
 
  

<a href="../terraform/network">Click here to view sample auto.tfvars for all Network components- VCNs, Subnets, Gateways etc.,</a> 

#### Network Firewall

OCI Network Firewall can be created using [CD3-Firewall-template.xlsx](https://github.com/oracle-devrel/cd3-automation-toolkit/blob/main/cd3_automation_toolkit/example/CD3-Firewall-template.xlsx). Below are the tabs to create OCI Network Firewall and its associated policy. Check out the blue section of each tab to know how to fill in the parameter values.

 - Firewall
 - Firewall-Policy
 - Firewall-Policy-Applicationlist
 - Firewall-Policy-Servicelist
 - Firewall-Policy-Urllist
 - Firewall-Policy-Address
 - Firewall-Policy-Secrets
 - Firewall-Policy-Decryptprofile
 - Firewall-Policy-DecryptRule
 - Firewall-Policy-Secrules

After the required details are filled in, choose "OCI Firewall" under the SetUpOCI menu to create the Firewall and its policy. 

It is recommended to execute the validator script for Firewall, to validate the input values before proceeding to create.

Once the toolkit execution is complete,  you will find the generated output terraform files in the below location :

---> **<outdir\>/<region\>/<service_dir\>/<prefix\>_firewall*.auto.tfvars**

Once terraform apply is done, you can view the resources under Identity and Security -> Network Firewalls for the region.

<a href="../terraform/firewall">Click here to view sample auto.tfvars for all Firewall components</a> 
  

!!! Note 

   In the setUpOCI menu of Greenfield Workflow, there's a feature that allows you to clone policies using the option 'OCI Firewall'-->'Clone'. This feature exports data from the OCI console for the specified policy, adds it to the Excel sheet with a new name, generates tfvars, and triggers the Terraform-apply pipeline for the cloned policy.

   

#### Private-DNS
  
 - [DNS-Views-Zones-Records](tabs.md#dns-views-zones-records-tab)
  
 - [DNS-Resolvers](tabs.md#dns-resolvers-tab)
  

<a href="../terraform/dns">Click here to view sample auto.tfvars for all DNS components </a> 

#### Load Balancer

 - [LB-Hostname-Certs tab](tabs.md#lb-hostname-certs-tab)
 
 - [LB-Backend Set and Backend Servers](tabs.md#lb-backend-set-and-backend-servers-tab)
 
 - [LB-RuleSet](tabs.md#lb-ruleset-tab)
 
 - [LB-PathRouteSet](tabs.md#lb-path-route-set-tab)
 
 - [LB-Listener](tabs.md#lb-listeners-tab)

<a href="../terraform/loadbalancer">Click here to view sample auto.tfvars for all Load Balancer components- Cipher suits,Backend sets, rule sets etc.,</a>


#### Compute
 
 - [DedicatedVMHosts](tabs.md#dedicatedvmhosts-tab)
 
 - [Instances](tabs.md#instances-tab)

<a href="../terraform/compute">Click here to view sample auto.tfvars for Compute components-Virtual Machine</a> 
 
#### Storage
 
 - [BlockVolumes](tabs.md#blockvolumes-tab)
 
 <a href="../terraform/storage">Click here to view sample auto.tfvars for Block Volumes </a> 

 - [FSS](tabs.md#fss-tab)
 
 - [Object Storage Buckets](tabs.md#buckets-tab)
 
 <a href="../terraform/storage.md#2-Buckets">Click here to view sample auto.tfvars for Object Storage Buckets</a> 
 

#### Database
 - [DBSystems-VM-BM](tabs.md#dbsystems-vm-bm-tab)
 
 - [ExaCS](tabs.md#exacs)
 
 - [ADB](tabs.md#adb-tab)
 
 
#### Monitoring Services
 
 - [Notifications](tabs.md#notifications-tab)
 
 - [Alarms](tabs.md#alarms-tab)

<a href="../terraform/managementservices">Click here to view sample auto.tfvars for management services Alarms, Notifications, Events etc.,</a> 
 
 - [ServiceConnectors](tabs.md#serviceconnectors-tab) 


<a href="../terraform/sch">Click here to view sample auto.tfvars for Service Connectors</a> 

 
#### Logging Services
 
 - [VCN Flow Logs]( tabs.md#vcn-flow-logs)
 - [LBaaS Logs]( tabs.md#lbaas-logs)
- [OSS Logs]( tabs.md#oss-logs)

<a href="../terraform/logging">Click here to view sample auto.tfvars for Logging components </a> 


#### Developer Services
 
 - [OKE]( tabs.md#oke-tab)

<a href="../terraform/oke">Click here to view sample auto.tfvars for OKE components- Clusters, Nodepools</a> 


#### SDDCs tab
 
 - [OCVS]( tabs.md#sddcs-tab)
   
<a href="../terraform/sddc">Click here to view sample auto.tfvars for OCVS </a> 


