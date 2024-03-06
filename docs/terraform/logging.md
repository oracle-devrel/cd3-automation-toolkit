## auto.tfvars syntax for logging services

These are the syntax and sample format for providing inputs to the modules via <b>*.auto.tfvars</b> files.
<b>"key"</b> must be unique to every resource that is created.


**1. VCN Flow logs and VCN log groups**

<br>

- **Syntax for vcn flow logs**
```
vcn_logs = {
  # Log map #
  ## key - Is a unique value to reference the resources respectively
   key = {
        display_name        =  string
        log_group_id        =  string
        log_type            =  string
        category            =  string
        resource            =  string
        service             =  string
        source_type         =  string
        compartment_id      =  string
        is_enabled          = bool
        retention_duration  = string
      }
}
```
- **Syntax for all log groups**

```
vcn_log_groups = {
  # Log Group map #
   ## key - Is a unique value to reference the resources respectively
     key = {
        compartment_id = string
        display_name   = string
        description    = string
      }
   }

```


<br>

- **Example**

```
############################
# ManagementServices
# VCN Logs - tfvars
# Allowed Values:
# compartment_id can be the ocid or the name of the compartment hierarchy delimited by double hiphens "--"
# Example : compartment_id = "ocid1.compartment.oc1..aaaaaaaahwwiefb56epvdlzfic6ah6jy3xf3c" or compartment_id = "Network-root-cpt--Network" where "Network-root-cpt" is the parent of "Network" compartment
############################
vcn_logs = {
  # Log map #
  cd3_vcn_subnet1-flow-log  = {
        display_name        = "subnet1-flow-log"
        log_group_id        = "cd3_vcn-flow-log-group"
        log_type            = "SERVICE"
        category            = "all"
        resource            = "cd3_vcn_subnet1"
        service             = "flowlogs"
        source_type         = "OCISERVICE"
        compartment_id      = "Network"
        is_enabled          = true
        retention_duration  = 30
      }
 ##Add New Logs for london here##
}
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
    cd3_vcn-flow-log-group = {
        compartment_id = "Network"
        display_name   = "cd3_vcn-flow-log-group"
        description    = "Log Group for VCN"
      },
##Add New Log Groups for london here##
}

```

<br>
<br>


**2.  LBaaS access and error logs, log groups**
<br>

- **Syntax for Load Balancer access and error logs**

```

loadbalancer_logs = {
  # Log map #
  ## key - Is a unique value to reference the resources respectively
    key  = {
        display_name        = string
        log_group_id        = string
        log_type            = string
        category            = string
        resource            = string
        service             = string
        source_type         = string
        compartment_id      = string
        is_enabled          = bool
        retention_duration  = string
        defined_tags        = map
      }
}
```
<br>

- **Example**
```
// Copyright (c) 2021, 2022, Oracle and/or its affiliates.
########################################################
# ManagementServices
# LOADBALANCER Logs - tfvars
# Allowed Values:
# compartment_id can be the ocid or the name of the compartment hierarchy delimited by double hiphens "--"
# Example : compartment_id = "ocid1.compartment.oc1..aaaaaaaahwwiefb56epvdlzfic6ah6jy3xf3c" or compartment_id = "Network-root-cpt--Network" where "Network-root-cpt" is the parent of "Network" compartment
############################
loadbalancer_logs = {
  # Log map #
    my_lbr1-log-access  = {
        display_name        = "my_lbr1_access-log"
        log_group_id        = "my_lbr1-log-group"
        log_type            = "SERVICE"
        category            = "access"
        resource            = "my_lbr1"
        service             = "loadbalancer"
        source_type         = "OCISERVICE"
        compartment_id      = "Networkt"
        is_enabled          = true
        retention_duration  = 30
        defined_tags = {
                "Operations.CostCenter"= "01" ,
                "Users.Name"= "user01"
        }
      },
    my_lbr1-log-error  = {
        display_name        = "my_lbr1_error-log"
        log_group_id        = "my_lbr1-log-group"
        log_type            = "SERVICE"
        category            = "error"
        resource            = "my_lbr1"
        service             = "loadbalancer"
        source_type         = "OCISERVICE"
        compartment_id      = "Network"
        is_enabled          = true
        retention_duration  = 30
        defined_tags = {
                "Operations.CostCenter"= "01" ,
                "Users.Name"= "user01"
        }
      },
##Add New Logs for london here##
}
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
    my_lbr1-log-group = {
        compartment_id = "Network"
        display_name   = "my_lbr1-log-group"
        description    = "Log Group for my_lbr1"
        defined_tags = {
                "Operations.CostCenter"= "01" ,
                "Users.Name"= "user01"
        }
      }
```

<br>
<br>


**3. Object Storage logs and log groups**

<br>

- **Syntax for Object Storage logs**

```
oss_logs = {
  # Log map #
   ## key - Is a unique value to reference the resources respectively
   key  = {
        display_name        =  string
        log_group_id        =  string
        log_type            =  string
        category            =  string
        resource            =  string
        service             =  string
        source_type         =  string
        compartment_id      =  string
        is_enabled          =  bool
        retention_duration  =  string
      }
```

<br>

- **Example**


```
# ManagementServices
# OSS Logs - tfvars
# Allowed Values:
# compartment_id can be the ocid or the name of the compartment hierarchy delimited by double hiphens "--"
# Example : compartment_id = "ocid1.compartment.oc1..aaaaaaaahwwiefb56epvdlzfic6ah6jy3xf3c" or compartment_id = "Network-root-cpt--Network" where "Network-root-cpt" is the parent of "Network" compartment
############################
oss_logs = {
  # Log map #
  cd3bucket-write-log  = {
        display_name        = "cd3bucket-write-log"
        log_group_id        = "cd3bucket-bucket-log-group"
        log_type            = "SERVICE"
        category            = "write"
        resource            = "cd3bucket"
        service             = "objectstorage"
        source_type         = "OCISERVICE"
        compartment_id      = "Security"
        is_enabled          = true
        retention_duration  = 30
      },
##Add New Logs for london here##
}
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
    cd3bucket-bucket-log-group = {
        compartment_id = "Security"
        display_name   = "cd3bucket-bucket-log-group"
        description    = "Log Group for OSS bucket"
      },
}
```
