<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.0.0 |
| <a name="requirement_oci"></a> [oci](#requirement\_oci) | >= 4.65.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_oci"></a> [oci](#provider\_oci) | 4.65.0 |

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_alarms"></a> [alarms](#module\_alarms) | ./modules/managementservices/alarm | n/a |
| <a name="module_custom-dhcps"></a> [custom-dhcps](#module\_custom-dhcps) | ./modules/network/custom-dhcp | n/a |
| <a name="module_default-dhcps"></a> [default-dhcps](#module\_default-dhcps) | ./modules/network/default-dhcp | n/a |
| <a name="module_default-route-tables"></a> [default-route-tables](#module\_default-route-tables) | ./modules/network/default-route-table | n/a |
| <a name="module_default-security-lists"></a> [default-security-lists](#module\_default-security-lists) | ./modules/network/default-sec-list | n/a |
| <a name="module_drg-attachments"></a> [drg-attachments](#module\_drg-attachments) | ./modules/network/drg-attachment | n/a |
| <a name="module_drg-route-distribution-statements"></a> [drg-route-distribution-statements](#module\_drg-route-distribution-statements) | ./modules/network/drg-route-distribution-statement | n/a |
| <a name="module_drg-route-distributions"></a> [drg-route-distributions](#module\_drg-route-distributions) | ./modules/network/drg-route-distribution | n/a |
| <a name="module_drg-route-rules"></a> [drg-route-rules](#module\_drg-route-rules) | ./modules/network/drg-route-rule | n/a |
| <a name="module_drg-route-tables"></a> [drg-route-tables](#module\_drg-route-tables) | ./modules/network/drg-route-table | n/a |
| <a name="module_drgs"></a> [drgs](#module\_drgs) | ./modules/network/drg | n/a |
| <a name="module_events"></a> [events](#module\_events) | ./modules/managementservices/event | n/a |
| <a name="module_exported-lpgs"></a> [exported-lpgs](#module\_exported-lpgs) | ./modules/network/lpg | n/a |
| <a name="module_fetch-vcns"></a> [fetch-vcns](#module\_fetch-vcns) | ./modules/network/network-data/vcns | n/a |
| <a name="module_hub-lpgs"></a> [hub-lpgs](#module\_hub-lpgs) | ./modules/network/lpg | n/a |
| <a name="module_iam-compartments"></a> [iam-compartments](#module\_iam-compartments) | ./modules/identity/iam-compartment | n/a |
| <a name="module_iam-groups"></a> [iam-groups](#module\_iam-groups) | ./modules/identity/iam-group | n/a |
| <a name="module_iam-policies"></a> [iam-policies](#module\_iam-policies) | ./modules/identity/iam-policy | n/a |
| <a name="module_igws"></a> [igws](#module\_igws) | ./modules/network/igw | n/a |
| <a name="module_log-groups"></a> [log-groups](#module\_log-groups) | ./modules/managementservices/log-group | n/a |
| <a name="module_logs"></a> [logs](#module\_logs) | ./modules/managementservices/log | n/a |
| <a name="module_ngws"></a> [ngws](#module\_ngws) | ./modules/network/ngw | n/a |
| <a name="module_none-lpgs"></a> [none-lpgs](#module\_none-lpgs) | ./modules/network/lpg | n/a |
| <a name="module_notifications-subscriptions"></a> [notifications-subscriptions](#module\_notifications-subscriptions) | ./modules/managementservices/notification-subscription | n/a |
| <a name="module_notifications-topics"></a> [notifications-topics](#module\_notifications-topics) | ./modules/managementservices/notification-topic | n/a |
| <a name="module_nsg-rules"></a> [nsg-rules](#module\_nsg-rules) | ./modules/network/nsg-rules | n/a |
| <a name="module_nsgs"></a> [nsgs](#module\_nsgs) | ./modules/network/nsg | n/a |
| <a name="module_peer-lpgs"></a> [peer-lpgs](#module\_peer-lpgs) | ./modules/network/lpg | n/a |
| <a name="module_route-tables"></a> [route-tables](#module\_route-tables) | ./modules/network/route-table | n/a |
| <a name="module_security-lists"></a> [security-lists](#module\_security-lists) | ./modules/network/sec-list | n/a |
| <a name="module_sgws"></a> [sgws](#module\_sgws) | ./modules/network/sgw | n/a |
| <a name="module_spoke-lpgs"></a> [spoke-lpgs](#module\_spoke-lpgs) | ./modules/network/lpg | n/a |
| <a name="module_sub-compartments-level1"></a> [sub-compartments-level1](#module\_sub-compartments-level1) | ./modules/identity/iam-compartment | n/a |
| <a name="module_sub-compartments-level2"></a> [sub-compartments-level2](#module\_sub-compartments-level2) | ./modules/identity/iam-compartment | n/a |
| <a name="module_sub-compartments-level3"></a> [sub-compartments-level3](#module\_sub-compartments-level3) | ./modules/identity/iam-compartment | n/a |
| <a name="module_sub-compartments-level4"></a> [sub-compartments-level4](#module\_sub-compartments-level4) | ./modules/identity/iam-compartment | n/a |
| <a name="module_sub-compartments-level5"></a> [sub-compartments-level5](#module\_sub-compartments-level5) | ./modules/identity/iam-compartment | n/a |
| <a name="module_subnets"></a> [subnets](#module\_subnets) | ./modules/network/subnet | n/a |
| <a name="module_vcns"></a> [vcns](#module\_vcns) | ./modules/network/vcn | n/a |

## Resources

| Name | Type |
|------|------|
| [oci_core_drg_route_distributions.drg_route_distributions](https://registry.terraform.io/providers/hashicorp/oci/latest/docs/data-sources/core_drg_route_distributions) | data source |
| [oci_core_drg_route_tables.drg_route_tables](https://registry.terraform.io/providers/hashicorp/oci/latest/docs/data-sources/core_drg_route_tables) | data source |
| [oci_identity_availability_domains.availability_domains](https://registry.terraform.io/providers/hashicorp/oci/latest/docs/data-sources/identity_availability_domains) | data source |
| [oci_identity_compartments.compartments](https://registry.terraform.io/providers/hashicorp/oci/latest/docs/data-sources/identity_compartments) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_alarms"></a> [alarms](#input\_alarms) | n/a | `map(any)` | `{}` | no |
| <a name="input_compartment_ocids"></a> [compartment\_ocids](#input\_compartment\_ocids) | # Do Not Modify #START\_Compartment\_OCIDs# | `list(any)` | <pre>[<br>  {}<br>]</pre> | no |
| <a name="input_compartments"></a> [compartments](#input\_compartments) | n/a | `map(any)` | <pre>{<br>  "compartment_level1": {},<br>  "compartment_level2": {},<br>  "compartment_level3": {},<br>  "compartment_level4": {},<br>  "compartment_level5": {},<br>  "root": {}<br>}</pre> | no |
| <a name="input_custom_dhcps"></a> [custom\_dhcps](#input\_custom\_dhcps) | n/a | `map(any)` | `{}` | no |
| <a name="input_data_drg_route_table_distributions"></a> [data\_drg\_route\_table\_distributions](#input\_data\_drg\_route\_table\_distributions) | n/a | `map(any)` | `{}` | no |
| <a name="input_data_drg_route_tables"></a> [data\_drg\_route\_tables](#input\_data\_drg\_route\_tables) | n/a | `map(any)` | `{}` | no |
| <a name="input_default_dhcps"></a> [default\_dhcps](#input\_default\_dhcps) | n/a | `map(any)` | `{}` | no |
| <a name="input_default_route_tables"></a> [default\_route\_tables](#input\_default\_route\_tables) | n/a | `map(any)` | `{}` | no |
| <a name="input_default_seclists"></a> [default\_seclists](#input\_default\_seclists) | n/a | `map(any)` | `{}` | no |
| <a name="input_drg_attachments"></a> [drg\_attachments](#input\_drg\_attachments) | n/a | `map(any)` | `{}` | no |
| <a name="input_drg_route_distribution_statements"></a> [drg\_route\_distribution\_statements](#input\_drg\_route\_distribution\_statements) | n/a | `map(any)` | `{}` | no |
| <a name="input_drg_route_distributions"></a> [drg\_route\_distributions](#input\_drg\_route\_distributions) | n/a | `map(any)` | `{}` | no |
| <a name="input_drg_route_rules"></a> [drg\_route\_rules](#input\_drg\_route\_rules) | n/a | `map(any)` | `{}` | no |
| <a name="input_drg_route_tables"></a> [drg\_route\_tables](#input\_drg\_route\_tables) | n/a | `map(any)` | `{}` | no |
| <a name="input_drgs"></a> [drgs](#input\_drgs) | n/a | `map(any)` | `{}` | no |
| <a name="input_events"></a> [events](#input\_events) | n/a | `map(any)` | `{}` | no |
| <a name="input_fingerprint"></a> [fingerprint](#input\_fingerprint) | n/a | `string` | `"<SSH KEY FINGERPRINT> - Use the create_keys.sh for easily creating keys and its fingerprint> "` | no |
| <a name="input_groups"></a> [groups](#input\_groups) | n/a | `map(any)` | `{}` | no |
| <a name="input_igws"></a> [igws](#input\_igws) | n/a | `map(any)` | `{}` | no |
| <a name="input_log_groups"></a> [log\_groups](#input\_log\_groups) | n/a | `map(any)` | `{}` | no |
| <a name="input_logs"></a> [logs](#input\_logs) | n/a | `map(any)` | `{}` | no |
| <a name="input_lpgs"></a> [lpgs](#input\_lpgs) | n/a | `map(any)` | <pre>{<br>  "exported-lpgs": {},<br>  "hub-lpgs": {},<br>  "none-lpgs": {},<br>  "peer-lpgs": {},<br>  "spoke-lpgs": {}<br>}</pre> | no |
| <a name="input_ngws"></a> [ngws](#input\_ngws) | n/a | `map(any)` | `{}` | no |
| <a name="input_notifications_subscriptions"></a> [notifications\_subscriptions](#input\_notifications\_subscriptions) | n/a | `map(any)` | `{}` | no |
| <a name="input_notifications_topics"></a> [notifications\_topics](#input\_notifications\_topics) | n/a | `map(any)` | `{}` | no |
| <a name="input_nsg_rules"></a> [nsg\_rules](#input\_nsg\_rules) | n/a | `map(any)` | `{}` | no |
| <a name="input_nsgs"></a> [nsgs](#input\_nsgs) | n/a | `map(any)` | `{}` | no |
| <a name="input_policies"></a> [policies](#input\_policies) | n/a | `map(any)` | `{}` | no |
| <a name="input_private_key_path"></a> [private\_key\_path](#input\_private\_key\_path) | n/a | `string` | `"<The Private key file path> - If you've used the createPEMKeys.py then the full path of where the .pem file is>"` | no |
| <a name="input_region"></a> [region](#input\_region) | n/a | `string` | `"<OCI Tenancy Region where these objects will be created - us-phoenix-1 or us-ashburn-1>"` | no |
| <a name="input_route_tables"></a> [route\_tables](#input\_route\_tables) | n/a | `map(any)` | `{}` | no |
| <a name="input_seclists"></a> [seclists](#input\_seclists) | n/a | `map(any)` | `{}` | no |
| <a name="input_sgws"></a> [sgws](#input\_sgws) | n/a | `map(any)` | `{}` | no |
| <a name="input_ssh_public_key"></a> [ssh\_public\_key](#input\_ssh\_public\_key) | n/a | `string` | `"<YOUR SSH PUB KEY STRING HERE>"` | no |
| <a name="input_subnets"></a> [subnets](#input\_subnets) | n/a | `map(any)` | `{}` | no |
| <a name="input_tenancy_ocid"></a> [tenancy\_ocid](#input\_tenancy\_ocid) | n/a | `string` | `"<YOUR TENANCY OCID HERE>"` | no |
| <a name="input_user_ocid"></a> [user\_ocid](#input\_user\_ocid) | n/a | `string` | `"<USER OCID HERE>"` | no |
| <a name="input_vcns"></a> [vcns](#input\_vcns) | n/a | `map(any)` | `{}` | no |

## Outputs

No outputs.
<!-- END_TF_DOCS -->