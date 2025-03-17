# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################################
# Module Block - MySQL Database
# Create MySQL DB Systems
############################################

data "oci_mysql_mysql_configurations" "mysql_configurations" {
  # depends_on = [module.mysql-configuration]
  for_each       = var.mysql_db_system != null ? var.mysql_db_system : {}
  compartment_id = each.value.configuration_compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.configuration_compartment_id)) > 0 ? each.value.configuration_compartment_id : var.compartment_ocids[each.value.configuration_compartment_id]) : var.compartment_ocids[each.value.configurations_compartment_id]
  display_name   = each.value.configuration_id
  state          = "ACTIVE"
}

data "oci_core_subnets" "oci_mysql_subnets" {
  # depends_on = [module.subnets] # Uncomment to create Network and MySQL together
  for_each       = var.mysql_db_system != null ? var.mysql_db_system : {}
  compartment_id = each.value.network_compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.network_compartment_id)) > 0 ? each.value.network_compartment_id : var.compartment_ocids[each.value.network_compartment_id]) : var.compartment_ocids[each.value.network_compartment_id]
  display_name   = each.value.subnet_id
  vcn_id         = data.oci_core_vcns.oci_mysql_vcns[each.key].virtual_networks.*.id[0]
}

data "oci_core_vcns" "oci_mysql_vcns" {
  # depends_on = [module.vcns] # Uncomment to create Network and MySQL together
  for_each       = var.mysql_db_system != null ? var.mysql_db_system : {}
  compartment_id = each.value.network_compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.network_compartment_id)) > 0 ? each.value.network_compartment_id : var.compartment_ocids[each.value.network_compartment_id]) : var.compartment_ocids[each.value.network_compartment_id]
  display_name   = each.value.vcn_names
}


module "mysql_db_system" {

  source   = "./modules/database/mysql-dbsystem"
  for_each = var.mysql_db_system != null ? var.mysql_db_system : {}

  compartment_id                             = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
  network_compartment_id                     = each.value.network_compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.network_compartment_id)) > 0 ? each.value.network_compartment_id : var.compartment_ocids[each.value.network_compartment_id]) : null
  configuration_compartment_id               = each.value.configuration_compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.configuration_compartment_id)) > 0 ? each.value.configuration_compartment_id : var.compartment_ocids[each.value.configuration_compartment_id]) : var.compartment_ocids[each.value.compartment_id]
  configuration_id                           = length(regexall("ocid1.mysqlconfiguration.*", each.value.configuration_id)) > 0 ? each.value.configuration_id : data.oci_mysql_mysql_configurations.mysql_configurations[each.key].configurations[0].id
  display_name                               = each.value.mysql_db_system_display_name
  shape_name                                 = each.value.mysql_shape_name
  admin_username                             = each.value.mysql_db_system_admin_username
  admin_password                             = each.value.mysql_db_system_admin_password
  availability_domain                        = each.value.mysql_db_system_availability_domain != "" && each.value.mysql_db_system_availability_domain != null ? data.oci_identity_availability_domains.availability_domains.availability_domains[each.value.mysql_db_system_availability_domain].name : ""
  vcn_names                                  = [each.value.vcn_names]
  subnet_id                                  = each.value.subnet_id != "" ? (length(regexall("ocid1.subnet.oc*", each.value.subnet_id)) > 0 ? each.value.subnet_id : data.oci_core_subnets.oci_mysql_subnets[each.key].subnets.*.id[0]) : null
  hostname_label                             = each.value.mysql_db_system_hostname_label
  backup_id                                  = each.value.backup_id
  backup_policy_is_enabled                   = each.value.mysql_db_system_backup_policy_is_enabled
  backup_policy_retention_in_days            = each.value.mysql_db_system_backup_policy_retention_in_days
  backup_policy_window_start_time            = each.value.mysql_db_system_backup_policy_window_start_time
  crash_recovery                             = each.value.mysql_db_system_crash_recovery
  data_storage_size_in_gb                    = each.value.mysql_db_system_data_storage_size_in_gb
  database_management                        = each.value.mysql_db_system_database_management
  deletion_policy_automatic_backup_retention = each.value.mysql_db_system_deletion_policy_automatic_backup_retention
  deletion_policy_final_backup               = each.value.mysql_db_system_deletion_policy_final_backup
  deletion_policy_is_delete_protected        = each.value.mysql_db_system_deletion_policy_is_delete_protected
  description                                = each.value.mysql_db_system_description
  fault_domain                               = each.value.mysql_db_system_fault_domain
  ip_address                                 = each.value.mysql_db_system_ip_address
  is_highly_available                        = each.value.mysql_db_system_is_highly_available
  maintenance_window_start_time              = each.value.mysql_db_system_maintenance_window_start_time
  pitr_policy_is_enabled                     = each.value.mysql_db_system_backup_policy_pitr_policy_is_enabled
  port                                       = each.value.mysql_db_system_port
  port_x                                     = each.value.mysql_db_system_port_x
  source_type                                = each.value.mysql_db_system_source_source_type != null ? each.value.mysql_db_system_source_source_type : null
  defined_tags                               = each.value.defined_tags != null ? each.value.defined_tags : null
  freeform_tags = each.value.freeform_tags != null ? each.value.freeform_tags : null
}

