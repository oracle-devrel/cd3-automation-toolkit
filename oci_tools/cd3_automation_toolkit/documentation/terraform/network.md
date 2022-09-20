## auto.tfvars syntax for Network Module
These are the syntax and sample format for providing inputs to the modules via <b>*.auto.tfvars</b> files.
<b>"key"</b> must be unique to every resource that is created.
Comments preceed with <b>##</b>.

## NETWORK
1. Virtual Cloud Networks (VCNs)
- <b>Syntax</b>
  
    ````
    vcns = {
        ## key - Is a unique value to reference the resources respectively
        key = {
            # Required
            compartment_id = string
          
            # Optional
            cidr_blocks    = list
            display_name   = string
            dns_label      = string
            is_ipv6enabled = bool
            defined_tags   = map
            freeform_tags  = map
        },
    }
    ````
- <b>Example</b>
    ````
    ############################
    # Network
    # Major Objects - VCNs, IGW, NGW, SGW, LPG, DRG - tfvars
    # Allowed Values:
    # compartment_id can be the ocid or the name of the compartment hierarchy delimited by double hiphens "--"
    # Example : compartment_id = "ocid1.compartment.oc1..aaaaaaaahwwiefb56epvdlzfic6ah6jy3xf3c" or compartment_id = "Network-root-cpt--Network" where "Network-root-cpt" is the parent of "Network" compartment
    ############################
    vcns = {
          vcn3 = {
                # Required
                compartment_id = "Network"
  
                # Optional
                cidr_blocks      = ["10.3.0.0/16"]
                display_name     = "vcn3"
                dns_label      = "vcn3"
                defined_tags = {
                        "Oracle-Tags.CreatedOn"= "2022-09-06T07:27:40.005Z" ,
                        "Oracle-Tags.CreatedBy"= "oracleidentitycloudservice/abc@oracle.com"
                }
              },
          vcn2 = {
                # Required
                compartment_id = "Network"
  
                # Optional
                cidr_blocks      = ["10.2.0.0/16"]
                display_name     = "vcn2"
                dns_label      = "vcn2"
                defined_tags = {
                        "Oracle-Tags.CreatedOn"= "2022-09-06T07:27:39.936Z" ,
                        "Oracle-Tags.CreatedBy"= "oracleidentitycloudservice/abc@oracle.com"
                }
              },
          vcn1 = {
                # Required
                compartment_id = "Network"
  
                # Optional
                cidr_blocks      = ["10.1.0.0/16"]
                display_name     = "vcn1"
                dns_label      = "vcn1"
                defined_tags = {
                        "Oracle-Tags.CreatedOn"= "2022-09-06T07:27:39.937Z" ,
                        "Oracle-Tags.CreatedBy"= "oracleidentitycloudservice/abc@oracle.com"
                }
              },
    }
    ````
  

2. Internet Gateways (IGWs)
- <b>Syntax</b>
  
    ````
    igws = {
        key = {
            # Required
            compartment_id = string
            vcn_id         = string
    
            # Optional
            enable_igw     = bool
            igw_name       = string
            defined_tags   = map
            freeform_tags  = map
        },
    }
    ````
- <b>Example</b>
    ````
    ############################
    # Network
    # Major Objects - IGW - tfvars
    # Allowed Values:
    # vcn_id can be the ocid or the key of vcns (map)
    # compartment_id can be the ocid or the name of the compartment hierarchy delimited by double hiphens "--"
    # Example : compartment_id = "ocid1.compartment.oc1..aaaaaaaahwwiefb56epvdlzfic6ah6jy3xf3c" or compartment_id = "Network-root-cpt--Network" where "Network-root-cpt" is the parent of "Network" compartment
    ############################
    igws = {
        vcn1_igw = {
              # Required
              compartment_id = "Network"
              vcn_id     = "vcn1"
  
              # Optional
              igw_name   = "igw"
              defined_tags = {
                      "Oracle-Tags.CreatedOn"= "2022-09-06T07:27:39.937Z" ,
                      "Oracle-Tags.CreatedBy"= "oracleidentitycloudservice/abc@oracle.com"
              }
        },
    }
    ````
  

3. Network Address Translation Gateways (NGWs)
- <b>Syntax</b>
  
    ````
  
    ````
- <b>Example</b>
    ````
  
    ````
  

4. Service Gateways (SGWs)
- <b>Syntax</b>
  
    ````
  
    ````
- <b>Example</b>
    ````
  
    ````
  

5. Drynamic Routing Gateways (DRGs)
- <b>Syntax</b>
  
    ````
  
    ````
- <b>Example</b>
    ````
  
    ````
  

6. Subnets
- <b>Syntax</b>
  
    ````
  
    ````
- <b>Example</b>
    ````
  
    ````
  

7. Security Lists (SLs)
- <b>Syntax</b>
  
    ````
  
    ````
- <b>Example</b>
    ````
  
    ````
  

8. Route Tables (RTs)
- <b>Syntax</b>
  
    ````
  
    ````
- <b>Example</b>
    ````
  
    ````
  

9. DHCP Options
- <b>Syntax</b>
  
    ````
  
    ````
- <b>Example</b>
    ````
  
    ````
  

10. Network Security Groups (NSGs)
- <b>Syntax</b>
  
    ````
  
    ````
- <b>Example</b>
    ````
  
    ````
  

11. DRG Route Distributions
- <b>Syntax</b>
  
    ````
  
    ````
- <b>Example</b>
    ````
  
    ````
  

13. DRG Route Tables
- <b>Syntax</b>
  
    ````
  
    ````
- <b>Example</b>
    ````
  
    ````
  

