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
from zipfile import ZipFile
import shutil
import time
import csv
import base64
from commonTools import *
from oci.config import DEFAULT_LOCATION
from oci.resource_manager.models import CreateStackDetails
from oci.resource_manager.models import UpdateStackDetails
from oci.resource_manager.models import CreateZipUploadConfigSourceDetails
from oci.resource_manager.models import UpdateZipUploadConfigSourceDetails

rm_region_service_map ={}
rm_region_comp_map = {}
comp_name = ''
stack_ocid = ''
tfStr ={}

def create_rm(service_rm_name, comp_id,ocs_stack,svcs):
    stackdetails = CreateStackDetails()
    zipConfigSource = CreateZipUploadConfigSourceDetails()
    if svcs == []:
        stackdetails.description = "Created by Automation ToolKit"
    else:
        stackdetails.description = "Created by Automation ToolKit for services - "+ ','.join(svcs)
    stackdetails.terraform_version = "1.5.x"
    stackdetails.compartment_id = comp_id
    stackdetails.display_name = service_rm_name

    with open(service_rm_name + ".zip", 'rb') as file:
        zipContents = file.read()
        encodedZip = base64.b64encode(zipContents).decode('ascii')
    zipConfigSource.config_source_type = 'ZIP_UPLOAD'
    zipConfigSource.zip_file_base64_encoded = encodedZip
    stackdetails.config_source = zipConfigSource
    mstack = ocs_stack.create_stack(create_stack_details=stackdetails)
    stack_ocid = mstack.data.id

    print("Resource Manager Stack OCID: "+ stack_ocid)
    print("Resource Manager Stack Name: "+service_rm_name)
    return stack_ocid

def update_rm(service_rm_name,service_rm_ocid,ocs_stack,svcs):
    updatestackdetails = UpdateStackDetails()
    zipConfigSource = UpdateZipUploadConfigSourceDetails()
    zipConfigSource.config_source_type = 'ZIP_UPLOAD'
    updatestackdetails.display_name = service_rm_name

    with open(service_rm_name + ".zip", 'rb') as file:
        zipContents = file.read()
        encodedZip = base64.b64encode(zipContents).decode('ascii')
    zipConfigSource.config_source_type = 'ZIP_UPLOAD'
    zipConfigSource.zip_file_base64_encoded = encodedZip
    updatestackdetails.config_source = zipConfigSource
    updatestackdetails.terraform_version = "1.5.x"
    if svcs == []:
        updatestackdetails.description = "Updated by Automation ToolKit"
    else:
        updatestackdetails.description = "Updated by Automation ToolKit for services - "+ ','.join(svcs)
    mstack = ocs_stack.update_stack(stack_id=service_rm_ocid, update_stack_details=updatestackdetails)
    stack_ocid = mstack.data.id

    time.sleep(5)
    return stack_ocid

