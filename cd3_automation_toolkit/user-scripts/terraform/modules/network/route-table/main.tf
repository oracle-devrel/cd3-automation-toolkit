# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Resource Block - Network
# Create Route Table
############################

# Data Source for Service Gateway
data "oci_core_services" "oci_services" {
}

resource "oci_core_route_table" "route_table" {

count = var.default_route_table ==true ? 0 : 1

  #Required
  compartment_id = var.compartment_id
  vcn_id         = var.vcn_id

  #Optional
  defined_tags  = var.defined_tags
  display_name  = var.display_name
  freeform_tags = var.freeform_tags

  # Create Private IP Routes
  dynamic "route_rules" {
    for_each = var.rt_details[var.key_name].route_rules_ip != [] ? var.rt_details[var.key_name].route_rules_ip : []

    content {
      #Required
      network_entity_id = (route_rules.value["network_entity_id"] != null && length(regexall("ocid1.privateip.oc*", route_rules.value["network_entity_id"])) > 0) ? route_rules.value["network_entity_id"] : ""

      #Optional
      description      = route_rules.value["description"] != "" ? route_rules.value["description"] : null
      destination      = route_rules.value["destination"]
      destination_type = route_rules.value["destination_type"]
    }
  }

  # Create LPG Routes
  dynamic "route_rules" {
    for_each = var.gateway_route_table == false ? (var.rt_details[var.key_name].route_rules_lpg != [] ? var.rt_details[var.key_name].route_rules_lpg : [] ) : []

    content {
      #Required
      network_entity_id = (route_rules.value["network_entity_id"] != null && length(regexall("ocid1.localpeeringgateway.oc*", route_rules.value["network_entity_id"])) > 0) ? route_rules.value["network_entity_id"] : try(var.hub_lpg_id[route_rules.value["network_entity_id"]]["lpg_tf_id"], var.spoke_lpg_id[route_rules.value["network_entity_id"]]["lpg_tf_id"], var.peer_lpg_id[route_rules.value["network_entity_id"]]["lpg_tf_id"], var.none_lpg_id[route_rules.value["network_entity_id"]]["lpg_tf_id"], var.exported_lpg_id[route_rules.value["network_entity_id"]]["lpg_tf_id"], var.drg_id[route_rules.value["network_entity_id"]]["drg_tf_id"])

      #Optional
      description      = route_rules.value["description"] != "" ? route_rules.value["description"] : null
      destination      = route_rules.value["destination"]
      destination_type = route_rules.value["destination_type"]
    }
  }

  # Create IGW Routes
  dynamic "route_rules" {
    for_each = var.gateway_route_table == false ? (var.rt_details[var.key_name].route_rules_igw != [] ? var.rt_details[var.key_name].route_rules_igw : []) : []

    content {
      #Required
      network_entity_id = (route_rules.value["network_entity_id"] != null && length(regexall("ocid1.internetgateway.oc*", route_rules.value["network_entity_id"])) > 0) ? route_rules.value["network_entity_id"] : var.igw_id[route_rules.value["network_entity_id"]]["igw_tf_id"]

      #Optional
      description      = route_rules.value["description"] != "" ? route_rules.value["description"] : null
      destination      = route_rules.value["destination"]
      destination_type = route_rules.value["destination_type"]
    }
  }

  # Create DRG Routes
  dynamic "route_rules" {
    for_each = var.rt_details[var.key_name].route_rules_drg != [] ? var.rt_details[var.key_name].route_rules_drg : []

    content {
      #Required
      network_entity_id = (route_rules.value["network_entity_id"] != null && length(regexall("ocid1.drg.oc*", route_rules.value["network_entity_id"])) > 0) ? route_rules.value["network_entity_id"] : var.drg_id[route_rules.value["network_entity_id"]]["drg_tf_id"]


      #length(regexall("ocid1.drg.oc*", route_rules.value["network_entity_id"])) > 0 ? route_rules.value["network_entity_id"] : null

      #Optional
      description      = route_rules.value["description"] != "" ? route_rules.value["description"] : null
      destination      = route_rules.value["destination"]
      destination_type = route_rules.value["destination_type"]
    }
  }

  # Create NAT Routes
  dynamic "route_rules" {
    for_each = var.gateway_route_table == false ?  (var.rt_details[var.key_name].route_rules_ngw != [] ? var.rt_details[var.key_name].route_rules_ngw : []) : []

    content {
      #Required
      network_entity_id = (route_rules.value["network_entity_id"] != null && length(regexall("ocid1.natgateway.oc*", route_rules.value["network_entity_id"])) > 0) ? route_rules.value["network_entity_id"] : var.ngw_id[route_rules.value["network_entity_id"]]["ngw_tf_id"]


      #length(regexall("ocid1.drg.oc*", route_rules.value["network_entity_id"])) > 0 ? route_rules.value["network_entity_id"] : null`

      #Optional
      description      = route_rules.value["description"] != "" ? route_rules.value["description"] : null
      destination      = route_rules.value["destination"]
      destination_type = route_rules.value["destination_type"]
    }
  }

  # Create SGW Routes
  dynamic "route_rules" {
    for_each = var.gateway_route_table == false ?  (var.rt_details[var.key_name].route_rules_sgw != [] ? var.rt_details[var.key_name].route_rules_sgw : [] ) : []

    content {
      #Required
      network_entity_id = (route_rules.value["network_entity_id"] != null && length(regexall("ocid1.servicegateway.oc*", route_rules.value["network_entity_id"])) > 0) ? route_rules.value["network_entity_id"] : var.sgw_id[route_rules.value["network_entity_id"]]["sgw_tf_id"]


      #length(regexall("ocid1.drg.oc*", route_rules.value["network_entity_id"])) > 0 ? route_rules.value["network_entity_id"] : null

      #Optional
      description      = route_rules.value["description"] != "" ? route_rules.value["description"] : null
      destination      = contains(split("-", route_rules.value["destination"]), "all") == true ? (contains(split("-", data.oci_core_services.oci_services.services.0.cidr_block), "all") == true ? data.oci_core_services.oci_services.services.0.cidr_block : data.oci_core_services.oci_services.services.1.cidr_block) : (contains(split("-", data.oci_core_services.oci_services.services.0.cidr_block), "objectstorage") == true ? data.oci_core_services.oci_services.services.0.cidr_block : data.oci_core_services.oci_services.services.1.cidr_block)
      destination_type = route_rules.value["destination_type"]
    }
  }

  lifecycle {
    create_before_destroy = true
  }

}



