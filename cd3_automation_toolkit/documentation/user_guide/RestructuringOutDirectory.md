## Restructuring Terraform Out Directory

CD3 Automation Toolkit generates all the output terraform files in a single region directory. OCI components like - network, instances, LBaaS, Databases etc are maintained in a single tfstate file. This may not be a viable option if you are planning to build a huge infrastructure.

This document explains how to organise separate TF files for each of the resources. TF files should be separated at the start, before you execute _terraform apply_ for any resource. If you already have components created in OCI, export them and follow the below steps before importing them into the state.


### Requirements:

Segregation of duties with terraform stacks is the main focus. Each service owner should be able to handle their services without stepping onto other's tfstate files.

Managing a large infrastructure using a single tfstate file will take a plethora of time for terraform refresh while applying any small change. So different tfstate files are needed for different services.

### Solution:

Below are steps that will split the resources into individual terraform files:

1. CD3 Automation Toolkit produces the out directory as shown in the screenshot below. Please note the changes for instances while re-organising  the directory structure.

   <img src = "https://user-images.githubusercontent.com/122371432/214547857-0b39cffa-aca3-4230-b125-33b0504b2196.png" width=25% height=25%>
   
   ![image](https://user-images.githubusercontent.com/122371432/214554139-890dd637-3752-47d5-a232-a9542368304d.png)

2. To modify and maintain the Terraform files effortlessly in future, consider each of the region based directories to be a datacenter, pull out the modules folder from each of them and place a single copy of the modules in a common location as shown below. This allows to add new regions/data centers while maintaining the modules at one place.

   <img src ="https://user-images.githubusercontent.com/122371432/214554830-987de0c3-5431-4f0e-ae28-b260b8b4eb35.png" width=80% height=80%>

3. To organise the folder according to the duties, split each region/datacenter directory to contain individual folders for all the OCI components.
   
   Example: 
   - 'Ceph-VMs' contains instances for Ceph. 
   - 'Elastic-VMs' contains instances for Elastic Search. 
   - 'ES-LBaaS' contains load balancers for Elastic Search. 
   - 'Network' contains all network components like VCNs, Subnets, Security Lists, Route Tables and so on.

   Each folder also has its own input .tfvars file and a .tfstate file.
   Example: 'Ceph-VMs' contains 2 .auto.tfvars files - one for instances and another one for attached block volumes. All the .tf files are the terraform root modules which in turn calls the terraform sub-modules for every entry in .tfvars.


   <img src ="https://user-images.githubusercontent.com/122371432/214557469-a98a2b96-5057-4b04-b74c-b410de98eb0e.png" width=60% height=60%>
   
4. Another change that is needed is to point the source parameter in the .tf files (root modules) to the right module path (sub-modules) for all module calls that may be affected.

   Example: The source parameter for the Ceph-VMs (instances.tf and block-volumes.tf) are modified to the right path as shown below:
   
   <img src="https://user-images.githubusercontent.com/122371432/214557965-3add97b6-5368-4772-9d84-9c6d602cbfa7.png" width=60% height=60%>
   
   
   Follow the steps 3,4 for all the components that needed to be segregated.
   
5. Run Terraform commands - init, plan and apply once the changes are complete to provision the resources in OCI.
 
 
</br>
This solution can also be integrated with any CI/CD pipeline. 

