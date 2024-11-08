#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will help in initializing the docker container; creates config and variables files.
#
# Author: Suruchi
#

import argparse
import logging
import os
import shutil
import sys
import datetime
import configparser
import time

import oci
from oci.object_storage import ObjectStorageClient
from copy import deepcopy
sys.path.append(os.getcwd()+"/..")
import subprocess
from os import environ
from commonTools import *



# Execution of code begins here
parser = argparse.ArgumentParser(description="cleans up prefix specific files form container and oci objects")
parser.add_argument("propsfile", help="Full Path of properties file. eg tenancyconfig.properties")
args = parser.parse_args()
config = configparser.RawConfigParser()
config.read(args.propsfile)

current_time=str(datetime.datetime.now())

# Initialize Toolkit Variables
user_dir = "/cd3user"

prefix = config.get('Default', 'prefix').strip()
if prefix == "" or prefix == "\n":
    print("Invalid Prefix. Please try again......Exiting !!")
    exit(1)


print("Executing Deletion for Prefix "+prefix+"...")
prefix_rem=input("Press y to continue. Default is n: ")
if(prefix_rem.lower()!='y'):
    print("Exiting without any deletion...")
    exit()

customer_tenancy_dir = user_dir + "/tenancies/" + prefix
config_files= user_dir + "/tenancies/" + prefix +"/.config_files"
config_file_path = config_files + "/" + prefix + "_oci_config"

auto_keys_dir = user_dir + "/tenancies/keys"
safe_file = user_dir + "/tenancies/createTenancyConfig.safe"

# Read Config file Variables
try:
    user=''
    _key_path=''
    fingerprint=''

    tenancy = config.get('Default', 'tenancy_ocid').strip()
    if tenancy == "" or tenancy == "\n":
        print("Tenancy ID cannot be left empty...Exiting !!")
        exit(1)

    auth_mechanism = config.get('Default', 'auth_mechanism').strip().lower()
    if auth_mechanism == "" or auth_mechanism == "\n" or (auth_mechanism!='api_key' and auth_mechanism!='session_token' and auth_mechanism!='instance_principal'):
        print("Auth Mechanism cannot be left empty...Exiting !!")
        exit(1)

    region = config.get('Default', 'region').strip()
    if region == "" or region == "\n":
        print("Region cannot be left empty...Exiting !!")
        exit(1)
    rg=region

    if auth_mechanism == 'api_key':
        print("=================================================================")
        print("NOTE: Make sure the API Public Key is added to the OCI Console!!!")
        print("=================================================================")

        fingerprint = config.get('Default', 'fingerprint').strip()
        if fingerprint == "" or fingerprint == "\n":
            print("Fingerprint cannot be left empty...Exiting !!")
            exit(1)

        key_path = config.get('Default', 'key_path').strip()
        if key_path == "" or key_path == "\n":
            key_path = auto_keys_dir +"/oci_api_private.pem"
        if not os.path.isfile(key_path):
            print("Invalid PEM Key File at "+key_path+". Please try again......Exiting !!")
            exit(1)

        user = config.get('Default', 'user_ocid').strip()
        if user == "" or user == "\n":
            print("user_ocid cannot be left empty...Exiting !!")
            exit(1)

    ## Advanced parameters ##
    remote_state = config.get('Default', 'use_remote_state').strip().lower()
    remote_state_bucket = config.get('Default', 'remote_state_bucket_name').strip()

    use_devops = config.get('Default', 'use_oci_devops_git').strip().strip().lower()
    devops_repo = config.get('Default', 'oci_devops_git_repo_name').strip().strip()
    devops_user = config.get('Default', 'oci_devops_git_user').strip()
    devops_user_key = config.get('Default', 'oci_devops_git_key').strip()
    outdir_structure_file = config.get('Default', 'outdir_structure_file').strip()
    multi_outdir=False
    if (outdir_structure_file != '' and outdir_structure_file != "\n") and os.path.isfile(outdir_structure_file):
        outdir_config = configparser.RawConfigParser()
        outdir_config.read(outdir_structure_file)
        multi_outdir=True

    if use_devops == 'yes' or remote_state == 'yes':
        #Use remote state if using devops
        remote_state='yes'

        # OCI DevOps GIT User and Key are mandatory while using instance_principal or session_token
        if auth_mechanism == 'instance_principal' or auth_mechanism == 'session_token':
            if devops_user == "" or devops_user == "\n":
                print("OCI DevOps GIT User cannot be left empty when using instance_principal or session_token...Exiting !!")
                exit(1)
            if use_devops == 'yes' and devops_user_key == "" or devops_user_key == "\n":
                print("OCI DevOps GIT Key cannot be left empty when using instance_principal or session_token...Exiting !!")
                exit(1)
        if auth_mechanism == 'api_key':
            # Use same user and key as $user_ocid and $key_path for OCI Devops GIT operations
            if devops_user == '' or devops_user=="\n":
                devops_user = user
            if devops_user_key == '' or devops_user_key=="\n":
                devops_user_key = config_files+"/"+os.path.basename(key_path)

    if remote_state == 'yes':
        # Use same oci_devops_git_user for managing terraform remote state backend
        remote_state_user=devops_user

        # Bucket Name
        if remote_state_bucket == '' or remote_state_bucket == "\n":
            bucket_name = prefix + "-automation-toolkit-bucket"
        else:
            bucket_name = remote_state_bucket.strip()
