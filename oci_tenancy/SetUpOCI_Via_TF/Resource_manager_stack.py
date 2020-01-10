#!/bin/python
import argparse
import os
import sys
import oci
import shutil
import glob
import base64
from zipfile import ZipFile
from oci.identity import IdentityClient
from oci.resource_manager.models import CreateStackDetails
from oci.resource_manager.models import UpdateStackDetails
from oci.resource_manager.models import UpdateConfigSourceDetails
from oci.resource_manager.models import CreateZipUploadConfigSourceDetails
from oci.resource_manager.models import UpdateZipUploadConfigSourceDetails
from oci.resource_manager.models import CreateImportTfStateJobOperationDetails
from oci.resource_manager.models import CreateJobOperationDetails
from oci.resource_manager.models import CreateJobDetails


def paginate(operation, *args, **kwargs):
    while True:
        response = operation(*args, **kwargs)
        for value in response.data:
            yield value
        kwargs["page"] = response.next_page
        if not response.has_next_page:
            break

def getOptions(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(description="Parses command.")
    parser.add_argument("-c", "--configFileName", help="Config file name",required=False)
    parser.add_argument("-d", "--outDir", help="Path to outdir containing region directories having variables_<region>.tf file.", required=True)
    parser.add_argument("-r", "--region", help="Upload stack for one region, should have corresponding subfolder in --outDir directory.", required=False)
    parser.add_argument("-s", "--stackName", help="Default Resource Manager stack name is OCS_CD3, use this option to specify the stack name", required=False)
    parser.add_argument("-e", "--exportState", dest="exportState", default=False, help="Export the terraform state from Resource Manager for the stack name", action='store_true')
    parser.add_argument("-i", "--importState", dest="importState", default=False, help="Import the terraform state into the Resource Manager for the stack name", action='store_true')
    options = parser.parse_args(args)
    return options

options = getOptions(sys.argv[1:])

#print(options.outDir)
#print(options.region)
#print(options.configFileName)
#print(options.stackName)
#print(options.exportState)
#print(options.importState)

if options.configFileName is not None:
    config = oci.config.from_file(file_location=options.configFileName)
else:
    config = oci.config.from_file()

stack_file_name = options.stackName

if options.stackName is None:
    stack_name = "OCS_CD3"
    stack_file_name = "OCS_CD3.zip"
else:
    stack_name = options.stackName
    stack_file_name = stack_file_name+".zip"

outDir = options.outDir
identityClient = IdentityClient(config)
tenancy_id = config['tenancy']
region_config = config['region'].split("-")[1]
tempStr = {}
tmpFolder = "rmstack"
foundRegion = False

if options.region is None:
    print("Processing for region specified in config - "+ region_config)
else:
    if ( options.region == region_config):
        print("Processing for region - "+ region_config)
    else:
        print("Region in config ["+region_config+"] does not match with specified region ["+options.region+"]")
        print("Quitting...")
        exit(1)


region_config = config['region']

for region in paginate(identityClient.list_region_subscriptions, tenancy_id=tenancy_id):
    if(region.STATUS_READY=='READY'):
        myregion=region.region_name.split("-")[1]
        #print("region_name->"+myregion)
        for subfolder in os.listdir(outDir):
            if myregion in subfolder:
                foundRegion = True
                #print(os.path.join(outDir, subfolder))
                os.chdir(os.path.join(outDir, subfolder))
                if not os.path.exists(tmpFolder):
                    os.makedirs(tmpFolder)
                else:
                    shutil.rmtree(tmpFolder, ignore_errors=True)
                    os.makedirs(tmpFolder)
                for filename in glob.glob("*.tf"):
                    shutil.copy(filename, tmpFolder)
                skip_vars = ["user_ocid", "fingerprint", "private_key_path"]
                with open('provider.tf') as origfile, open(tmpFolder+'/provider.tf', 'w') as newfile:
                    for line in origfile:
                        if not any(skip_var in line for skip_var in skip_vars):
                            newfile.write(line)
                skipline = False

                if os.path.exists('terraform.tfstate'):
                    with open('terraform.tfstate') as origfile, open(tmpFolder+'/terraform.tfstate', 'w') as newfile:
                        for line in origfile:
                            if "0.12.13" in line:
                                line = line.replace("0.12.13","0.12.6")
                            newfile.write(line)

                if not os.path.exists('variables_'+myregion+'.tf'):
                    print("File - variables_"+myregion+".tf"+" does not exits")
                    print("Quitting...")
                    exit(1)

                with open('variables_'+myregion+'.tf') as origfile, open(tmpFolder+'/variables_'+myregion+'.tf', 'w') as newfile:
                    for line in origfile:
                        if any(skip_var in line for skip_var in skip_vars):
                            skipline = True
                        if not skipline:
                            newfile.write(line)
                        if skipline:
                            if ('}' in line):
                                skipline = False
                os.chdir(os.path.join(outDir, subfolder,tmpFolder))
                with ZipFile(stack_file_name,'w') as zip: 
                    for file in glob.glob("*.tf"):
                        zip.write(file) 
                print('All files zipped successfully!')  
                
                compartment_id = config["ocs_compartment_ocid"]
                #print("compartment_id->"+compartment_id)
                ocs_stack = oci.resource_manager.ResourceManagerClient(config)

                check_stack_status = "NotExists"
                for rmstack in paginate(ocs_stack.list_stacks, compartment_id=compartment_id):
                    if (rmstack.display_name == stack_name):
                        if ( rmstack.lifecycle_state in [ "CREATING","ACTIVE" ]):
                            check_stack_status = "Update"
                            stack_ocid = rmstack.id
                        else:
                            check_stack_status = "Create"
                        #print(rmstack.display_name)
                        #print(rmstack.description)
                        #print(rmstack.id)
                        #print(rmstack.lifecycle_state)
                        #print(rmstack.terraform_version)
                #print("check_stack_status->"+check_stack_status)

                if ( check_stack_status == "NotExists") and options.exportState:
                    print("Resource Manager stack - "+stack_name+" does not exist")
                    print("Quitting...")
                    exit(1)

                if ( check_stack_status == "NotExists"):
                   check_stack_status = "Create"

                if options.exportState:
                   check_stack_status = "Export"

                if ( check_stack_status == "Create" ) or ( check_stack_status == "Update" ):
                    with open( stack_file_name,'rb' ) as file:
                        zipContents = file.read()
                        encodedZip = base64.b64encode(zipContents).decode('ascii')

                if ( check_stack_status == "Create" ):
                    print("Creating Resource Manager Stack - "+stack_name);
                    zipConfigSource = CreateZipUploadConfigSourceDetails()
                    zipConfigSource.config_source_type = 'ZIP_UPLOAD'
                    #zipConfigSource.working_directory = "ashburn"
                    zipConfigSource.zip_file_base64_encoded = encodedZip

                    request = CreateStackDetails()
                    request.compartment_id = compartment_id
                    request.display_name = stack_name
                    request.description = "OCS CD3 Stack"
                    request.config_source = zipConfigSource
                    request.terraform_version = "0.12.x"
                    mstack = ocs_stack.create_stack(create_stack_details=request)
                    #print(mstack.data) 
                    stack_ocid = mstack.data.id

                if ( check_stack_status == "Update" ):
                    print("Updating Resource Manager Stack - "+stack_name);
                    zipConfigSource = UpdateZipUploadConfigSourceDetails()
                    zipConfigSource.config_source_type = 'ZIP_UPLOAD'
                    #zipConfigSource.working_directory = "ashburn"
                    zipConfigSource.zip_file_base64_encoded = encodedZip

                    request = UpdateStackDetails()
                    request.compartment_id = compartment_id
                    #request.display_name = stack_name
                    #request.description = "OCS CD3 Stack"
                    request.config_source = zipConfigSource
                    request.terraform_version = "0.12.x"
                    mstack = ocs_stack.update_stack(stack_id = stack_ocid, update_stack_details=request)

                found_job= False
                #TODO
                if ( check_stack_status == "Export" ):
                    print("Exporting terraform state from Resource Manager Stack - "+stack_name);
                    mstack_stream = ocs_stack.get_stack_tf_state(stack_id = stack_ocid)
                    print(mstack_stream)
                    print(mstack_stream.headers)
                    print(mstack_stream.data)
                    if not ( "gzip" in str(mstack_stream.headers)):
                        print ("Terraform state does not exists for stack - "+stack_name);
                        print("Quitting...")
                        exit(1)

                    #with open('mtry.zip','w+b') as mzipfile:
                    #    mzipfile.write(mstack_stream.content)

                    for stackjobs in paginate(ocs_stack.list_jobs, stack_id = stack_ocid, compartment_id=compartment_id):
                        #print(stackjobs)
                        if (stackjobs.operation == "APPLY" ) or ( stackjobs.operation == "DESTROY"):
                            if (stackjobs.lifecycle_state in [ "ACCEPTED", "IN_PROGRESS", "FAILED", "CANCELING", "CANCELED" ] ):
                                print('Cannot export terraform state, job lifecycle in "ACCEPTED", "IN_PROGRESS", "FAILED", "CANCELING" or "CANCELED" state')
                            else:
                                found_job= True
                                #print('Exporting terraform state')


                if options.importState:
                   check_stack_status = "Import"

                if ( check_stack_status == "Import" ):
                    os.chdir(os.path.join(outDir, subfolder, tmpFolder))
                    if not os.path.exists('terraform.tfstate'):
                        print("File - terraform.tfstate does not exit in folder - "+os.path.join(outDir, subfolder))
                        print("Quitting...")
                        exit(1)
                    with open( 'terraform.tfstate' ,'rb' ) as file:
                        tfszipContents = file.read()
                        tfsencodedZip = base64.b64encode(tfszipContents).decode('ascii')

                    print("Importing terraform state into Resource Manager Stack - "+stack_name);
                    importTFStateOpsDetail = CreateImportTfStateJobOperationDetails()
                    importTFStateOpsDetail.operation = 'IMPORT_TF_STATE'
                    importTFStateOpsDetail.tf_state_base64_encoded = tfsencodedZip

                    jobDetails = CreateJobDetails(stack_id = stack_ocid, display_name = "Import TFState", job_operation_details = importTFStateOpsDetail)
                    mimport = ocs_stack.create_job(create_job_details = jobDetails)

        if not foundRegion:
            print("Region folder not found -"+ os.path.join(outDir, subfolder))
            print("Quitting...")
            exit(1)

