#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will help in initializing the docker container; creates config and variables files.
#
# Author: Shruthi Subramanian
#

import argparse
import logging
import os
import shutil
import datetime
import configparser
from azure.identity import ClientSecretCredential
from azure.mgmt.compute import ComputeManagementClient


def paginate(operation, *args, **kwargs):
    while True:
        response = operation(*args, **kwargs)
        for value in response.data:
            yield value
        kwargs["page"] = response.next_page
        if not response.has_next_page:
            break



# Execution of code begins here
parser = argparse.ArgumentParser(description="Connects the Container to Azure Subscription")
parser.add_argument("propsfile", help="Full Path of properties file. eg createtenancyAzure.properties")
args = parser.parse_args()
config = configparser.RawConfigParser()
config.read(args.propsfile)

current_time=str(datetime.datetime.now())
cloud="Azure"

# Initialize Toolkit Variables
user_dir = "/cd3user/"+cloud.lower()+"/"
toolkit_dir = os.path.dirname(os.path.abspath(__file__))+"/.."
tf_modules_dir = toolkit_dir + "/azurecloud/terraform"

setupcloud_props_toolkit_file_path = toolkit_dir + "/setUpAzure.properties"



prefix = config.get('Default', 'prefix').strip()
if prefix == "" or prefix == "\n":
    print("Invalid Prefix. Please try again......Exiting !!")
    exit(1)

prefixes=[]
f = os.path.basename(__file__).rstrip("py")+"safe"
safe_file = user_dir + f
if os.path.exists(safe_file):
    f=open(safe_file,"r")
    safe_file_lines = f.readlines()
    for l in safe_file_lines:
        if "SUCCESS" in l:
            prefixes.append(l.split("\t")[0])

if prefixes !=[]:
    if prefix in prefixes:
        print("WARNING!!! Container has already been successfuly connected to the Azure with same prefix. Please proceed only if you re-running the script for new project subscription")
        inp = input("\nDo you want to proceed (y/n):")
        if inp.lower()=="n":
            exit(1)


# Initialize Tenancy Variables

prefix_dir = user_dir +"/" + prefix
config_files= prefix_dir +"/.config_files"

terraform_files = prefix_dir + "/terraform_files"
az_provider_file = terraform_files + "/provider.tf"
setupcloud_props_file_path = prefix_dir + "/"+prefix+"_setUp"+cloud+".properties"

connected = 1

# Read Config file Variables
try:
    subscription_id=''
    tenant_id=''
    client_id=''
    client_secret=''

    subscription_id = config.get('Default', 'subscription_id').strip()

    tenant_id = config.get('Default', 'tenant_id').strip()

    client_id = config.get('Default', 'client_id').strip()

    client_secret = config.get('Default', 'client_secret').strip()

    if (subscription_id == '' or tenant_id == '' or  client_id == '' or client_secret == ''):
        print("Creating "+prefix_dir + " without setting up authentication")
        connected=0
except Exception as e:
    print(e)
    print('Check if input properties exist and try again..exiting...')
    exit(1)


if not os.path.exists(prefix_dir):
    os.makedirs(prefix_dir)
if not os.path.exists(config_files):
    os.makedirs(config_files)


# Copy input properties file to customer_tenancy_dir
shutil.copy(args.propsfile,config_files+"/"+prefix+"_connectAzure.properties")

if connected == 1:
    credential = ClientSecretCredential(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret
        )

    # Use the credential to create a client for an Azure service (e.g., Compute)
    compute_client = ComputeManagementClient(credential, subscription_id)


# 3. Generate setUpCloud.properties file
print("Creating Azure specific setUpAzure.properties.................")
with open(setupcloud_props_toolkit_file_path, 'r+') as setUpCloud_file:
    setupcloud_props_toolkit_file_data = setUpCloud_file.read().rstrip()

setupcloud_props_toolkit_file_data = setupcloud_props_toolkit_file_data.replace("outdir=", "outdir="+terraform_files)
setupcloud_props_toolkit_file_data = setupcloud_props_toolkit_file_data.replace("prefix=", "prefix="+prefix)
if connected == 1:
    setupcloud_props_toolkit_file_data = setupcloud_props_toolkit_file_data.replace("subscription_id=", "subscription_id=" + subscription_id)
    setupcloud_props_toolkit_file_data = setupcloud_props_toolkit_file_data.replace("tenant_id=", "tenant_id="+tenant_id)
    setupcloud_props_toolkit_file_data = setupcloud_props_toolkit_file_data.replace("client_id=", "client_id="+client_id)
    setupcloud_props_toolkit_file_data = setupcloud_props_toolkit_file_data.replace("client_secret=", "client_secret="+client_secret)

f = open(setupcloud_props_file_path, "w+")
f.write(setupcloud_props_toolkit_file_data)
f.close()


# Copy modules dir to terraform_files folder
try:
    shutil.copytree(tf_modules_dir, terraform_files )
except FileExistsError as fe:
    print(fe)


# 6. Read variables.tf from examples folder and copy the variables as string

if connected == 1:
    print("Creating subscription specific terraform provider file................")
    with open(az_provider_file, 'r+') as provider_file:
        az_provider_file_data = provider_file.read().rstrip()

    az_provider_file_data = az_provider_file_data.replace("<SUBSCRIPTION ID HERE>", subscription_id)
    az_provider_file_data = az_provider_file_data.replace("<TENANT ID HERE>", tenant_id)
    az_provider_file_data = az_provider_file_data.replace("<CLIENT ID HERE>", client_id)
    az_provider_file_data = az_provider_file_data.replace("<CLIENT SECRET HERE>", client_secret)

    f = open(az_provider_file, "w+")
    f.write(az_provider_file_data)
    f.close()
    
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
logging.info("Modify "+prefix_dir + "/" +prefix+"_setUpAzure.properties with input values for cd3file and workflow_type")
logging.info("cd "+user_dir+"/oci_tools/cd3_automation_toolkit")
logging.info("python setUpCloud.py azure "+prefix_dir + "/" +prefix+"_setUpAzure.properties")

with open(outfile, 'r') as log_file:
    data = log_file.read().rstrip()
print(data)

print("==================================================================================================================================")

