# auto.tfvars syntax for Logging Module
These are the syntax and sample format for providing inputs to the modules via <b>*.auto.tfvars</b> files.
<b>"key"</b> must be unique to every resource that is created.
Comments preceed with <b>##</b>.

## Object Storage logs

**1. Object Storage Log Groups**

- <b>Syntax</b>
  
```
    oss_log_groups = {
        ## key - Is a unique value to reference the resources respectively
        key = {
            # Required
            compartment_id = string
            display_name   = string
    
            # Optional
            description    = string
            defined_tags   = map
            freeform_tags  = map
          }
    }
```

- <b>Example</b>
```
  // Copyright (c) 2021, 2022, Oracle and/or its affiliates.
  ############################
  # ManagementServices
  # OSS Log Groups - tfvars
  # Allowed Values:
  # compartment_id can be the ocid or the name of the compartment hierarchy delimited by double hiphens "--"
  # Example : compartment_id = "ocid1.compartment.oc1..aaaaaaaahwwiefb56epvdlzfic6ah6jy3xf3c" or compartment_id = "Security--Prod" where "Security" is the parent of "Prod" compartment
  ############################
  oss_log_groups = {
    # Log Group map #
    CD3-london-oss-log-group = {
        compartment_id = "Storage"
        display_name   = "CD3-london-oss-log-group"
        description    = "Log Group for OSS bucket"
      },
  ##Add New Log Groups for london here##
  }
```

**2. Object Storage Logs**

- <b>Syntax</b>
  
```
    oss_logs = {
        ## key - Is a unique value to reference the resources respectively
        key = {
            # Required
            display_name             = string
            log_group_id             = string
            log_type                 = string
    
            # Optional
            compartment_id           = string
            category                 = string
            resource                 = string
            service                  = string
            source_type              = string
            is_enabled               = bool
            retention_duration       = number
            defined_tags             = map
            freeform_tags            = map
        }
    
    }

```

- <b>Example</b>
```
  // Copyright (c) 2021, 2022, Oracle and/or its affiliates.
  ############################
  # ManagementServices
  # OSS Logs - tfvars
  # Allowed Values:
  # compartment_id can be the ocid or the name of the compartment hierarchy delimited by double hiphens "--"
  # Example : compartment_id = "ocid1.compartment.oc1..aaaaaaaahwwiefb56epvdlzfic6ah6jy3xf3c" or compartment_id = "Network-root-cpt--Network" where "Network-root-cpt" is the parent of "Network" compartment
  ############################
  oss_logs = {
    # Log map #
    CD3-london-oss-log  = {
          display_name = "CD3-london-oss-log"
          log_group_id = "CD3-london-oss-log-group"
          log_type     = "SERVICE"
          category    = "write"
          resource    = "CD3-london-oss-bucket"
          service     = "objectstorage"
          source_type = "OCISERVICE"
          compartment_id = "Storage"
          is_enabled         = true
          retention_duration = 30
        },
  ##Add New Logs for london here##
  }
            
```

## VCN Flow logs

**3. VCN Log Groups**

- <b>Syntax</b>
  
```
    vcn_log_groups = {
        ## key - Is a unique value to reference the resources respectively
        key = {
            # Required
            compartment_id = string
            display_name   = string
    
            # Optional
            description    = string
            defined_tags   = map
            freeform_tags  = map
        }
    }
```

- <b>Example</b>
```
  // Copyright (c) 2021, 2022, Oracle and/or its affiliates.
  ############################
  # ManagementServices
  # VCN Log Groups - tfvars
  # Allowed Values:
  # compartment_id can be the ocid or the name of the compartment hierarchy delimited by double hiphens "--"
  # Example : compartment_id = "ocid1.compartment.oc1..aaaaaaaahwwiefb56epvdlzfic6ah6jy3xf3c" or compartment_id = "Security--Prod" where "Security" is the parent of "Prod" compartment
  ############################
  vcn_log_groups = {
    # Log Group map #
      fwl-vcn-flow-log-group = {
          # Required
          compartment_id = "Network"
          display_name   = "fwl-vcn-flow-log-group"
  
          # Optional
          description    = "Log Group for VCN"
          defined_tags = {
                  "Oracle-Tags.CreatedOn"= "2023-01-10T08:18:18.100Z" ,
                  "Oracle-Tags.CreatedBy"= "oracleidentitycloudservice/abc@xyz.com" ,                  
          }
          freeform_tags = {}
        },
  ##Add New Log Groups for london here##
  }
```

**4. VCN Flow Logs**

- <b>Syntax</b>
  
```
    vcn_logs = {
        ## key - Is a unique value to reference the resources respectively
        key = {
            # Required
            display_name             = string
            log_group_id             = string
            log_type                 = string
    
            # Optional
            compartment_id           = string
            category                 = string
            resource                 = string
            service                  = string
            source_type              = string
            is_enabled               = bool
            retention_duration       = number
            defined_tags             = map
            freeform_tags            = map
        }
    }
```

