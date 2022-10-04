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
  

5. Dynamic Routing Gateways (DRGs)
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
  
6. Dynamic Routing Gateway Attachements (DRG Attachments)
- <b>Syntax</b>
  
    ````
    drg_attachments = {
          ## key - Is a unique value to reference the resources respectively
          key = {
              # Required
              drg_id            = string
              display_name      = string
   
              # Optional
              # Required only for DRG V2; Set drg_route_table_id = "" and network_details = [] when using DRG V1
              drg_route_table_id = string 
              network_details    = [{
                  id                 = string
                  type               = string
                  vcn_route_table_id = string
              }]
  
              # Required only for DRG v1; Set route_table_id = "" and vcn_id = "" when using DRG V2
              route_table_id     = string 
              vcn_id             = string
              
              # Optional; set them to {} when not needed; example-> defined_tags = {}
              defined_tags       = map
              freeform_tags      = map
          },
    }
    ````
- <b>Example</b>
    ````
  ############################
  # Network
  # Major Objects - DRG Attachment - tfvars
  # Allowed Values:
  # vcn_id can be the ocid or the key of vcns (map)
  ############################
  drg_attachments = {
        vcn2_drg_attach = {
  
              # Required
              drg_id = "vcn2_drg"
              display_name = "vcn2_drg_attach"
      
              # Optional
              # DRG v2
              drg_route_table_id = "vcn2_drg_rt"
              # Required only for DRG V2; Set drg_route_table_id = "" and network_details = [] when using DRG V1
              network_details = [{
              id = "Svcs"
              type = "VCN"
              vcn_route_table_id = "Svcs_Route-Table-associated-with-vcn2_drg"
              }]
              # Set DRGv1 params to null
              route_table_id =""
              vcn_id = ""
              defined_tags = {
                      "Oracle-Tags.CreatedOn"= "2022-02-28T05:46:42.914Z" ,
                      "Oracle-Tags.CreatedBy"= "abc@oracle.com"
              }
              freeform_tags = {}
        },
  }
    ````

7. DRG Route Distributions
- <b>Syntax</b>
  
    ````
  drg_route_distributions = {
      ## key - Is a unique value to reference the resources respectively
      key = {
          # Required
          distribution_type = string
          drg_id            = string
  
          # Optional
          defined_tags      = map
          freeform_tags     = map
          display_name      = string
      }
  }   
    ````
- <b>Example</b>
    ````
  #################################
  # Network
  # DRG Route Distributions - tfvars
  # Allowed Values:
  # drg_id can be the ocid or the key of drgs (map)
  #################################
  drg_route_distributions = {
      # DRG Distribution for Region - ashburn
      vcn2_drg_import_routes_01 = {
            distribution_type = "IMPORT"
            drg_id = "vcn2_drg"
            display_name = "vcn2_drg_import_routes_01"
            defined_tags = {
                "Oracle-Tags.CreatedOn"= "2022-02-28T05:46:42.914Z" ,
                "Oracle-Tags.CreatedBy"= "abc@oracle.com"
            }
            freeform_tags = {}
      },
      vcn1_drg_import_routes_01 = {
            distribution_type = "IMPORT"
            drg_id = "vcn1_drg"
            display_name = "vcn1_drg_import_routes_01"
            defined_tags = {
                "Oracle-Tags.CreatedOn"= "2022-02-28T05:46:42.914Z" ,
                "Oracle-Tags.CreatedBy"= "abc@oracle.com"
            }
            freeform_tags = {}
      },
  }
    ````

8. DRG Route Distribution Statements
- <b>Syntax</b>
  
    ````
  drg_route_distribution_statements = {
      ## key - Is a unique value to reference the resources respectively
      key = {
          # Required
          drg_route_distribution_id = string
          action            = string
  
          # Optional
          match_criteria = [{
              # Required
              match_type        = string
            
              # Optional
              attachment_type   = string
              drg_attachment_id = string
          }]
          priority      = map
          action        = map
      }
  }
    ````
- <b>Example</b>
    ````
  ##########################################
  # Module Block - Network
  # Create DRG Route Distribution Statements
  # Allowed Values:
  # drg_route_distribution_id can be the ocid or the key of drg_route_distributions (map)
  ##########################################
  drg_route_distribution_statements = {
      # DRG Distribution Statement for Region - ashburn
      vcn2_drg_import_route_01_statement1 = {
            drg_route_distribution_id = "vcn2_drg_import_routes_01"
            match_criteria = [
            {
            match_type = "DRG_ATTACHMENT_TYPE"
            attachment_type = "VCN"
            drg_attachment_id = ""
            },
            ]
            priority = "1"
            action = "ACCEPT"
      },
      vcn1_drg_import_routes_01_statement1 = {
            drg_route_distribution_id = "vcn1_drg_import_routes_01"
            match_criteria = [
            {
            match_type = "DRG_ATTACHMENT_TYPE"
            attachment_type = "IPSEC_TUNNEL"
            drg_attachment_id = ""
            },
            ]
            priority = "2"
            action = "ACCEPT"
      },
  }
    ````

9. DRG Route Tables
- <b>Syntax</b>
  
    ````
  drg_route_tables = {
      ## key - Is a unique value to reference the resources respectively
      key = {
          # Required
          drg_id            = string
          display_name      = string
  
          # Optional
          import_drg_route_distribution_id = string
          is_ecmp_enabled                  = bool
          # set the tags to {} when not needed; example-> defined_tags = {}
          defined_tags                     = map
          freeform_tags                    = map
      }
  }
    ````
