## auto.tfvars syntax for Load Balancer Module
These are the syntax and sample format for providing inputs to the modules via <b>*.auto.tfvars</b> files.
<b>"key"</b> must be unique to every resource that is created.
Comments preceed with <b>##</b>.

## Load Balancers
1. Load Balancers (LBR)
- <b>Syntax</b>

  ````
  load_balancers = {
      ## key - Is a unique value to reference the resources respectively
      key = {
          # Required
          compartment_id             = string
          vcn_id                     = string
          shape                      = string
          subnet_ids                 = list
          network_compartment_id     = string
          display_name               = string
        
          # Optional
          shape_details              = list(map)
          nsg_ids                    = list
          is_private                 = bool
          ip_mode                    = string
          reserved_ips_id            = string
          defined_tags               = map
          freeform_tags              = map
      },
  }
    ````
- <b>Example</b>
  ````
    // Copyright (c) 2021, 2022, Oracle and/or its affiliates.
    #############################
    # Network
    # Load Balancers - tfvars
    # Allowed values:
    # vcn_name and subnet_names must be the names of the VCN and Subnets as per OCI respectively
    # compartment_id and network_compartment_id can be the ocid or the name of the compartment hierarchy delimited by double hiphens "--"
    # Example : compartment_id = "ocid1.compartment.oc1..aaaaaaaahwwiefb56epvdlzfic6ah6jy3xf3c" or compartment_id = "Network-root-cpt--Network" where "Network-root-cpt" is the parent of "Network" compartment
    # ip_mode can be one of IPV4 or IPV6
    # shape can be one of 100Mbps|10Mbps|10Mbps-Micro|400Mbps|8000Mbps|flexible
    # reserved_ips_id accepts OCID (to use the existing reserved IP) or 'Y' to create a new Reserved IP or 'N' for Ephemeral IP; Defaults to "".
    # Sample import command for Load Balancers:
    # terraform import "module.load-balancers[\"<<load_balancers terraform variable name>>\"].oci_load_balancer_load_balancer.load_balancer" <<loadbalancer ocid>>
    #############################
    load_balancers = {
        lbr1 = {
       
            # Required
            display_name = "lbr1"
            compartment_id = "AppDev"
            shape = "flexible"
            network_compartment_id = "Network"
            vcn_id = "fwl-vcn"
            subnet_ids =  ["fwl-pub"]
       
            # Optional
            is_private = false
            reserved_ips_id = "N"
            ip_mode = "IPV4"
            shape_details = [{
                #Required
                maximum_bandwidth_in_mbps = 150
                minimum_bandwidth_in_mbps = 100
            }]
            freeform_tags = {
                    "Name"="lbr01",
                    "App"="Server01"
                        }
            },
        lbr2 = {
       
            # Required
            display_name = "lbr2"
            compartment_id = "AppDev"
            shape = "100Mbps"
            network_compartment_id = "Network"
            vcn_id = "fwl-vcn"
            subnet_ids =  ["fwl-pub"]
       
            # Optional
            reserved_ips_id = "N"
            ip_mode = "IPV4"
            },
    ##Add New Load Balancers for london here##
    }
    ````
  
2. Hostname
- <b>Syntax</b>
  ````
   hostnames = {
      ## key - Is a unique value to reference the resources respectively
      key = {
     
          # Required
          load_balancer_id           = string # Key of load balancer created by terraform
          hostname                   = string
          name                       = string
      },      
   }
  ````
- <b>Example</b>
  ````
    // Copyright (c) 2021, 2022, Oracle and/or its affiliates.
    #############################
    # Network
    # Hostname - tfvars
    # Allowed Values:
    # load_balancer_id can be the ocid or the key of load_balancers (map)
    # Sample import command for Hostname:
    # terraform import "module.hostnames[\"<<hostnames terraform variable name>>\"].oci_load_balancer_hostname.hostname" loadBalancers/<<loadbalancer ocid>>/hostnames/<<hostname>>
    #############################
    hostnames = {
      ## key - Is a unique value to reference the resources respectively
      lbr1_lbr01_hostname = {
           
        # Required
        name               = "lbr01"
        load_balancer_id   = "lbr1"
        hostname           = "lbrhostname01"
        },     
    }
  ````

