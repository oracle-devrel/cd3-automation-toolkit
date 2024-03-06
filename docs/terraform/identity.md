## auto.tfvars syntax for Identity Module
These are the syntax and sample format for providing inputs to the modules via <b>*.auto.tfvars</b> files.
<b>"key"</b> must be unique to every resource that is created.
Comments preceed with <b>##</b>.

## IDENTITY
**1. Compartments**
- <b>Syntax</b>
  
    ````
  compartments = {
        root = {
            ## key - Is a unique value to reference the resources respectively
            key = { 
                # Required
                parent_compartment_id = string
                name                  = string
  
                # Optional
                description           = string 
                enable_delete         = boolean 
                defined_tags          = map 
                freeform_tags         = map 
               },
            },
    
        compartment_level1 = {
             ## key - Is a unique value to reference the resources respectively
             key = {
                # Required
                parent_compartment_id = string
                name                  = string
  
                # Optional
                description           = string 
                enable_delete         = boolean 
                defined_tags          = map 
                freeform_tags         = map 
                },
            },
    
        compartment_level2 = {
            ## key - Is a unique value to reference the resources respectively
            key = {
                # Required
                parent_compartment_id = string
                name                  = string
  
                # Optional
                description           = string 
                enable_delete         = boolean 
                defined_tags          = map 
                freeform_tags         = map 
                },
            },
    
        compartment_level3 = {
            ## key - Is a unique value to reference the resources respectively
            key = {
                # Required
                parent_compartment_id = string
                name                  = string
  
                # Optional
                description           = string 
                enable_delete         = boolean 
                defined_tags          = map 
                freeform_tags         = map 
                },
            },
    
        compartment_level4 = {
            ## key - Is a unique value to reference the resources respectively
            key = {
                # Required
                parent_compartment_id = string
                name                  = string
  
                # Optional
                description           = string 
                enable_delete         = boolean 
                defined_tags          = map 
                freeform_tags         = map 
                },
            },
    
        compartment_level5 = {
            ## key - Is a unique value to reference the resources respectively
            key = {
                # Required
                parent_compartment_id = string
                name                  = string
  
                # Optional
                description           = string 
                enable_delete         = boolean 
                defined_tags          = map 
                freeform_tags         = map 
                },
            },
    }
  ````
  
- <b>Example:</b>
  ````
    ############################
    # Identity
    # Compartments - tfvars
    # Allowed Values:
    # parent_compartment_id can be the ocid or the name of the compartment hierarchy delimited by double hiphens "--"
    # Example : parent_compartment_id = "ocid1.compartment.oc1..aaaaaaaahwwiefb56epvdlzfic6ah6jy3xf3c" or parent_compartment_id = "Network-root-cpt--Network" where "Network-root-cpt" is the parent of "Network" compartment
    ############################

    compartments = {
        root = {
            Network = {
                # Required
                parent_compartment_id = root
                name                  = "Network"
                
                # Optional
                description           = "Compartment for all network related resources: VCNs, subnets, network gateways, security lists, NSGs, load balancers, VNICs."
                defined_tags          = {
                          "Oracle-Tags.CreatedOn"= "2022-08-09T11:15:45.919Z" ,
                          "Oracle-Tags.CreatedBy"= "oracleidentitycloudservice/abc@oracle.com"
                }
                },
            Database = {
                # Required
                parent_compartment_id = root
                name                  = "Database"
    
                # Optional
                description           = "Compartment for all database related resources."
                defined_tags          = {
                          "Oracle-Tags.CreatedOn"= "2022-08-09T11:15:45.919Z" ,
                          "Oracle-Tags.CreatedBy"= "oracleidentitycloudservice/abc@oracle.com"
                }
                freeform_tags         = {}
                },
            AppDev = {
                # Required
                parent_compartment_id = root
                name                  = "AppDev"
    
                # Optional
                description           = "Compartment for all resources related to application development: functions, OKE, API Gateway, streaming, notifications."
                defined_tags          = {
                          "Oracle-Tags.CreatedOn"= "2022-08-09T11:15:45.919Z" ,
                          "Oracle-Tags.CreatedBy"= "oracleidentitycloudservice/abc@oracle.com"
                }
                },
            },
    
        compartment_level1 = {
            Non-Prod = {
                # Required
                parent_compartment_id = AppDev
                name                  = "Non-Prod"
    
                # Optional
                description           = "Compartment for all the non-prod application resources."
                enable_delete         = true
                defined_tags          = {
                          "Oracle-Tags.CreatedOn"= "2022-08-09T11:15:45.919Z" ,
                          "Oracle-Tags.CreatedBy"= "oracleidentitycloudservice/abc@oracle.com"
                }
                },
            Prod = {
                # Required
                parent_compartment_id = AppDev
                name                  = "Prod"
    
                # Optional
                description           = "Compartment for all the prod application resources."
                enable_delete         = true
                defined_tags          = {
                          "Oracle-Tags.CreatedOn"= "2022-08-09T11:15:45.919Z" ,
                          "Oracle-Tags.CreatedBy"= "oracleidentitycloudservice/abc@oracle.com"
                }
                },
            },
    
        ## Similar values can be entered for the compartment levels below.
    
        compartment_level2 = {},
    
        compartment_level3 = {},
    
        compartment_level4 = {},
    
        compartment_level5 = {},
    }
  ````
    