############################################
# Module Block - MySQL Database
# Create MySQL Configurations
############################################

data "oci_mysql_shapes" "mysql_shapes" {
    for_each       = var.mysql_configuration != null ? var.mysql_configuration : {}
    compartment_id = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : var.compartment_ocids[each.value.compartment_id]
    name = each.value.mysql_configuration_shape_name
}

module "mysql_configuration" {

  source   = "./modules/database/mysql-configuration"
  for_each = var.mysql_configuration != null ? var.mysql_configuration : {}

  compartment_id                              = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
  mysql_configuration_shape_name = each.value.mysql_configuration_shape_name != null ? (length(regexall("(VM\\.Standard\\.(E[234]\\.[12468]|E[34]\\.(16|24|32|48|64))|MySQL\\.(VM\\.Standard\\.(E[34]\\.[12468]|E[34]\\.(16|24|32|48|64)\\.(8|16|32|64|128|256|384|512|768|1024)GB)|HeatWave\\.(BM\\.Standard(\\.E3)?|VM\\.Standard(\\.E3)?)|VM\\.Optimized3\\.[12468]\\.((8|16|32|64|128|256|384|512|768|1024)GB)|[12468]|16|32|48|64|256))", each.value.mysql_configuration_shape_name)) > 0 ? each.value.mysql_configuration_shape_name : data.oci_mysql_shapes.mysql_shapes[each.key].shapes.*.name[0]) : null
  defined_tags                                = each.value.defined_tags
  mysql_configuration_description             = each.value.mysql_configuration_description
  mysql_configuration_display_name            = each.value.mysql_configuration_display_name
  freeform_tags                               = each.value.freeform_tags
  mysql_configuration_init_variables_lower_case_table_names                 = each.value.mysql_configuration_init_variables_lower_case_table_names
  mysql_configuration_variables_autocommit                                  = each.value.mysql_configuration_variables_autocommit
  mysql_configuration_variables_big_tables                                  = each.value.mysql_configuration_variables_big_tables
  mysql_configuration_variables_binlog_expire_logs_seconds                  = each.value.mysql_configuration_variables_binlog_expire_logs_seconds
  mysql_configuration_variables_binlog_row_metadata                         = each.value.mysql_configuration_variables_binlog_row_metadata
  mysql_configuration_variables_binlog_row_value_options                    = each.value.mysql_configuration_variables_binlog_row_value_options
  mysql_configuration_variables_binlog_transaction_compression              = each.value.mysql_configuration_variables_binlog_transaction_compression
  mysql_configuration_variables_completion_type                             = each.value.mysql_configuration_variables_completion_type
  mysql_configuration_variables_connect_timeout                             = each.value.mysql_configuration_variables_connect_timeout
  mysql_configuration_variables_connection_memory_chunk_size                = each.value.mysql_configuration_variables_connection_memory_chunk_size
  mysql_configuration_variables_connection_memory_limit                     = each.value.mysql_configuration_variables_connection_memory_limit
  mysql_configuration_variables_cte_max_recursion_depth                     = each.value.mysql_configuration_variables_cte_max_recursion_depth
  mysql_configuration_variables_default_authentication_plugin               = each.value.mysql_configuration_variables_default_authentication_plugin
  mysql_configuration_variables_foreign_key_checks                          = each.value.mysql_configuration_variables_foreign_key_checks
  mysql_configuration_variables_global_connection_memory_limit              = each.value.mysql_configuration_variables_global_connection_memory_limit
  mysql_configuration_variables_global_connection_memory_tracking           = each.value.mysql_configuration_variables_global_connection_memory_tracking
  mysql_configuration_variables_group_replication_consistency               = each.value.mysql_configuration_variables_group_replication_consistency
  mysql_configuration_variables_information_schema_stats_expiry             = each.value.mysql_configuration_variables_information_schema_stats_expiry
  mysql_configuration_variables_innodb_buffer_pool_dump_pct                 = each.value.mysql_configuration_variables_innodb_buffer_pool_dump_pct
  mysql_configuration_variables_innodb_buffer_pool_instances                = each.value.mysql_configuration_variables_innodb_buffer_pool_instances
  mysql_configuration_variables_innodb_buffer_pool_size                     = each.value.mysql_configuration_variables_innodb_buffer_pool_size
  mysql_configuration_variables_innodb_ddl_buffer_size                      = each.value.mysql_configuration_variables_innodb_ddl_buffer_size
  mysql_configuration_variables_innodb_ddl_threads                          = each.value.mysql_configuration_variables_innodb_ddl_threads
  mysql_configuration_variables_innodb_ft_enable_stopword                   = each.value.mysql_configuration_variables_innodb_ft_enable_stopword
  mysql_configuration_variables_innodb_ft_max_token_size                    = each.value.mysql_configuration_variables_innodb_ft_max_token_size
  mysql_configuration_variables_innodb_ft_min_token_size                    = each.value.mysql_configuration_variables_innodb_ft_min_token_size
  mysql_configuration_variables_innodb_ft_num_word_optimize                 = each.value.mysql_configuration_variables_innodb_ft_num_word_optimize
  mysql_configuration_variables_innodb_ft_result_cache_limit                = each.value.mysql_configuration_variables_innodb_ft_result_cache_limit
  mysql_configuration_variables_innodb_ft_server_stopword_table             = each.value.mysql_configuration_variables_innodb_ft_server_stopword_table
  mysql_configuration_variables_innodb_lock_wait_timeout                    = each.value.mysql_configuration_variables_innodb_lock_wait_timeout
  mysql_configuration_variables_innodb_log_writer_threads                   = each.value.mysql_configuration_variables_innodb_log_writer_threads
  mysql_configuration_variables_innodb_max_purge_lag                        = each.value.mysql_configuration_variables_innodb_max_purge_lag
  mysql_configuration_variables_innodb_max_purge_lag_delay                  = each.value.mysql_configuration_variables_innodb_max_purge_lag_delay
  mysql_configuration_variables_innodb_stats_persistent_sample_pages        = each.value.mysql_configuration_variables_innodb_stats_persistent_sample_pages
  mysql_configuration_variables_innodb_stats_transient_sample_pages         = each.value.mysql_configuration_variables_innodb_stats_transient_sample_pages
  mysql_configuration_variables_interactive_timeout                         = each.value.mysql_configuration_variables_interactive_timeout
  mysql_configuration_variables_local_infile                                = each.value.mysql_configuration_variables_local_infile
  mysql_configuration_variables_mandatory_roles                             = each.value.mysql_configuration_variables_mandatory_roles
  mysql_configuration_variables_max_allowed_packet                          = each.value.mysql_configuration_variables_max_allowed_packet
  mysql_configuration_variables_max_binlog_cache_size                       = each.value.mysql_configuration_variables_max_binlog_cache_size
  mysql_configuration_variables_max_connect_errors                          = each.value.mysql_configuration_variables_max_connect_errors
  mysql_configuration_variables_max_connections                             = each.value.mysql_configuration_variables_max_connections
  mysql_configuration_variables_max_execution_time                          = each.value.mysql_configuration_variables_max_execution_time
  mysql_configuration_variables_max_heap_table_size                         = each.value.mysql_configuration_variables_max_heap_table_size
  mysql_configuration_variables_max_prepared_stmt_count                     = each.value.mysql_configuration_variables_max_prepared_stmt_count
  mysql_configuration_variables_mysql_firewall_mode                         = each.value.mysql_configuration_variables_mysql_firewall_mode
  mysql_configuration_variables_mysqlx_connect_timeout                      = each.value.mysql_configuration_variables_mysqlx_connect_timeout
  mysql_configuration_variables_mysqlx_deflate_default_compression_level    = each.value.mysql_configuration_variables_mysqlx_deflate_default_compression_level
  mysql_configuration_variables_mysqlx_deflate_max_client_compression_level = each.value.mysql_configuration_variables_mysqlx_deflate_max_client_compression_level
  mysql_configuration_variables_mysqlx_enable_hello_notice                  = each.value.mysql_configuration_variables_mysqlx_enable_hello_notice
  mysql_configuration_variables_mysqlx_interactive_timeout                  = each.value.mysql_configuration_variables_mysqlx_interactive_timeout
  mysql_configuration_variables_mysqlx_lz4default_compression_level         = each.value.mysql_configuration_variables_mysqlx_lz4default_compression_level
  mysql_configuration_variables_mysqlx_lz4max_client_compression_level      = each.value.mysql_configuration_variables_mysqlx_lz4max_client_compression_level
  mysql_configuration_variables_mysqlx_max_allowed_packet                   = each.value.mysql_configuration_variables_mysqlx_max_allowed_packet
  mysql_configuration_variables_mysqlx_read_timeout                         = each.value.mysql_configuration_variables_mysqlx_read_timeout
  mysql_configuration_variables_mysqlx_wait_timeout                         = each.value.mysql_configuration_variables_mysqlx_wait_timeout
  mysql_configuration_variables_mysqlx_write_timeout                        = each.value.mysql_configuration_variables_mysqlx_write_timeout
  mysql_configuration_variables_mysqlx_zstd_default_compression_level       = each.value.mysql_configuration_variables_mysqlx_zstd_default_compression_level
  mysql_configuration_variables_mysqlx_zstd_max_client_compression_level    = each.value.mysql_configuration_variables_mysqlx_zstd_max_client_compression_level
  mysql_configuration_variables_net_read_timeout                            = each.value.mysql_configuration_variables_net_read_timeout
  mysql_configuration_variables_net_write_timeout                           = each.value.mysql_configuration_variables_net_write_timeout
  mysql_configuration_variables_parser_max_mem_size                         = each.value.mysql_configuration_variables_parser_max_mem_size
  mysql_configuration_variables_regexp_time_limit                           = each.value.mysql_configuration_variables_regexp_time_limit
  mysql_configuration_variables_sort_buffer_size                            = each.value.mysql_configuration_variables_sort_buffer_size
  mysql_configuration_variables_sql_mode                                    = each.value.mysql_configuration_variables_sql_mode
  mysql_configuration_variables_sql_require_primary_key                     = each.value.mysql_configuration_variables_sql_require_primary_key
  mysql_configuration_variables_sql_warnings                                = each.value.mysql_configuration_variables_sql_warnings
  mysql_configuration_variables_thread_pool_dedicated_listeners             = each.value.mysql_configuration_variables_thread_pool_dedicated_listeners
  mysql_configuration_variables_thread_pool_max_transactions_limit          = each.value.mysql_configuration_variables_thread_pool_max_transactions_limit
  mysql_configuration_variables_time_zone                                   = each.value.mysql_configuration_variables_time_zone
  mysql_configuration_variables_tmp_table_size                              = each.value.mysql_configuration_variables_tmp_table_size
  mysql_configuration_variables_transaction_isolation                       = each.value.mysql_configuration_variables_transaction_isolation
  mysql_configuration_variables_wait_timeout                                = each.value.mysql_configuration_variables_wait_timeout

}