3. Load Balancer Reserved IP 
- <b>Syntax</b>
  ````
   lbr_reserved_ips = {
      ## key - Is a unique value to reference the resources respectively
     key = {
          # Required
          compartment_id           = string
          display_name             = string
          lifetime                 = string
         
          # Optional
          private_ip_id            = string
          public_ip_pool_id        = string
          lifetime                 = string
          defined_tags             = map
          freeform_tags            = map
      }
   }
  ````
- <b>Example</b>
  ````
  // Copyright (c) 2021, 2022, Oracle and/or its affiliates.
  ############################
  # Network
  # Create Reserved IPs for Load Balancers
  # Allowed Values:
  # lifetime can be EPHEMERAL or RESERVED
  # private_ip_id and public_ip_pool_id can be the ocids or the key of private_ips (map) and public_ip_pools (map) respectively
  # compartment_id can be the ocid or the name of the compartment hierarchy delimited by double hiphens "--"
  # Example : compartment_id = "ocid1.compartment.oc1..aaaaaaaahwwiefb56epvdlzfic6ah6jy3xf3c" or compartment_id = "Network-root-cpt--Network" where "Network-root-cpt" is the parent of "Network" compartment
  ########################################################
  lbr_reserved_ips = {
     ## key - Is a unique value to reference the resources respectively
     lbr2-reserved-ip = {
     
          # Required
          compartment_id = "OMCDev--OMCDev-VM"
          display_name   = "lbr2-reserved-ip"
          lifetime       = "RESERVED"
     
          defined_tags = {
               "Operations.os"= "Linux" ,
               "Organization.department"= "Administrators" ,
          },
     },
  ##Add New Load Balancer Reserved IPs for london here##
  }
  ````
4. Certificates
- <b>Syntax</b>
  ````
  certificates = {
      ## key - Is a unique value to reference the resources respectively
      key = {
          # Required
          certificate_name           = string
          load_balancer_id           = string # Key of load balancer created by terraform
         
          # Optional
          ca_certificate             = string
          passphrase                 = string
          private_key                = string
          public_certificate         = string
     }
  }
  ````
- <b>Example</b>
  ````
  // Copyright (c) 2021, 2022, Oracle and/or its affiliates.
  #############################
  # Network
  # Certificates - tfvars
  # Allowed Values:
  # load_balancer_id can be ocid or the key of load_balancers (map)
  # Sample import command for Certificates:
  # terraform import "module.certificates[\"<<certificates terraform variable name>>\"].oci_load_balancer_certificate.certificate" loadBalancers/<<loadbalancer ocid>>/certificates/<<certificate name>>
  #############################
  certificates = {
      ## key - Is a unique value to reference the resources respectively
     lbr1_cert = {
     
       # Required
       certificate_name = "lbr-cert"
       load_balancer_id = "lbr1"
     
       # Optional
       ca_certificate     = "abc-selfsigned.key"
       private_key        = "abc-selfsigned.key"
       public_certificate = "abc-selfsigned.crt"
     },
     lbr2_cert = {
          
        # Required
        certificate_name  = "lbr2-cert"
        load_balancer_id   = "lbr2"
           
        # Optional
        ca_certificate     = "def-ca-certificate.cert"
        public_certificate = "def-cert-public-certificate.cert"
     },
  ##Add New Certificates for london here##
  }
  ````
5. Cipher Suites
- <b>Syntax</b>
  ````
  cipher_suites = {
      ## key - Is a unique value to reference the resources respectively
      key = {
          # Required
          ciphers          = list(string)
          name             = string
          load_balancer_id = string # Key of load balancer created by terraform
     }
  }
  ````
- <b>Example</b>
  ````
  // Copyright (c) 2021, 2022, Oracle and/or its affiliates.
  #############################
  # Network
  # Cipher Suites - tfvars
  # Allowed Values:
  # load_balancer_id can be ocid or the key of load_balancers (map)
  # Sample import command for Cipher Suites:
  # terraform import "module.cipher-suites[\"<<cipher_suites terraform variable name>>\"].oci_load_balancer_ssl_cipher_suite.ssl_cipher_suite" loadBalancers/<<loadbalancer ocid>>/sslCipherSuites/<<cipher suite name>>
  #############################
  cipher_suites = {
      ## key - Is a unique value to reference the resources respectively
      lbr1_testcipher = {
           # Required
           ciphers          = ["AES128-SHA"]
           name             = "testcipher"
           load_balancer_id = "lbr1"
     },
  ##Add New Ciphers for london here##
  }
  ````
