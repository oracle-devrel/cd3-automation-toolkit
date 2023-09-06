##################################################################
#Deny Launching instances for a given compartments,subnets,shapes#
##################################################################


package terraform

import future.keywords.in
import input as tfplan

allowed_compartment_ocids = ["ocid1.compartment.oc1..aaaaaaaapmksuq5cemyfej4ljckx5yt32aajhcvvpon2bhnxn26odngehd7a"]
allowed_subnet_ids = ["ocid1.subnet.oc1.phx.aaaaaaaa275meofdizqggkyfucfkxypgbx22aj5vhrtmqhbbkueftnuh3l3q"]
allowed_vm_shapes = ["VM.Standard3.Flex"]
allowed_vm_images = ["ocid1.image.oc1.phx.aaaaaaaagbskuejoeto55cp2rgohle3qiesqv76irqoje2bnz64lsiokwh2a"]



deny_vm_launch[msg] {
     resource := tfplan.resource_changes[_]
     compartment_id = resource.change.after.compartment_id

     some ocid in allowed_compartment_ocids
        deny := contains(compartment_id, ocid)
	msg := sprintf(
         "%s: resource is not allowed to launch in compartment_id %q",
          [resource.address, ocid]
          )
	
}

deny_vm_subnet_launch[reason] {
    resource := tfplan.resource_changes[_]
    subnet_id = resource.change.after.create_vnic_details[_].subnet_id

    some subnet in allowed_subnet_ids
        deny_launch := contains(subnet_id, subnet)
	reason := sprintf(
	"%s: resource is not allowed to launch in subnet_id %q",
	[resource.address, subnet_id]
	)
  
}

deny_shape[msg] {
    resource := tfplan.resource_changes[_]
    vm_shape = resource.change.after.shape

    some shape in allowed_vm_shapes
       deny_vm := contains(vm_shape, shape)
       msg := sprintf(
        "%s: resource is not allowed to launch with instance shape %q",
        [resource.address, vm_shape]
        )

}

deny_image[msg] {
   resource := tfplan.resource_changes[_]
   vm_image = resource.change.after.source_details[_].source_id

   some image in allowed_vm_images
      deny_image := contains(vm_image, image)
      msg :=  sprintf(
        "%s: resource is not allowed to launch with image OCID %q",
        [resource.address, vm_image]
        )


}


