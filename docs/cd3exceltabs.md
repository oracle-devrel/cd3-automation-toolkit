
# OCI Services currently supported by Automation Toolkit

Click on the links below to know about the specifics of each tab in the excel sheet.

#### IAM/Identity

 - [Compartments](tabs.md#compartments-tab)

 - [Groups/Dynamic Groups](tabs.md#groups-tab)
  
 - [Policies](tabs.md#policies-tab)

 - [Users](tabs.md#users-tab)

 - [NetworkSources](tabs.md#network-sources-tab)

<a href="../terraform/identity"> Click here to view sample auto.tfvars for the Identity components</a> 
	


#### Governance

 - [Tags](tabs.md#tags-tab)

<a href="../terraform/governance/#1-tag-namespaces">Click here to view sample auto.tfvars for Tags</a> 

 - [Quotas](tabs.md#quotas-tab)

<a href="../terraform/governance/#4-quotas">Click here to view sample auto.tfvars for Quotas </a>


#### Cost Management

- [Budgets](tabs.md#budgets-tab)

<a href="../terraform/costmanagement/#budgets">Click here to view sample auto.tfvars for Budgets </a> 
   
<a href="../terraform/costmanagement/#budget-alert-rules">Click here to view sample auto.tfvars for Budget Alert Rules</a>



#### Network
  
 - [VCNs](tabs.md#a-vcns-tab)
  
 - [DRGs - VCN Attachments and RPC Attachments](tabs.md#b-drgs-tab)
  
 - [VCN Info](tabs.md#c-vcn-info-tab)
  
 - [DHCP](tabs.md#d-dhcp-tab)
  
 - [SubnetsVLANs](tabs.md#e-subnetsvlans-tab)
 
 - [DRGRouteRulesinOCI](tabs.md#f-rules)

 - [SecRulesinOCI](tabs.md#f-rules)

 - [RouteRulesinOCI](tabs.md#f-rules)

 - [NSGs](tabs.md#g-nsgs)
 
  

<a href="../terraform/network">Click here to view sample auto.tfvars for all Network components- VCNs, Subnets, Gateways etc.,</a> 

#### OCI Network Firewall

 - [Firewall](tabs.md#firewall-tabs)
 - [Firewall-Policy](tabs.md#firewall-tabs)
 - [Firewall-Policy-Applicationlist](tabs.md#firewall-tabs)
 - [Firewall-Policy-Servicelist](tabs.md#firewall-tabs)
 - [Firewall-Policy-Urllist](tabs.md#firewall-tabs)
 - [Firewall-Policy-Address](tabs.md#firewall-tabs)
 - [Firewall-Policy-Secrets](tabs.md#firewall-tabs)
 - [Firewall-Policy-Decryptprofile](tabs.md#firewall-tabs)
 - [Firewall-Policy-DecryptRule](tabs.md#firewall-tabs)
 - [Firewall-Policy-Secrules](tabs.md#firewall-tabs)

<a href="../terraform/firewall">Click here to view sample auto.tfvars for all Firewall components</a>    

#### Private-DNS
  
 - [DNS-Views-Zones-Records](tabs.md#dns-views-zones-records-tab)
  
 - [DNS-Resolvers](tabs.md#dns-resolvers-tab)
  

<a href="../terraform/dns">Click here to view sample auto.tfvars for all DNS components </a> 

#### Load Balancer

 - [LB-Hostname-Certs tab](tabs.md#lb-hostname-certs-tab)
 
 - [LB-Backend Set and Backend Servers](tabs.md#lb-backend-set-and-backend-servers-tab)
 
 - [LB-RuleSet](tabs.md#lb-ruleset-tab)
 
 - [LB-PathRouteSet](tabs.md#lb-path-route-set-tab)
 
 - [LB-RoutingPolicy](tabs.md#lb-routing-policy-tab)
 
 - [LB-Listener](tabs.md#lb-listeners-tab)

<a href="../terraform/loadbalancer">Click here to view sample auto.tfvars for all Load Balancer components- Cipher suits,Backend sets, rule sets etc.,</a>


#### Compute
 
 - [DedicatedVMHosts](tabs.md#dedicatedvmhosts-tab)
 
 - [Instances](tabs.md#instances-tab)

<a href="../terraform/compute">Click here to view sample auto.tfvars for Compute components-Virtual Machine</a> 

 
#### Storage
 
 - [BlockVolumes](tabs.md#blockvolumes-tab)
 
 <a href="../terraform/storage#block-volumes">Click here to view sample auto.tfvars for Block Volumes </a> 

 - [FSS](tabs.md#fss-tab)

 <a href="../terraform/storage#fss">Click here to view sample auto.tfvars for File Systems </a> 
 
 - [Object Storage Buckets](tabs.md#buckets-tab)
 
 <a href="../terraform/storage#buckets">Click here to view sample auto.tfvars for Object Storage Buckets</a> 
 

#### Oracle Database
 - [DBSystems-VM-BM](tabs.md#dbsystems-vm-bm-tab)
 
 - [ExaCS](tabs.md#exacs)
 
 - [ADB](tabs.md#adb-tab)
 

#### MySQL Database

 - [MySQL](tabs.md#mysql-tabs)
 
 
#### Monitoring Services
 
 - [Notifications](tabs.md#notifications-tab)
 
 - [Alarms](tabs.md#alarms-tab)

<a href="../terraform/managementservices">Click here to view sample auto.tfvars for management services Alarms, Notifications, Events etc.,</a> 
 
 - [ServiceConnectors](tabs.md#serviceconnectors-tab) 


<a href="../terraform/sch">Click here to view sample auto.tfvars for Service Connectors</a> 

 
#### Logging Services
 
 - [VCN Flow Logs]( tabs.md#vcn-flow-logs)

<a href="../terraform/logging#vcn-flow-logs">Click here to view sample auto.tfvars for VCN Flow Logs </a> 

 - [LBaaS Logs]( tabs.md#lbaas-logs)

<a href="../terraform/logging#load-balancer-logs">Click here to view sample auto.tfvars for Load Balancer Logs </a> 

 - [OSS Logs]( tabs.md#oss-logs)

<a href="../terraform/logging#object-storage-logs">Click here to view sample auto.tfvars for Object storage Logs </a> 
 
 - [FSS Logs]( tabs.md#fss-logs)
  
<a href="../terraform/logging#nfs-logs">Click here to view sample auto.tfvars for FSS Logs </a> 

 - [Firewall Logs]( tabs.md#firewall-logs)

<a href="../terraform/logging#firewall-logs">Click here to view sample auto.tfvars for Firewall Logs </a> 


#### Developer Services
 - [Upload to OCI Resource Manager Stack](../resource-manager-upload)
 
 - [OKE]( tabs.md#oke-tab)

<a href="../terraform/oke">Click here to view sample auto.tfvars for OKE components- Clusters, Nodepools</a> 


#### SDDCs tab
 
 - [OCVS]( tabs.md#sddcs-tab)
   
<a href="../terraform/sddc">Click here to view sample auto.tfvars for OCVS </a> 


#### Security

- [KMS](tabs.md#kms-tab)

<a href="../terraform/security/#1vaults">Click here to view sample auto.tfvars for KMS Vaults </a> 

<a href="../terraform/security/#2keys">Click here to view sample auto.tfvars for KMS Keys </a> 


- [Cloud Guard](tabs.md#cloud-guard)

<a href="../terraform/security/#cloud-guard">Click here to view sample auto.tfvars for Cloud Guard </a> 


