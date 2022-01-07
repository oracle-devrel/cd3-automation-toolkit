// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Variable Block - Identity
# Fetch Compartments
############################

variable "compartment_ocids" {
            type = list(any)
            default = [{}]
}