**2. Groups/Dynamic Groups**

   &#9432; The parameter that differentiate dynamic groups from normal groups is <b> matching_rule </b>. Normal Groups will be created when you <b>omit</b> this parameter or pass it as <b>""</b> or <b>null</b>. All the groups are created in the root compartment.
- <b>Syntax</b>
  
    ````
  groups = {
     ## key - Is a unique value to reference the resources respectively
     key = {
        # Required
        group_name            = string
        group_description     = string
  
        # Optional
        matching_rule         = string  (Required only for Dynamic Group)
        defined_tags          = map 
        freeform_tags         = map 
        },
     }
    ````
  
- <b>Example:</b>
  ````
    ############################
    # Identity
    # Groups/Dynamic Groups - tfvars
    ############################
    
    groups = {
    # Normal Group
    Administrators = {
        # Required
        group_name        = "Administrators"
        group_description = "Administrators"
    },
    # Normal Group
    IAMAdmins = {
        # Required
        group_name        = "IAMAdmins"
        group_description = "Group responsible for managing IAM resources in the tenancy."
        
        # Optional
        defined_tags = {
                "Oracle-Tags.CreatedOn"= "2022-03-23T07:00:34.666Z" ,
                "Oracle-Tags.CreatedBy"= "oracleidentitycloudservice/abc@oracle.com"
        }
    },
    # Dynamic Group
    CD3_Instances = {
        group_name        = "CD3_Instances"
        group_description = "Instance Group for CD3 Instances"
        
        # Optional 
        matching_rule     = "Any {Any {instance.compartment.id = 'ocid1.compartment.oc1..aaaaaaaasfwefuhwkjfew2rrcxx37d5ntq7r53wtaq'},Any {instance.compartment.id = 'ocid1.compartment.oc1..aaz2ylwikr5rg4slidxzec7aijanq'}}" # Can be null or "" for regular groups
    },
    }
  ````

**3. Policies**

   &#9432; The parameter that differentiate dynamic groups from normal groups is <b> matching_rule </b>. Normal Groups will be created when you <b>omit</b> this parameter or pass it as <b>""</b> or <b>null</b>.
- <b>Syntax</b>
  
    ````
  policies = {
     ## key - Is a unique value to reference the resources respectively
     key = {
        # Required
        name               = string
        compartment_id     = string
        policy_description = string
        policy_statements  = list(string)
  
        # Optional
        policy_version_date   = string
        defined_tags          = map 
        freeform_tags         = map 
        },
     }
    ````
  