except Exception as e:
    print(e.message)
    print('Check if input properties exist and try again..exiting...')
    exit(1)


#Removes OCI Objects
exception= False
if use_devops == 'yes':
    print("Removing OCI Objects...")

    if devops_repo == '' or devops_repo == "\n":
        topic_name = prefix + "-automation-toolkit-topic"
        project_name = prefix + "-automation-toolkit-project"
        repo_name = prefix + "-automation-toolkit-repo"
        devops_exists = False
    else:
        topic_name = ''
        project_name = devops_repo.split("/")[0]
        repo_name = devops_repo.split("/")[1]
        devops_exists = True

    ct = commonTools()
    config, signer = ct.authenticate(auth_mechanism, config_file_path)
    try:
        ct.get_subscribedregions(config,signer)
    except Exception as e:
        print(str(e.message))
        f = open(safe_file, "a")
        data = prefix + "\t" + "FAIL\t" + current_time + "\n"
        f.write(data)
        f.close()
        exit(1)
    home_region = ct.home_region

    # Remove bucket
    buckets_client = ObjectStorageClient(config=config,
                                             retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY,
                                             signer=signer)
    namespace = buckets_client.get_namespace().data

    object_list=None
    try:
        buckets_client.get_bucket(namespace, bucket_name).data
        object_list = buckets_client.list_objects(namespace, bucket_name).data
    except Exception as e:
        print(e.message)

    count = 0
    if object_list!=None:
        for o in object_list.objects:
            count += 1
            buckets_client.delete_object(namespace, bucket_name, o.name)

        if count > 0:
            print(f'Deleted {count} objects in {bucket_name}')
        else:
            print(f'Bucket is empty. No objects to delete.')

        try:
            cmd = "oci os object bulk-delete-versions -ns "+namespace+" -bn "+bucket_name+" --force --auth "+auth_mechanism
            cmd_list = cmd.split()
            if auth_mechanism == "instance_principal":
                subprocess.run(cmd_list)
            else:
                cmd_list.append("--config-file")
                cmd_list.append(config_file_path)
                subprocess.run(cmd_list)
            print("Force deleted object versions")
            response = buckets_client.delete_bucket(namespace, bucket_name)
            print(f'Deleted bucket {bucket_name}')
        except Exception as e:
            print(e.message)
            exception=True

    #Remove Customer Secret Key
    new_config = deepcopy(config)
    new_config.__setitem__("region", ct.region_dict[home_region])
    identity_client = oci.identity.IdentityClient(config=new_config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY,
                                                  signer=signer)
    # Get user ocid for DevOps User Name
    if "ocid1.user.oc" not in remote_state_user:
        if '@' in remote_state_user:
            remote_state_user = remote_state_user.rsplit("@",1)[0]

        user_data = identity_client.list_users(compartment_id=tenancy).data
        found=0
        for user_d in user_data:
            if user_d.name==remote_state_user and user_d.lifecycle_state=="ACTIVE":
                remote_state_user = user_d.id
                found =1
                break
        if found == 0:
            print("Unable to find the user ocid for creating customer secret key. Exiting...")
            exit(1)

    customer_secret_cred_name = prefix+"-automation-toolkit-csk"
    list_customer_secret_key_response = identity_client.list_customer_secret_keys(user_id=remote_state_user).data
    customer_secret_key_id=''
    for keys in list_customer_secret_key_response:
        if keys.display_name == customer_secret_cred_name:
            customer_secret_key_id=keys.id
            break

    if customer_secret_key_id!='':
        try:
            identity_client.delete_customer_secret_key(user_id=remote_state_user,
                                                           customer_secret_key_id=customer_secret_key_id)
            print("Customer Secret Key deleted for user "+remote_state_user+"\n")
        except Exception as e:
            print(e.message)
            exception=True
    else:
        print("Customer Secret Key not found for user "+remote_state_user+"\n")

    # Remove Devops GIT Repo and Project
    devops_client = oci.devops.DevopsClient(config=config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY,
                                                    signer=signer)
    ons_client = oci.ons.NotificationControlPlaneClient(config=config,
                                                        retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY,
                                                        signer=signer)

    resource_search = oci.resource_search.ResourceSearchClient(config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY,
                                                               signer=signer)

    #Fetch Topic
    ons_query = 'query onstopic resources where displayname = \'' + topic_name + '\''
    ons_search_details = oci.resource_search.models.StructuredSearchDetails(type='Structured',
                                                                            query=ons_query)
    ons_resources = oci.pagination.list_call_get_all_results(resource_search.search_resources, ons_search_details,
                                                             limit=1000)
    toolkit_topic_id=''
    topic_state=''
    for ons in ons_resources.data:
        topic_state = ons.lifecycle_state
        toolkit_topic_id = ons.identifier

    if toolkit_topic_id!='':
        if topic_state != 'ACTIVE':
            print("Topic "+topic_name+" not in ACTIVE state\n")
        else:
            try:
                ons_client.delete_topic(topic_id=toolkit_topic_id)
                print("Topic "+topic_name+" is in Deleting State. Wait for few minutes to rerun createTenancyConfig.py with same prefix\n")
            except Exception as e:
                print(e.message)
                exception=True
    else:
        print("Topic "+topic_name+" does not exist in OCI\n")

    #Fetch Project
    devops_query = 'query devopsproject resources where displayname = \'' + project_name + '\''
    devops_search_details = oci.resource_search.models.StructuredSearchDetails(type='Structured',
                                                                               query=devops_query)
    devops_resources = oci.pagination.list_call_get_all_results(resource_search.search_resources, devops_search_details,
                                                                limit=1000)
    toolkit_project_id=''
    for project in devops_resources.data:
        project_state = project.lifecycle_state
        toolkit_project_id = project.identifier

    if toolkit_project_id!='':
        if project_state != 'ACTIVE':
            print("Devops Project " + project_name + " not in ACTIVE state\n")
        else:
            #Fetch Repo
            list_repository_response = devops_client.list_repositories(project_id=toolkit_project_id, name=repo_name).data
            repo_state = ""
            repo_id=''
            for item in list_repository_response.items:
                repo_state = item.lifecycle_state
                repo_id = item.id

            if repo_id!='':
                if repo_state != "ACTIVE":
                    print("Repo " + repo_name + " not in ACTIVE state\n")
                else:
                    try:
                        devops_client.delete_repository(repository_id=repo_id)
                        print("Waiting for repository ("+repo_name+") to be in DELETED state.")
                    except Exception as e:
                        print(e.message)
                        exception = True
                    try:
                        repo_state=''
                        while repo_state != "DELETED":
                            repo_data = devops_client.get_repository(repository_id=repo_id).data
                            repo_state = repo_data.lifecycle_state
                    except Exception as e:
                        print("Devops Repo "+repo_name+" deleted\n")
            else:
                print("Devops Repo "+repo_name+" does not exist in OCI\n")

            try:
                devops_client.delete_project(project_id=toolkit_project_id)
                print("Devops Project "+project_name+" deleted.\n\n")
            except Exception as e:
                print(e.message)
                exception = True

    else:
        print("Devops Project "+project_name+" does not exist in OCI\n\n")