- <b>Example</b>
    ````
  #################################
  # Network
  # DRG Route Tables - tfvars
  # Allowed Values:
  # drg_id can be ocid or the key of drgs (map)
  #################################
  drg_route_tables = {
      # DRG Route Tables for Region - ashburn
      # Start of #ashburn_vcn1_drg_static# #
      vcn1_drg_static = {
            drg_id = "vcn1_drg"
            display_name = "vcn1_drg_static"
            import_drg_route_distribution_id = ""
            is_ecmp_enabled = "false"
            defined_tags = {}
            freeform_tags = {}
      },
      # End of #ashburn_vcn1_drg_static# #
      # Start of #ashburn_vcn2_drg_static# #
      vcn2_drg_static = {
            drg_id = "vcn2_drg"
            display_name = "vcn2_drg_static"
            import_drg_route_distribution_id = "vcn2_drg_import_routes_01"
            is_ecmp_enabled = "false"
             defined_tags = {
                "Oracle-Tags.CreatedOn"= "2022-02-28T05:46:42.914Z" ,
                "Oracle-Tags.CreatedBy"= "abc@oracle.com"
            }
            freeform_tags = {}
      },
  }
 
    ````
  
10. DRG Route Rules
- <b>Syntax</b>
  
    ````
  drg_route_rules = {
      ## key - Is a unique value to reference the resources respectively
      key = {
          # Required
          drg_route_table_id = string
          destination        = string
          destination_type   = string
          next_hop_drg_attachment_id = string
      }
  }
    ````
- <b>Example</b>
    ````
  #################################
  # Network
  # DRG Route Rules - tfvars
  # Allowed Values:
  # drg_route_table_id and next_hop_drg_attachment_id can be the ocid or the key of drg_route_tables (map) and the key of drg_attachments (map) respectively
  #################################
  drg_route_rules = {
      # DRG Route Rules for Region - ashburn
      vcn1_drg_static_route_rule1 = {
              #Required
              drg_route_table_id = "vcn1_drg_static"
              destination = "10.0.8.0/23"
              destination_type = "CIDR_BLOCK"
              next_hop_drg_attachment_id = "vcn1_drg_attach"
      },
      vcn1_drg_static_route_rule2 = {
              #Required
              drg_route_table_id = "vcn1_drg_static"
              destination = "10.0.4.0/22"
              destination_type = "CIDR_BLOCK"
              next_hop_drg_attachment_id = "vcn1_drg_attach2"
      },
  }
    ````
  
11. Subnets
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

12. Security Lists (SLs)
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
                    all = [] # for protocol = all
                    icmp = [{
                        icmp_type = string
                        icmp_code = number
                    }] 
                    (or)
                    icmp = [] # for all ICMP option
                    udp = [{
                        udp_destination_port_range_max = string
                        udp_destination_port_range_min = string
  
                        udp_source_port_range_max = string
                        udp_source_port_range_min = string
                    }]
                    (or)
                    udp = [] # for all UDP option
                    tcp = [{
                        tcp_destination_port_range_max = string
                        tcp_destination_port_range_min = string
  
                        tcp_source_port_range_max = string
                        tcp_source_port_range_min = string
                    }]
                    (or)
                    tcp = [] # for all TCP option
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
                    (or)
                    icmp = [] # for all ICMP option
                    udp = [{
                        udp_destination_port_range_max = string
                        udp_destination_port_range_min = string
  
                        udp_source_port_range_max = string
                        udp_source_port_range_min = string
                    }]
                    (or)
                    udp = [] # for all UDP option
                    tcp = [{
                        tcp_destination_port_range_max = string
                        tcp_destination_port_range_min = string
  
                        tcp_source_port_range_max = string
                        tcp_source_port_range_min = string
                    }]
                    (or)
                    tcp = [] # for all TCP option
                }
              }]
          }
    }
    ````
- <b>Example</b>
  ````
  // Copyright (c) 2021, 2022, Oracle and/or its affiliates.
  ############################
  # Network
  # Major Objects - Security List - tfvars
  # Allowed Values:
  # vcn_id can be the ocid or the key of vcns (map)
  # compartment_id can be the ocid or the name of the compartment hierarchy delimited by double hiphens "--"
  # Example : compartment_id = "ocid1.compartment.oc1..aaaaaaaahwwiefb56epvdlzfic6ah6jy3xf3c" or compartment_id = "Network-root-cpt--Network" where "Network-root-cpt" is the parent of "Network" compartment
  ############################
  seclists = {
  
    # Seclist map #
    # Start of #phoenix_vcn3_subnet3-1# #
    vcn3_subnet3-1 = {
          compartment_id = "Network"
          vcn_id     = "vcn3"
          display_name     = "subnet3-1"
          ingress_sec_rules = [
               {  #vcn3_subnet3-1_10.3.1.0/24#
                  protocol = "all"
                  source = "10.3.1.0/24"
                  options = {
                      all = []
                  }
               },
               {  #vcn3_subnet3-1_10.3.1.0/24#
                  protocol = "6"
                  source = "10.3.2.0/24"
                  options = {
                      tcp= [{
                          tcp_destination_port_range_max = "22"
                          tcp_destination_port_range_min = "22"
  
                          tcp_source_port_range_max = "22"
                          tcp_source_port_range_min = "22"
                      }]
                  }
               },
               {  #vcn3_subnet3-1_10.3.1.0/24#
                  protocol = "17"
                  source = "10.3.1.0/24"
                  options = {
                    udp = [{
                        udp_destination_port_range_max = "7003"
                        udp_destination_port_range_min = "7003"
                    }]
                  }
               },
  ####ADD_NEW_INGRESS_SEC_RULES #phoenix_vcn3_subnet3-1# ####
          ]
          egress_sec_rules = [
               {
                  protocol = "all"
                  destination = "0.0.0.0/0"
                  options = {
                      all = []
                  }
               },
  ####ADD_NEW_EGRESS_SEC_RULES #phoenix_vcn3_subnet3-1# ####
          ]
          defined_tags = {
                  "Oracle-Tags.CreatedOn"= "2022-09-06T07:27:48.895Z" ,
                  "Oracle-Tags.CreatedBy"= "oracleidentitycloudservice/suruchi.singla@oracle.com"
          }
        },
    # End of #phoenix_vcn3_subnet3-1# #
    # Start of #phoenix_vcn3_subnet3-2# #
    vcn3_subnet3-2 = {
          compartment_id = "Network"
          vcn_id     = "vcn3"
          display_name     = "subnet3-2"
          ingress_sec_rules = [
               {  #vcn3_subnet3-2_10.3.2.0/24#
                  protocol = "6"
                  source = "0.0.0.0/0"
                  options = {
                      icmp= [{
                        icmp_type = "2"
                        icmp_code = "-1"
                      }]
                  }
               },
  ####ADD_NEW_INGRESS_SEC_RULES #phoenix_vcn3_subnet3-2# ####
          ]
          egress_sec_rules = [
               {
                  protocol = "all"
                  destination = "0.0.0.0/0"
                  options = {
                      all = []
                  }
               },
  ####ADD_NEW_EGRESS_SEC_RULES #phoenix_vcn3_subnet3-2# ####
          ]
          defined_tags = {
                  "Oracle-Tags.CreatedOn"= "2022-09-06T07:27:48.895Z" ,
                  "Oracle-Tags.CreatedBy"= "oracleidentitycloudservice/suruchi.singla@oracle.com"
          }
        },
    # End of #phoenix_vcn3_subnet3-2# #
  }
    ````

