
## Make sure the oci python environment has already been setup using the create_oci_python_env.sh
(and follow the associated readme)

1.  Unpack OVA and upload to Object Store
	b.  Disk-1 is normally the C drive or root partition and will be a vmdk.
	c.  use "upload_boot_volume.py <full path to vmdk>" to upload to object store.
	d.  use "create_boot_volume.py <disk_name>" to create the image.  This will take a long time -but the script will return instantly with the response of "Importing"
	e.  Once the Import is complete ( check via console) - you can Launch an Instance from the Console.




