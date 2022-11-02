#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI core components
# Resource Manager
#
# Author: Shruthi Subramanian
#

import argparse
import os
import shutil
import datetime
import oci
import time
import csv
import base64
from commonTools import *
from oci.config import DEFAULT_LOCATION
from oci.resource_manager.models import CreateStackDetails
from oci.resource_manager.models import UpdateStackDetails
from oci.resource_manager.models import CreateZipUploadConfigSourceDetails
from oci.resource_manager.models import UpdateZipUploadConfigSourceDetails

rm_name_ocid_map = {}
rm_region_name_map = {}
comp_name = ''
stack_ocid = ''

def create_rm(region,comp_name,ocs_stack,ct,rm_stack_name,rm_ocids_file,create_rm_flag):
    print("\nCreating a new Resource Manager Stack for " + region + ".......................")
    stackdetails = CreateStackDetails()
    zipConfigSource = CreateZipUploadConfigSourceDetails()
    stackdetails.description = "Created using Automation Tool Kit"
    stackdetails.terraform_version = "1.0.x"
    try:
        stackdetails.compartment_id = ct.ntk_compartment_ids[comp_name]
    except KeyError as fe:
        print("Compartment specified for the stack previously doesn't exist in OCI")
        print("Removing rm_ocids.csv file from outdir")
        if os.path.exists(rm_ocids_file):
            os.remove(rm_ocids_file)
        comp_name = input("Enter a new Compartment Name for Resource Manager: ")
        stackdetails.compartment_id = ct.ntk_compartment_ids[comp_name]

    stackdetails.display_name = rm_stack_name + "-" + region
    with open(region + ".zip", 'rb') as file:
        zipContents = file.read()
        encodedZip = base64.b64encode(zipContents).decode('ascii')
    zipConfigSource.config_source_type = 'ZIP_UPLOAD'
    zipConfigSource.zip_file_base64_encoded = encodedZip
    stackdetails.config_source = zipConfigSource
    mstack = ocs_stack.create_stack(create_stack_details=stackdetails)
    stack_ocid = mstack.data.id
    print("Resource Manager Stack is created for " + region + " region. ")
    print("Resource Manager Stack OCID: "+ stack_ocid)
    print("Resource Manager Stack Name: "+rm_stack_name+"-"+region)
    write_to_ocids_file(rm_ocids_file, region, rm_stack_name+"-"+region, stack_ocid,create_rm_flag,comp_name)
    return stack_ocid

def write_to_ocids_file(rm_ocids_file, rm_region, rm_name,rm_ocid,create_rm_flag,comp_name):
    #If the file exists
    if os.path.exists(rm_ocids_file):
        #If the RM is created newly or If there is no data in the file:
        if create_rm_flag == 1 or  os.stat(rm_ocids_file).st_size == 0:
            with open(rm_ocids_file, 'a+') as n:
                n.write(comp_name+";"+rm_region+";"+rm_name + ";" + rm_ocid + '\n')
            n.close()
        else:
            #If there is data in the file; Take a back up of existing file and update the existing RM details
            if create_rm_flag == 0:
                os.replace(rm_ocids_file, rm_ocids_file + "_backup")
                with open(rm_ocids_file + "_backup", 'r+') as f:
                    with open(rm_ocids_file, 'w+') as n:
                        for line in f:
                            if rm_name in line and comp_name in line:
                                n.write(line.replace(line, comp_name+";"+rm_region+";"+rm_name + ";" + rm_ocid + '\n'))
                            else:
                                n.write(line)
                    n.close()
                f.close()
    else:
        #If file does not exist create a new one
        if create_rm_flag == 1:
            with open(rm_ocids_file, 'w+') as n:
                n.write(comp_name+";"+rm_region+";"+rm_name + ";" + rm_ocid + '\n')
            n.close()

def parse_args():
    # Read the input arguments
    parser = argparse.ArgumentParser(description="Creates Resource Manager and performs terraform plan or apply")
    parser.add_argument('outdir', help='Output directory for creation of TF files')
    parser.add_argument('prefix', help='TF files prefix')
    parser.add_argument("--configFileName", help="Config file name", required=False)
    return parser.parse_args()


