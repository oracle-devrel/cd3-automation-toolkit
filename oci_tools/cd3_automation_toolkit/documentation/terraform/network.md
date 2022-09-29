## auto.tfvars syntax for Network Module
These are the syntax and sample format for providing inputs to the modules via <b>*.auto.tfvars</b> files.
<b>"key"</b> must be unique to every resource that is created.
Comments preceed with <b>##</b>.

Points to Note:
- To associate Route Table to the Gateways like IGW, SGW etc, please make sure to have the route tables created in the OCI tenancy first, and then edit the auto.tfvars file to add the route table keys/ocids to the gateway resources as per need.Uncomment the parameter - route_table_id for the respective gateway module calls in network.tf and main.tf files.
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
            byoipv6cidr_details = [{
                byoipv6range_id = string
                ipv6cidr_block = string
            }]
            is_ipv6enabled = bool
            defined_tags   = map
            freeform_tags  = map
            ipv6private_cidr_blocks = list
            is_oracle_gua_allocation_enabled = bool
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
        ## key - Is a unique value to reference the resources respectively
        key = {
            # Required
            compartment_id = string
            vcn_id         = string
    
            # Optional
            enable_igw     = bool
            igw_name       = string
            defined_tags   = map
            freeform_tags  = map
            route_table_id = string
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
    ngws = {
          ## key - Is a unique value to reference the resources respectively
          key = {
              # Required
              compartment_id = string
              vcn_id         = string
    
              # Optional
              ngw_name       = string
              public_ip_id   = string
              block_traffic  = bool
              defined_tags   = map
              freeform_tags  = map
              route_table_id = string
          }
    }
    ````
- <b>Example</b>
    ````
  ############################
  # Network
  # Major Objects - NGW - tfvars
  # Allowed Values:
  # vcn_id can be the ocid or the key of vcns (map)
  # compartment_id can be the ocid or the name of the compartment hierarchy delimited by double hiphens "--"
  # Example : compartment_id = "ocid1.compartment.oc1..aaaaaaaahwwiefb56epvdlzfic6ah6jy3xf3c" or compartment_id = "Network-root-cpt--Network" where "Network-root-cpt" is the parent of "Network" compartment
  ############################
  ngws = {
        ## key - Is a unique value to reference the resources respectively
        vcn1_ngw = {
            # Required
            compartment_id = "Network"
            vcn_id         = "vcn1"
      
            # Optional
            ngw_name       = "vcn1_ngw"
            block_traffic  = false
        },
  
        vcn2_ngw = {
            # Required
            compartment_id = "Network"
            vcn_id         = "vcn2"
    
            # Optional
            ngw_name       = "vcn2_ngw"
            defined_tags = {
                  "Oracle-Tags.CreatedOn"= "2022-09-06T07:27:39.937Z" ,
                  "Oracle-Tags.CreatedBy"= "oracleidentitycloudservice/abc@oracle.com"
            }
        }
  }
    ````
  

4. Service Gateways (SGWs)
- <b>Syntax</b>
  
    ````
    sgws = {
          ## key - Is a unique value to reference the resources respectively
          key = {
              # Required
              compartment_id = string
              vcn_id         = string
      
              # Optional
              service        = string         # Possible values for service: "", "all", "objectstorage"
              sgw_name       = string
              defined_tags   = map
              freeform_tags  = map
              route_table_id = string
          }
    }
    ````
- <b>Example</b>
    ````
  ############################
  # Network
  # Major Objects - SGW - tfvars
  # Allowed Values:
  # vcn_id can be the ocid or the key of vcns (map)
  # compartment_id can be the ocid or the name of the compartment hierarchy delimited by double hiphens "--"
  # Example : compartment_id = "ocid1.compartment.oc1..aaaaaaaahwwiefb56epvdlzfic6ah6jy3xf3c" or compartment_id = "Network-root-cpt--Network" where "Network-root-cpt" is the parent of "Network" compartment
  ############################
  sgws = {
         vcn1_sgw = {
              # Required
              compartment_id = "Network"
              
              # Optional
              vcn_id         = "vcn1"
              sgw_name       = "vcn1_sgw"
              freeform_tags  = {
                  "Environment" = "Dev",
                  "Application" = "SPX"
              }
         },
         vcn2_sgw = {
              # Required
              compartment_id = "Network"
 
              # Optional
              vcn_id         = "vcn2"
              sgw_name       = "vcn2_sgw"
         },
  }
    ````
  

5. Drynamic Routing Gateways (DRGs)
- <b>Syntax</b>
  
    ````
    drgs = {
          ## key - Is a unique value to reference the resources respectively
          key = {
              # Required
              compartment_id    = string
  
              # Optional
              display_name      = string
              defined_tags      = map
              freeform_tags     = map
          },
    }
    ````
- <b>Example</b>
    ````
    ############################
    # Network
    # Major Objects - DRG - tfvars
    # Allowed Values:
    # compartment_id can be the ocid or the name of the compartment hierarchy delimited by double hiphens "--"
    # Example : compartment_id = "ocid1.compartment.oc1..aaaaaaaahwwiefb56epvdlzfic6ah6jy3xf3c" or compartment_id = "Network-root-cpt--Network" where "Network-root-cpt" is the parent of "Network" compartment
    ############################
    drgs = {
         vcn1_drg = {
              compartment_id     = "Network"
              display_name       = "vcn1_drg"
         },
         vcn2_drg = {
              compartment_id     = "Network"
              display_name       = "vcn2_drg"
              defined_tags = {
                      "Oracle-Tags.CreatedOn"= "2022-09-06T07:27:39.937Z" ,
                      "Oracle-Tags.CreatedBy"= "oracleidentitycloudservice/abc@oracle.com"
              } 
         }
    }
    ````
  

6. Subnets
- <b>Syntax</b>
  
    ````
    subnets = {
        ## key - Is a unique value to reference the resources respectively
        key = {
            # Required
            compartment_id             = string
            vcn_id                     = string
            cidr_block                 = string
            
            # Optional
            display_name               = string
            dns_label                  = string
            ipv6cidr_block             = string
            defined_tags               = map
            freeform_tags              = map
            prohibit_internet_ingress  = string
            prohibit_public_ip_on_vnic = string
            availability_domain        = string
            dhcp_options_id            = string
            route_table_id             = string
            security_list_ids          = list
        }
    }
    ````
- <b>Example</b>
    ````
  #############################
  # Network
  # Major Objects - Subnets - tfvars
  # Allowed Values:
  # vcn_id, route_table_id, dhcp_options_id can be the ocid or the key of vcns (map), route_tables (map) and dhcp_options (map) respectively
  # security_list_ids can be a list of ocids or the key of security_lists (map)
  # compartment_id can be the ocid or the name of the compartment hierarchy delimited by double hiphens "--"
  # Example : compartment_id = "ocid1.compartment.oc1..aaaaaaaahwwiefb56epvdlzfic6ah6jy3xf3c" or compartment_id = "Network-root-cpt--Network" where "Network-root-cpt" is the parent of "Network" compartment
  #############################
  subnets = {
      vcn1_subnet1 = {
          # Required
          cidr_block                 = "10.201.4.0/28"
          compartment_id             = "Network"
          vcn_id                     = "vcn1"
  
          # Optional
          display_name               = "subnet1"
          prohibit_public_ip_on_vnic = "true"
          route_table_id             = "vcn1-hub-rt"
          dns_label                  = "phxvcnosubnetdn"
          dhcp_options_id            = "vcn1-hub-dhcp"
          security_list_ids          = ["vcn1-hub-sl"]
          freeform_tags              = {
                  "Environment" = "Dev",
                  "Application" = "SPX"
          }
        },
      vcn2_subnet1 = {
          # Required
          cidr_block                 = "10.201.4.0/28"
          compartment_id             = "Network"
          vcn_id                     = "vcn2"
  
          # Optional
          display_name               = "subnet1"
          prohibit_public_ip_on_vnic = "true"
          route_table_id             = "vcn2-hub-rt"
          dns_label                  = "phxvcntsubnetdn"
          dhcp_options_id            = "vcn2-hub-dhcp"
          security_list_ids          = ["vcn1-hub-sl"]
        },
    }
    ````
  

7. Security Lists (SLs)
- <b>Syntax</b>
  
    ````
    seclists = {
          ## key - Is a unique value to reference the resources respectively
          key = {
              # Required
              compartment_id = string
              vcn_id         = string
              
              # Optional
              display_name   = string
              defined_tags   = map
              freeform_tags  = map
              ingress_sec_rules = [{
                protocol    = string
                stateless   = string
                description = string
                source      = string
                source_type = string
                options     = {
                    all = []
                    icmp = [{
                        icmp_type = string
                        icmp_code = number
                    }]
                    udp = [{
                        udp_destination_port_range_max = string
                        udp_destination_port_range_min = string
  
                        udp_source_port_range_max = string
                        udp_source_port_range_min = string
                    }]
                    tcp = [{
                        tcp_destination_port_range_max = string
                        tcp_destination_port_range_min = string
  
                        tcp_source_port_range_max = string
                        tcp_source_port_range_min = string
                    }]
                }
              }]
              egress_sec_rules = [{
                protocol         = string
                stateless        = string
                description      = string
                destination      = string
                destination_type = string
                options     = {
                    all = []
                    icmp = [{
                        icmp_type = string
                        icmp_code = number
                    }]
                    udp = [{
                        udp_destination_port_range_max = string
                        udp_destination_port_range_min = string
  
                        udp_source_port_range_max = string
                        udp_source_port_range_min = string
                    }]
                    tcp = [{
                        tcp_destination_port_range_max = string
                        tcp_destination_port_range_min = string
  
                        tcp_source_port_range_max = string
                        tcp_source_port_range_min = string
                    }]
                }
              }]
          }
    }
    ````
- <b>Example</b>
    ````
  ############################
  # Network
  # Major Objects - Security List - tfvars
  # Allowed Values:
  # vcn_id can be the ocid or the key of vcns (map)
  # compartment_id can be the ocid or the name of the compartment hierarchy delimited by double hiphens "--"
  # Example : compartment_id = "ocid1.compartment.oc1..aaaaaaaahwwiefb56epvdlzfic6ah6jy3xf3c" or compartment_id = "Network-root-cpt--Network" where "Network-root-cpt" is the parent of "Network" compartment
  ############################
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
  

12. DRG Route Tables
- <b>Syntax</b>
  
    ````
  
    ````
- <b>Example</b>
    ````
  
    ````
  

