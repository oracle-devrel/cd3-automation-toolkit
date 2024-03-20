# auto.tfvars syntax for Firewall Module
These are the syntax and sample format for providing inputs to the modules via <b>*.auto.tfvars</b> files.
<b>"key"</b> must be unique to every resource that is created.
Comments preceed with <b>##</b>.

**1. Firewalls**

- <b>Syntax</b>
```
firewalls = {
  ## key - Is a unique value to reference the resources respectively
  key = {
	# Required
	compartment_id = 		string
	display_name   = 		string
	network_firewall_policy_id =	string
	network_compartment_id =string
	vcn_name   =string
	subnet_id  =string
	ipv4address=string
	availability_domain.   =string
	nsg_id==list

	# Optional
	defined_tags   = map
	freeform_tags  = map
	},
}
```

- <b>Example</b>
```
############################
# Firewalls
# Firewall - tfvars
# Allowed Values:
# compartment_id and network_compartment_id can be the ocid or the name of the compartment hierarchy delimited by double hiphens "--"
# Example : "ocid1.compartment.oc1..aaaaaaaahwwiefb56epvdlzfic6ah6jy3xf3c" or compartment_id = "Network-root-cpt--Network" where "Network-root-cpt" is the parent of "Network" compartment
# network_firewall_policy_id can be the ocid or the name of the firewall Policy that needs to be attached to the Firewall
# vcn_name must be the name of the VCN as in OCI
# subnet_id can be the ocid of the subnet or the name as in OCI
# Sample import command for Firewall:
# terraform import "module.firewalls[\"<<firewall terraform variable name>>\"].oci_network_firewall_network_firewall.network_firewall" <<firewall ocid>>
############################

firewalls = {
  OCI-FWL = {
	compartment_id = "Network"
	display_name = "OCI-FWL"
	network_firewall_policy_id = "OCI-FWL-Policy"
	network_compartment_id = "Network"
	vcn_name = "fwl-vcn"
	subnet_id = "fwl-mgmt"
	ipv4address = "10.110.1.23"
	availability_domain = "0"
	defined_tags = {
		"Oracle-Tags.CreatedOn"= "2024-03-14T06:18:47.503Z" ,
		"Oracle-Tags.CreatedBy"= "oracleidentitycloudservice/abc@xyz.com"
		}
  	},
	##Add New firewall for phoenix here##
  }
```  

**2. Firewall Policy Address Lists**

- <b>Syntax</b>
```
address_lists = {
  ## key - Is a unique value to reference the resources respectively
  key = {
	# Required
	address_list_name= string
	network_firewall_policy_id   = string
	addresses   = list
	address_type = string
	},
}
```

- <b>Example</b>
```
############################
# Firewall Policy Address Lists
# Firewall Policy Address List - tfvars
# Allowed Values:
# network_firewall_policy_id can be the ocid or the name of the firewall Policy that needs  
to be attached to the Firewall
# address_type can be  IP or FQDN
# Sample import command for Firewall Policy Address List:
# terraform import "module.address_lists[\"<<address-list terraform variable 
name>>\"].oci_network_firewall_network_firewall_policy_address_list.network_firewall_policy_address_list\" networkFirewallPolicies/<<firewall-policy ocid>>/addressLists/<<address-list ocid>>
############################
address_lists = {
  OCI-FWL-Policy_pub-list = {
  	address_list_name = "pub-list"
  	network_firewall_policy_id = "OCI-FWL-Policy"
  	addresses = ["0.0.0.0/0"]
  	address_type = "IP"
  	},
        ##Add New application list for phoenix here##
  }
```
  

**3. Firewall Policy Application Lists**
 
- <b>Syntax</b>
```
application_groups = {
  ## key - Is a unique value to reference the resources respectively
  key = {
	# Required
	app_group_name		= string
	network_firewall_policy_id 	= string
	apps 		= list
 	},
}
  
```

- <b>Example</b>
```
############################
# Firewall Policy Application Lists
# Firewall Policy Application List - tfvars
# Allowed Values:
# network_firewall_policy_id can be the ocid or the name of the firewall Policy that needs to be attached to the Firewall
# Sample import command for Firewall Policy Address List:
# terraform import "module.application_groups[\"<<application-list terraform variable name>>\"].oci_network_firewall_network_firewall_policy_application_group.network_firewall_policy_application_group\"
networkFirewallPolicies/<<firewall-policy ocid>>/applicationGroups/<<application-list ocid>>
############################
application_groups = {
  OCI-FWL-Policy_App-List-1 = {
  	app_group_name = "App-List-1"
  	network_firewall_policy_id = "OCI-FWL-Policy"
  	apps = ["icmp-resp","icmpv6-req"]
  	},

  }
```


