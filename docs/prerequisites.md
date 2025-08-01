# **Prerequisites to use the CD3 Toolkit**

Before using the CD3 Toolkit to create or export resources in OCI, make sure that the required IAM policies are in place.

❗At a minimum, users or instance principals must have <b>read access</b> to the tenancy.


!!! Example "Minimum Policy Requirement"
    Allow group <i><group_name\></i>  to read all resources in tenancy

<br>

<b>🔐 Sample IAM Policies to Manage Specific Services</b>

To allow creation and export of specific OCI services using the toolkit, apply the following sample scoped policy:

!!! Example "Sample Policy for Specific OCI Services"
    Allow group <i><group_name\></i> to manage all-resources in tenancy where any {target.resource = 'instance-family', target.resource = 'object-family', target.resource = 'volume-family', target.resource = 'virtual-network-family', target.resource = 'database-family', target.resource = 'dns', target.resource = 'file-family'}

<br> 

<b>🔐 Additional IAM Policies for Jenkins Integrations </b>

These permissions enable Jenkins to interact with OCI DevOps and Object Storage for CD3 automation

!!! Example "Additional policies needed when using toolkit with Jenkins"
    Allow group <i><group_name\></i> to read devops-project in tenancy <br>
    Allow group <i><group_name\></i> to manage devops-repository-family in tenancy <br>
    Allow group <i><group_name\></i> to read buckets in tenancy <br>
    Allow group <i><group_name\></i>to manage objects in tenancy <br>


> Replace <i><group_name\></i> with the actual IAM group in your tenancy.