- <b>Example:</b>
  ````
    ############################
    # Identity
    # Policies - tfvars
    # Allowed Values:
    # compartment_id can be the ocid or the name of the compartment hierarchy delimited by double hiphens "--"
    # Example : compartment_id = "ocid1.compartment.oc1..aaaaaaaahwwiefb56epvdlzfic6ah6jy3xf3c" or compartment_id = "Network-root-cpt--Network" where "Network-root-cpt" is the parent of "Network" compartment
    ############################
    
    policies = {
       CD3_Instances_Policy = {
            # Required
            name               = "CD3_Instances_Policy"
            compartment_id     = "root"
            policy_description = "Policy for VMs in CD3 Compartment"
            policy_statements  = [ "Allow dynamic-group CD3_Instances to manage object-family in tenancy" ,"Allow dynamic-group CD3_Instances to manage instance-family in tenancy" ,"Allow dynamic-group CD3_Instances to manage database-family in tenancy" ,"Allow dynamic-group CD3_Instances to manage secret-family in tenancy" ,"Allow dynamic-group CD3_Instances to read all-resources in tenancy"  ]
       },
       IAMAdmins-Policy = {
            # Required
            name        = "IAMAdmins-Policy"
            compartment_id = "root"
            policy_description = "Policy allowing IAMAdmins group to manage IAM resources in tenancy, except changing Administrators group assignments."
            policy_statements = [ "Allow group IAMAdmins to manage policies in tenancy" ,"Allow group IAMAdmins to manage compartments in tenancy" ,"Allow group IAMAdmins to manage tag-defaults in tenancy" ,"Allow group IAMAdmins to manage tag-namespaces in tenancy" ,"Allow group IAMAdmins to manage orm-stacks in tenancy" ,"Allow group IAMAdmins to manage orm-jobs in tenancy" ,"Allow group IAMAdmins to manage orm-config-source-providers in tenancy" ,"Allow group IAMAdmins to inspect users in tenancy" ,"Allow group IAMAdmins to inspect groups in tenancy" ,"Allow group IAMAdmins to manage groups in tenancy where all {target.group.name != 'Administrators', target.group.name != 'CredAdmins'}" ,"Allow group IAMAdmins to inspect identity-providers in tenancy" ,"Allow group IAMAdmins to manage identity-providers in tenancy where any {request.operation = 'AddIdpGroupMapping', request.operation = 'DeleteIdpGroupMapping'}" ,"Allow group IAMAdmins to manage dynamic-groups in tenancy" ,"Allow group IAMAdmins to manage authentication-policies in tenancy" ,"Allow group IAMAdmins to manage network-sources in tenancy" ,"Allow group IAMAdmins to manage quota in tenancy" ,"Allow group IAMAdmins to read audit-events in tenancy" ,"Allow group IAMAdmins to use cloud-shell in tenancy"  ]
            
            # Optional
            defined_tags = {
                    "Oracle-Tags.CreatedOn"= "2022-03-23T07:19:18.918Z" ,
                    "Oracle-Tags.CreatedBy"= "oracleidentitycloudservice/abc@oracle.com"
            }
       },
    }
  ````
  
 
**4. Users**

- <b>Syntax</b>
  
    ````
  users = {
     ## key - Is a unique value to reference the resources respectively
     key = {
    # Required
      name                  = string
      description           = string
      email                 = string
      group_membership      = list(string)
    disable_capabilities  = list(string)

      # Optional
      defined_tags          = map
      },
  }
    ````
    
- <b>Example:</b>

    ````
      ############################
      # Identity
      # Users - tfvars
      ############################
      users = {
         testUser = {
          # Required
          name                 = "testUser"
          description          = "this is a test user"
          email                = "testUser@oracle.com"
          group_membership     = ["OSAdmin","Administrators"]
          disable_capabilities = ["can_use_console_password","can_use_customer_secret_keys"]

          # Optional
              defined_tags = {
                      "Oracle-Tags.CreatedOn"= "2023-05-23T07:19:18.918Z" ,
                      "Oracle-Tags.CreatedBy"= "oracleidentitycloudservice/abc@oracle.com"
                }      
            }            
        }
   ````


**5. Network Sources**

- <b>Syntax</b>

    ````
      networkSources = {
         ## key - Is a unique value to reference the resources respectively
         key = {
            # Required
            name                  = string
            description           = string
            public_source_list    = list(string)
            virtual_source_list   = list(map)

          # Optional
          defined_tags          = map
          },
        }
 
    ````

- <b>Example</b>

       
     ````
        ############################
        # Identity
        # Network Sources - tfvars
        ############################
        networkSources = {
           networkSourcesExample = {
            # Required
            name                 = "myNetworkSource"
            description          = "this is a network source"
            public_source_list   = ["192.0.2.0/24","192.0.3.0/26"]
            virtual_source_list  =
              [
                {
                  vcn_name               = ["VCN1"],
                  network_compartment_id = ["NetworkCompartment"],
                  ip_ranges              = [ "10.169.0.0/16"]
                },
                {
                  vcn_name 			         = ["VCN2"],
                  network_compartment_id = ["NetworkCompartment"],
                  ip_ranges              = ["172.16.2.0/24", "172.16.2.0/26"]
                }
              ]

		  # Optional
          defined_tags = {
                  "Oracle-Tags.CreatedOn"= "2023-05-23T07:19:18.918Z" ,
                  "Oracle-Tags.CreatedBy"= "oracleidentitycloudservice/abc@oracle.com"
		            }
          }
       }
       
    ````
 

