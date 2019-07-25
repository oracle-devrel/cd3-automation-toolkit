#!/bin/python
import argparse
import sys
import oci
import datetime
#import shutil


parser = argparse.ArgumentParser(description="Takes in arg mentioning comaprtment OCID and fetches backups for boot and block vols of all instances in that compartment")
parser.add_argument("compartment_file", help="input file containing compartment info")
parser.add_argument("out_dir", help="output directory for log files having backup info")

if len(sys.argv)==2:
        parser.print_help()
        sys.exit(1)

args = parser.parse_args()
compartment_file = args.compartment_file
out_dir = args.out_dir
fname = open(compartment_file, "r")

x = str(datetime.date.today())
#date = x.strftime("%f").strip()

signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()

for line in fname:
    if not line.startswith('#'):
        linearr = line.split("=")
        comp_name=linearr[0].strip()
        comp_ocid=linearr[1].strip()

        out_file=out_dir+"/backups_"+comp_name+"_"+x+".log"

        outf=open(out_file,"w")
        if("Ryder-Prod" in comp_name):
            storage_client = oci.core.BlockstorageClient(config={'region': 'us-ashburn-1'}, signer=signer)
            compute_client = oci.core.ComputeClient(config={'region': 'us-ashburn-1'}, signer=signer)
        elif("Ryder-DR" in comp_name or "Ryder-NonProd" in comp_name):
            storage_client = oci.core.BlockstorageClient(config={'region': 'us-phoenix-1'}, signer=signer)
            compute_client = oci.core.ComputeClient(config={'region': 'us-phoenix-1'}, signer=signer)
        else:
            storage_client = oci.core.BlockstorageClient(config={}, signer=signer)
            compute_client = oci.core.ComputeClient(config={}, signer=signer)

        instances_list=oci.pagination.list_call_get_all_results(compute_client.list_instances,compartment_id=comp_ocid,lifecycle_state="RUNNING")
        inst_count=0
        for instance in instances_list.data:
            inst_count=inst_count+1
            instance_ocid=instance.id
            instance_ad=instance.availability_domain
            instance_name=instance.display_name
            outf.write(str(inst_count)+ ". "+instance_name)
            outf.write("\n===================================================================================================================================\n")
            boot_vol_attachments_list = oci.pagination.list_call_get_all_results(compute_client.list_boot_volume_attachments,availability_domain =instance_ad,
                                                                            compartment_id=comp_ocid,instance_id=instance_ocid)
            for boot_vol_attachment in boot_vol_attachments_list.data:
                if(boot_vol_attachment.lifecycle_state == "ATTACHED"):
                    boot_vol_attachment_ocid=boot_vol_attachment.id
                    boot_volume_id = boot_vol_attachment.boot_volume_id
                    outf.write("Listing backups for Boot Vol Id: "+boot_volume_id)
                    outf.write("\n===================================================================================================================================\n")
                    boot_vol_backups=oci.pagination.list_call_get_all_results(storage_client.list_boot_volume_backups,compartment_id=comp_ocid,
                                                                              boot_volume_id=boot_volume_id,sort_by="TIMECREATED")
                    outf.write("\nBackUpName                                             |   BackupType   |    LifeCycleState     |     Create_Time      |       Expiration_Time\n")
                    for boot_vol_backup in boot_vol_backups.data:
                        outf.write(boot_vol_backup.display_name+"   |   "+boot_vol_backup.type+" |   "+boot_vol_backup.lifecycle_state+"  |   "+str(boot_vol_backup.time_created)+"    |   "+str(boot_vol_backup.expiration_time))
                        outf.write("\n")
                        #print(boot_vol_backup.display_name)
                        #print(boot_vol_backup.lifecycle_state)
                        #print(boot_vol_backup.expiration_time)
                        #print(boot_vol_backup.time_created)

            block_vol_attachments_list=oci.pagination.list_call_get_all_results(compute_client.list_volume_attachments,compartment_id=comp_ocid,
                                                                            instance_id=instance_ocid)
            for block_vol_attachment in block_vol_attachments_list.data:
                if(block_vol_attachment.lifecycle_state == "ATTACHED"):
                    volume_id =block_vol_attachment.volume_id
                    outf.write("\n===================================================================================================================================\n")
                    outf.write("Listing backups for Block Vol Id: " + volume_id)
                    outf.write("\n===================================================================================================================================\n")

                    block_vol_backups = oci.pagination.list_call_get_all_results(storage_client.list_volume_backups,
                                                                                compartment_id=comp_ocid,
                                                                                volume_id=volume_id,
                                                                                sort_by="TIMECREATED")
                    outf.write("\nBackUpName                                             |   BackupType   |    LifeCycleState     |     Create_Time      |       Expiration_Time\n")
                    for block_vol_backup in block_vol_backups.data:
                        outf.write(block_vol_backup.display_name + "   |   " + block_vol_backup.type + " |   "+ block_vol_backup.lifecycle_state + "  |   " + str(block_vol_backup.time_created) + "    |   " + str(block_vol_backup.expiration_time))
                        outf.write("\n")
                    outf.write("\n=====================================================================================\n")
                    #    print(block_vol_backup.display_name)
                    #    print(block_vol_backup.lifecycle_state)
                    #    print(block_vol_backup.expiration_time)
                    #    print(block_vol_backup.time_created)


print("Check output files created at "+out_dir)