- <b>Example</b>
```
    // Copyright (c) 2021, 2022, Oracle and/or its affiliates.
    ############################
    # ManagementServices
    # VCN Logs - tfvars
    # Allowed Values:
    # compartment_id can be the ocid or the name of the compartment hierarchy delimited by double hiphens "--"
    # Example : compartment_id = "ocid1.compartment.oc1..aaaaaaaahwwiefb56epvdlzfic6ah6jy3xf3c" or compartment_id = "Network-root-cpt--Network" where "Network-root-cpt" is the parent of "Network" compartment
    ############################
    vcn_logs = {
      # Log map #
      fwl-vcn_fwl-priv-flow-log  = {
        # Required
        display_name = "fwl-priv-flow-log"
        log_group_id = "fwl-vcn-flow-log-group"
        log_type     = "SERVICE"
  
        # Optional
        category    = "all"
        resource    = "fwl-vcn_fwl-priv"
        service     = "flowlogs"
        source_type = "OCISERVICE"
        compartment_id = "Network"
        is_enabled         = true
        retention_duration = 30
        defined_tags = {
                "Oracle-Tags.CreatedOn"= "2023-01-10T08:18:18.100Z" ,
                "Oracle-Tags.CreatedBy"= "oracleidentitycloudservice/abc@xyz.com" ,
        }
      },
      fwl-vcn_fwl-mgmt-flow-log  = {
        # Required
        display_name = "fwl-mgmt-flow-log"
        log_group_id = "fwl-vcn-flow-log-group"
        log_type     = "SERVICE"
  
        # Optional
        category    = "all"
        resource    = "fwl-vcn_fwl-mgmt"
        service     = "flowlogs"
        source_type = "OCISERVICE"
        compartment_id = "Network"
        is_enabled         = true
        retention_duration = 30
        defined_tags = {
                "Oracle-Tags.CreatedOn"= "2023-01-10T08:18:19.064Z" ,
                "Oracle-Tags.CreatedBy"= "oracleidentitycloudservice/abc@xyz.com" ,
        }
      },
    ##Add New Logs for london here##
    }
```

## Load balancer logs

**5. Load Balancer Log Groups**

- <b>Syntax</b>
  
```
    loadbalancer_log_groups = {
        ## key - Is a unique value to reference the resources respectively
        key = {
            # Required
            compartment_id = string
            display_name   = string
    
            # Optional
            description    = string
            defined_tags   = map
            freeform_tags  = map
        }
    }
```

- <b>Example</b>
```
  // Copyright (c) 2021, 2022, Oracle and/or its affiliates.
  ############################
  # ManagementServices
  # LOADBALANCER Log Groups - tfvars
  # Allowed Values:
  # compartment_id can be the ocid or the name of the compartment hierarchy delimited by double hiphens "--"
  # Example : compartment_id = "ocid1.compartment.oc1..aaaaaaaahwwiefb56epvdlzfic6ah6jy3xf3c" or compartment_id = "Security--Prod" where "Security" is the parent of "Prod" compartment
  ############################
  loadbalancer_log_groups = {
    # Log Group map #
    lbr2-log-group = {
        compartment_id = "Network"
        display_name   = "lbr2-log-group"
        description    = "Log Group for lbr2"
        defined_tags = {
                "Oracle-Tags.CreatedOn"= "2023-01-11T08:02:47.567Z" ,
                "Oracle-Tags.CreatedBy"= "oracleidentitycloudservice/abc@xyz.com" ,
        }
        freeform_tags = {}
      },
    lbr1-log-group = {
        compartment_id = "Network"
        display_name   = "lbr1-log-group"
        description    = "Log Group for lbr1"
        defined_tags = {
                "Oracle-Tags.CreatedOn"= "2023-01-11T08:02:47.566Z" ,
                "Oracle-Tags.CreatedBy"= "oracleidentitycloudservice/abc@xyz.com" ,              
        }
        freeform_tags = {}
      },
  ##Add New Log Groups for london here##
  }
```

**6. Load Balancer Logs**

- <b>Syntax</b>
  
```
    loadbalancer_logs = {
        ## key - Is a unique value to reference the resources respectively
        key = {
            # Required
            display_name             = string
            log_group_id             = string
            log_type                 = string
    
            # Optional
            compartment_id           = string
            category                 = string
            resource                 = string
            service                  = string
            source_type              = string
            is_enabled               = bool
            retention_duration       = number
            defined_tags             = map
            freeform_tags            = map
        }
    }
```

