# **Prerequisites to use Toolkit**

- IAM policy to allow user/instance principal to manage the services that need to be created/exported using the toolkit.

- Minimum requirement is to have read access to the tenancy.

!!! Example "Sample Policies"
    Allow group <cd3_group\> to read all resources in tenancy <br>
    Allow group <cd3_group\> to manage all-resources in tenancy where any {target.resource = 'instance-family', target.resource = 'object-family', target.resource = 'volume-family', target.resource = 'virtual-network-family', target.resource = 'database-family' ,target.resource = 'dns',target.resource = 'file-family'}


!!! Example "Additional policies needed when using toolkit with Jenkins"
    Allow group <group_name\> to read devops-project in tenancy <br>
    Allow group <group_name\> to manage devops-repository-family in tenancy <br>
    Allow group <group_name\> to read buckets in tenancy <br>
    Allow group <group_name\> to manage objects in tenancy <br>