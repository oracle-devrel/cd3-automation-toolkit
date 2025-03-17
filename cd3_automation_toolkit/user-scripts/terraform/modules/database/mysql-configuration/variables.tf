# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Variables Block - Database
# Create MySQL Configurations
############################

variable "defined_tags" {
  type = map(any)
  default = null
}

variable "freeform_tags" {
  type = map(any)
  default = null
}

variable "mysql_configuration_description" {
    type = string

    default = null
}

variable "compartment_id" {
    type = string
    default = null
}

variable "mysql_configuration_shape_name" {
    type = string
    default = null

}
variable "mysql_configuration_display_name" {
    type = string
    default = null

}
variable "mysql_configuration_init_variables_lower_case_table_names" {
    type = string
    default = null


}
variable "mysql_configuration_variables_autocommit" {
    type = string
default = null

}
variable "mysql_configuration_variables_big_tables" {
    type = string
default = null

}
variable "mysql_configuration_variables_binlog_expire_logs_seconds" {
    type = string
default = null

}
variable "mysql_configuration_variables_binlog_row_metadata" {
    type = string
default = null

}
variable "mysql_configuration_variables_binlog_row_value_options" {
    type = string
default = null

}
variable "mysql_configuration_variables_binlog_transaction_compression" {
    type = string
default = null

}
variable "mysql_configuration_variables_completion_type" {
    type = string
default = null

}
variable "mysql_configuration_variables_connect_timeout" {
    type = string
default = null

}
variable "mysql_configuration_variables_connection_memory_chunk_size" {
    type = string
default = null

}
variable "mysql_configuration_variables_connection_memory_limit" {
    type = string
default = null

}
variable "mysql_configuration_variables_cte_max_recursion_depth" {
    type = string
default = null

}
variable "mysql_configuration_variables_default_authentication_plugin" {
    type = string
default = null

}
variable "mysql_configuration_variables_foreign_key_checks" {
    type = string
default = null

}
variable "mysql_configuration_variables_global_connection_memory_limit" {
    type = string
default = null

}
variable "mysql_configuration_variables_global_connection_memory_tracking" {
    type = string
default = null

}
variable "mysql_configuration_variables_group_replication_consistency" {
    type = string
default = null

}
variable "mysql_configuration_variables_information_schema_stats_expiry" {
    type = string
default = null

}
variable "mysql_configuration_variables_innodb_buffer_pool_dump_pct" {
    type = string
default = null

}
variable "mysql_configuration_variables_innodb_buffer_pool_instances" {
    type = string
default = null

}
variable "mysql_configuration_variables_innodb_buffer_pool_size" {
    type = string
default = null

}
variable "mysql_configuration_variables_innodb_ddl_buffer_size" {
    type = string
default = null

}
variable "mysql_configuration_variables_innodb_ddl_threads" {
    type = string
default = null

}
variable "mysql_configuration_variables_innodb_ft_enable_stopword" {
    type = string
default = null

}
variable "mysql_configuration_variables_innodb_ft_max_token_size" {
    type = string
default = null

}
variable "mysql_configuration_variables_innodb_ft_min_token_size" {
    type = string
default = null

}
variable "mysql_configuration_variables_innodb_ft_num_word_optimize" {
    type = string
default = null

}
variable "mysql_configuration_variables_innodb_ft_result_cache_limit" {
    type = string
default = null

}
variable "mysql_configuration_variables_innodb_ft_server_stopword_table" {
    type = string
default = null

}
variable "mysql_configuration_variables_innodb_lock_wait_timeout" {
    type = string
default = null

}
variable "mysql_configuration_variables_innodb_log_writer_threads" {
    type = string
default = null

}
variable "mysql_configuration_variables_innodb_max_purge_lag" {
    type = string
default = null

}
variable "mysql_configuration_variables_innodb_max_purge_lag_delay" {
    type = string
default = null

}
variable "mysql_configuration_variables_innodb_stats_persistent_sample_pages" {
    type = string
default = null

}
variable "mysql_configuration_variables_innodb_stats_transient_sample_pages" {
    type = string
default = null

}
variable "mysql_configuration_variables_interactive_timeout" {
    type = string
default = null

}
variable "mysql_configuration_variables_local_infile" {
    type = string
default = null

}
variable "mysql_configuration_variables_mandatory_roles" {
    type = string
default = null

}
variable "mysql_configuration_variables_max_allowed_packet" {
    type = string
default = null

}
variable "mysql_configuration_variables_max_binlog_cache_size" {
    type = string
default = null

}
variable "mysql_configuration_variables_max_connect_errors" {
    type = string
default = null

}
variable "mysql_configuration_variables_max_connections" {
    type = string
default = null

}
variable "mysql_configuration_variables_max_execution_time" {
    type = string
default = null

}
variable "mysql_configuration_variables_max_heap_table_size" {
    type = string
default = null

}
variable "mysql_configuration_variables_max_prepared_stmt_count" {
    type = string
default = null

}
variable "mysql_configuration_variables_mysql_firewall_mode" {
    type = string
default = null

}
variable "mysql_configuration_variables_mysqlx_connect_timeout" {
    type = string
default = null

}
variable "mysql_configuration_variables_mysqlx_deflate_default_compression_level" {
    type = string
default = null

}
variable "mysql_configuration_variables_mysqlx_deflate_max_client_compression_level" {
    type = string
default = null

}
variable "mysql_configuration_variables_mysqlx_enable_hello_notice" {
    type = string
default = null

}
variable "mysql_configuration_variables_mysqlx_interactive_timeout" {
    type = string
default = null

}
variable "mysql_configuration_variables_mysqlx_lz4default_compression_level" {
    type = string
default = null

}
variable "mysql_configuration_variables_mysqlx_lz4max_client_compression_level" {
    type = string
default = null

}
variable "mysql_configuration_variables_mysqlx_max_allowed_packet" {
    type = string
default = null

}
variable "mysql_configuration_variables_mysqlx_read_timeout" {
    type = string
default = null

}
variable "mysql_configuration_variables_mysqlx_wait_timeout" {
    type = string
default = null

}
variable "mysql_configuration_variables_mysqlx_write_timeout" {
    type = string
default = null

}
variable "mysql_configuration_variables_mysqlx_zstd_default_compression_level" {
    type = string
default = null

}
variable "mysql_configuration_variables_mysqlx_zstd_max_client_compression_level" {
    type = string
default = null

}
variable "mysql_configuration_variables_net_read_timeout" {
    type = string
default = null

}
variable "mysql_configuration_variables_net_write_timeout" {
    type = string
default = null

}
variable "mysql_configuration_variables_parser_max_mem_size" {
    type = string
default = null

}
variable "mysql_configuration_variables_regexp_time_limit" {
    type = string
default = null

}
variable "mysql_configuration_variables_sort_buffer_size" {
    type = string
default = null

}
variable "mysql_configuration_variables_sql_mode" {
    type = string
default = null

}
variable "mysql_configuration_variables_sql_require_primary_key" {
    type = string
default = null

}
variable "mysql_configuration_variables_sql_warnings" {
    type = string
default = null

}
variable "mysql_configuration_variables_thread_pool_dedicated_listeners" {
    type = string
default = null

}
variable "mysql_configuration_variables_thread_pool_max_transactions_limit" {
    type = string
default = null

}
variable "mysql_configuration_variables_time_zone" {
    type = string
default = null

}
variable "mysql_configuration_variables_tmp_table_size" {
    type = string
default = null

}
variable "mysql_configuration_variables_transaction_isolation" {
    type = string
default = null

}
variable "mysql_configuration_variables_wait_timeout" {
    type = string
    default = null

}