- <b>Example</b>
```
    // Copyright (c) 2021, 2022, Oracle and/or its affiliates.
    ############################
    # ManagementServices
    # LOADBALANCER Logs - tfvars
    # Allowed Values:
    # compartment_id can be the ocid or the name of the compartment hierarchy delimited by double hiphens "--"
    # Example : compartment_id = "ocid1.compartment.oc1..aaaaaaaahwwiefb56epvdlzfic6ah6jy3xf3c" or compartment_id = "Network-root-cpt--Network" where "Network-root-cpt" is the parent of "Network" compartment
    ############################
    loadbalancer_logs = {
      # Log map #
        lbr2-log-access  = {
            display_name = "lbr2_access-log"
            log_group_id = "lbr2-log-group"
            log_type     = "SERVICE"
            category    = "access"
            resource    = "lbr2"
            service     = "loadbalancer"
            source_type = "OCISERVICE"
            compartment_id = "OMCDev--OMCDev-VM"
            is_enabled         = true
            retention_duration = 30
            defined_tags = {
                    "Oracle-Tags.CreatedOn"= "2023-01-11T08:02:47.567Z" ,
                    "Oracle-Tags.CreatedBy"= "oracleidentitycloudservice/abc@xyz.com" ,
            }
          },
        lbr2-log-error  = {
            display_name = "lbr2_error-log"
            log_group_id = "lbr2-log-group"
            log_type     = "SERVICE"
            category    = "error"
            resource    = "lbr2"
            service     = "loadbalancer"
            source_type = "OCISERVICE"
            compartment_id = "OMCDev--OMCDev-VM"
            is_enabled         = true
            retention_duration = 30
            defined_tags = {
                    "Oracle-Tags.CreatedOn"= "2023-01-11T08:02:47.567Z" ,
                    "Oracle-Tags.CreatedBy"= "oracleidentitycloudservice/abc@xyz.com" ,
            }
          },
      ##Add New Logs for london here##
      }
```

## NFS Logs

**7. NFS Log Groups**

- <b>Syntax</b>
  
```
    nfs_log_groups = {
        ## key - Is a unique value to reference the resources respectively
        key = {
            # Required
            compartment_id = string
            display_name   = string
    
            # Optional
            description    = string
            defined_tags   = map
            freeform_tags  = map
        }
    }
```

- <b>Example</b>
```
    // Copyright (c) 2021, 2022, Oracle and/or its affiliates.
    ############################
    # ManagementServices
    # NFS Log Groups - tfvars
    # Allowed Values:
    # compartment_id can be the ocid or the name of the compartment hierarchy delimited by double hiphens "--"
    # Example : compartment_id = "ocid1.compartment.oc1..aaaaaaaahwwiefb56epvdlzfic6ah6jy3xf3c" or compartment_id = "Security--Prod" where "Security" is the parent of "Prod" compartment
    ############################
    nfs_log_groups = {
        # Log Group map #
        MT1_nfs-log-group = {
            compartment_id = "AppDev"
            display_name   = "MT1_nfs-log-group"
            description    = "Log Group for MT1"
            defined_tags = {
                "Oracle-Tags.CreatedOn"= "2024-05-31T17:28:50.621Z" ,
                "Oracle-Tags.CreatedBy"= "oracleidentitycloudservice/abc@oracle.com"
            }
        },
    ##Add New Log Groups for london here##
    }
```

**8. NFS Logs**

- <b>Syntax</b>
  
```
    nfs_logs = {
        ## key - Is a unique value to reference the resources respectively
        key = {
            # Required
            display_name             = string
            log_group_id             = string
            log_type                 = string
    
            # Optional
            compartment_id           = string
            category                 = string
            resource                 = string
            service                  = string
            source_type              = string
            is_enabled               = bool
            retention_duration       = number
            defined_tags             = map
            freeform_tags            = map
        }

    }
```

- <b>Example</b>
``` 
    ############################
    # ManagementServices
    # NFS Logs - tfvars
    # Allowed Values:
    # compartment_id can be the ocid or the name of the compartment hierarchy delimited by double hiphens "--"
    # Example : compartment_id = "ocid1.compartment.oc1..aaaaaaaahwwiefb56epvdlzfic6ah6jy3xf3c" or compartment_id = "Network-root-cpt--Network" where "Network-root-cpt" is the parent of "Network" compartment
    ############################
    nfs_logs = {
        # Log map #
        MT1_nfslogs-log  = {
            display_name        = "MT1_nfslogs-log"
            log_group_id        = "MT1_nfs-log-group"
            log_type            = "SERVICE"
            category            = "nfslogs"
            resource            = "MT1"
            service             = "filestorage"
            source_type         = "OCISERVICE"
            compartment_id      = "AppDev"
            is_enabled          = true
            retention_duration  = 30
            defined_tags = {
                "Oracle-Tags.CreatedOn"= "2024-05-31T17:28:50.621Z" ,
                "Oracle-Tags.CreatedBy"= "oracleidentitycloudservice/abc@oracle.com"
            }
        },
        MT1_nfslogs-log  = {
            display_name        = "MT1_nfslogs-log"
            log_group_id        = "MT1_nfs-log-group"
            log_type            = "SERVICE"
            category            = "nfslogs"
            resource            = "MT1"
            service             = "filestorage"
            source_type         = "OCISERVICE"
            compartment_id      = "AppDev"
            is_enabled          = true
            retention_duration  = 30
            defined_tags = {
                "Oracle-Tags.CreatedOn"= "2024-05-31T17:28:50.621Z" ,
                "Oracle-Tags.CreatedBy"= "oracleidentitycloudservice/abc@oracle.com"
            }
        },      
        ##Add New Logs for london here##
     }
```
## Firewall logs

