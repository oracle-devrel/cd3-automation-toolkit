// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Module Block - Network
# Fetch ADs
############################

module "fetch-ads" {
  source         = "./modules/network/network-data/ads"
  tenancy_ocid = var.tenancy_ocid
}
