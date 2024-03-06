## auto.tfvars syntax for DNS Module
These are the syntax and sample format for providing inputs to the modules via <b>*.auto.tfvars</b> files.
<b>"key"</b> must be unique to every resource that is created.
Comments preceed with <b>##</b>.
## DNS
1. DNS View-Zones-Records
- <b>Syntax</b>
  
    ````
    views = {
  ## key - Is a unique value to reference the resources respectively
       key =  {
            compartment_id       = string
            display_name         = string
       },
    }
   zones = {
       key =  {
            compartment_id       = string
            display_name         = string
            zone_type            = string
            view_compartment_id  = string
            view_id              = string
       },
   }
   rrsets = {
       key =  {
            zone_id             = string
            domain              = string
            view_id             = string
            view_compartment_id = string
            compartment_id      = string
            rtype               = string
            ttl                 = number
            rdata               = list(string)
       },
  }
    ````
- <b>Example</b>
   ````
  // Copyright (c) 2021, 2022, 2023 Oracle and/or its affiliates.
  #############################
  # DNS
  # DNS Views - tfvars
  # Allowed Values:
  # view_id can be the ocid of the view or the name as in OCI
  # compartment_id and view_compartment_id can be the ocid or the name of the compartment hierarchy delimited by double hiphens "--"
  # Example : compartment_id = "ocid1.compartment.oc1..aaaaaaaah6jy3xf3c" or compartment_id = "AppDev--Prod" where "AppDev" is the parent of "Prod" compartment
  # Sample import command for dns-zone :
  # terraform import "module.dns-views[\"<<dns-zone terraform variable name>>\"].oci_dns_view.view" <<dns-view ocid>>
  ############################
  views = {
         "custom-view-1" =  {
              compartment_id       = "Network"
              display_name         = "custom-view-1"
      },
     "custom-view-2" =  {
              compartment_id       = "Network"
              display_name         = "custom-view-2"
      },
    }
  
  ############################
  # DNS
  # DNS Zones - tfvars
  # Allowed Values:
  # view_id can be the ocid of the view or the name as in OCI
  # compartment_id and view_compartment_id can be the ocid or the name of the compartment hierarchy delimited by double hiphens "--"
  # Example : compartment_id = "ocid1.compartment.oc1..aaaaaaaah6jy3xf3c" or compartment_id = "AppDev--Prod" where "AppDev" is the parent of "Prod" compartment
  # Sample import command for dns-zone :
  # terraform import "module.dns-zones[\"<<dns-zone terraform variable name>>\"].oci_dns_zone.zone" <<dns-zone ocid>>
  ############################
  zones = {
     "custom-view-1_zone1_com" =  {
              compartment_id       = "Network"
              display_name         = "zone1.com"
              zone_type            = ""
              view_compartment_id = "Network"
              view_id = "custom-view-1"
      },
     "custom-view-2_zone2_com" =  {
              compartment_id       = "Network"
              display_name         = "zone2.com"
              zone_type            = ""
              view_compartment_id = "Network"
              view_id = "custom-view-2"
      },
    }
  
  ############################
  # DNS
  # DNS Records - tfvars
  # Allowed Values:
  # view_id can be the ocid of the view or the name as in OCI
  # compartment_id and view_compartment_id can be the ocid or the name of the compartment hierarchy delimited by double hiphens "--"
  # Example : compartment_id = "ocid1.compartment.oc1..aaaaaaaah6jy3xf3c" or compartment_id = "AppDev--Prod" where "AppDev" is the parent of "Prod" compartment
  # Sample import command for dns-zone :
  # terraform import "module.dns-rrsets[\"<<dns-zone terraform variable name>>\"].oci_dns_rrset.rrset" <<dns-zone ocid>>
  ############################
  rrsets = {
     "custom-view-1_zone1_com_domain1_zone1_com_A" =  {
              zone_id = "zone1.com"
              domain         = "domain1.zone1.com"
              view_id = "custom-view-1"
              view_compartment_id = "Network"
              compartment_id = "Network"
              rtype = "A"
              ttl = 3600
              rdata = ["10.20.1.10", "10.20.1.20"]
      },
     "custom-view-1_zone1_com_domain2_zone1_com_CNAME" =  {
              zone_id = "zone1.com"
              domain         = "domain2.zone1.com"
              view_id = "custom-view-1"
              view_compartment_id = "Network"
              compartment_id = "Network"
              rtype = "CNAME"
              ttl = 300
              rdata = ["host1.example.com"]
      },
     "custom-view-2_zone2_com_domain1_zone2_com_A" =  {
              zone_id = "zone2.com"
              domain         = "domain1.zone2.com"
              view_id = "custom-view-2"
              view_compartment_id = "Network"
              compartment_id = "Network"
              rtype = "A"
              ttl = 300
              rdata = ["10.20.1.30"]
      },
  ##Add New rrsets for phoenix here##
  }
   ````
  