**4. Firewall Policy Applications**

- <b>Syntax</b>
```
applications = {
  ## key - Is a unique value to reference the resources respectively
  key = {
 	#Required
 	app_list_name = string
 	network_firewall_policy_id = string
 	app_type   = string
	icmp_type  = string
	icmp_code = string
  	},
}
```

- <b>Example</b>
```
// Copyright (c) 2021, 2022, Oracle and/or its affiliates.
############################
# Firewall Policy Applications
# Firewall Policy Application - tfvars
# Allowed Values:
# network_firewall_policy_id can be the ocid or the name of the firewall Policy that needs to be attached to the Firewall
# app_type can be ICMP or ICMP_V6
# Sample import command for Firewall Policy Address List:
# terraform import "module.applications[\"<<application terraform variable name>>\"].oci_network_firewall_network_firewall_policy_application.network_firewall_policy_application\"  networkFirewallPolicies/<<firewall-policy ocid>>/applications/<<application ocid>>
############################
applications = {
  OCI-FWL-Policy_icmp-resp = {
	app_list_name = "icmp-resp"
 	network_firewall_policy_id = "OCI-FWL-Policy"
  	app_type = "ICMP"
  	icmp_type = "129"
  	},
  }

```
**5. Firewall Policy Decryption Profiles**

- <b>Syntax</b>
```
decryption_profiles = {
  ## key - Is a unique value to reference the resources respectively
  key = {
  	#Required
  	profile_name  = string
  	network_firewall_policy_id  = string
  	profile_type = string
  	are_certificate_extensions_restricted   = string
	is_auto_include_alt_name = string
	is_expired_certificate_blocked = string
	is_out_of_capacity_blocked = string
	is_revocation_status_timeout_blocked = string
	is_unknown_revocation_status_blocked = string
	is_unsupported_cipher_blocked = string
	is_unsupported_version_blocked = string
	is_untrusted_issuer_blocked = string
	},
}
```

- <b>Example</b>
```
// Copyright (c) 2021, 2022, Oracle and/or its affiliates.
############################
# Firewall Policy Decryption Profiles
# Firewall Policy Decryption Profile - tfvars
# Allowed Values:
# network_firewall_policy_id can be the ocid or the name of the firewall Policy that needs to be attached to the Firewall
# profile_type can be SSL_FORWARD_PROXY or SSL_INBOUND_INSPECTION
# Sample import command for Firewall Policy Decryption Profile:
# terraform import "module.decryption_profiles[\"<<decryption-profile terraform variable name>>\"].oci_network_firewall_network_firewall_policy_decryption_profile.network_firewall_policy_decryption_profile\"  networkFirewallPolicies/<<firewall-policy ocid>>/decryptionProfiles/<<decryption-profile ocid>>
############################
decryption_profiles = {
  OCI-FWL-Policy_decrypt-profile
	profile_name = "decrypt-profile"
        network_firewall_policy_id = "OCI-FWL-Policy"
        profile_type = "SSL_FORWARD_PROXY"
        are_certificate_extensions_restricted = "true"
        is_auto_include_alt_name = "true"
        is_expired_certificate_blocked = "true"
        is_out_of_capacity_blocked = "true"
        is_revocation_status_timeout_blocked = "false"
        is_unknown_revocation_status_blocked = "true"
        is_unsupported_cipher_blocked = "true"
        is_unsupported_version_blocked = "true"
        is_untrusted_issuer_blocked = "true"
	},
  }
```
**6. Firewall Policy Decryption Rules**

- <b>Syntax</b>
```
decryption_rules = {
  ## key - Is a unique value to reference the resources respectively
  key = {
  	#Required
  	rule_name  = string
  	network_firewall_policy_id  = string
  	action = string
  	condition = [{
		source_address = list
		destination_address = list
	}]
	secret 	= string
	decryption_profile = string
	placement = string
	},
}
```

- <b>Example</b>
```
// Copyright (c) 2021, 2022, Oracle and/or its affiliates.
############################
# Firewall Policy Decryption Rules
# Firewall Policy Decryption Rule - tfvars
# Allowed Values:
# network_firewall_policy_id can be the ocid or the name of the firewall Policy that needs to be attached to the Firewall
# action can be NO_DECRYPT or DECRYPT
# Sample import command for Firewall Policy Decryption Rules:
# terraform import "module.decryption_rules[\"<<decryption-rule terraform variable name>>\"].oci_network_firewall_network_firewall_policy_decryption_rule.network_firewall_policy_decryption_rule\"  networkFirewallPolicies/<<firewall-policy ocid>>/decryptionRules/<<decryption-rule ocid>>
############################
decryption_rules = {
  OCI-FWL-Policy_decrypt-rule
	rule_name = "decrypt-rule"
        network_firewall_policy_id = "OCI-FWL-Policy"
        action = "DECRYPT"
	condition = [{
        }]
        secret = "secret"
        decryption_profile = "decrypt-profile"
      },
  }
```