6. Backend Sets
- <b>Syntax</b>
  ````
  backend_sets = {
      ## key - Is a unique value to reference the resources respectively
      key = {
        # Required
        name                        = string
        load_balancer_id            = string # Key of load balancer created by terraform
        policy                      = string
      
        # Optional 
        protocol                   = string
        interval_ms                = string
        port                       = string
        response_body_regex        = string
        retries                    = string
        return_code                = string
        timeout_in_millis          = string
        url_path                   = string
        lb_cookie_session          = [{
          cookie_name        = string
          disable_fallback   = string
          path               = string
          domain             = string
          is_http_only       = string
          is_secure          = string
          max_age_in_seconds = string
        }]
        session_persistence_configuration       = [{
          cookie_name      = string
          disable_fallback = string
        }]
        certificate_name         = string # Key of certificate created by terraform
        cipher_suite_name        = string # Key of cipher suite created by terraform or default cipher suite name
        ssl_configuration        = [{
          certificate_ids        = list
          server_order_preference= string
          trusted_certificate_authority_ids = list
          verify_peer_certificate = string
          verify_depth            = string
          protocols               = list
          }]
      }
  }
  ````
- <b>Example</b>
  ````
  // Copyright (c) 2021, 2022, Oracle and/or its affiliates.
  #############################
  # Network
  # Backend Sets - tfvars
  # Allowed Values:
  # load_balancer_id can be ocid or the key of load_balancers (map)
  # protocols in ssl configuration defaults to "TLSv1","TLSv1.1","TLSv1.2"
  # Sample import command for Backend Sets:
  # terraform import "module.backend-sets[\"<<backend_sets terraform variable name>>\"].oci_load_balancer_backend_set.backend_set" loadBalancers/<<loadbalancer ocid>>/backendSets/<<backendset name>>
  #############################
  backend_sets = {
     lbr2_bs01 = {
         # Required
         name = "bs01"
         load_balancer_id = "lbr2"
         policy = "ROUND_ROBIN"
     
         # Optional
         protocol = "HTTP"
         interval_ms = "10000"
         port = "90"
         url_path = "/"
         session_persistence_configuration = [{
             #Required
             cookie_name = "test"
             #Optional
             disable_fallback = "true"
         }]
     },
     lbr1_bset01 = {
         # Required
         name = "bset01"
         load_balancer_id = "lbr1"
         policy = "ROUND_ROBIN"
     
         # Optional
         protocol = "HTTP"
         interval_ms = "10000"
         port = "80"
         url_path = "/"
         certificate_name = "lbr1_cert"
         cipher_suite_name = "oci-wider-compatible-ssl-cipher-suite-v1"
         ssl_configuration  = [{
             verify_peer_certificate = true
             verify_depth = 1
             protocols = [ "TLSv1.2","TLSv1","TLSv1.1", ]
         }]
     },
  ##Add New Backend Sets for london here##
  }
  ````
7. Backends
- <b>Syntax</b>
  ````
  backends = {
      ## key - Is a unique value to reference the resources respectively
      key = {
          # Required
          backendset_name  = string # Key of backend sets created by terraform
          ip_address       = string
          load_balancer_id = string # Key of load balancer created by terraform
          port             = string
            
          # Optional
          instance_compartment = string
          backup               = string
          drain                = string
          offline              = string
          weight               = string
     }
  }
  ````
- <b>Example</b>
  ````
  // Copyright (c) 2021, 2022, Oracle and/or its affiliates.
  #############################
  # Network
  # Backends - tfvars
  # Allowed Values:
  # backendset_name must be the key of backend_sets (map)
  # load_balancer_id can be ocid or the key of load_balancers (map)
  # Sample import command for Backend Sets:
  # terraform import "module.backends[\"<<backends terraform variable name>>\"].oci_load_balancer_backend.backend" loadBalancers/<<loadbalancer ocid>>/backendSets/<<backendset name>>/backends/<<backend server name or ip>>:<<port>>
  #############################
  backends = {
     lbr2_bs01_c10-218-3-7-1 = {
         # Required
         backendset_name = "lbr2_bs01"
         load_balancer_id = "lbr2"
         ip_address = "IP:10.218.3.7" # Format -->  "IP:<ip_address>" or "NAME:<server_name>"
         port = "80"
            
         # Optional
         backup = "false"
         },
     lbr1_bset01_c192-9-88-40-1 = {
         # Required
         backendset_name = "lbr1_bset01"
         load_balancer_id = "lbr1"
         ip_address = "IP:192.9.88.40" # Format -->  "IP:<ip_address>" or "NAME:<server_name>"
         port = "80"
     
         # Optional
         backup = "false"
         },
  ##Add New Backends for london here##
  }
  ````
