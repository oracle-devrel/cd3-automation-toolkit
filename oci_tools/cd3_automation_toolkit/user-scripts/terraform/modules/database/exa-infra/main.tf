// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Resource Block - Database
# Create ExaInfra
############################

resource "oci_database_cloud_exadata_infrastructure" "exa_infra" {
  availability_domain = var.availability_domain
  compartment_id      = var.compartment_id
  display_name        = var.display_name
  shape               = var.shape

  #Optional
  compute_count = var.compute_count
  storage_count = var.storage_count

  #  customer_contacts {
  #    #Optional
  #    email = var.customer_contacts_email
  #  }
  #  maintenance_window {
  #    #Required
  #    preference = var.maintenance_window_preference
  #    #Optional
  #    days_of_week {
  #      #Required
  #      name = var.maintenance_window_days_of_week_name
  #    }
  #    hours_of_day       = var.maintenance_window_hours_of_day
  #    lead_time_in_weeks = var.maintenance_window_lead_time_in_weeks
  #    months {
  #      #Required
  #      name = var.maintenance_window_months_name
  #    }
  #    weeks_of_month = var.maintenance_window_weeks_of_month
  #  }

  defined_tags  = var.defined_tags
  freeform_tags = var.freeform_tags

}

