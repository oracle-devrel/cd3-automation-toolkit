##### Author : Suruchi ###
##### Oracle Consulting ####
##### v3.0 #####

# This is v3.0 for base_tf_creations scripts. It supports multiple VCNs and hub spoke model implementation.
This would also accept CD3 excel file as input for creation of Networking objects

MAKE SURE TO LOOK AT ALL THE REQUIRED VARIABLES FOR TERRAFORM in the variables-example.tf provided.


### Setup of the Scripts ###
## See example folder for sample format of the files
A.  The scripts accept 2 kinds of inputs- either CD3 excel file having different sheets for different components or CSV input files.
    So there are 2 flows of the code.
B.  Both of them use vcn-info.properties.
C.  Setup the vcn-info.properties file.
D.  Make sure to use unique names for VCN names.
E.  Look at the example folder for sample input files.
F.  Scripts provide capability to have different compartments for different VCNs, subnets.


### Use of the Scripts ###
### Make sure to have the extension .tf for the terraform files that are created below.

1.  create_all_tf_objects.py -- This is the wrapper script that calls all below scripts so you should run only this script with required input variables.
    See Description for its usage.
    Note- specify the optional parameter --inputCD3 for code to create tf files based on CD3 excel file

2.  create_terraform_major_objects.py -- This creates the VCN and other components. DHCP Options, IGW, NGW, SGW, LPG and DRG for each VCN are created
    in the same compartment as the VCN.
3.  create_terraform_seclist.py  -- Creates security lists with default rules for every subnet defined in the subnet file. Egress allow everything to 0.0.0.0/0
    along with default ingress rules, creates ping rules for VCN peering based on property: add_ping_sec_rules_onprem and  defined in vcn-info.properties.
4.  create_terraform_dhcp_options.py -- Creates DHCP options for the subnets.  It supports both the CustomDnsServer serverType and VcnLocalPlusInternet type.
    Both have different requirements. Look at the example.
5.  create_terraform_route.py -- Creates the routes for each subnet.  It creates default routes as per information given for each subnet(in subnet file) and
    based upon VCN peering.
6.  create_terraform_subnet.py -- Creates the subnet with the Security list, routes and dhcp options based on the subnet file.
    The names are generated based on all the previous scripts run.
    If the Default VCN Security list needs to be attached to the subnet - set "add_default_seclist=y".


---- Creating the Objects ---

1. Move each of the files that are created to your terraform directory (I create a terraform_files directory for all my .tf files)
2. Run terraform plan & then terraform apply if things look right.  This should create the objects.

