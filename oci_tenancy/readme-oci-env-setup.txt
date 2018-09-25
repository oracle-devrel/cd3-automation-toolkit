1.  create_oci_python_env.sh
2.  run create_keys.sh.  Upload the resultant Public key to the OCI User
2a. Update the ~/.oci/config file with all the relevant information.
2b. Add "compartment_id=<compartment_id>" to the ~/.oci/config file.
3.  create_tenancy_config.sh
        a.  This will create the list of ADs in the config file - for the region.
        b.  This will create the namespace entry in the config file
        c.  This will create an entry for the default bucket for the OCI Objects that we use for the scripts
        d.  This will also create the Bucket in the Object store if it doesnt exist