**7. Firewall Policy Secrets**

- <b>Syntax</b>
```
Secrets = {
  ## key - Is a unique value to reference the resources respectively
  key = {
  	#Required
  	secret_name  = string
  	network_firewall_policy_id  = string
  	secret_source = string
  	secret_type = string
	vault_secret_id = string
	vault_name = string
	version_number = string
	vault_compartment_id = string
	},
}
```

- <b>Example</b>
```
// Copyright (c) 2021, 2022, Oracle and/or its affiliates.
############################
# Firewall Policy Secrets
# Firewall Policy Secret - tfvars
# Allowed Values:
# network_firewall_policy_id can be the ocid or the name of the firewall Policy that needs to be attached to the Firewall
# secret_source can be OCI_VAULT
# secret_type can be SSL_FORWARD_PROXY or SSL_INBOUND_INSPECTION
# vault_compartment_id can be the ocid or the name of the compartment hierarchy delimited by double hiphens "--"
# Example : "ocid1.compartment.oc1..aaaaaaaahwwiefb56epvdlzfic6ah6jy3xf3c" or compartment_id = "Vault-root-cpt--Vault" where "Vault-root-cpt" is the parent of "Vault" compartment
# Sample import command for Firewall Policy Decryption Rules:
# terraform import "module.secrets[\"<<decryption-rule terraform variable name>>\"].oci_network_firewall_network_firewall_policy_mapped_secret.network_firewall_policy_mapped_secret\"  networkFirewallPolicies/<<firewall-policy ocid>>/mappedSecrets/<<mapped-secret ocid>>
############################
Secrets = {
  OCI-FWL-Policy_secret {
	secret_name = "secret"
  	network_firewall_policy_id = "OCI-FWL-Policy"
  	secret_source = "OCI_VAULT"
  	secret_type = "SSL_FORWARD_PROXY"
  	vault_secret_id = "test"
  	vault_name = "test"
  	version_number = "1"
  	vault_compartment_id = "Security"
  	},

  }
```

**8. Firewall Policy Service Lists**

- <b>Syntax</b>
```
service_lists = {
  ## key - Is a unique value to reference the resources respectively
  key = {
  	#Required
  	service_list_name  = string
  	network_firewall_policy_id  = string
  	services = list
  	},
}
```

- <b>Example</b>
```
// Copyright (c) 2021, 2022, Oracle and/or its affiliates.
############################
# Firewall Policy Service Lists
# Firewall Policy Service List - tfvars
# Allowed Values:
# network_firewall_policy_id can be the ocid or the name of the firewall Policy that needs to be attached to the Firewall
# Sample import command for Firewall Policy Service List:
# terraform import "module.service_lists[\"<<service-list terraform variable name>>\"].oci_network_firewall_network_firewall_policy_service_list.network_firewall_policy_service_list\"  networkFirewallPolicies/<<firewall-policy ocid>>/serviceLists/<<service-list ocid>>
############################
service_lists = {
  OCI-FWL-Policy_svclist1 = {
  	service_list_name = "svclist1"
  	network_firewall_policy_id = "OCI-FWL-Policy"
  	services = ["svc-1"]

  }
```

**9. Firewall Policy Services**

- <b>Syntax</b>
```
services = {
  ## key - Is a unique value to reference the resources respectively
  key = {
  	#Required
  	service_name  = string
  	network_firewall_policy_id  = string
  	port_ranges = list
	service_type = string
  	},
}
```

- <b>Example</b>
```
// Copyright (c) 2021, 2022, Oracle and/or its affiliates.
############################
# Firewall Policy Services
# Firewall Policy Service - tfvars
# Allowed Values:
# network_firewall_policy_id can be the ocid or the name of the firewall Policy that needs to be attached to the Firewall
# service_type can be TCP_SERVICE and UDP_SERVICE
# Sample import command for Firewall Policy Service:
# terraform import "module.services[\"<<service terraform variable name>>\"].oci_network_firewall_network_firewall_policy_service.network_firewall_policy_service\"  networkFirewallPolicies/<<firewall-policy ocid>>/services/<<service ocid>>
############################

services = {
  OCI-FWL-Policy_svc-1 = {
  	service_name = "svc-1"
  	network_firewall_policy_id = "OCI-FWL-Policy"
  	port_ranges = [{
    		minimum_port ="12"
   		maximum_port ="23"
  	}]
  	service_type = "UDP_SERVICE"
  	},
  }
```