resource "oci_core_default_route_table" "default_route_table" {

 count = var.default_route_table ==true ? 1 : 0
  #Required
  manage_default_resource_id = var.manage_default_resource_id

  #Optional
  defined_tags  = var.defined_tags
  display_name  = var.display_name
  freeform_tags = var.freeform_tags

  # Create Private IP Routes
  dynamic "route_rules" {
    for_each = var.rt_details[var.key_name].route_rules_ip != [] ? var.rt_details[var.key_name].route_rules_ip : []

    content {
      #Required
      network_entity_id = (route_rules.value["network_entity_id"] != null && length(regexall("ocid1.privateip.oc*", route_rules.value["network_entity_id"])) > 0) ? route_rules.value["network_entity_id"] : ""

      #Optional
      description      = route_rules.value["description"]
      destination      = route_rules.value["destination"]
      destination_type = route_rules.value["destination_type"]
    }
  }

  # Create LPG Routes
  dynamic "route_rules" {
    for_each = var.gateway_route_table == false ? (var.rt_details[var.key_name].route_rules_lpg != [] ? var.rt_details[var.key_name].route_rules_lpg : []): []

    content {
      #Required
      network_entity_id = (route_rules.value["network_entity_id"] != null && length(regexall("ocid1.localpeeringgateway.oc*", route_rules.value["network_entity_id"])) > 0) ? route_rules.value["network_entity_id"] : try(var.hub_lpg_id[route_rules.value["network_entity_id"]]["lpg_tf_id"], var.spoke_lpg_id[route_rules.value["network_entity_id"]]["lpg_tf_id"], var.exported_lpg_id[route_rules.value["network_entity_id"]]["lpg_tf_id"], var.drg_id[route_rules.value["network_entity_id"]]["drg_tf_id"])

      #Optional
      description      = route_rules.value["description"]
      destination      = route_rules.value["destination"]
      destination_type = route_rules.value["destination_type"]
    }
  }

  # Create IGW Routes
  dynamic "route_rules" {
    for_each = var.gateway_route_table == false ? (var.rt_details[var.key_name].route_rules_igw != [] ? var.rt_details[var.key_name].route_rules_igw : []) : []

    content {
      #Required
      network_entity_id = (route_rules.value["network_entity_id"] != null && length(regexall("ocid1.internetgateway.oc*", route_rules.value["network_entity_id"])) > 0) ? route_rules.value["network_entity_id"] : var.igw_id[route_rules.value["network_entity_id"]]["igw_tf_id"]

      #Optional
      description      = route_rules.value["description"]
      destination      = route_rules.value["destination"]
      destination_type = route_rules.value["destination_type"]
    }
  }

  # Create DRG Routes
  dynamic "route_rules" {
    for_each = var.rt_details[var.key_name].route_rules_drg != [] ? var.rt_details[var.key_name].route_rules_drg : []

    content {
      #Required
      network_entity_id = (route_rules.value["network_entity_id"] != null && length(regexall("ocid1.drg.oc*", route_rules.value["network_entity_id"])) > 0) ? route_rules.value["network_entity_id"] : var.drg_id[route_rules.value["network_entity_id"]]["drg_tf_id"]


      #length(regexall("ocid1.drg.oc*", route_rules.value["network_entity_id"])) > 0 ? route_rules.value["network_entity_id"] : null

      #Optional
      description      = route_rules.value["description"]
      destination      = route_rules.value["destination"]
      destination_type = route_rules.value["destination_type"]
    }
  }

  # Create NAT Routes
  dynamic "route_rules" {
    for_each = var.gateway_route_table == false ? (var.rt_details[var.key_name].route_rules_ngw != [] ? var.rt_details[var.key_name].route_rules_ngw : []) :[]

    content {
      #Required
      network_entity_id = (route_rules.value["network_entity_id"] != null && length(regexall("ocid1.natgateway.oc*", route_rules.value["network_entity_id"])) > 0) ? route_rules.value["network_entity_id"] : var.ngw_id[route_rules.value["network_entity_id"]]["ngw_tf_id"]


      #length(regexall("ocid1.drg.oc*", route_rules.value["network_entity_id"])) > 0 ? route_rules.value["network_entity_id"] : null

      #Optional
      description      = route_rules.value["description"]
      destination      = route_rules.value["destination"]
      destination_type = route_rules.value["destination_type"]
    }
  }

  # Create SGW Routes
  dynamic "route_rules" {
    for_each = var.gateway_route_table == false ? (var.rt_details[var.key_name].route_rules_sgw != [] ? var.rt_details[var.key_name].route_rules_sgw : []) :[]

    content {
      #Required
      network_entity_id = (route_rules.value["network_entity_id"] != null && length(regexall("ocid1.servicegateway.oc*", route_rules.value["network_entity_id"])) > 0) ? route_rules.value["network_entity_id"] : var.sgw_id[route_rules.value["network_entity_id"]]["sgw_tf_id"]


      #length(regexall("ocid1.drg.oc*", route_rules.value["network_entity_id"])) > 0 ? route_rules.value["network_entity_id"] : null

      #Optional
      description      = route_rules.value["description"]
      destination      = contains(split("-", route_rules.value["destination"]), "all") == true ? (contains(split("-", data.oci_core_services.oci_services.services.0.cidr_block), "all") == true ? data.oci_core_services.oci_services.services.0.cidr_block : data.oci_core_services.oci_services.services.1.cidr_block) : (contains(split("-", data.oci_core_services.oci_services.services.0.cidr_block), "objectstorage") == true ? data.oci_core_services.oci_services.services.0.cidr_block : data.oci_core_services.oci_services.services.1.cidr_block)
      destination_type = route_rules.value["destination_type"]
    }
  }

  lifecycle {
    create_before_destroy = true
  }

}