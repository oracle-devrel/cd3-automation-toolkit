##### Author : Murali Nagulakonda Venkata ###
##### Oracle Consulting ####
##### v0.1a #####
The set of scripts creates the baseline terraform objects to use.
## Pre Reqs ##
1.  Create the terraform keys, setup the OCI tenancy with the API key.
2.  Initialize Terraform with the required variables.  A copy of variables.tf is included for reference in this package.
3.  provider.tf has also been provided - which will use the variables in variables.tf and initialize the oci provider when you run terraform init.  You can use the provider.tf file as is  - unless you've made changes to variables.tf resource names (changes not recommmended)

##### You can use the below script or follow the steps below to create your terraform environment ####
#!/bin/bash

echo "Download terraform.zio from terraform.io for your platform"
echo "Example: wget <URL> -O terraform.zip"
echo "Unzip it and move it over to /usr/local/bin.  Make sure /usr/local/bin is in your path"
echo "This will download the v2.1.0 OCI terraform provider"


wget https://github.com/oracle/terraform-provider-oci/releases/download/v2.1.0-beta/linux.tar.gz
tar -xvzf linux.tar.gz linux_amd64
mkdir ~/.terraform.d/plugins/
mv linux_amd64/terraform-provider-oci_v2.1.0-beta ~/.terraform.d/plugins/
rmdir linux_amd64

Once complete with setting up terraform and changing variables.tf - initialize Terraform 
terraform init

This should show you that terraform oci provider is initialized.
Now ready for the below scripts
######



The scripts assume that you have two compartments - one for Networking Objects, One for all the other objects.  If you have only one compartment, set the compartment_ocid's to the same value.
The "ntk_compartment_ocid" is the name of the network compartment ocid variable.  MAKE SURE TO LOOK AT ALL THE REQUIRED VARIABLES FOR TERRAFORM in the variables-example.tf provided.


### Setup of the Scripts ###
A.  Setup the oci-tf.properties file with the correct IDs for network compartment, compartment etc.  If the Network objects compartment and the rest of the objects compartment are the same - then put the same variable name for it (look at variables.tf). 
B.  Create a dhcp file - The section headings is what is used as the name of the dhcp-options.  An example is provided for both.
C.  Create a subnet file with the format "#name,subnet-cidr,availabilty-domain(AD1|AD2|AD3),private|public,dhcp-options-name



### Use of the Scripts ###
### Make sure to have the extension .tf for the terraform files that are created below.

1.  create_terraform_major_objects.py -- This creates the VCN, IGW mapped to the VCN and DRG.  All the in the Network Compartment.
2.  create_terraform_seclist.py  -- Creates security lists for every subnet defined in the subnet file (D above).  
3.  create_terraform_dhcp_options.py -- Creates DHCP options for the subnets.  It supports both the CustomDnsServer serverType and VcnLocalPlusInternet type.  Both have different requirements. Look at the example.  The "section heading" will be the dhcp option name, that will be specified in the subnets file (D above) for each of the subnets.  DO not leave it blank.
4.  create_terraform_route.py -- Creates the routes for each subnet.  Every route defined in the routes file (see example) will be created for every subnet. If you need a different combination - create the baseline and then delete what you dont need (or create multiple subnet and route files) -- Thsi si not required anymore as we are creatign default routes based on inouts in oci-tf.prooperties
5.  create_terraform_subnet.py -- Creates the subnet with the Security list, routes and dhcp options based on the subnet file.  The names are generated based on all the previous scripts run.  Do not change any of the resource object names.  If the Default VCN Security list needs to be attached to the subnet - set "add_vcn_to_all_sec_lists=true" in the oci-tf.properties file.  If not - set it to false.
6.  create_all_tf_objects.py -- This is the wrapper script that calls all above scripts so you should run only this script with required input variables. See Description for its usage.

---- Creating the Objects ---

1.  Move each of the files that are created to your terraform directory (I create a terraform_files directory for all my .tf files)
2. Run terraform plan & then terraform apply if things look right.  This should create the objects.

