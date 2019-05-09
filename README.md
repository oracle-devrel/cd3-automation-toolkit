###################### OCI Automation ##################

When entering a new customer - to create the OCS Work VCN & VM - start at:
"oci_tenancy/OCSWorkVM".
   1a.  Create your PEM keys using the "createPEMKeys.py"
   1b. Follow the README to setup the "ocswork.properties" & "python_config" with the required values
       The python_config sets up the user, tenancy, fingerprint and private key file.


The CoreInfra & Governance have the key infra components that we use for OCI build outs.

The "oci_automation" directory has the server control scripts.

The utility scripts directory is a staging area for scripts that are reusable by other team members - such as
a.  Starting & stopping servers
b.  creating PEM keys on a linux host.
c.  Updating instance display names.