8. Rule Sets
- <b>Syntax</b>
  ````
  rule_sets = {
      ## key - Is a unique value to reference the resources respectively
      key = {
         # Required
         name                     = string
         load_balancer_id         = string # Key of load balancer created by terraform

         # Optional
         access_control_rules     = [{
             # Required
             action          = string
             # Optional
             attribute_name  = string
             attribute_value = string
             description     = string
         }] (OR)
         access_control_method_rules = [{
             # Required
             action           = string
             # Optional
             allowed_methods  = list
             status_code      = string
         }] (OR)
         http_header_rules        = [{
             # Required
             action           = string
             # Optional
             action   = string
             are_invalid_characters_allowed  = bool
             http_large_header_size_in_kb    = string
         }] (OR)
         uri_redirect_rules       = [{
             # Required
             action           = string
             # Optional
             attribute_name   = string
             attribute_value  = string
             operator         = string
             host             = string
             path             = string
             port             = string
             protocol         = string
             query            = string
             response_code    = string
         }] (OR)
         request_response_header_rules = [{
             # Required
             action           = string
             # Optional
             header           = string
             prefix           = string
             suffix           = string
             value            = string
         }]
     }
  }
  ````
- <b>Example</b>
  ````
  // Copyright (c) 2021, 2022, Oracle and/or its affiliates.
  #############################
  # Network
  # Rule Set - tfvars
  # Allowed Values:
  # load_balancer_id can be the ocid or the key of load_balancers (map)
  # Sample import command for Rule Set:
  # terraform import "module.rule-sets[\"<<rule_sets terraform variable name>>\"].oci_load_balancer_rule_set.rule_set" loadBalancers/<<loadbalancer ocid>>/ruleSets/<<rule set name>>
  #############################
  rule_sets = {
     lbr1_test = {
         # Required
         name = "test"
         load_balancer_id = "lbr1"
            
         # Optional
         access_control_rules = [
            {
             action = "ALLOW"
             attribute_name = "SOURCE_IP_ADDRESS"
             attribute_value = "10.20.2.10/32"
             },
             {
             action = "ALLOW"
             attribute_name = "SOURCE_IP_ADDRESS"
             attribute_value = "10.10.1.10/32"
             },
     ## Add_access_control_rules_here_for_lbr1_test ##
         ]
         access_control_method_rules = [
             {
             action = "CONTROL_ACCESS_USING_HTTP_METHODS"
             allowed_methods = ["ACL","BIND","CHECKIN","CONNECT"]
             status_code = "405"
             },
     ## Add_access_control_method_rules_here_for_lbr1_test ##
         ]
         http_header_rules = [
             {
             #Required
             action = "HTTP_HEADER"
             are_invalid_characters_allowed = true
             http_large_header_size_in_kb = 64
             },
     ## Add_http_header_rules_here_for_lbr1_test ##
         ]
         uri_redirect_rules = [
             {
             action = "REDIRECT"
             attribute_name = "PATH"
             attribute_value = "/"
             operator = "PREFIX_MATCH"
             host = "10.0.0.1"
             path = "/"
             port = "80"
             protocol = "http"
             query = "?{query}"
             response_code = "302"
             },
     ## Add_uri_redirect_rules_here_for_lbr1_test ##
         ]
         request_response_header_rules = [
             {
             action = "EXTEND_HTTP_REQUEST_HEADER_VALUE"
             header = "head"
             prefix = "pre"
             suffix = "suf"
             },
                 {
             action = "REMOVE_HTTP_RESPONSE_HEADER"
             header = "fri"
             },
     ## Add_request_response_header_rules_here_for_lbr1_test ##
         ]
     },
  ##Add New Rule Sets for london here##
  }
  ````