**9. Firewall Log Groups**

- <b>Syntax</b>
  
```
    fw_log_groups = {
        ## key - Is a unique value to reference the resources respectively
        key = {
            # Required
            compartment_id = string
            display_name   = string
    
            # Optional
            description    = string
            defined_tags   = map
            freeform_tags  = map
      }
    }
```

- <b>Example</b>
```
    // Copyright (c) 2021, 2022, Oracle and/or its affiliates.
    ############################
    # ManagementServices
    # FW Log Groups - tfvars
    # Allowed Values:
    # compartment_id can be the ocid or the name of the compartment hierarchy delimited by double hiphens "--"
    # Example : compartment_id = "ocid1.compartment.oc1..aaaaaaaahwwiefb56epvdlzfic6ah6jy3xf3c" or compartment_id = "Security--Prod" where "Security" is the parent of "Prod" compartment
    ############################
    fw_log_groups = {
    # Log Group map #
        OCI-FWL_fw-log-group = {
            compartment_id = "Network"
            display_name   = "OCI-FWL_fw-log-group"
            description    = "Log Group for OCI-FWL"
            defined_tags = {
                "Oracle-Tags.CreatedOn"= "2024-03-14T06:18:47.503Z" ,
                "Oracle-Tags.CreatedBy"= "oracleidentitycloudservice/abc@oracle.com"
            } 
        },
    ##Add New Log Groups for phoenix here##
    }
```


**10. Firewall Logs**

- <b>Syntax</b>
  
```
    fw_logs = {
        ## key - Is a unique value to reference the resources respectively
        key = {
            # Required
            display_name             = string
            log_group_id             = string
            log_type                 = string
    
            # Optional
            compartment_id           = string
            category                 = string
            resource                 = string
            service                  = string
            source_type              = string
            is_enabled               = bool
            retention_duration       = number
            defined_tags             = map
            freeform_tags            = map
      }
    }
```

- <b>Example</b>
```
    ############################
    # ManagementServices
    # FW Logs - tfvars
    # Allowed Values:
    # compartment_id can be the ocid or the name of the compartment hierarchy delimited by double hiphens "--"
    # Example : compartment_id = "ocid1.compartment.oc1..aaaaaaaahwwiefb56epvdlzfic6ah6jy3xf3c" or compartment_id = "Network-root-cpt--Network" where "Network-root-cpt" is the parent of "Network" compartment
    ############################
    fw_logs = {
    # Log map #
        OCI-FWL_threatlog-log  = {
            display_name        = "OCI-FWL_threatlog-log"
            log_group_id        = "OCI-FWL_fw-log-group"
            log_type            = "SERVICE"
            category            = "threatlog"
            resource            = "OCI-FWL"
            service             = "ocinetworkfirewall"
            source_type         = "OCISERVICE"
            compartment_id      = "Network"
            is_enabled          = true
            retention_duration  = 30
            defined_tags = {
                "Oracle-Tags.CreatedOn"= "2024-03-14T06:18:47.503Z" ,
                "Oracle-Tags.CreatedBy"= "oracleidentitycloudservice/suruchi.singla@oracle.com"
            }
        },
        OCI-FWL_trafficlog-log  = {
            display_name        = "OCI-FWL_trafficlog-log"
            log_group_id        = "OCI-FWL_fw-log-group"
            log_type            = "SERVICE"
            category            = "trafficlog"
            resource            = "OCI-FWL"
            service             = "ocinetworkfirewall"
            source_type         = "OCISERVICE"
            compartment_id      = "Network"
            is_enabled          = true
            retention_duration  = 30
            defined_tags = {
                "Oracle-Tags.CreatedOn"= "2024-03-14T06:18:47.503Z" ,
                "Oracle-Tags.CreatedBy"= "oracleidentitycloudservice/abc@oracle.com"
            }
        },
        ##Add New Logs for phoenix here##
    } 
```