2. DNS-Resolvers
   - <b>Syntax</b>
  
       ````
       resolvers = {
           ## key - vcn name to reference the resources respectively
           key = {
               vcn_name = string
               network_compartment_id = string
               display_name = string
               views = {
                   key = {
                       view_id = string
                       view_compartment_id = string
                   },
               }
               endpoint_names = {
                   key = {
                       is_forwarding = bool
                       is_listening = bool
                       name = string
                       subnet_name = string
                       forwarding_address = string
                       listening_address = string
                       nsg_ids = list(string)
                   }
               }
               resolver_rules = {
                   key = {
                       client_address_conditions = list(string)
                       destination_addresses = list(string)
                       qname_cover_conditions = list(string)
                       source_endpoint_name = string
                   }
               }
           }
       }
       ````
   - <b>Example</b>
     ````
     ############################
     # DNS
     # DNS Resolvers - tfvars
     # Allowed Values:
     # view_id can be the ocid of the view or the name as in OCI
     # compartment_id and view_compartment_id can be the ocid or the name of the compartment hierarchy delimited by double hiphens "--"
     # Example : compartment_id = "ocid1.compartment.oc1..aaaaaaaah6jy3xf3c" or compartment_id = "AppDev--Prod" where "AppDev" is the parent of "Prod" compartment
     # Sample import command for dns-zone :
     # terraform import "module.dns-resolvers[\"<<dns-resolver terraform variable name>>\"].oci_dns_resolver.resolver" <<dns-resolver ocid>>
     # terraform import "module.dns-resolvers[\"<<dns-resolver-endpoint terraform variable name>>\"].oci_dns_resolver_endpoint.resolver_endpoint" <<resolverId/{resolverId}/name/{resolverEndpointName}>>
     ############################
     resolvers = {
            "fwl-vcn" =  {
                 vcn_name = "fwl-vcn"
                 network_compartment_id = "Network"
                 display_name = "fwl-vcn"
                 views = {
                     "fwl-vcn_order1" = {
                         view_id = "custom-view-1"
                         view_compartment_id = "Network"
                     }
                     "fwl-vcn_order2" = {
                         view_id = "fwl-vcn"
                         view_compartment_id = "Network"
                     }
                 }
                 endpoint_names = {
                     "forwarder_endpoint1" = {
                         is_forwarding = true
                         is_listening = false
                         name = "forwarder_endpoint1"
                         subnet_name = "fwl-mgmt"
                         forwarding_address = "10.110.1.35"
                         listening_address = ""
                         nsg_ids = []
                     }
                     "listener_endpoint1" = {
                         is_forwarding = false
                         is_listening = true
                         name = "listener_endpoint1"
                         subnet_name = "fwl-mgmt"
                         forwarding_address = ""
                         listening_address = ""
                         nsg_ids = []
                     }
                 }
                 resolver_rules = {
                     "rule1" = {
                         client_address_conditions = []
                         destination_addresses = ["10.0.0.20"]
                         qname_cover_conditions = ["internal.example.com", "internal3.example.com"]
                         source_endpoint_name = "forwarder_endpoint1"
                     }
                     "rule2" = {
                         client_address_conditions = []
                         destination_addresses = ["10.0.0.20"]
                         qname_cover_conditions = ["internal2.example.com"]
                         source_endpoint_name = "forwarder_endpoint1"
                     }
                     "rule3" = {
                         client_address_conditions = []
                         destination_addresses = ["10.0.0.30"]
                         qname_cover_conditions = []
                         source_endpoint_name = "forwarder_endpoint1"
                     }
                     "rule4" = {
                         client_address_conditions = ["10.0.2.0/24", "10.0.3.0/24"]
                         destination_addresses = ["10.0.0.40"]
                         qname_cover_conditions = []
                         source_endpoint_name = "forwarder_endpoint1"
                     }
                 }
         },
        "prod-vcn" =  {
                 vcn_name = "prod-vcn"
                 network_compartment_id = "Network"
                 display_name = "prod-vcn-res"
                 views = {
                     "prod-vcn_order1" = {
                         view_id = "custom-view-2"
                         view_compartment_id = "Network"
                     }
                     "prod-vcn_order2" = {
                         view_id = "prod-vcn"
                         view_compartment_id = "Network"
                     }
                 }
                 endpoint_names = {
                     "listener_endpoint1" = {
                         is_forwarding = false
                         is_listening = true
                         name = "listener_endpoint1"
                         subnet_name = "prod-web"
                         forwarding_address = ""
                         listening_address = ""
                         nsg_ids = []
                     }
                     "forwarder_endpoint1" = {
                         is_forwarding = true
                         is_listening = false
                         name = "forwarder_endpoint1"
                         subnet_name = "prod-web"
                         forwarding_address = "10.111.2.90"
                         listening_address = ""
                         nsg_ids = []
                     }
                 }
                 resolver_rules = {
                 }
         },
     }
     ````
 