**10. Firewall Policy URL Lists**

- <b>Syntax</b>
```
url_lists = {
  ## key - Is a unique value to reference the resources respectively
  key = {
  	#Required
  	urllist_name  = string
  	network_firewall_policy_id  = string
  	urls = list
  	},
}
```

- <b>Example</b>
```
// Copyright (c) 2021, 2022, Oracle and/or its affiliates.
############################
# Firewall Policy URL Lists
# Firewall Policy URL List - tfvars
# Allowed Values:
# network_firewall_policy_id can be the ocid or the name of the firewall Policy that needs to be attached to the Firewall
# Sample import command for Firewall Policy URL List:
# terraform import "module.url_lists[\"<<url-list terraform variable name>>\"].oci_network_firewall_network_firewall_policy_url_list.network_firewall_policy_url_list\\"  networkFirewallPolicies/<<firewall-policy ocid>>/urlLists/<<url-list ocid>>
############################

url_lists = {
  OCI-FWL-Policy_trusted-url-list = {
  	urllist_name = "trusted-url-list"
  	network_firewall_policy_id = "OCI-FWL-Policy"
  	urls = [{
	  pattern = "*.oracle.com"
    	  type = "SIMPLE"
 	},
  	{
    	  pattern = "*.oraclecloud.com"
    	  type = "SIMPLE"
  	},
  }
```
**11. Firewall Policy Security Rules**

- <b>Syntax</b>
```
security_rules = {
  ## key - Is a unique value to reference the resources respectively
  key = {
  	#Required
  	rule_name  = string
	action = string
  	network_firewall_policy_id  = string
	condition = [{
		source_address = list
		destination_address = list
		service	= list
		application = list
		url = list
	}]
	inspection = string
	placement = string
  	},
}
```

- <b>Example</b>
```
// Copyright (c) 2021, 2022, Oracle and/or its affiliates.
############################
# Firewall Policy Security Rules
# Firewall Policy Security Rule - tfvars
# Allowed Values:
# network_firewall_policy_id can be the ocid or the name of the firewall Policy that needs to be attached to the Firewall
# action can be ALLOW, DROP, REJECT, INSPECT
# inspection can be INTRUSION_DETECTION, INTRUSION_PREVENTION
# Sample import command for Firewall Policy Security Rule:
# terraform import "module.security_rules[\"<<secrule terraform variable name>>\"].oci_network_firewall_network_firewall_policy_security_rule.network_firewall_policy_security_rule\"  networkFirewallPolicies/<<firewall-policy ocid>>/securityRules/<<secrule ocid>>
############################


security_rules = {
  OCI-FWL-Policy_rule-1 = {
        rule_name = "rule-1"
        action = "REJECT"
        network_firewall_policy_id = "OCI-FWL-Policy"
        condition = [{
            source_address = ["pub-list"]
        }]
      },
  OCI-FWL-Policy_rule-2 = {
        rule_name = "rule-2"
        action = "INSPECT"
        network_firewall_policy_id = "OCI-FWL-Policy"
        condition = [{
            destination_address = ["pub-list"]
            service = ["svclist1"]
            application = ["App-List-1"]
            url = ["trusted-url-list"]
        }]
        inspection = "INTRUSION_PREVENTION"
        after_rule = "rule-1"
      },
##Add New Security rules for phoenix here##
}
```

**12. Firewall Policies**

- <b>Syntax</b>
```
fw-policies = {
  ## key - Is a unique value to reference the resources respectively
  key = {
  	#Required
  	display_name  = string
  	compartment_id  = string
	#Optional
	defined_tags = map
	freeform_tags = map
  	},
}
```

- <b>Example</b>
```
// Copyright (c) 2021, 2022, Oracle and/or its affiliates.
############################
# Firewall Policy
# Firewall Policy - tfvars
# Allowed Values:
# compartment_id can be the ocid or the name of the Compartment where the firewall policy needs to be created
# Sample import command for Firewall Policy:
# terraform import "module.policies[\"<<policy terraform variable name>>\"].ci_network_firewall_network_firewall_policy.network_firewall_policy" <<policy ocid>>
############################

fw-policies = {
  OCI-FWL-Policy = {
        compartment_id = "Network"
        display_name = "OCI-FWL-Policy"
        defined_tags = {
                "Oracle-Tags.CreatedOn"= "2024-03-14T06:15:46.139Z" ,
                "Oracle-Tags.CreatedBy"= "oracleidentitycloudservice/abc@xyz.com"
        }
      },
  }
```




