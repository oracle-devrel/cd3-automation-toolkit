terraform {

  required_version = "~> 1.2.0, < 1.3.0"
  required_providers {
    # Recommendation from ORM / OCI provider teams
    oci = {
      version = ">= 4.21.0"
    }

  }

}
