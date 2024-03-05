## auto.tfvars syntax for SDDC Module
These are the syntax and sample format for providing inputs to the modules via <b>*.auto.tfvars</b> files.
<b>"key"</b> must be unique to every resource that is created.Comments preceed with <b>##</b>.

## SDDC

- **Syntax**

```
sddcs = {
## key - Is a unique value to reference the resources respectively
      key =  {
          compartment_id                = string
          display_name                  = string
          availability_domain           = string
          is_hcx_enabled                = bool
          vmware_software_version       = string
          initial_sku                   = string
          initial_host_shape_name       = string
          management_datastore          = list
          workload_datastore            = list
          hcx_action                    = string
          initial_host_ocpu_count       = string
          esxi_hosts_count              = string
          instance_display_name_prefix  = string
          is_shielded_instance_enabled  = bool
          ssh_authorized_keys           = string
          network_compartment_id        = string
          vcn_name                      = string
          provisioning_subnet_id        = string
          nsx_edge_uplink1vlan_id       = string
          nsx_edge_uplink2vlan_id       = string
          nsx_edge_vtep_vlan_id         = string
          nsx_vtep_vlan_id              = string
          vmotion_vlan_id               = string
          vsan_vlan_id                  = string
          vsphere_vlan_id               = string
          hcx_vlan_id                   = string
          replication_vlan_id           = string
          provisioning_vlan_id          = string
          workload_network_cidr         = string
          defined_tags                  = map
         }           
    }
```
<br>

- **Example**

```
// Copyright (c) 2021, 2022, Oracle and/or its affiliates.
############################
# SDDCs
# SDDC - tfvars
# Allowed Values:
# vcn_name must be the name of the VCN as in OCI
# vlan_name must be the name of the vlan as in OCI
# subnet_id can be the ocid of the subnet or the name as in OCI
# compartment_id and network_compartment_id can be the ocid or the name of the compartment hierarchy delimited by double hiphens "--"
# Example : compartment_id = "ocid1.compartment.oc1..aaaaaaaahwwiefb56epvdlzfic6ah6jy3xf3c" or compartment_id = "AppDev--Prod" where "AppDev" is the parent of "Prod" compartment
# Sample import command for SDDC:
# terraform import "module.sddc[\"<<sddc terraform variable name>>\"].oci_ocvp_sddc.sddc" <<sddc ocid>>
############################
sddcs = {
      sddc-std =  {
          compartment_id                = "AppDev"
          display_name                  = "sddc-std"
          availability_domain           =  0
          is_hcx_enabled                = "true"
          vmware_software_version       = "7.0 update 3"
          initial_sku                   = "HOUR"
          initial_host_shape_name       = "BM.Standard.E4.128"
          management_datastore          = ["AppDev@vMGMT_LUN"]
          workload_datastore            = ["AppDev@workload_vol1","AppDev@workload_vol2"]
          hcx_action                    = "UPGRADE"
          initial_host_ocpu_count       = "32"
          esxi_hosts_count              = 3
          instance_display_name_prefix  = "sddc-std2"
          is_shielded_instance_enabled  = "false"
          ssh_authorized_keys           = "sddc-std"
          network_compartment_id        = "Network"
          vcn_name                      = "vcn-sddc"
          provisioning_subnet_id        = "Subnet-sddc"
          nsx_edge_uplink1vlan_id       = "VLAN-sddc-std2-NSX Edge Uplink 1"
          nsx_edge_uplink2vlan_id       = "VLAN-sddc-std2-NSX Edge Uplink 2"
          nsx_edge_vtep_vlan_id         = "VLAN-sddc-std2-NSX Edge VTEP"
          nsx_vtep_vlan_id              = "VLAN-sddc-std2-NSX VTEP"
          vmotion_vlan_id               = "VLAN-sddc-std2-vMotion"
          vsan_vlan_id                  = "VLAN-sddc-std2-vSAN"
          vsphere_vlan_id               = "VLAN-sddc-std2-vSphere"
          hcx_vlan_id                   = "VLAN-sddc-std2-HCX"
          replication_vlan_id           = "VLAN-sddc-std2-Replication Net"
          provisioning_vlan_id          = "VLAN-sddc-std2-Provisioning Net"
          workload_network_cidr         = ""
            defined_tags = {
                    "Oracle-Tags.CreatedOn"= "2023-06-05T16:57:49.375Z" ,
                    "Oracle-Tags.CreatedBy"= "oracleidentitycloudservice/abc@oracle.com" ,
            }
    },
   
}
```
