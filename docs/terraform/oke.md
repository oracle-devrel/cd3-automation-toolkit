# auto.tfvars syntax for OKE Module
These are the syntax and sample format for providing inputs to the modules via <b>*.auto.tfvars</b> files.
<b>"key"</b> must be unique to every resource that is created.Comments preceed with <b>##</b>.


**1. Clusters**

- <b>Syntax</b>

```
  clusters = {
      ## key - Is a unique value to reference the resources respectively
      key = {
        display_name = string
        compartment_id = string
        network_compartment_id = string
        vcn_name = string
        kubernetes_version = string
        cni_type = string
        is_kubernetes_dashboard_enabled = optional(bool)
        is_tiller_enabled = optional(bool)
        is_public_ip_enabled = optional(bool)
        nsg_ids = optional(list(string))
        endpoint_subnet_id = string
        is_pod_security_policy_enabled = optional(bool)
        pods_cidr = optional(string)
        services_cidr = optional(string)
        service_lb_subnet_ids = optional(list(string))
        defined_tags = optional(map(any))
        freeform_tags = optional(map(any))
      }
  }
```

- <b>Example</b>
```
    // Copyright (c) 2021, 2022, Oracle and/or its affiliates.
    ############################
    # Developer Services
    # OKE Cluster - tfvars
    ############################
    clusters = {
      key = {
        display_name = "phn_cluster_dev"
        compartment_id = "App-Dev"
        network_compartment_id = "App-Network"
        vcn_name = "vcn-oke"
        kubernetes_version = "v1.24.0"
        cni_type = "OCI_VCN_IP_NATIVE"
        is_kubernetes_dashboard_enabled = false
        is_tiller_enabled = false
        is_public_ip_enabled = false
        nsg_ids = ["app-network-nsg-cp","app-network-nsg-lb"]
        endpoint_subnet_id = "endpoint-sn"
        is_pod_security_policy_enabled = true
        pods_cidr = "10.24.0.0/16"
        services_cidr = "10.10.0.0/16"
        service_lb_subnet_ids = ["loadbalancer-sn"]
        defined_tags = {
             Oracle-Tags.CreatedOn=2022-12-07T11:37:21.641Z,
             Oracle-Tags.CreatedBy=oracleidentitycloudservice/user.name@oracle.com
             }
        freeform_tags = {
             Department="Finance",
             CostCentre="xx1234"
             }
      },
  ##Add New Cluster for phoenix here##
  }
```

**2. Nodepools**

- <b>Syntax</b>

```
  nodepools = {
      ## key - Is a unique value to reference the resources respectively
      key = {
        display_name = string
        cluster_name = string
        compartment_id = string
        network_compartment_id = string
        vcn_name = string
        node_shape = string
        initial_node_labels = optional(map(any))
        kubernetes_version = string
        is_pv_encryption_in_transit_enabled = optional(bool)
        availability_domain = number
        subnet_id = string
        size = number
        cni_type = string
        max_pods_per_node = optional(number)
        pod_nsg_ids = optional(list(string))
        pod_subnet_ids = optional(string)
        worker_nsg_ids = optional(list(string))
        memory_in_gbs = optional(number)
        ocpus = optional(number)
        image_id = string
        source_type = string
        boot_volume_size_in_gbs = optional(number)
        ssh_public_key = optional(string)
        node_defined_tags = optional(map(any))
        node_freeform_tags = optional(map(any))
        nodepool_defined_tags = optional(map(any))
        nodepool_freeform_tags = optional(map(any))
      },
  }
```

- <b>Example</b>
```
    // Copyright (c) 2021, 2022, Oracle and/or its affiliates.
    ############################
    # Developer Services
    # OKE Nodepool - tfvars
    ############################
    nodepools = {
      key = {
        display_name = "nodepool1"
        cluster_name = "cluster2"
        compartment_id = "AppDev"
        network_compartment_id = "Network"
        vcn_name = "prod-vcn"
        node_shape = "VM.Standard.E3.Flex"
        initial_node_labels = {
                label = "node1"
        }
        kubernetes_version = "v1.24.1"
        availability_domain = 2
        subnet_id = "prod-app"
        size = 1
        cni_type = "OCI_VCN_IP_NATIVE"
        max_pods_per_node = 31
        pod_subnet_ids = "prod-app"
        worker_nsg_ids = ["prod-vcn-app-nsg"]
        memory_in_gbs = 32
        ocpus = 1
        image_id = "Oracle-Linux-8-6-2022-10-04-0-OKE-1-24-1-491"
        source_type = "IMAGE"
        boot_volume_size_in_gbs = 64
        nodepool_defined_tags = {
                "Oracle-Tags.CreatedOn"= "2023-01-10T04:29:33.383Z" ,
                "Oracle-Tags.CreatedBy"= "oracleidentitycloudservice/suruchi.singla@oracle.com"
        }
    },  ##Add New nodepool for phoenix here##
  }
```