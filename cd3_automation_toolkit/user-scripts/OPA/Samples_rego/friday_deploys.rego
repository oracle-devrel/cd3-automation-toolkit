###############################
# OCI friday deploys deny rule#
###############################


package terraform

import input as tfplan

deny[msg] {
    time.weekday(time.now_ns()) == "Friday"
    msg := "False : No deployments allowed on Fridays in OCI tenancy"
}