9. Path Route Sets
- <b>Syntax</b>
  ````
  path_route_sets = {
      ## key - Is a unique value to reference the resources respectively
      key = {
          # Required
          name             = string
          load_balancer_id = string # Key of load balancer created by terraform
          path_routes      = [{
             backend_set_name = string # Key of backend sets created by terraform
             path             = string
             match_type       = string
         }]
     }
  }
  ````
- <b>Example</b>
  ````
  // Copyright (c) 2021, 2022, Oracle and/or its affiliates.
  #############################
  # Network
  # Path Route Set - tfvars
  # Allowed Values:
  # load_balancer_id can be the ocid or the key of load_balancers (map)
  # Sample import command for Path Route Set:
  # terraform import "module.path-route-sets[\"<<path_route_sets terraform variable name>>\"].oci_load_balancer_path_route_set.path_route_set" loadBalancers/<<loadbalancer ocid>>/pathRouteSets/<<path route set name>>
  #############################
  path_route_sets = {
    lbr1_prt = {
         # Required
         load_balancer_id = "lbr1"
         name = "prt"
         path_routes = [
         {
             #Required
             backend_set_name = "bset01"
             path = "find"
             match_type = "PREFIX_MATCH"
         },
                 {
             #Required
             backend_set_name = "bset01"
             path = "word"
             match_type = "FORCE_LONGEST_PREFIX_MATCH"
         },
                 {
             #Required
             backend_set_name = "bset01"
             path = "hello"
             match_type = "SUFFIX_MATCH"
         },
         #Add_Rules_for_lbr1_prt_here
             ]
       },
    lbr2_prs01 = {
         # Required
         load_balancer_id = "lbr2"
         name = "prs01"
         path_routes = [
         {
             #Required
             backend_set_name = "bs01"
             path = "find"
             match_type = "FORCE_LONGEST_PREFIX_MATCH"
         },
                 {
             #Required
             backend_set_name = "bs01"
             path = "word"
             match_type = "PREFIX_MATCH"
         },
         #Add_Rules_for_lbr2_prs01_here
             ]
       },
  ##Add New Path Route Sets for london here##
  }
  ````
10. Listeners
- <b>Syntax</b>
  ````
  listeners = {
      ## key - Is a unique value to reference the resources respectively
      key = {
          # Required
          name             = string
          load_balancer_id = string # Key of load balancer created by terraform
          port             = string
          protocol         = string
          default_backend_set_name   = string
             
          # Optional
          path_route_set_name = string
          routing_policy_name = string
          certificate_name    = string # Key of certificate created by terraform
          cipher_suite_name   = string # Key of cipher suite created by terraform
          connection_configuration = [{
             idle_timeout_in_seconds = string
             backend_tcp_proxy_protocol_version = string
          }]
          hostname_names   = list
          rule_set_names   = list
          ssl_configuration      = [{
             certificate_ids = list  # Oracle Managed Certificate IDs
             server_order_preference  = string
             trusted_certificate_authority_ids = list # Oracle Managed trusted_certificate_authority_ids
             verify_peer_certificate  = string
             verify_depth             = string
             protocols                = list
         }]
     }
  }
  ````
- <b>Example</b>
  ````
  // Copyright (c) 2021, 2022, Oracle and/or its affiliates.
  #############################
  # Network
  # Listeners - tfvars
  # Allowed Values:
  # HTTPS listener must have the protocol specified as HTTP
  # protocols in ssl configuration defaults to "TLSv1.2"
  # load_balancer_id can be the ocid or the key of load_balancers (map)
  # default_backend_set_name,hostname_names,path_route_set_name,rule_set_names,cipher_suite_name,certificate_name must be the key of the respective maps
  # Sample import command for Listeners:
  # terraform import "module.listeners[\"<<listeners terraform variable name>>\"].oci_load_balancer_listener.listener" loadBalancers/<<loadbalancer ocid>>/listeners/<<listener name>>
  #############################
  listeners = {
     lbr1_lis = {
         # Required
         name = "lis"
         load_balancer_id = "lbr1"
         port = "80"
         protocol = "HTTP"
         default_backend_set_name = "lbr1_bset01"
     
         # Optional
         connection_configuration = [{
             idle_timeout_in_seconds = "7000"
             }]
         hostname_names = ["lbr1_lbr01_hostname"]
         path_route_set_name = "lbr1_prt"
         rule_set_names = []
     },
  ##Add New Listeners for london here##
  }
  ````