13. Default Security Lists (Default SLs)
- <b>Syntax</b>
  
    ````
    default_seclists = {
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
                    all = [] # for protocol = all
                    icmp = [{
                        icmp_type = string
                        icmp_code = number
                    }] 
                    (or)
                    icmp = [] # for all ICMP option
                    udp = [{
                        udp_destination_port_range_max = string
                        udp_destination_port_range_min = string
  
                        udp_source_port_range_max = string
                        udp_source_port_range_min = string
                    }]
                    (or)
                    udp = [] # for all UDP option
                    tcp = [{
                        tcp_destination_port_range_max = string
                        tcp_destination_port_range_min = string
  
                        tcp_source_port_range_max = string
                        tcp_source_port_range_min = string
                    }]
                    (or)
                    tcp = [] # for all TCP option
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
                    (or)
                    icmp = [] # for all ICMP option
                    udp = [{
                        udp_destination_port_range_max = string
                        udp_destination_port_range_min = string
  
                        udp_source_port_range_max = string
                        udp_source_port_range_min = string
                    }]
                    (or)
                    udp = [] # for all UDP option
                    tcp = [{
                        tcp_destination_port_range_max = string
                        tcp_destination_port_range_min = string
  
                        tcp_source_port_range_max = string
                        tcp_source_port_range_min = string
                    }]
                    (or)
                    tcp = [] # for all TCP option
                }
              }]
          }
    }
    ````
- <b>Example</b>
  ````
  // Copyright (c) 2021, 2022, Oracle and/or its affiliates.
  ############################
  # Network
  # Major Objects - Default Security List - tfvars
  # Allowed Values:
  # vcn_id can be the ocid or the key of vcns (map)
  # compartment_id can be the ocid or the name of the compartment hierarchy delimited by double hiphens "--"
  # Example : compartment_id = "ocid1.compartment.oc1..aaaaaaaahwwiefb56epvdlzfic6ah6jy3xf3c" or compartment_id = "Network-root-cpt--Network" where "Network-root-cpt" is the parent of "Network" compartment
  ############################
  default_seclists = {
  
    # Seclist map #
    # Start of #phoenix_vcn3_subnet3-1# #
    vcn3_subnet3-1 = {
          compartment_id = "Network"
          vcn_id     = "vcn3"
          display_name     = "Default Security List for subnet3-1"
          ingress_sec_rules = [
               {  #vcn3_subnet3-1_10.3.1.0/24#
                  protocol = "all"
                  source = "10.3.1.0/24"
                  options = {
                      all = []
                  }
               },
               {  #vcn3_subnet3-1_10.3.1.0/24#
                  protocol = "6"
                  source = "10.3.2.0/24"
                  options = {
                      tcp= [{
                          tcp_destination_port_range_max = "22"
                          tcp_destination_port_range_min = "22"
  
                          tcp_source_port_range_max = "22"
                          tcp_source_port_range_min = "22"
                      }]
                  }
               },
               {  #vcn3_subnet3-1_10.3.1.0/24#
                  protocol = "17"
                  source = "10.3.1.0/24"
                  options = {
                    udp = [{
                        udp_destination_port_range_max = "7003"
                        udp_destination_port_range_min = "7003"
                    }]
                  }
               },
  ####ADD_NEW_INGRESS_SEC_RULES #phoenix_vcn3_subnet3-1# ####
          ]
          egress_sec_rules = [
               {
                  protocol = "all"
                  destination = "0.0.0.0/0"
                  options = {
                      all = []
                  }
               },
  ####ADD_NEW_EGRESS_SEC_RULES #phoenix_vcn3_subnet3-1# ####
          ]
          defined_tags = {
                  "Oracle-Tags.CreatedOn"= "2022-09-06T07:27:48.895Z" ,
                  "Oracle-Tags.CreatedBy"= "oracleidentitycloudservice/suruchi.singla@oracle.com"
          }
        },
    # End of #phoenix_vcn3_subnet3-1# #
    # Start of #phoenix_vcn3_subnet3-2# #
    vcn3_subnet3-2 = {
          compartment_id = "Network"
          vcn_id     = "vcn3"
          display_name     = "Default Security List for subnet3-2"
          ingress_sec_rules = [
               {  #vcn3_subnet3-2_10.3.2.0/24#
                  protocol = "6"
                  source = "0.0.0.0/0"
                  options = {
                      icmp= [{
                        icmp_type = "2"
                        icmp_code = "-1"
                      }]
                  }
               },
  ####ADD_NEW_INGRESS_SEC_RULES #phoenix_vcn3_subnet3-2# ####
          ]
          egress_sec_rules = [
               {
                  protocol = "all"
                  destination = "0.0.0.0/0"
                  options = {
                      all = []
                  }
               },
  ####ADD_NEW_EGRESS_SEC_RULES #phoenix_vcn3_subnet3-2# ####
          ]
          defined_tags = {
                  "Oracle-Tags.CreatedOn"= "2022-09-06T07:27:48.895Z" ,
                  "Oracle-Tags.CreatedBy"= "oracleidentitycloudservice/suruchi.singla@oracle.com"
          }
        },
    # End of #phoenix_vcn3_subnet3-2# #
    # Start of #phoenix_vcn3_subnet4-2# #
  Customer1Zone_Default-Security-List-for-Customer1Zone = {
        compartment_id = "Network"
        vcn_id     = "vcn3"
        display_name     = "Default Security List for subnet4-2"
        ingress_sec_rules = [
        ####ADD_NEW_INGRESS_SEC_RULES #phoenix_vcn3_Default-Security-List-for-subnet4-2# ####
        ]
        egress_sec_rules = [
        ####ADD_NEW_EGRESS_SEC_RULES #phoenix_vcn3_Default-Security-List-for-subnet4-2# ####
        ]
        defined_tags = {
                "Oracle-Tags.CreatedOn"= "2022-02-28T05:46:42.861Z" ,
                "Oracle-Tags.CreatedBy"= "john.saleh@oracle.com"
        }
        freeform_tags = {}
      },
  # End of #phoenix_vcn3_subnet4-2# #
  }
    ````

