# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Resource Block - Database
# Create MySQL Configurations
############################

resource "oci_mysql_mysql_configuration" "mysql_configuration" {
    #Required
    compartment_id = var.compartment_id
    shape_name = var.mysql_configuration_shape_name

    #Optional
    defined_tags = var.defined_tags
    description = var.mysql_configuration_description
    display_name = var.mysql_configuration_display_name
    freeform_tags = var.freeform_tags
    init_variables {

        #Optional
        lower_case_table_names = var.mysql_configuration_init_variables_lower_case_table_names
    }

    variables {

        #Optional
        autocommit = var.mysql_configuration_variables_autocommit
        big_tables = var.mysql_configuration_variables_big_tables
        binlog_expire_logs_seconds = var.mysql_configuration_variables_binlog_expire_logs_seconds
        binlog_row_metadata = var.mysql_configuration_variables_binlog_row_metadata
        binlog_row_value_options = var.mysql_configuration_variables_binlog_row_value_options
        binlog_transaction_compression = var.mysql_configuration_variables_binlog_transaction_compression
        completion_type = var.mysql_configuration_variables_completion_type
        connect_timeout = var.mysql_configuration_variables_connect_timeout
        connection_memory_chunk_size = var.mysql_configuration_variables_connection_memory_chunk_size
        connection_memory_limit = var.mysql_configuration_variables_connection_memory_limit
        cte_max_recursion_depth = var.mysql_configuration_variables_cte_max_recursion_depth
        default_authentication_plugin = var.mysql_configuration_variables_default_authentication_plugin
        foreign_key_checks = var.mysql_configuration_variables_foreign_key_checks
        global_connection_memory_limit = var.mysql_configuration_variables_global_connection_memory_limit
        global_connection_memory_tracking = var.mysql_configuration_variables_global_connection_memory_tracking
        group_replication_consistency = var.mysql_configuration_variables_group_replication_consistency
        information_schema_stats_expiry = var.mysql_configuration_variables_information_schema_stats_expiry
        innodb_buffer_pool_dump_pct = var.mysql_configuration_variables_innodb_buffer_pool_dump_pct
        innodb_buffer_pool_instances = var.mysql_configuration_variables_innodb_buffer_pool_instances
        innodb_buffer_pool_size = var.mysql_configuration_variables_innodb_buffer_pool_size
        innodb_ddl_buffer_size = var.mysql_configuration_variables_innodb_ddl_buffer_size
        innodb_ddl_threads = var.mysql_configuration_variables_innodb_ddl_threads
        innodb_ft_enable_stopword = var.mysql_configuration_variables_innodb_ft_enable_stopword
        innodb_ft_max_token_size = var.mysql_configuration_variables_innodb_ft_max_token_size
        innodb_ft_min_token_size = var.mysql_configuration_variables_innodb_ft_min_token_size
        innodb_ft_num_word_optimize = var.mysql_configuration_variables_innodb_ft_num_word_optimize
        innodb_ft_result_cache_limit = var.mysql_configuration_variables_innodb_ft_result_cache_limit
        innodb_ft_server_stopword_table = var.mysql_configuration_variables_innodb_ft_server_stopword_table
        innodb_lock_wait_timeout = var.mysql_configuration_variables_innodb_lock_wait_timeout
        innodb_log_writer_threads = var.mysql_configuration_variables_innodb_log_writer_threads
        innodb_max_purge_lag = var.mysql_configuration_variables_innodb_max_purge_lag
        innodb_max_purge_lag_delay = var.mysql_configuration_variables_innodb_max_purge_lag_delay
        innodb_stats_persistent_sample_pages = var.mysql_configuration_variables_innodb_stats_persistent_sample_pages
        innodb_stats_transient_sample_pages = var.mysql_configuration_variables_innodb_stats_transient_sample_pages
        interactive_timeout = var.mysql_configuration_variables_interactive_timeout
        local_infile = var.mysql_configuration_variables_local_infile
        mandatory_roles = var.mysql_configuration_variables_mandatory_roles
        max_allowed_packet = var.mysql_configuration_variables_max_allowed_packet
        max_binlog_cache_size = var.mysql_configuration_variables_max_binlog_cache_size
        max_connect_errors = var.mysql_configuration_variables_max_connect_errors
        max_connections = var.mysql_configuration_variables_max_connections
        max_execution_time = var.mysql_configuration_variables_max_execution_time
        max_heap_table_size = var.mysql_configuration_variables_max_heap_table_size
        max_prepared_stmt_count = var.mysql_configuration_variables_max_prepared_stmt_count
        mysql_firewall_mode = var.mysql_configuration_variables_mysql_firewall_mode
        mysqlx_connect_timeout = var.mysql_configuration_variables_mysqlx_connect_timeout
        mysqlx_deflate_default_compression_level = var.mysql_configuration_variables_mysqlx_deflate_default_compression_level
        mysqlx_deflate_max_client_compression_level = var.mysql_configuration_variables_mysqlx_deflate_max_client_compression_level
        mysqlx_enable_hello_notice = var.mysql_configuration_variables_mysqlx_enable_hello_notice
        mysqlx_interactive_timeout = var.mysql_configuration_variables_mysqlx_interactive_timeout
        mysqlx_lz4default_compression_level = var.mysql_configuration_variables_mysqlx_lz4default_compression_level
        mysqlx_lz4max_client_compression_level = var.mysql_configuration_variables_mysqlx_lz4max_client_compression_level
        mysqlx_max_allowed_packet = var.mysql_configuration_variables_mysqlx_max_allowed_packet
        mysqlx_read_timeout = var.mysql_configuration_variables_mysqlx_read_timeout
        mysqlx_wait_timeout = var.mysql_configuration_variables_mysqlx_wait_timeout
        mysqlx_write_timeout = var.mysql_configuration_variables_mysqlx_write_timeout
        mysqlx_zstd_default_compression_level = var.mysql_configuration_variables_mysqlx_zstd_default_compression_level
        mysqlx_zstd_max_client_compression_level = var.mysql_configuration_variables_mysqlx_zstd_max_client_compression_level
        net_read_timeout = var.mysql_configuration_variables_net_read_timeout
        net_write_timeout = var.mysql_configuration_variables_net_write_timeout
        parser_max_mem_size = var.mysql_configuration_variables_parser_max_mem_size
        regexp_time_limit = var.mysql_configuration_variables_regexp_time_limit
        sort_buffer_size = var.mysql_configuration_variables_sort_buffer_size
        sql_mode = var.mysql_configuration_variables_sql_mode
        sql_require_primary_key = var.mysql_configuration_variables_sql_require_primary_key
        sql_warnings = var.mysql_configuration_variables_sql_warnings
        thread_pool_dedicated_listeners = var.mysql_configuration_variables_thread_pool_dedicated_listeners
        thread_pool_max_transactions_limit = var.mysql_configuration_variables_thread_pool_max_transactions_limit
        time_zone = var.mysql_configuration_variables_time_zone
        tmp_table_size = var.mysql_configuration_variables_tmp_table_size
        transaction_isolation = var.mysql_configuration_variables_transaction_isolation
        wait_timeout = var.mysql_configuration_variables_wait_timeout
    }
}