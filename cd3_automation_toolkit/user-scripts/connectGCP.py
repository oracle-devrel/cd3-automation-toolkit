#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will help in initializing the docker container; creates config and variables files.
#
# Author: Suruchi Bansal
# Oracle Consulting
#
import sys
import argparse
import configparser
import datetime
import shutil
import distutils
import os,sys,logging
sys.path.append(os.getcwd())
sys.path.append(os.getcwd()+"/..")
from gcpcloud.python import *
from google.cloud import resourcemanager_v3

# Execution of code begins here
parser = argparse.ArgumentParser(description="Connects the Container to GCP Project")
parser.add_argument("propsfile", help="Full Path of properties file. eg connectGCP.properties")
args = parser.parse_args()
config = configparser.RawConfigParser()
config.read(args.propsfile)

current_time=str(datetime.datetime.now())
cloud="GCP"

# Initialize Toolkit Variables
user_dir = "/cd3user/"+cloud.lower()+"/"

toolkit_dir = os.path.dirname(os.path.abspath(__file__))+"/.."
tf_modules_dir = toolkit_dir + "/"+cloud.lower()+"cloud/terraform"
setupcloud_props_toolkit_file_path = toolkit_dir + "/setUp"+cloud+".properties"
auto_keys_dir = user_dir + "/keys"


prefix = config.get('Default', 'prefix').strip()
if prefix == "" or prefix == "\n":
    print("Invalid Prefix. Please try again......Exiting !!")
    exit(1)

prefixes=[]
f = os.path.basename(__file__).rstrip("py")+".safe"
safe_file = user_dir + f
if os.path.exists(safe_file):
    f=open(safe_file,"r")
    safe_file_lines = f.readlines()
    for l in safe_file_lines:
        if "SUCCESS" in l:
            prefixes.append(l.split("\t")[0])

if prefixes !=[]:
    if prefix in prefixes:
        print("WARNING!!! Container has already been successfuly connected to "+cloud+" with same prefix. Please proceed only if you re-running the script for new project")
        inp = input("\nDo you want to proceed (y/n):")
        if inp.lower()=="n":
            exit(1)

# Initialize Tenancy Variables
prefix_dir = user_dir +"/" + prefix
config_files= prefix_dir +"/.config_files"

terraform_files = prefix_dir + "/terraform_files"
gcp_provider_file = terraform_files + "/provider.tf"
setupcloud_props_file_path = prefix_dir + "/"+prefix+"_setUp"+cloud+".properties"

connected = 1
# Read Config file Variables

try:
    config_file=''
    config_file = config.get('Default', 'config_file').strip()
    if config_file == "" or config_file == "\n":
        config_file = auto_keys_dir +"/gcp_api_private.json"

except Exception as e:
    print(e)
    print('Check if input properties exist and try again..exiting...')
    exit(1)


if not os.path.exists(prefix_dir):
    os.makedirs(prefix_dir)
if not os.path.exists(config_files):
    os.makedirs(config_files)


# 1. Copy input properties file
shutil.copy(args.propsfile,config_files+"/"+prefix+"_"+os.path.basename(args.propsfile))

# 2. Authenticate and Get Projects

if connected == 1:
    gct = gcpCommonTools()

    # Copy onfig file  to customer_tenancy_dir
    filename = os.path.basename(config_file)
    _config_file=config_files + "/" + filename
    shutil.copy(config_file, _config_file)
    os.chmod(_config_file,0o600)
    credentials = gct.authenticate(config_file)
    project_id=credentials.project_id

    client = resourcemanager_v3.ProjectsClient(credentials=credentials)

    # Request project details using the project ID
    # The name parameter must follow the format: projects/{project_id}
    request = resourcemanager_v3.GetProjectRequest(name=f"projects/{project_id}")
    project = client.get_project(request=request)

    # 'display_name' contains the human-readable Project Name
    project_name = project.display_name


# 3. Generate setUpCloud.properties file
print("Creating "+cloud+" specific setUp"+cloud+".properties.................")
with open(setupcloud_props_toolkit_file_path, 'r+') as setUpCloud_file:
    setupcloud_props_toolkit_file_data = setUpCloud_file.read().rstrip()

setupcloud_props_toolkit_file_data = setupcloud_props_toolkit_file_data.replace("outdir=", "outdir="+terraform_files)
setupcloud_props_toolkit_file_data = setupcloud_props_toolkit_file_data.replace("prefix=", "prefix="+prefix)

if connected ==1:
    setupcloud_props_toolkit_file_data = setupcloud_props_toolkit_file_data.replace("config_file=", "config_file="+_config_file)

f = open(setupcloud_props_file_path, "w+")
f.write(setupcloud_props_toolkit_file_data)
f.close()

# Copy modules dir to terraform_files folder
try:
    shutil.copytree(tf_modules_dir, terraform_files )
except FileExistsError as fe:
    print(fe)


if connected == 1:
    print("Creating project specific terraform provider file.................")
    with open(gcp_provider_file, 'r+') as provider_file:
        gcp_provider_file_data = provider_file.read().rstrip()

    gcp_provider_file_data = gcp_provider_file_data.replace("<PATH TO JSON KEY FILE>", _config_file)

    f = open(gcp_provider_file, "w+")
    f.write(gcp_provider_file_data)
    f.close()


# Logging information
outfile = prefix_dir+'/'+os.path.basename(__file__).rstrip("py")+"out"
logging.basicConfig(filename=outfile, format='%(message)s', filemode='w', level=logging.INFO)

print("==================================================================================================================================")
print("\nThe toolkit has been setup successfully. !!!\n")
f = open(safe_file, "a")
data=prefix + "\t" + "SUCCESS\t"+current_time+"\n"
f.write(data)
f.close()

logging.info("Prefix Specific Working Directory Path: "+prefix_dir+"\n")

logging.info("\n######################################")
logging.info("Next Steps for using toolkit via CLI")
logging.info("######################################")
logging.info("Modify "+prefix_dir + "/" +prefix+"_setUp"+cloud+".properties with input values for cd3file and workflow_type")
logging.info("cd /cd3user/oci_tools/cd3_automation_toolkit")
logging.info("python setUpCloud.py azure "+prefix_dir + "/" +prefix+"_setUp"+cloud+".properties")

with open(outfile, 'r') as log_file:
    data = log_file.read().rstrip()
print(data)

print("==================================================================================================================================")