# Execution of the code begins here
def create_resource_manager(outdir,var_file, outdir_struct,prefix,auth_mechanism, config_file, ct, regions):

    # Get list of services for one directory
    dir_svc_map = {}
    for svc, dir in outdir_struct.items():
        dir_svc_map[dir]=[]

    for svc,dir in outdir_struct.items():
        dir_svc_map[dir].append(svc)


    print("Fetching Compartment Detail. Please wait...")

    config, signer = ct.authenticate(auth_mechanism, config_file)
    #ct.get_network_compartment_ids(config['tenancy'],"root",configFileName)
    ct.get_compartment_map(var_file,'RM')
    print("Proceeding further...")

    x = datetime.datetime.now()
    date = x.strftime("%f").strip()

    save_outdir_struct = outdir_struct.copy()
    for region in regions:
        region=region.strip().lower()

        region_dir=outdir + "/" + region

        for path, subdirs, files in os.walk(region_dir):
            for name in files:
                filep = os.path.join(path, name)
                if 'backend.tf' in filep:
                    f_b=open(filep,"r")
                    f_d=f_b.read()
                    if 'This line will be removed when using remote state' not in f_d:
                        print("Toolkit has been configured to use remote state. OCI Resource Manager does not support that. Exiting!")
                        exit(1)

        if region == 'global':
            outdir_struct = {'rpc':'rpc'}
        else:
            outdir_struct = save_outdir_struct.copy()

        rm_dir = region_dir + '/RM/'

        # 1. Copy all the TF files for specified regions to RM directory. Also copy modules directory
        try:
            shutil.copytree(region_dir, rm_dir, ignore=shutil.ignore_patterns('*.terraform.lock.hcl','*.terraform','provider.tf','*.zip*','*.safe*','*.log*','*cis_report','*.csv*','*cd3validator', 'variables_*.tf*'))
            shutil.copytree(outdir+"/modules", rm_dir)
        except FileExistsError as fe:
            shutil.rmtree(rm_dir)
            shutil.copytree(region_dir, rm_dir, ignore=shutil.ignore_patterns('*.terraform.lock.hcl','*.terraform','provider.tf','*.zip*','*.safe*','*.log*','*cis_report','*.csv*','*cd3validator', 'variables_*.tf*'))
            shutil.copytree(outdir+"/modules", rm_dir+"/modules")

        #2. Change the provider.tf and variables_<region>.tf to include just the region variable in all stacks for specified regions
        tfStr[region]=''

        # Copy provider.tf to each region dir within RM
        if len(outdir_struct.items())==0:
            try:
                with open(region_dir + '/provider.tf') as origfile, open(rm_dir + '/provider.tf', 'w') as newfile:
                    for line in origfile:
                        if 'version' in line or 'tenancy_ocid' in line or "user_ocid" in line or "fingerprint" in line or "private_key_path" in line:
                            pass
                        #elif 'terraform {' in line:
                        #    experimental_line = "experiments = [module_variable_optional_attrs]"
                        #    line = line + "\n  " + experimental_line + "\n  "
                        #    newfile.write(line)
                        else:
                            newfile.write(line)
            except FileNotFoundError as e:
                pass

            # Copy variables_<region>.tf to each region directory within RM
            skipline = False
            try:
                with open(region_dir + '/variables_' + region + '.tf') as origfile, open(rm_dir + '/variables_' + region + '.tf', 'w') as newfile:
                    for line in origfile:
                        '''
                        if 'gateway_route_table = optional(bool,false)' in line:
                            line = line.replace('gateway_route_table = optional(bool,false)','gateway_route_table = optional(bool)')
                        if 'default_route_table = optional(bool,false)' in line:
                            line = line.replace('default_route_table = optional(bool,false)','default_route_table = optional(bool)')
                        '''
                        if "user_ocid" in line or "fingerprint" in line or "private_key_path" in line:
                            skipline = True
                        if not skipline:
                            newfile.write(line)
                        if skipline:
                            if ('}' in line):
                                skipline = False
            except FileNotFoundError as e:
                pass
        else:
            for service,service_dir in outdir_struct.items():
                #Copy provider.tf to each service_dir
                try:
                    with open(region_dir+'/'+service_dir+'/provider.tf') as origfile, open(rm_dir+'/'+service_dir+ '/provider.tf', 'w') as newfile:
                        for line in origfile:
                            if 'version' in line or 'tenancy_ocid' in line or "user_ocid" in line or "fingerprint" in line or "private_key_path" in line:
                                pass

                            #elif 'terraform {' in line:
                            #    experimental_line = "experiments = [module_variable_optional_attrs]"
                            #    line = line+"\n  "+experimental_line+"\n  "
                            #    newfile.write(line)
                            else:
                                newfile.write(line)
                except FileNotFoundError as e:
                    pass

                #Copy variables_<region>.tf to each service_dir
                skipline = False
                try:
                    with open(region_dir+'/'+service_dir+'/variables_' + region + '.tf') as origfile, open(rm_dir + '/'+ service_dir +'/variables_' + region + '.tf','w') as newfile:
                        for line in origfile:
                            '''
                            if 'gateway_route_table = optional(bool,false)' in line:
                                line = line.replace('gateway_route_table = optional(bool,false)',
                                                    'gateway_route_table = optional(bool)')
                            if 'default_route_table = optional(bool,false)' in line:
                                line = line.replace('default_route_table = optional(bool,false)',
                                                    'default_route_table = optional(bool)')
                            '''
                            if "user_ocid"  in line or "fingerprint"  in line or "private_key_path" in line:
                                skipline = True
                            if not skipline:
                                newfile.write(line)
                            if skipline:
                                if ('}' in line):
                                    skipline = False
                except FileNotFoundError as e:
                    pass

    if ct.orm_comp_filter == "null":
        comp_name = None
    else:
        comp_name = ct.orm_comp_filter if ct.orm_comp_filter else input(
            "Enter Resource Manager Compartment Name : ")

    #3. Read existing rm_ocids.csv file and get the data in map;
    for region in regions:
        rm_ocids_file = outdir+'/'+region+'/rm_ocids.csv'
        if os.path.exists(rm_ocids_file):
            with open(rm_ocids_file) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=';')
                for row in csv_reader:
                    if (len(row)==0):
                        continue
                    rm_region = row[0]
                    rm_comp_name = row[1]
                    rm_name = row[2]
                    rm_ocid = row[3]

                    rm_region_service_map.update({(rm_region,rm_name):(rm_comp_name,rm_ocid)})
                #put comp name of last stack in the variable
                comp_name = rm_comp_name
        else:
            comp_name = comp_name

            #comp_name= input("Enter Resource Manager Compartment Name for "+region +" region: ")

        try:
            comp_id = ct.ntk_compartment_ids[comp_name]
        except KeyError as e:
            #print("Compartment Name "+comp_name +" does not exist in OCI. Please Try Again")
            if os.path.exists(rm_ocids_file):
                print("Removing rm_ocids.csv file for region "+region)
                os.remove(rm_ocids_file)
            #comp_name = input("Enter a new Compartment Name for Resource Manager for "+region +" region: ")
            #try:
            #    comp_id = ct.ntk_compartment_ids[comp_name]
            #except Exception as e:
            print("Invalid Compartment Name. Please Try again. Exiting...")
            exit(1)


    # Start creating stacks
    cwd = os.getcwd()

    svcs = []

    save_dir_svc_map = dir_svc_map.copy()

    for region in regions:

        print("\nStart creating Stacks for "+region+ " region...")
        region_dir = outdir + "/" + region
        if region == 'global':
            outdir_struct = {'rpc':'rpc'}
            dir_svc_map['rpc']=['rpc']

        else:
            outdir_struct = save_outdir_struct.copy()
            dir_svc_map = save_dir_svc_map.copy()

        rm_dir = region_dir + '/RM/'

        os.chdir(rm_dir)
        region=region.strip().lower()
        new_config = config
        if region == 'global':
            new_config.__setitem__("region", str(ct.region_dict[ct.home_region]))
        else:
            new_config.__setitem__("region", str(ct.region_dict[region]))

        ocs_stack = oci.resource_manager.ResourceManagerClient(config=new_config,signer=signer)

        #Process files in region directory - single outdir
        if len(outdir_struct.items())==0:
            rm_name = prefix + "-" + region
            zip_name = rm_name + ".zip"
            # Fix for make_archive huge zip file issue - Ulag
            file_paths = []
            for file in os.listdir(rm_dir):
                if ".tf" in file and "variables" not in file and "provider" not in file and 'backend' not in file:
                    with open(file, 'r') as tf_file:
                        module_data = tf_file.read().rstrip()
                        module_data = module_data.replace("\"../modules", "\"./modules")
                    f = open(file, "w+")
                    f.write(module_data)
                    f.close()

            for root, directories, files in os.walk(rm_dir):
                for filename in files:
                    rel_dir = os.path.relpath(root, rm_dir)
                    filepath = os.path.join(rel_dir, filename)
                    file_paths.append(filepath)

            with ZipFile(zip_name, 'w') as zipp:
                for file in file_paths:
                    if zip_name not in file and 'terraform.tfstate' not in file:
                        zipp.write(file)

            if (region, rm_name) in rm_region_service_map.keys():
                try:
                    comp_name,rm_ocid = rm_region_service_map[(region, rm_name)]
                    status = ocs_stack.get_stack(rm_ocid).data

                    if status.lifecycle_state == "ACTIVE":
                        rm_comp_id=status.compartment_id
                        for nm, id in ct.ntk_compartment_ids.items():
                            if id == rm_comp_id:
                                comp_name = nm
                                break
                        print("Resource Manager Stack " + rm_name + " with ocid " + rm_ocid + " for region " + region + " exists in '" + comp_name + "' Compartment.\nUpdating the same.................")
                        stack_ocid = update_rm(rm_name, rm_ocid, ocs_stack,svcs)
                except Exception as e:
                    print("Resource Manager " + rm_name + " for region " + region + " created previously in compartment '" + comp_name + "' is inactive/terminated!!. Creating a new one...")
                    comp_id = ct.ntk_compartment_ids[comp_name]
                    stack_ocid = create_rm(rm_name, comp_id, ocs_stack,svcs)

            else:
                print("Resource Manager stack does not exist for for region " + region + ". Creating a new one...")
                comp_id = ct.ntk_compartment_ids[comp_name]
                stack_ocid = create_rm(rm_name, comp_id, ocs_stack,svcs)

            tfStr[region] = tfStr[region] + region + ";" + comp_name + ";" + rm_name + ";" + stack_ocid + "\n"
            tfstate_file = rm_dir + '/' +  'terraform.tfstate'
            if os.path.exists(tfstate_file):
                create_job_details = oci.resource_manager.models.CreateJobDetails()
                createjoboperationdetails = oci.resource_manager.models.CreateImportTfStateJobOperationDetails()
                createjoboperationdetails.operation = "IMPORT_TF_STATE"
                with open(tfstate_file, 'rb') as file:
                    encodetfstate = file.read()
                    encodetfstate = base64.b64encode(encodetfstate).decode('ascii')
                createjoboperationdetails.tf_state_base64_encoded = encodetfstate
                create_job_details.display_name = rm_name + "-TFImport"
                create_job_details.job_operation_details = createjoboperationdetails
                create_job_details.operation = "IMPORT_TF_STATE"
                create_job_details.stack_id = stack_ocid
                print("Uploading Terraform State file to Resource Manager for stack " + rm_name + "..............")
                ocs_stack.create_job(create_job_details)

            rm_dir_zip = region_dir + '/' + prefix + '-' + region +'.zip'
            # Take a backup of zip file if it exists
            if os.path.exists(rm_dir_zip):
                shutil.move(rm_dir_zip, rm_dir_zip + "_backup")

            os.chdir("../")

            shutil.move(rm_dir+"/"+zip_name,region_dir)

        #Process service_dirs - separate outdir
        else:
            service_dir_processed = []

            for service, service_dir in outdir_struct.items():
                svcs = dir_svc_map[service_dir]
                if(service_dir in service_dir_processed):
                    continue
                if(not os.path.exists(rm_dir+"/"+service_dir)):
                    print("\nDirectory for services - "+ ','.join(svcs) +" does not exist in region "+region)
                    continue

                print("\nProcessing Directory "+service_dir+"...")
                service_dir_processed.append(service_dir)

                if (os.path.exists(rm_dir + "/modules")):
                    shutil.copytree(rm_dir + "/modules", rm_dir+"/"+ service_dir+"/modules")

                for svc in svcs:
                    if os.path.exists(service_dir+"/"+ svc + ".tf"):
                        with open(service_dir+"/"+ svc + ".tf", 'r') as tf_file:
                            module_data = tf_file.read().rstrip()
                            module_data = module_data.replace("\"../../modules", "\"./modules")
                        if svc == 'rpc':
                            f = open(service_dir+"/"+ svc + "-temp.tf", "w+")
                        else:
                            f = open(service_dir + "/" + svc + ".tf", "w+")
                        f.write(module_data)
                        f.close()

                    if svc == 'rpc' and os.path.exists(service_dir+"/"+ svc + ".tf"):
                        try:
                            with open(service_dir+"/"+ svc + "-temp.tf",'r') as origfile, open(service_dir+"/"+ svc + ".tf", 'w') as newfile:
                                for line in origfile:
                                    if 'tenancy_ocid' in line or "user_ocid" in line or "fingerprint" in line or "private_key_path" in line:
                                        pass
                                    else:
                                        newfile.write(line)
                        except FileNotFoundError as e:
                            pass

                        os.remove(service_dir+"/"+ svc + "-temp.tf")

                service_rm_name = prefix + "-" + region + "-" + service_dir

                zip_name = service_rm_name + ".zip"
                # Fix for make_archive huge zip file issue - Ulag
                file_paths = []

                for root, directories, files in os.walk(service_dir):
                    for filename in files:
                        rel_dir = os.path.relpath(root, service_dir)
                        filepath = os.path.join(rel_dir, filename)
                        file_paths.append(filepath)

                with ZipFile(zip_name, 'w') as zipp:
                    for file in file_paths:
                        if zip_name not in file and 'terraform.tfstate' not in file:
                            os.chdir(rm_dir + "/" + service_dir)
                            zipp.write(file)
                            os.chdir("../")
                if (region,service_rm_name) in rm_region_service_map.keys():
                    try:
                        comp_name,service_rm_ocid = rm_region_service_map[(region,service_rm_name)]
                        status = ocs_stack.get_stack(service_rm_ocid).data

                        if status.lifecycle_state == "ACTIVE":
                            rm_comp_id = status.compartment_id
                            for nm, id in ct.ntk_compartment_ids.items():
                                if id == rm_comp_id:
                                    comp_name = nm
                                    break
                            print("Resource Manager Stack "+service_rm_name +" with ocid "+ service_rm_ocid + " for region " + region + " exists in '" + comp_name + "' Compartment.\nUpdating the same.................")
                            stack_ocid = update_rm(service_rm_name,service_rm_ocid,ocs_stack, svcs)
                    except Exception as e:
                        print("Resource Manager "+ service_rm_name + " for region " + region + " created previously in compartment '" + comp_name + "' is inactive/terminated!!. Creating a new one...")
                        comp_id = ct.ntk_compartment_ids[comp_name]
                        stack_ocid = create_rm(service_rm_name, comp_id, ocs_stack,svcs)

                else:
                    print("Resource Manager stack does not exist for services - "+ ','.join(svcs)+" for region "+ region+". Creating a new one...")
                    comp_id = ct.ntk_compartment_ids[comp_name]
                    stack_ocid = create_rm(service_rm_name,comp_id, ocs_stack,svcs)

                tfStr[region] = tfStr[region] + region +";" +comp_name + ";" + service_rm_name + ";" + stack_ocid+"\n"

                # 5. Terraform state import if it exists
                tfstate_file = rm_dir + '/' +service_dir+ '/terraform.tfstate'
                if os.path.exists(tfstate_file):
                    create_job_details = oci.resource_manager.models.CreateJobDetails()
                    createjoboperationdetails = oci.resource_manager.models.CreateImportTfStateJobOperationDetails()
                    createjoboperationdetails.operation = "IMPORT_TF_STATE"
                    with open(tfstate_file,'rb') as file:
                        encodetfstate = file.read()
                        encodetfstate = base64.b64encode(encodetfstate).decode('ascii')
                    createjoboperationdetails.tf_state_base64_encoded = encodetfstate
                    create_job_details.display_name = service_rm_name + "-TFImport"
                    create_job_details.job_operation_details = createjoboperationdetails
                    create_job_details.operation = "IMPORT_TF_STATE"
                    create_job_details.stack_id = stack_ocid
                    print("Uploading Terraform State file to Resource Manager for stack "+service_rm_name+"..............")
                    ocs_stack.create_job(create_job_details)

                shutil.rmtree(rm_dir + "/" + service_dir)

            rm_dir_zip = region_dir + '/' + prefix + '-' + region + '-stacks.zip'
            # Take a backup of zip file if it exists
            if os.path.exists(rm_dir_zip):
                shutil.move(rm_dir_zip, rm_dir_zip + "_backup")

            base_name = prefix + "-" + region + "-stacks"
            if (os.path.exists(os.path.join(os.getcwd(),"modules"))):
                shutil.rmtree("modules")
            os.chdir("../")
            shutil.make_archive(base_name, 'zip', rm_dir)

        # Remove the contents of RM directory;
        if os.path.exists(rm_dir):
            # remove existing RM dir
            shutil.rmtree(rm_dir)

        # write data to rm_ocids file
        rm_ocids_file = outdir+'/'+region+'/rm_ocids.csv'
        with open (rm_ocids_file, "w") as f:
            f.write(tfStr[region])

        print("\nProcess Completed for region "+region +"!!!\n"
              "Terraform Configuration (and/or) State files are uploaded to  respective Resource Manager Stacks in " + comp_name + " Compartment.")
        print("=====================================================================================================================")

    os.chdir(cwd)
