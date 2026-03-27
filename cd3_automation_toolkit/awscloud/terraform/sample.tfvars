
# ==============================================================================
# MANDATORY: Exadata Infrastructures
# ==============================================================================
aws_oci_exa_infra = {
  # --- FIRST INFRASTRUCTURE: (Active) ---
  dev_infra = {
    # General & Placement
    environment          = "dev"
    region               = "us-west-2"
    availability_zone    = "us-west-2c"
    availability_zone_id = "usw2-az3"

    # Infrastructure Details
    # Allowed shapes: Exadata.X9M, Exadata.X10M, Exadata.X11M
    display_name         = "exadata-infra-dev"
    shape                = "Exadata.X11M"
    database_server_type = "X11M"
    storage_server_type  = "X11M-HC"
    compute_count        = 2 # Valid range: 2-32
    storage_count        = 3 # Valid range: 3-64

    # Support Contacts
    customer_contacts = [
      { email = "dba-team@example.com" },
      { email = "xyz@example.com" }
    ]

    # --- MAINTENANCE WINDOW ---
    maintenance_window = {
      # Patching Mode: "ROLLING" (one by one) or "NONROLLING" (all at once)
      patching_mode = "ROLLING"

      # Preference: "NO_PREFERENCE" (Oracle chooses) or "CUSTOM_PREFERENCE" (custom schedule)
      preference = "CUSTOM_PREFERENCE"

      is_custom_action_timeout_enabled = true
      custom_action_timeout_in_mins    = 30

      # Schedule Configuration (when preference = "CUSTOM_PREFERENCE")
      # Valid day names: MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY
      days_of_week = ["SUNDAY"]

      # Hours in UTC (0-23)
      hours_of_day = [2, 3]

      # Valid month names: JANUARY, FEBRUARY, MARCH, APRIL, MAY, JUNE,
      #                    JULY, AUGUST, SEPTEMBER, OCTOBER, NOVEMBER, DECEMBER
      months = ["JANUARY", "APRIL", "JULY", "OCTOBER"]

      # Weeks of month: 1=First week, 2=Second week, 3=Third week, 4=Fourth week
      weeks_of_month = [2]

      # Minimum notice before patching (in weeks)
      lead_time_in_weeks = 2
    }

    # Tags - Specific to this infrastructure
    tags = {
      Project     = "OracleDB-AWS"
      Owner       = "Database-Team"
      CostCenter  = "IT-Database"
      Environment = "Dev"
    }
  }

  # --- SECOND INFRASTRUCTURE: PRODUCTION (Example - Commented Out) ---
  /*
  prod_infra = {
    environment          = "prod"
    region               = "us-west-2"
    availability_zone    = "us-west-2a"
    availability_zone_id = "usw2-az1"
    display_name         = "exadata-infra-prod"
    shape                = "Exadata.X11M"
    compute_count        = 4
    storage_count        = 6
    database_server_type = "X11M"
    storage_server_type  = "X11M-HC"
    customer_contacts    = [{ email = "dba-prod@example.com" }]

    maintenance_window = {
      patching_mode = "ROLLING"
      preference    = "NO_PREFERENCE"
    }

    tags = {
      Project     = "OracleDB-AWS"
      Owner       = "Database-Team"
      CostCenter  = "IT-Database"
      Environment = "Production"
      Criticality = "High"
    }
  }
  */
}

aws_oci_exa_vmclusters = {
  # ════════════════════════════════════════════════════════════════════════
  # CLUSTER 1: Active Development Cluster
  # ════════════════════════════════════════════════════════════════════════
  dev_vm_cluster = {
    # MANDATORY: Existing Resource References
    exadata_infrastructure_name = "pds-infra-01"
    odb_network_name            = "pds-network-01"

    # MANDATORY: Configuration
    environment     = "dev"       # Allowed: dev, test, stage, prod
    region          = "us-west-2" # Must match infrastructure region
    display_name    = "PDS_DEV_CLUSTER"
    cluster_name    = "pdsdev"   # 1-11 alphanumeric characters. Must start with a letter.
    hostname_prefix = "pdsdev"   # Alphanumeric and hyphens only. Max 63 characters.
    gi_version      = "19.0.0.0" # Allowed: "19.0.0.0" or "23.0.0.0"

    # MANDATORY: Compute & Storage
    cpu_core_count              = 4   # Minimum 2 per node. Must be a multiple of 2.
    memory_size_in_gbs          = 60  # Minimum 30 GB per node.
    data_storage_size_in_tbs    = 2.0 # Minimum 2.0 TB.
    db_node_storage_size_in_gbs = 120 # Range: 120 GB to 1200 GB.
    ssh_public_keys             = ["ssh-rsa AAAAB3Nza... user@host"]

    # OPTIONAL: Configuration (With defaults)
    license_model          = "LICENSE_INCLUDED" # "LICENSE_INCLUDED" | "BRING_YOUR_OWN_LICENSE"
    timezone               = "UTC"              # Default: "UTC". Supports standard TZ database names.
    scan_listener_port_tcp = 1521               # Default: 1521. Allowed: 1024 to 8999.

    # IMMUTABLE: (Changing these triggers resource replacement)
    is_local_backup_enabled     = false
    is_sparse_diskgroup_enabled = false

    # OPTIONAL: Data Collection
    data_collection_options = {
      is_diagnostics_events_enabled = true
      is_health_monitoring_enabled  = true
      is_incident_logs_enabled      = true
    }

    # OPTIONAL: Timeouts
    timeout_create = "24h"
    timeout_update = "2h"
    timeout_delete = "8h"

    # Tags
    tags = {
      Project     = "PDS"
      Environment = "dev"
    }
  }

  # ════════════════════════════════════════════════════════════════════════
  # CLUSTER 2: Production Template (Uncomment to Deploy)
  # ════════════════════════════════════════════════════════════════════════
  # prod_vm_cluster = {
  #   exadata_infrastructure_name = "pds-infra-prod"
  #   odb_network_name            = "pds-network-prod"
  #   environment                 = "prod"
  #   region                      = "us-west-2"
  #   display_name                = "PDS_PROD_CLUSTER"
  #   cluster_name                = "pdsprod"
  #   hostname_prefix             = "pdsprod"
  #   gi_version                  = "19.0.0.0"
  #   cpu_core_count              = 8
  #   memory_size_in_gbs          = 120
  #   data_storage_size_in_tbs    = 5.0
  #   db_node_storage_size_in_gbs = 250
  #   ssh_public_keys             = ["ssh-rsa AAAAB3Nza... admin@corp"]
  #   license_model               = "BRING_YOUR_OWN_LICENSE"
  #   timezone                    = "America/New_York"
  #   scan_listener_port_tcp      = 1521
  #   is_local_backup_enabled     = true
  #   is_sparse_diskgroup_enabled = false
  #   data_collection_options = {
  #     is_diagnostics_events_enabled = true
  #     is_health_monitoring_enabled  = true
  #     is_incident_logs_enabled      = true
  #   }
  #   timeout_create = "8h"
  #   timeout_update = "2h"
  #   timeout_delete = "2h"
  #   tags = {
  #     Project     = "PDS"
  #     Environment = "prod"
  #   }
  # }
}