print("Cleaning up local files from container after successful deletion of OCI objects...")

# Removes prefix from jenkins.properties
jenkins_home = user_dir+"/tenancies/jenkins_home"
if environ.get('JENKINS_HOME') is not None:
    jenkins_home = os.environ['JENKINS_HOME']

if (os.path.exists(jenkins_home+"/jenkins.properties")):
    jenkins_properties_file_path = jenkins_home+"/jenkins.properties"
    jenkins_config = configparser.RawConfigParser()
    jenkins_config.read(jenkins_properties_file_path)
    if (prefix in jenkins_config.sections()):
        jenkins_config.remove_section(prefix)
        file = open(jenkins_properties_file_path, "w")
        jenkins_config.write(file)
        file.close()

    #Removes prefix from git config file
#user_ssh_dir = os.path.expanduser("~") + "/.ssh"
#ssh_config_file = user_ssh_dir + '/config'
ssh_config_file = jenkins_home+"/git_config"
if os.path.exists(ssh_config_file):
    f = open(ssh_config_file,"r")
    new_lines = []
    config_file_data = f.readlines()
    ptr = 1
    found=False
    for line in config_file_data:
        if prefix in line or found==True:
            found=True
            if ptr==7:
                found=False
            ptr=ptr+1

        else:
            found=False
            new_lines.append(line)
    f.close()

    file = open(ssh_config_file, "w")
    file.writelines(new_lines)
    file.close()

if exception == False:
    # Removes prefix directory
    if (os.path.exists(customer_tenancy_dir)):
        shutil.rmtree(customer_tenancy_dir)
    if (os.path.exists(jenkins_home+"/jobs/"+prefix)):
        shutil.rmtree(jenkins_home+"/jobs/"+prefix)

    #Removes prefix from createTenancyConfig.safe
    if os.path.exists(safe_file):
        f=open(safe_file,"r")
        safe_file_lines = f.readlines()
        new_lines = []
        for l in safe_file_lines:
            if prefix not in l:
                new_lines.append(l)
        f.close()
        file = open(safe_file, "w")
        file.writelines(new_lines)
        file.close()

    print("\nCleanup Completed!\n")
else:
    print("\nRe run this script to remove OCI Objects completely.\n")