def create_resource_manager(outdir, prefix, config=DEFAULT_LOCATION):

    configFileName = config
    config = oci.config.from_file(file_location=configFileName)

    ct = commonTools()
    ct.get_subscribedregions(configFileName)
    ct.get_network_compartment_ids(config['tenancy'],"root",configFileName)

    new_config = config
    new_config.__setitem__("region", str(ct.region_dict[ct.home_region]))
    ocs_stack = oci.resource_manager.ResourceManagerClient(new_config)

    x = datetime.datetime.now()
    date = x.strftime("%f").strip()

    #1. Copy files to RM directory
    rm_dir = outdir+'/RM/'
    rm_dir_zip = outdir+'/'+prefix+'.zip'

    #Take a backup of zip file if it exists
    if os.path.exists(rm_dir_zip):
        shutil.copy(rm_dir_zip,rm_dir_zip+"_backup")

    #Copy all the TF files to RM directory
    try:
        shutil.copytree(outdir, rm_dir, ignore=shutil.ignore_patterns('*.terraform.lock.hcl','*.terraform','provider.tf','*.zip*'))
    except FileExistsError as fe:
        shutil.rmtree(rm_dir)
        shutil.copytree(outdir, rm_dir, ignore=shutil.ignore_patterns('*.terraform.lock.hcl','*.terraform', 'provider.tf','*.zip*'))

    #2. Change the provider.tf to include just the region variable in all the subscribed regions
    for region in ct.all_regions:
        with open(outdir+'/'+region+'/provider.tf') as origfile, open(rm_dir+'/'+region + '/provider.tf', 'w') as newfile:
            for line in origfile:
                if 'version' in line or 'tenancy_ocid' in line or "user_ocid" in line or "fingerprint" in line or "private_key_path" in line:
                    pass
                elif 'terraform {' in line:
                    experimental_line = "experiments = [module_variable_optional_attrs]"
                    line = line+"\n  "+experimental_line+"\n  "
                    newfile.write(line)
                else:
                    newfile.write(line)

    skipline = False


    for region in ct.all_regions:
        with open(outdir+'/'+region+'/variables_' + region + '.tf') as origfile, open(rm_dir+'/'+region + '/variables_' + region + '.tf','w') as newfile:
            for line in origfile:
                if "user_ocid"  in line or "fingerprint"  in line or "private_key_path" in line:
                    skipline = True
                if not skipline:
                    newfile.write(line)
                if skipline:
                    if ('}' in line):
                        skipline = False


    #4. Create RM if not present and store the ocid in a tempfile;
    os.chdir(rm_dir)
    rm_ocids_file = outdir+'/rm_ocids.csv'
    if os.path.exists(rm_ocids_file):
        with open(rm_ocids_file) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=';')
            for row in csv_reader:
                comp_name = row[0]
                rm_region = row[1]
                rm_name = row[2]
                rm_ocid = row[3]
                rm_region_name_map.update({rm_region: rm_name})
                rm_name_ocid_map.update({rm_name:rm_ocid})
        if comp_name == '':
            comp_name = input("Resource Manager Compartment Name: ")
    else:
        comp_name = input("Resource Manager Compartment Name: ")

    for region in ct.all_regions:
        shutil.make_archive(region, 'zip', region)
        rm_name = prefix + "-" + region

        if rm_name_ocid_map != {}:
            if region in rm_region_name_map.keys():
                ocid = rm_name_ocid_map[rm_region_name_map[region]]
                try:
                    status = ocs_stack.get_stack(ocid).data
                    if status.lifecycle_state == "ACTIVE":
                        print("\nResource Manager ("+rm_region_name_map[region]+") "+ ocid + " for region " + region + " exists in '" + comp_name + "' Compartment.Updating the same.................")
                        updatestackdetails = UpdateStackDetails()
                        zipConfigSource = UpdateZipUploadConfigSourceDetails()
                        zipConfigSource.config_source_type = 'ZIP_UPLOAD'
                        updatestackdetails.display_name = rm_region_name_map[region]
                        with open(region + ".zip", 'rb') as file:
                            zipContents = file.read()
                            encodedZip = base64.b64encode(zipContents).decode('ascii')
                        zipConfigSource.config_source_type = 'ZIP_UPLOAD'
                        zipConfigSource.zip_file_base64_encoded = encodedZip
                        updatestackdetails.config_source = zipConfigSource
                        updatestackdetails.terraform_version = "1.0.x"
                        updatestackdetails.description = "Updated by Automation Tool Kit"
                        mstack = ocs_stack.update_stack(stack_id=ocid, update_stack_details=updatestackdetails)
                        stack_ocid = mstack.data.id
                        time.sleep(5)

                except Exception as e:
                    print("\nResource Manager ("+rm_name+") "+ ocid + " for region " + region + " created previously in compartment '" + comp_name + "' is inactive/terminated!!")
                    create_rm_flag = 0
                    stack_ocid = create_rm(region, comp_name, ocs_stack, ct, prefix, rm_ocids_file,create_rm_flag)

            else:
                create_rm_flag = 1
                stack_ocid = create_rm(region, comp_name, ocs_stack, ct, prefix, rm_ocids_file, create_rm_flag)

        else:
            create_rm_flag = 1
            stack_ocid = create_rm(region, comp_name, ocs_stack, ct, prefix,rm_ocids_file,create_rm_flag)

        # 5. Terraform state import if it exists
        tfstate_file = rm_dir + '/' + region + '/terraform.tfstate'
        if os.path.exists(outdir+'/'+region+'/terraform.tfstate'):
            create_job_details = oci.resource_manager.models.CreateJobDetails()
            createjoboperationdetails = oci.resource_manager.models.CreateImportTfStateJobOperationDetails()
            createjoboperationdetails.operation = "IMPORT_TF_STATE"
            with open(tfstate_file,'rb') as file:
                encodetfstate = file.read()
                encodetfstate = base64.b64encode(encodetfstate).decode('ascii')
            createjoboperationdetails.tf_state_base64_encoded = encodetfstate
            create_job_details.display_name = rm_name + "-TFImport"
            create_job_details.job_operation_details = createjoboperationdetails
            create_job_details.operation = "IMPORT_TF_STATE"
            create_job_details.stack_id = stack_ocid
            print("\nUploading Terraform State file to Resource Manager for region "+region+"..............\n")
            ocs_stack.create_job(create_job_details)

    os.chdir("../..")
    base_name = outdir+'/'+prefix
    shutil.make_archive(base_name,'zip',rm_dir)

    # Remove the contents of RM directory;
    if os.path.exists(rm_dir):
        #remove existing RM dir
        shutil.rmtree(rm_dir)

    print("\nProcess Completed !!!\n"
          "Terraform Configuration (and/or) State files are uploaded to  Resource Manager Stack in "+comp_name+" Compartment.")


if __name__ == '__main__':
    args = parse_args()
    create_resource_manager(args.outdir, args.prefix, args.config)
