#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will help in initilizing the docker container; creates config and variables files.
#
# Author: Shruthi Subramanian
#
import calendar
import glob
import argparse
import logging
import os
import sys
sys.path.append(os.getcwd()+"/..")
from commonTools import *


from datetime import datetime

def paginate(operation, *args, **kwargs):
    while True:
        response = operation(*args, **kwargs)
        for value in response.data:
            yield value
        kwargs["page"] = response.next_page
        if not response.has_next_page:
            break

def seek_info():

    parser = argparse.ArgumentParser(description="Creates OCS Work related components")
    parser.add_argument("propsfile", help="Full Path of properties file. eg tenancyconfig.properties")
    args = parser.parse_args()
    config = configparser.RawConfigParser()
    config.read(args.propsfile)

    ct = commonTools()

    # 1. Creation of Config File -
    print("=================================================================")
    print("NOTE: Make sure the API Public Key is added to the OCI Console!!!")
    print("=================================================================")

    # Read Config file Variables
    try:
        tenancy = config.get('Default', 'tenancy_ocid').strip()
        if tenancy == "" or tenancy == "\n":
            print("Invalid Tenancy ID. Please try again......Exiting !!")
            exit(1)

        fingerprint = config.get('Default', 'fingerprint').strip()
        if fingerprint == "" or fingerprint == "\n":
            print("Invalid Fingerprint. Please try again......Exiting !!")
            exit(1)

        user = config.get('Default', 'user_ocid').strip()
        if user == "" or user == "\n":
            print("Invalid User ID. Please try again......Exiting !!")
            exit(1)

        prefix = config.get('Default', 'customer_name').strip()
        if prefix == "" or prefix == "\n":
           print("Invalid Prefix. Please try again......Exiting !!")
           exit(1)

        key_path = config.get('Default', 'key_path').strip()

        region = config.get('Default', 'region').strip()
        if (region == '' or key_path == "\n"):
            region = "us-ashburn-1"

        ssh_public_key = config.get('Default', 'ssh_public_key').strip()

    except Exception as e:
        print(e)
        print('Check if input properties exist and try again..exiting...`    ')
        exit()

    root_dir = "/root/ocswork/tenancies/" + prefix
    regions_dir = root_dir+"/terraform_files/"
    config_file_path = root_dir+"/"+prefix+"_config"
    auto_keys_dir = "/root/ocswork/tenancies/keys"

    if not os.path.exists(root_dir):
        os.makedirs(root_dir)

    # 2. Move the newly created PEM keys to /root/ocswork/tenancies/<customer_name>/
    files = glob.glob(auto_keys_dir+"/*")

    # If the keys are auto-generated
    if os.path.exists(auto_keys_dir):
        print("Moving the key files to /root/ocswork/tenancies/"+prefix+"/")
        for f in files:
            shutil.move(f,root_dir)
        shutil.rmtree(auto_keys_dir)

    # If the private key is empty; initialize it to the default path
    if (key_path == '' or key_path == "\n"):
        key_path = root_dir+"/oci_api_private.pem"
    # If the private key is already present in the tenancy folder; do nothing
    elif (root_dir+ '/oci_api_private.pem' in key_path):
        key_path = root_dir+'/oci_api_private.pem'
    # If the private key is elsewhere; move it to the tenancy folder
    else:
        shutil.move(key_path, root_dir+'/oci_api_private.pem')
        key_path = root_dir+"/oci_api_private.pem"

    if not os.path.exists(regions_dir):
        os.makedirs(regions_dir)

    # 1. Create config file
    print("Creating the Tenancy specific config, terraform provider , variables and properties files.................")
    file = open(config_file_path, "w")
    file.write("[DEFAULT]\n"
               "tenancy = "+tenancy+"\n"
               "fingerprint = "+fingerprint+"\n"
               "user = "+user+"\n"
               "key_file = "+key_path+"\n"
               "region = "+region+"\n")
    file.close()

    # 3. Fetch AD Names -
    print('Fetching AD names from tenancy and writing to config file if it does not exist.............')
    python_config = oci.config.from_file(file_location=config_file_path)
    identity_client = oci.identity.IdentityClient(python_config)
    conf_file = open(config_file_path, "a")
    tenancy_id = tenancy
    i = 1
    for ad in paginate(identity_client.list_availability_domains, compartment_id=tenancy_id):
        ad_name = "ad_" + str(i)
        if not ad_name in python_config:
            conf_file.write("ad_" + str(i) + "=" + ad.name + "\n")
        i = i + 1
    conf_file.close()

    # 4. Generate setUpOCI.properties file
    ct.get_subscribedregions(config_file_path)

    setupoci_props_file = open(root_dir + "/" +prefix+"_setUpOCI.properties", "w")
    setupoci_props_file.write("[Default]\n"
                              "\n"
                              "#Input variables required to run setUpOCI script\n"
                              "\n"
                              "#path to output directory where terraform file will be generated. eg /root/tenancies/<customer_tenancy_name>/terraform_files when running from OCS VM\n"
                              "outdir="+regions_dir+"\n"
                              "\n"
                              "#prefix for output terraform files eg client name\n"
                              "prefix="+prefix+"\n"
                              "\n"
                              "#input config file for Python API communication with OCI eg example\config; Leave it blank if code is being executed from OCS Work VM\n"
                              "config_file="+config_file_path+"\n"
                              "\n"
                              "#params required if input data format is cd3\n"
                              "#path to cd3 excel eg example\CD3-Flat-template.xlsx\n"
                              "cd3file=\n"
                              "\n"
                              "#Is it Non GreenField tenancy\n"
                              "non_gf_tenancy=false \n""")
    setupoci_props_file.close()

    # 5. Fetch Subscribed regions and create the TF related files
    for region in ct.all_regions:
        linux_image_id = ''
        windows_image_id = ''

        new_config = python_config
        new_config.__setitem__("region", ct.region_dict[region])
        cc = oci.core.ComputeClient(new_config)

        # fetch latest image ocids
        for image in paginate(cc.list_images, compartment_id=tenancy_id, operating_system='Oracle Linux',
                              sort_by='TIMECREATED'):
            if ("Gen2-GPU" not in image.display_name):
                linux_image_id = image.id
                break
        for image in paginate(cc.list_images, compartment_id=tenancy_id, operating_system='Windows',
                              sort_by='TIMECREATED'):
            if ("Gen2-GPU" not in image.display_name):
                windows_image_id= image.id
                break

        if not os.path.exists(regions_dir+region):
            os.mkdir(regions_dir+region)

        # 6. Writing Terraform config files provider.tf and variables.tf
        provider_data = """provider "oci" {
          tenancy_ocid     = var.tenancy_ocid
          user_ocid        = var.user_ocid
          fingerprint      = var.fingerprint
          private_key_path = var.private_key_path
          region           = var.region
        }

        terraform {
          required_providers {
            oci = {
              version = ">= 3.0.0"
            }
          }
        }"""


        f = open(regions_dir+"/"+region+"/provider.tf", "w+")
        f.write(provider_data)
        f.close()

        today = datetime.today()
        dt = str(today.day) +" "+ calendar.month_name[today.month]+" "+ str(today.year)

        variables_data = """variable "ssh_public_key" {
                type = string
                default = \"""" + ssh_public_key + """"
        }
        variable "tenancy_ocid" {
                type = string
                default = \"""" + tenancy + """"
        }
        variable "user_ocid" {
                type = string
                default = \"""" + user + """"
        }
        variable "fingerprint" {
                type = string
                default = \"""" + fingerprint + """"
        }
        variable "private_key_path" {
                type = string
                default =  \"""" + key_path + """"
        }
        variable "region" {
                type = string
                default = \"""" + ct.region_dict[region] + """"
        }
        """
        if (windows_image_id != ''):
            variables_data = variables_data + """
        #Example for OS value 'Windows' in Instances sheet
        variable "Windows" {
                type = string
                default = \"""" + windows_image_id + """"
                description = "Latest ocid as on """ + dt + """"
        }"""
        if (linux_image_id != ''):
            variables_data = variables_data + """
        #Example for OS value 'Linux' in Instances sheet
        variable "Linux"{
                type = string
                default = \"""" + linux_image_id + """"
                description = "Latest ocid as on """ + dt + """"
        }"""
        f = open(regions_dir+"/"+region+"/variables_" + region + ".tf", "w+")
        f.write(variables_data)
        f.close()

    #logging information
    logging.basicConfig(filename=root_dir+'/cmds.log', format='%(message)s', filemode='w', level=logging.INFO)

    print("==================================================================================================================================")
    print("\nDocker has been configured to connect with OCI successfully !!!")
    print("Working Directory Path: "+root_dir)
    print("Config File Path: "+ config_file_path )
    print("Path to region based directories, terraform provider and the variables files: " + regions_dir)
    print("\nPlease use "+prefix+"_setUpOCI.properties file at "+root_dir +" to proceed with the execution of the SetUpOCI script !!!!")
    print("Update the path of CD3 Excel input file in "+root_dir + "/" +prefix+"_setUpOCI.properties before executing the next command......")
    print("\nCommands to execute: (Alternately, you may also check the cmds.log in outdir for the same information)")
    logging.info("Commands to execute:")
    print("cd /root/ocswork/git_oci/oci_tenancy/SetUpOCI_Via_TF/")
    logging.info("cd /root/ocswork/git_oci/oci_tenancy/SetUpOCI_Via_TF/")
    print("python setUpOCI.py "+root_dir + "/" +prefix+"_setUpOCI.properties")
    logging.info("python setUpOCI.py "+root_dir + "/" +prefix+"_setUpOCI.properties")
    print("python fetch_compartments_to_variablesTF.py "+regions_dir + " --config "+root_dir + "/"+prefix+"_config")
    logging.info("python fetch_compartments_to_variablesTF.py "+regions_dir + " --config "+root_dir + "/"+prefix+"_config")
    print("==================================================================================================================================")

if __name__ == '__main__':

    # Execution of the code begins here
    seek_info()