14. Route Tables (RTs)
- <b>Syntax</b>
  
    ````
  route_tables = {
        ## key - Is a unique value to reference the resources respectively
        key = {
  
            # Required
            compartment_id   = string
            vcn_id           = string
            display_name     = string
  
            # Optional
            # IGW Rules
            route_rules_igw  = [] # When there are no IGW Rules
            (OR)
            route_rules_igw  = [{
                  network_entity_id = string
                  description       = string
                  destination       = string
                  destination_type  = string
            }]
  
            # SGW Rules
            route_rules_sgw  = [] # When there are no SGW Rules
            (OR)
            route_rules_sgw  = [{
                  network_entity_id = string
                  description       = string
                  destination       = string
                  destination_type  = string
            }]
  
            # NGW Rules
            route_rules_ngw  = [] # When there are no NGW Rules
            (OR)
            route_rules_ngw  = [{
                  network_entity_id = string
                  description       = string
                  destination       = string
                  destination_type  = string
            }]
  
            # DRG Rules
            route_rules_drg  = [] # When there are no DRG Rules
            (OR)
            route_rules_drg  = [{
                  network_entity_id = string
                  description       = string
                  destination       = string
                  destination_type  = string
            }]
  
            # LPG Rules
            route_rules_lpg  = [] # When there are no LPG Rules
            (OR)
            route_rules_lpg  = [{
                  network_entity_id = string
                  description       = string
                  destination       = string
                  destination_type  = string
            }]
  
            # IP Rules
            route_rules_ip   = [] # When there are no IP Rules
            (OR)
            route_rules_ip   = [{
                  network_entity_id = string
                  description       = string
                  destination       = string
                  destination_type  = string
            }]
            # set the tags to {} when not needed; example-> defined_tags = {}
            defined_tags     = map
            freeform_tags    = map
  }
    ````
- <b>Example</b>
    ````
  // Copyright (c) 2021, 2022, Oracle and/or its affiliates.
  ############################
  # Network
  # Major Objects - Route Table - tfvars
  # Allowed Values:
  # vcn_id can be the ocid or the key of vcns (map)
  # compartment_id can be the ocid or the name of the compartment hierarchy delimited by double hiphens "--"
  # Example : compartment_id = "ocid1.compartment.oc1..aaaaaaaahwwiefb56epvdlzfic6ah6jy3xf3c" or compartment_id = "Network-root-cpt--Network" where "Network-root-cpt" is the parent of "Network" compartment
  ############################
  
  default_route_tables = {
    # Route Table map #
    # Start of #ashburn_vcn_app-subnet-rtable# #
      vcn_app-subnet-rtable = {
          # Required
          compartment_id = "fc-network-cmp"
          vcn_id     = "vcn1"
          display_name     = "vcn_app-subnet-rtable"
  
          # Optional
          route_rules_igw = [
      ####ADD_NEW_IGW_RULES #ashburn_vcn_app-subnet-rtable# ####
          ]
          route_rules_sgw = [
      ####ADD_NEW_SGW_RULES #ashburn_vcn_app-subnet-rtable# ####
          ]
          route_rules_ngw = [
                  ## Start Route Rule ashburn_vcn_app-subnet-rtable-natgw_0.0.0.0/0
              {
                    network_entity_id = "vcn-natgw"
                    description       = ""
                    destination       = "0.0.0.0/0"
                    destination_type  = "CIDR_BLOCK"
                   },
              ## End Route Rule ashburn_vcn_app-subnet-rtable-natgw_0.0.0.0/0
      ####ADD_NEW_NGW_RULES #ashburn_vcn_app-subnet-rtable# ####
          ]
          route_rules_drg = [
                  ## Start Route Rule ashburn_vcn_app-subnet-rtable-drg_10.0.2.0/22
              {
                    network_entity_id = "vcn-drg"
                    description       = ""
                    destination       = "10.0.2.0/22"
                    destination_type  = "CIDR_BLOCK"
                   },
              ## End Route Rule ashburn_vcn_app-subnet-rtable-drg_10.0.2.0/22
      ####ADD_NEW_DRG_RULES #ashburn_vcn_app-subnet-rtable# ####
          ]
          route_rules_lpg = [
      ####ADD_NEW_LPG_RULES #ashburn_vcn_app-subnet-rtable# ####
          ]
          route_rules_ip = [
      ####ADD_NEW_IP_RULES #ashburn_vcn_app-subnet-rtable# ####
          ]
          defined_tags = {
                  "Oracle-Tags.CreatedOn"= "2022-08-23T15:03:30.750Z" ,
                  "Oracle-Tags.CreatedBy"= "abc@oracle.com"
          }
          freeform_tags = {}
        },
    # End of #ashburn_vcn_app-subnet-rtable# #
    # Start of #ashburn_vcn_dmz-subnet-rtable# #
      dmz-subnet-rtable = {
          # Required
          compartment_id = "fc-network-cmp"
          vcn_id     = "vcn2"
          display_name     = "dmz-subnet-rtable"
  
          # Optional
          route_rules_igw = [
                  ## Start Route Rule ashburn_vcn_dmz-subnet-rtable-igw_0.0.0.0/0
              {
                    network_entity_id = "vcn-igw"
                    description       = ""
                    destination       = "0.0.0.0/0"
                    destination_type  = "CIDR_BLOCK"
                   },
              ## End Route Rule ashburn_vcn_dmz-subnet-rtable-igw_0.0.0.0/0
      ####ADD_NEW_IGW_RULES #ashburn_vcn_dmz-subnet-rtable# ####
          ]
          route_rules_sgw = [
      ####ADD_NEW_SGW_RULES #ashburn_vcn_dmz-subnet-rtable# ####
          ]
          route_rules_ngw = [
      ####ADD_NEW_NGW_RULES #ashburn_vcn_dmz-subnet-rtable# ####
          ]
          route_rules_drg = [
                  ## Start Route Rule ashburn_vcn_dmz-subnet-rtable-drg_10.0.2.0/22
              {
                    network_entity_id = "vcn-drg"
                    description       = ""
                    destination       = "10.0.2.0/22"
                    destination_type  = "CIDR_BLOCK"
                   },
              ## End Route Rule ashburn_vcn_dmz-subnet-rtable-drg_10.0.2.0/22
              ## Start Route Rule ashburn_vcn_dmz-subnet-rtable-drg_10.3.2.0/23
              {
                    network_entity_id = "vcn-drg"
                    description       = "Route to Freight internal"
                    destination       = "10.3.2.0/23"
                    destination_type  = "CIDR_BLOCK"
                   },
              ## End Route Rule ashburn_vcn_dmz-subnet-rtable-drg_10.3.2.0/23
      ####ADD_NEW_DRG_RULES #ashburn_vcn_dmz-subnet-rtable# ####
          ]
          route_rules_lpg = [
      ####ADD_NEW_LPG_RULES #ashburn_vcn_dmz-subnet-rtable# ####
          ]
          route_rules_ip = [
      ####ADD_NEW_IP_RULES #ashburn_vcn_dmz-subnet-rtable# ####
          ]
          defined_tags = {
                  "Oracle-Tags.CreatedOn"= "2022-08-23T12:42:06.703Z" ,
                  "Oracle-Tags.CreatedBy"= "abc@oracle.com"
          }
          freeform_tags = {}
        },
  }
    ````

15. Default Route Tables (Default RTs)
- <b>Syntax</b>
  
    ````
  default_route_tables = {
        ## key - Is a unique value to reference the resources respectively
        key = {
  
            # Required
            compartment_id   = string
            vcn_id           = string
            display_name     = string
  
            # Optional
            # IGW Rules
            route_rules_igw  = [] # When there are no IGW Rules
            (OR)
            route_rules_igw  = [{
                  network_entity_id = string
                  description       = string
                  destination       = string
                  destination_type  = string
            }]
  
            # SGW Rules
            route_rules_sgw  = [] # When there are no SGW Rules
            (OR)
            route_rules_sgw  = [{
                  network_entity_id = string
                  description       = string
                  destination       = string
                  destination_type  = string
            }]
  
            # NGW Rules
            route_rules_ngw  = [] # When there are no NGW Rules
            (OR)
            route_rules_ngw  = [{
                  network_entity_id = string
                  description       = string
                  destination       = string
                  destination_type  = string
            }]
  
            # DRG Rules
            route_rules_drg  = [] # When there are no DRG Rules
            (OR)
            route_rules_drg  = [{
                  network_entity_id = string
                  description       = string
                  destination       = string
                  destination_type  = string
            }]
  
            # LPG Rules
            route_rules_lpg  = [] # When there are no LPG Rules
            (OR)
            route_rules_lpg  = [{
                  network_entity_id = string
                  description       = string
                  destination       = string
                  destination_type  = string
            }]
  
            # IP Rules
            route_rules_ip   = [] # When there are no IP Rules
            (OR)
            route_rules_ip   = [{
                  network_entity_id = string
                  description       = string
                  destination       = string
                  destination_type  = string
            }]
            # set the tags to {} when not needed; example-> defined_tags = {}
            defined_tags     = map
            freeform_tags    = map
  }
    ````
- <b>Example</b>
    ````
  // Copyright (c) 2021, 2022, Oracle and/or its affiliates.
  ############################
  # Network
  # Major Objects - Default Route Table - tfvars
  # Allowed Values:
  # vcn_id can be the ocid or the key of vcns (map)
  # compartment_id can be the ocid or the name of the compartment hierarchy delimited by double hiphens "--"
  # Example : compartment_id = "ocid1.compartment.oc1..aaaaaaaahwwiefb56epvdlzfic6ah6jy3xf3c" or compartment_id = "Network-root-cpt--Network" where "Network-root-cpt" is the parent of "Network" compartment
  ############################
  
  default_route_tables = {
    # Route Table map #
    # Start of #ashburn_vcn_app-subnet-rtable# #
      vcn_app-subnet-rtable = {
          # Required
          compartment_id = "fc-network-cmp"
          vcn_id     = "vcn1"
          display_name     = "Default Route Table for vcn_app-subnet-rtable"
  
          # Optional
          route_rules_igw = [
      ####ADD_NEW_IGW_RULES #ashburn_vcn_app-subnet-rtable# ####
          ]
          route_rules_sgw = [
      ####ADD_NEW_SGW_RULES #ashburn_vcn_app-subnet-rtable# ####
          ]
          route_rules_ngw = [
                  ## Start Route Rule ashburn_vcn_app-subnet-rtable-natgw_0.0.0.0/0
              {
                    network_entity_id = "vcn-natgw"
                    description       = ""
                    destination       = "0.0.0.0/0"
                    destination_type  = "CIDR_BLOCK"
                   },
              ## End Route Rule ashburn_vcn_app-subnet-rtable-natgw_0.0.0.0/0
      ####ADD_NEW_NGW_RULES #ashburn_vcn_app-subnet-rtable# ####
          ]
          route_rules_drg = [
                  ## Start Route Rule ashburn_vcn_app-subnet-rtable-drg_10.0.2.0/22
              {
                    network_entity_id = "vcn-drg"
                    description       = ""
                    destination       = "10.0.2.0/22"
                    destination_type  = "CIDR_BLOCK"
                   },
              ## End Route Rule ashburn_vcn_app-subnet-rtable-drg_10.0.2.0/22
      ####ADD_NEW_DRG_RULES #ashburn_vcn_app-subnet-rtable# ####
          ]
          route_rules_lpg = [
      ####ADD_NEW_LPG_RULES #ashburn_vcn_app-subnet-rtable# ####
          ]
          route_rules_ip = [
      ####ADD_NEW_IP_RULES #ashburn_vcn_app-subnet-rtable# ####
          ]
          defined_tags = {
                  "Oracle-Tags.CreatedOn"= "2022-08-23T15:03:30.750Z" ,
                  "Oracle-Tags.CreatedBy"= "abc@oracle.com"
          }
          freeform_tags = {}
        },
    # End of #ashburn_vcn_app-subnet-rtable# #
    # Start of #ashburn_vcn_dmz-subnet-rtable# #
      dmz-subnet-rtable = {
          # Required
          compartment_id = "fc-network-cmp"
          vcn_id     = "vcn2"
          display_name     = "Default Route Table for dmz-subnet-rtable"
  
          # Optional
          route_rules_igw = [
                  ## Start Route Rule ashburn_vcn_dmz-subnet-rtable-igw_0.0.0.0/0
              {
                    network_entity_id = "vcn-igw"
                    description       = ""
                    destination       = "0.0.0.0/0"
                    destination_type  = "CIDR_BLOCK"
                   },
              ## End Route Rule ashburn_vcn_dmz-subnet-rtable-igw_0.0.0.0/0
      ####ADD_NEW_IGW_RULES #ashburn_vcn_dmz-subnet-rtable# ####
          ]
          route_rules_sgw = [
      ####ADD_NEW_SGW_RULES #ashburn_vcn_dmz-subnet-rtable# ####
          ]
          route_rules_ngw = [
      ####ADD_NEW_NGW_RULES #ashburn_vcn_dmz-subnet-rtable# ####
          ]
          route_rules_drg = [
                  ## Start Route Rule ashburn_vcn_dmz-subnet-rtable-drg_10.0.2.0/22
              {
                    network_entity_id = "vcn-drg"
                    description       = ""
                    destination       = "10.0.2.0/22"
                    destination_type  = "CIDR_BLOCK"
                   },
              ## End Route Rule ashburn_vcn_dmz-subnet-rtable-drg_10.0.2.0/22
              ## Start Route Rule ashburn_vcn_dmz-subnet-rtable-drg_10.3.2.0/23
              {
                    network_entity_id = "vcn-drg"
                    description       = "Route to Freight internal"
                    destination       = "10.3.2.0/23"
                    destination_type  = "CIDR_BLOCK"
                   },
              ## End Route Rule ashburn_vcn_dmz-subnet-rtable-drg_10.3.2.0/23
      ####ADD_NEW_DRG_RULES #ashburn_vcn_dmz-subnet-rtable# ####
          ]
          route_rules_lpg = [
      ####ADD_NEW_LPG_RULES #ashburn_vcn_dmz-subnet-rtable# ####
          ]
          route_rules_ip = [
      ####ADD_NEW_IP_RULES #ashburn_vcn_dmz-subnet-rtable# ####
          ]
          defined_tags = {
                  "Oracle-Tags.CreatedOn"= "2022-08-23T12:42:06.703Z" ,
                  "Oracle-Tags.CreatedBy"= "abc@oracle.com"
          }
          freeform_tags = {}
        },
  }
    ````
  
16. Custom DHCP Options
- <b>Syntax</b>
  
    ````
  custom_dhcps = {
      ## key - Is a unique value to reference the resources respectively
      key = {
          # Required
          compartment_id              = string
          server_type                 = string
          vcn_id                      = string
  
          # Optional
          search_domain               =  {  # Required for type SearchDomain
                names                 = list
          }
          custom_dns_servers          = list # Required only for type DomainNameServer
          domain_name_type            = string
          display_name                = string
          defined_tags                = map
          freeform_tags               = map
      }
  }
    ````
- <b>Example</b>
    ````
  ############################
  # Network
  # Custom DHCP - tfvars
  # Allowed Values:
  # vcn_id can be the ocid or the key of vcns (map)
  # compartment_id can be the ocid or the name of the compartment hierarchy delimited by double hiphens "--"
  # Example : compartment_id = "ocid1.compartment.oc1..aaaaaaaahwwiefb56epvdlzfic6ah6jy3xf3c" or compartment_id = "Network-root-cpt--Network" where "Network-root-cpt" is the parent of "Network" compartment
  ############################
  custom_dhcps = {
    Services-Internal = {
      # Required
      compartment_id     = "Network"
      vcn_id             = "Services"
      server_type        = "VcnLocalPlusInternet"
  
      # Optional
      display_name       = "Services-Internal"
      search_domain = {
        names = ["abc.com"]
      }
      defined_tags = {
        "Oracle-Tags.CreatedOn"    = "2022-02-28T05:46:44.814Z",
        "Oracle-Tags.CreatedBy"    = "abc@oracle.com"
      }
    },
    Services_Custom = {
      # Required
      compartment_id     = "Network"
      vcn_id             = "Services"
      server_type        = "CustomDnsServer"
  
      # Optional
      custom_dns_servers = ["10.28.24.10", "10.28.53.10"]
      display_name       = "Services_Custom"
      search_domain = {
        names = ["abc.com"]
      }
      defined_tags = {
        "Oracle-Tags.CreatedOn"    = "2022-02-28T05:46:44.517Z",
        "Oracle-Tags.CreatedBy"    = "abc@oracle.com"
      }
    },
  }
    ````

17. Default DHCP Options
- <b>Syntax</b>
  
    ````
  default_dhcps = {
      ## key - Is a unique value to reference the resources respectively
      key = {
          # Required
          server_type                 = string
  
          # Optional
          manage_default_resource_id = string # can be vcn name or default dhcp ocid
          search_domain               =  {  # Required for type SearchDomain
                names                 = list
          }
          custom_dns_servers          = list # Required only for type DomainNameServer
          defined_tags                = map
          freeform_tags               = map
      }
  }
    ````
- <b>Example</b>
    ````
  ############################
  # Network
  # Major Objects - Default DHCP - tfvars
  # Allowed Values:
  # manage_default_resource_id can be the ocid or the key of vcns (map)
  ############################
  default_dhcps = {
    vcn3_Default-DHCP-Options-for-vcn3 = {
            # Required
            server_type          = "VcnLocalPlusInternet"
            manage_default_resource_id = "vcn3" # can be vcn name or default dhcp ocid

            # Optional
            defined_tags = {
                    "Oracle-Tags.CreatedOn"= "2022-09-06T07:27:40.005Z" ,
                    "Oracle-Tags.CreatedBy"= "oracleidentitycloudservice/abc@oracle.com"
            }
    },
    vcn2_Default-DHCP-Options-for-vcn2 = {
            # Required
            server_type          = "VcnLocalPlusInternet"
            manage_default_resource_id = "vcn2" # can be vcn name or default dhcp ocid

            # Optional
            defined_tags = {
                    "Oracle-Tags.CreatedOn"= "2022-09-06T07:27:39.936Z" ,
                    "Oracle-Tags.CreatedBy"= "oracleidentitycloudservice/abc@oracle.com"
            }
    },
  }
    ````
  
18. Network Security Groups (NSGs)
- <b>Syntax</b>
    ````
    nsgs = {
        ## key - Is a unique value to reference the resources respectively
        key = {
            # Required
            compartment_id = string
            vcn_id         = string
  
            # Optional
            display_name   = string
            defined_tags   = string
            freeform_tags  = string
        }   
    }
    ````
- <b>Example</b>
    ````
  ############################
  # Network
  # Network Security Group - tfvars
  # Allowed Values:
  # vcn_id can be the ocid or vcns map key
  # compartment_id can be the ocid or the name of the compartment hierarchy delimited by double hiphens "--"
  # Example : compartment_id = "ocid1.compartment.oc1..aaaaaaaahwwiefb56epvdlzfic6ah6jy3xf3c" or compartment_id = "Network-root-cpt--Network" where "Network-root-cpt" is the parent of "Network" compartment
  ############################
  nsgs = {
      # NSG map #
      ##Add New NSGs for phoenix here##
      # Start of phoenix_NSG1-1 #
      NSG1-1 = {
            # Required
            compartment_id   = "Network"
            vcn_id           = "vcn1"
  
            # Optional
            display_name     = "NSG1-1"
            defined_tags = {
                    "Oracle-Tags.CreatedOn"= "2022-09-30T10:48:50.016Z" ,
                    "Oracle-Tags.CreatedBy"= "abc@oracle.com"
            }
        },
      # End of phoenix_NSG1-1 #
      # Start of phoenix_NSG1-2 #
      NSG1-2 = {
            # Required
            compartment_id   = "Network"
            vcn_id           = "vcn2"

            # Optional
            display_name     = "NSG1-2"
            defined_tags = {
                    "Oracle-Tags.CreatedOn"= "2022-09-29T09:18:01.888Z" ,
                    "Oracle-Tags.CreatedBy"= "abc@oracle.com"
            }
        },
      # End of phoenix_NSG1-2 #
  }
    ````
  
19. Network Security Group Rules (NSG Rules)
- <b>Syntax</b>
  
    ````
  nsg_rules = {
      ## key - Is a unique value to reference the resources respectively
      key = {
          # Required
          nsg_id          = string
          direction       = string
          protocol        = string
   
          # Optional
          description     = string
          stateless       = string
          source_type     = string
          source          = string
          destinaion_type = string
          destination     = string
  
          # ICMP Options
          icmp_options    = [{
                icmp_type = string 
                icmp_code = string   #  icmp_code = "" if you want to pass only the type
            }] 
          (OR)
          # When there are no ICMP rules
          icmp_options = [{
                icmp_type = ""
                icmp_code = ""
            }]
 
          # TCP Options 
          tcp_options = [{
              source_port_range = [{
                  tcp_options_source_port_max = string
                  tcp_options_source_port_min = string
                  }]
              (OR) 
              # When there are no Source Port Range
              source_port_range = []
  
              destination_port_range = [{
                  tcp_options_destination_port_max = string
                  tcp_options_destination_port_min = string
                  }]
              (OR) 
              # When there are no Destination Port Range
              destination_port_range = []
              }]
          (OR) 
          # When there are no TCP Options
          tcp_options = []
  
          # UDP Options 
          udp_options = [{
              source_port_range = [{
                  udp_options_source_port_max = string
                  udp_options_source_port_min = string
                  }]
              (OR) 
              # When there are no Source Port Range
              source_port_range = []
  
              destination_port_range = [{
                  udp_options_destination_port_max = string
                  udp_options_destination_port_min = string
                  }]
              (OR) 
              # When there are no Destination Port Range
              destination_port_range = []
              }]
          (OR) 
          # When there are no UDP Options
          udp_options = []
    
      }
  }
    ````
- <b>Example</b>
    ````
  ############################
  # Network
  # Network Security Group Rules
  # Allowed Values:
  # nsg_id can be ocid or the key of nsgs (map)
  ############################
  nsg_rules = {
      # NSG Rule map #
      ##Add New NSG Rules for ashburn here##
      dns_nsg_rule1 =  {
            # Required
            nsg_id = "dns_nsg"
            direction = "INGRESS"
            protocol = "UDP"
    
            # Optional
            description = "dns_nsg_rule1"
            stateless = "false"
            source_type = "CIDR_BLOCK"
            destination_type = null
            destination = ""
            source = "10.0.0.0/14"
            icmp_options = [{
                icmp_type = ""
                icmp_code = ""
            }]
            tcp_options = []
            udp_options = [{
                destination_port_range  = [{
                    udp_options_destination_port_max = "53"
                    udp_options_destination_port_min = "53"
                }]
                source_port_range = []
            }]
       },
      dns_nsg_rule2 =  {
            # Required
            nsg_id = "dns_nsg"
            direction = "INGRESS"
            protocol = "ICMP"
  
            # Optional
            description = " "
            stateless = "false"
            source_type = "CIDR_BLOCK"
            destination_type = null
            destination = ""
            source = "10.0.0.0/14"
            icmp_options = [{
                icmp_type = ""
                icmp_code = ""
            }]
            tcp_options = []
            udp_options = []
       },
      dns_nsg_rule3 =  {
            # Required
            nsg_id = "dns_nsg"
            direction = "EGRESS"
            protocol = "TCP"
  
            # Optional
            description = "dns_nsg_rule3"
            stateless = "false"
            source_type = null
            destination_type = "CIDR_BLOCK"
            destination = "10.0.0.0/32"
            source = ""
            icmp_options = [{
                icmp_type = ""
                icmp_code = ""
            }]
            tcp_options = [{
                source_port_range = []
                destination_port_range = [{
                    tcp_options_destination_port_max = "53"
                    tcp_options_destination_port_min = "53"
                    }]
            }]
            udp_options = []
      },
  }
    ````
  
20. Local Peering Gateways (LPGs)
- <b>Syntax</b>
    ````
    lpgs = {
        ## key - Is a unique value to reference the resources respectively
        key = {
  
            # LPGs of Hub VCN
            hub-lpgs      = {
                # Required
                compartment_id = string
                vcn_id         = string
                lpg_name       = string
  
                # Optional
                route_table_id = string
                peer_id        = string
                # set the tags to {} when not needed; example-> defined_tags = {}
                defined_tags    = map
                freeform_tags   = map
            },
            (OR)
            # When there are no LPGs in Hub VCN
            hub-lpgs      = {}, 
  
            # LPGs of Spoke VCN
            spoke-lpgs    = {
                # Required
                compartment_id = string
                vcn_id         = string
                lpg_name       = string
  
                # Optional
                route_table_id = string
                peer_id        = string
                # set the tags to {} when not needed; example-> defined_tags = {}
                defined_tags    = map
                freeform_tags   = map
            },
            (OR)
            # When there are no LPGs in Spoke VCN
            spoke-lpgs      = {},  
  
            # LPGs of Peer VCN
            peer-lpgs     = {
                # Required
                compartment_id = string
                vcn_id         = string
                lpg_name       = string
  
                # Optional
                route_table_id = string
                peer_id        = string
                # set the tags to {} when not needed; example-> defined_tags = {}
                defined_tags    = map
                freeform_tags   = map
            },
            (OR)
            # When there are no LPGs in Peer VCN
            peer-lpgs      = {}, 
  
            # LPGs of VCN that are declared as neither hub nor spoke
            none-lpgs     = {
                # Required
                compartment_id = string
                vcn_id         = string
                lpg_name       = string
  
                # Optional
                route_table_id = string
                peer_id        = string
                # set the tags to {} when not needed; example-> defined_tags = {}
                defined_tags    = map
                freeform_tags   = map
            },
            (OR)
            # When there are no LPGs in a VCN that is neither hub nor spoke
            none-lpgs      = {}, 
  
            # LPGs of VCN Exported by the toolkit
            exported-lpgs = {
                # Required
                compartment_id = string
                vcn_id         = string
                lpg_name       = string
  
                # Optional
                route_table_id = string
                peer_id        = string
                # set the tags to {} when not needed; example-> defined_tags = {}
                defined_tags    = map
                freeform_tags   = map
            }, 
            (OR)
            # When there are no LPGs in the VCNs that are exported by the toolkit
            exported-lpgs      = {}, 
        }
    }
    ````
- <b>Example</b>
    ````
    ````

