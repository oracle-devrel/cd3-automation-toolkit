# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
# Azure RM Terraform Provider
provider "azurerm" {
  features {}

  subscription_id = "<SUBSCRIPTION ID HERE>"
  tenant_id       = "<TENANT ID HERE>"
  client_id       = "<CLIENT ID HERE>"
  client_secret   = "<CLIENT SECRET HERE>"
}