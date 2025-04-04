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
import sys
import datetime
import configparser
import oci
from oci.object_storage import ObjectStorageClient
import glob
import subprocess
sys.path.append(os.getcwd()+"/..")
from os import environ
from commonTools import *
from copy import deepcopy
from subprocess import DEVNULL
global topic_name
global project_name
global repo_name
global devops_exists
global devops_repo
global commit_id
global bucket_name
global jenkins_home


def paginate(operation, *args, **kwargs):
    while True:
        response = operation(*args, **kwargs)
        for value in response.data:
            yield value
        kwargs["page"] = response.next_page
        if not response.has_next_page:
            break

def create_devops_resources(config,signer):
    resource_search = oci.resource_search.ResourceSearchClient(config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY,
                                                               signer=signer)
    toolkit_topic_id = ''
    if not devops_exists:
        # Check existence of Topic

        ons_query = 'query onstopic resources where displayname = \''+topic_name+'\''
        ons_search_details = oci.resource_search.models.StructuredSearchDetails(type='Structured',
                                                                                query=ons_query)
        ons_resources = oci.pagination.list_call_get_all_results(resource_search.search_resources, ons_search_details,
                                                                 limit=1000)
        for ons in ons_resources.data:
            topic_state = ons.lifecycle_state
            if topic_state != 'ACTIVE':
                print("Topic exists with name(" + topic_name + ") but is not in ACTIVE state. Exiting...")
                exit(1)
            toolkit_topic_id = ons.identifier
            topic_comp = ons.compartment_id
            print("Topic exists with name(" + topic_name + ") in compartment '"+topic_comp+"' Reusing same.")

        # Create New Topic
        if toolkit_topic_id=='':
            # Initialize ONS service client with default config file
            ons_client = oci.ons.NotificationControlPlaneClient(config=config,
                                                                retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY,
                                                                signer=signer)

            try:
                create_topic_response = ons_client.create_topic(create_topic_details=oci.ons.models.CreateTopicDetails(
                    name=topic_name, compartment_id=compartment_ocid, description="Created by Automation ToolKit")).data
            except Exception as e:
                print(e.message)
                if ('Topic with same name already exists in the same tenant or compartment' in str(e.message)):
                    print("If it is in Deleting State, wait for few minutes for it to get terminated and re-try.")
                print("\nExiting!!!")
                exit()
            toolkit_topic_id = create_topic_response.topic_id


    # Check existence of DevOps Project
    toolkit_project_id = ''
    devops_query = 'query devopsproject resources where displayname = \'' + project_name + '\''
    devops_search_details = oci.resource_search.models.StructuredSearchDetails(type='Structured',
                                                                               query=devops_query)
    devops_resources = oci.pagination.list_call_get_all_results(resource_search.search_resources, devops_search_details,
                                                                limit=1000)
    for project in devops_resources.data:
        project_state = project.lifecycle_state
        if project_state != 'ACTIVE':
            print("Project exists with name(" + project_name + ") but is not in ACTIVE state. Exiting...")
            exit(1)
        toolkit_project_id = project.identifier
        project_comp = project.compartment_id
        print("Project exists with name(" + project_name + ") in compartment '"+project_comp+"' Reusing same.")

    # Initialize Devops service client with default config file
    devops_client = oci.devops.DevopsClient(config=config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY,
                                                signer=signer)
    # Create Devops Project
    if toolkit_project_id=='':
        if (toolkit_topic_id==''):
            print("Topic ID is empty for Project - "+project_name+". Please check your input properties file")
            exit(1)
        create_project_response = devops_client.create_project(
            create_project_details=oci.devops.models.CreateProjectDetails(
                name=project_name,
                notification_config=oci.devops.models.NotificationConfig(
                    topic_id=toolkit_topic_id),
                compartment_id=compartment_ocid,
                description="Created by Automation ToolKit")).data

        toolkit_project_id = create_project_response.id
    # Check if repository exists
    list_repository_response = devops_client.list_repositories(project_id=toolkit_project_id,name=repo_name).data
    repo_state = ""
    if list_repository_response.items:
        for item in list_repository_response.items:
            repo_state = item.lifecycle_state
            repo_id = item.id
        if repo_state != "ACTIVE":
            print("Repository exists with name("+repo_name+") but is not in ACTIVE state. Please retry with different prefix. Exiting...")
            exit(1)
        else:
            repo_url = item.ssh_url
            print("Repository exists with name("+repo_name+") and is in ACTIVE state. Reusing same.")

    else:
        # Create Repository
        #print("Creating Repository with name(" + repo_name + ").")
        create_repository_response = devops_client.create_repository(
            create_repository_details=oci.devops.models.CreateRepositoryDetails(
                name=repo_name,
                project_id=toolkit_project_id,
                repository_type="HOSTED",
                description="Created by Automation ToolKit")).data
        repo_url = create_repository_response.ssh_url
        repo_id = create_repository_response.id
        print("Waiting for repository ("+repo_name+") to be in ACTIVE state.")
        while repo_state != "ACTIVE":
            repo_data = devops_client.get_repository(repository_id=repo_id).data
            repo_state = repo_data.lifecycle_state
    list_paths_response = devops_client.list_paths(repository_id=repo_id)
    files_in_repo = len(list_paths_response.data.items)
    return repo_url,files_in_repo


def update_devops_config(prefix, repo_ssh_url,files_in_repo,dir_values,devops_user,devops_user_key,devops_dir,ct):

    repo_ssh_url = repo_ssh_url.replace("ssh://","")
    repo_ssh_url_parts = repo_ssh_url.split("/",1)

    # create git config file
    new_data = "Host "+prefix+"\n " \
               "Hostname "+repo_ssh_url_parts[0]+"\n " \
               "StrictHostKeyChecking no\n " \
               "User " + str(devops_user) + "\n " \
               "IdentityFile " + str(devops_user_key) + "\n"

    '''
    user_ssh_dir = os.path.expanduser("~") + "/.ssh"
    if not os.path.exists(user_ssh_dir):
        os.makedirs(user_ssh_dir)
    '''
    #ssh_config_file = user_ssh_dir + '/config'

    if not os.path.exists(jenkins_home):
        os.mkdir(jenkins_home)
    git_config_file = jenkins_home + '/git_config'

    #if git_config_file exists
    if os.path.exists(git_config_file):
        f = open(git_config_file,"r")
        config_file_data = f.read()
        f.close()

        # new prefix config
        if prefix not in config_file_data:
            f = open(git_config_file,"a")
            config_file_data =  "\n\n" + new_data
            f.write(config_file_data)
            f.close()
        # existing prefix - no changes to be done
        else:
            pass

    # file doesnot exist
    else:
        f = open(git_config_file, "w")
        config_file_data = new_data
        f.write(config_file_data)
        f.close()

    #shutil.copyfile(git_config_file, user_ssh_dir + '/config')
    # change permissions of private key file and config file for GIT
    os.chmod(devops_user_key, 0o600)
    os.chmod(git_config_file, 0o600)
    #os.chmod(git_config_file, 0o600)


    # create symlink for Git Config file for SSH operations.
    src = git_config_file
    if not os.path.exists("/cd3user/.ssh"):
        os.makedirs("/cd3user/.ssh")
    dst = "/cd3user/.ssh/config"
    try:
        os.symlink(src,dst)
    except FileExistsError as e:
        os.unlink(dst)
        os.symlink(src,dst)

    # create jenkins.properties file
    jenkins_properties_file_path = jenkins_home+"/jenkins.properties"

    if dir_values:
        dir_structure = "Multiple_Outdir"
    else:
        dir_structure = "Single_Outdir"

    try:
        jenkins_config = configparser.RawConfigParser()
        jenkins_config.read(jenkins_properties_file_path)

        if (prefix in jenkins_config.sections()):
            jenkins_config.set(prefix, 'regions', str(ct.all_regions))
            jenkins_config.set(prefix, 'services', str(dir_values))
        else:
            jenkins_config.add_section(prefix)
            jenkins_config.set(prefix, 'git_url', "\"" + prefix+":/"+repo_ssh_url_parts[1] + "\"")
            jenkins_config.set(prefix, 'regions', str(ct.all_regions))
            jenkins_config.set(prefix, 'services', str(dir_values))
            jenkins_config.set(prefix, 'outdir_structure', "\"" + dir_structure + "\"")
            jenkins_config.set(prefix, 'tf_or_tofu', "\"" + tf_or_tofu + "\"")

        file = open(jenkins_properties_file_path, "w")
        jenkins_config.write(file)
        file.close()

    except Exception as e:
        print(e)

    if os.path.exists(devops_dir+"../.terraform_files"):
        shutil.rmtree(devops_dir+"../.terraform_files", ignore_errors=True)
    os.rename(devops_dir,devops_dir+"../.terraform_files")

    if not os.path.exists(devops_dir):
        os.makedirs(devops_dir)
    subprocess.run(['git', 'config', '--global', 'init.defaultBranch', "main"], cwd=devops_dir)
    subprocess.run(['git', 'init'], cwd=devops_dir,stdout=DEVNULL)
    subprocess.run(['git', 'config', '--global', 'safe.directory', devops_dir], cwd=devops_dir)
    subprocess.run(['git', 'config','--global','user.email',devops_user], cwd=devops_dir)
    subprocess.run(['git', 'config', '--global', 'user.name', devops_user], cwd=devops_dir)

    # Cleanup existing "origin" remote and create required one
    existing_remote = subprocess.run(['git', 'remote'], cwd=devops_dir,capture_output=True).stdout
    existing_remote = str(existing_remote).split('\'')[1][:-2]
    if existing_remote == "origin":
        subprocess.run(['git', 'remote','remove','origin'], cwd=devops_dir,stdout=DEVNULL)
    subprocess.run(['git', 'remote', 'add', 'origin',"ssh://"+prefix+":/"+repo_ssh_url_parts[1]], cwd=devops_dir,stdout=DEVNULL)
    try:
        subprocess.run(['git', 'fetch','-q'], cwd=devops_dir,stdout=DEVNULL)
    except Exception as e:
        print(str(e))
        f = open(safe_file, "a")
        data = prefix + "\t" + "FAIL\t"+current_time+"\n"
        f.write(data)
        f.close()
        exit(1)


    # Create local branch "main" from remote "main"
    subprocess.run(['git', 'checkout', '-B', 'main'], cwd=devops_dir,stdout=DEVNULL)

    subprocess.run(['git', 'pull', 'origin', 'main','--rebase'], cwd=devops_dir,stdout=DEVNULL)
    f = open(devops_dir + ".gitignore", "w")
    git_ignore_file_data = ".DS_Store\n*tfstate*\n*terraform*\ntfplan.out\ntfplan.json\n*backup*\nimport_commands*\n*cis_report*\n*showoci_report*\n*.safe\n*stacks.zip\n*cd3Validator*"
    f.write(git_ignore_file_data)
    f.close()

    all_items = glob.glob(devops_dir + "../.terraform_files/*")+ [devops_dir+ "/../.terraform_files/.safe"]
    for f in all_items:
        actual_file = f.split("/")[-1]
        path = devops_dir+actual_file
        if os.path.exists(path) and os.path.isfile(path):
            os.remove(devops_dir+actual_file)
        if os.path.exists(path) and os.path.isdir(path):
            shutil.rmtree(path, ignore_errors=True)
        if actual_file.endswith(".tf_backup") or actual_file.endswith(".tfstate"):
            continue
        shutil.move(f,devops_dir)
    for f in glob.glob(jenkins_install + "/*.groovy"):
        actual_file = f.split("/")[-1]
        path = devops_dir+actual_file
        if os.path.exists(path) and os.path.isfile(path):
            os.remove(devops_dir+actual_file)
        shutil.copy(f,devops_dir)

    last_commit_id = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], cwd=devops_dir,capture_output=True).stdout
    current_status = subprocess.run(['git', 'status','--porcelain'], cwd=devops_dir,capture_output=True).stdout
    current_status = str(current_status).split('\'')[1]
    subprocess.run(['git', 'add', '-A'], cwd=devops_dir,stdout=DEVNULL)
    subprocess.run(['git', 'commit', '-m','Initial commit from createTenancyConfig'], cwd=devops_dir,stdout=DEVNULL)
    if current_status and files_in_repo > 0:
        repo_changes = input("\nData in local terraform_files and repo is not same, which changes you want to retain? Enter local or repo, default is local : ")
        if ("repo" in repo_changes.lower()):
            print("Ignoring local changes......")
            subprocess.run(['git', 'branch','main', '-u', 'origin/main'], cwd=devops_dir,stdout=DEVNULL)
            subprocess.run(['git','reset','--hard','@{u}'], cwd=devops_dir,stdout=DEVNULL)
            subprocess.run(['git', 'pull','origin','main'], cwd=devops_dir,stdout=DEVNULL)
        else:
            print("Updating remote with local changes.....")

    commit_id='None'
    try:
        #subprocess.run(['git', 'commit', '-m','Initial commit from createTenancyConfig.py'], cwd=devops_dir,stdout=DEVNULL)
        commit_id = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], cwd=devops_dir,capture_output=True).stdout
        commit_id = str(commit_id).split('\'')[1][:-2]
        subprocess.run(['git', 'push','origin','main'], cwd=devops_dir, stdout=DEVNULL)
        print("Latest Commit to DevOps Repository done with commit id: " + commit_id)
    except git.exc.GitCommandError as e:
        if ("nothing to commit, working directory clean" in str(e)):
            print("Nothing to commit to DevOps Repository.")
    except Exception as e:
        print(e)
        print("Exiting...")
        exit(1)
    # Create develop branch from main
    subprocess.run(['git', 'checkout', '-B', 'develop','main'], cwd=devops_dir, stdout=DEVNULL)
    subprocess.run(['git', 'pull', 'origin', 'develop','--rebase'], cwd=devops_dir,stdout=DEVNULL,stderr=DEVNULL)
    subprocess.run(['git', 'push', 'origin', 'develop','-f'], cwd=devops_dir, stdout=DEVNULL)
    return commit_id

def create_bucket(config, signer):
    bucket_region = config.get('region').strip()
    buckets_client = ObjectStorageClient(config=config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY, signer=signer)
    namespace = buckets_client.get_namespace().data
    try:
        buckets_client.get_bucket(namespace, bucket_name).data
        print("Bucket exists with name(" + bucket_name + ") in " + bucket_region + ". Reusing same.")
    except Exception as e:
        #print("\nCreating bucket " + bucket_name + " under root compartment in " + bucket_region+" for remote state...")
        create_bucket_response = buckets_client.create_bucket(
        namespace_name=namespace,
        create_bucket_details=oci.object_storage.models.CreateBucketDetails(name=bucket_name,compartment_id=compartment_ocid,versioning='Enabled'))
    return bucket_region,bucket_name


# Execution of code begins here
parser = argparse.ArgumentParser(description="Connects the container to tenancy")
parser.add_argument("propsfile", help="Full Path of properties file. eg tenancyconfig.properties")
args = parser.parse_args()
config = configparser.RawConfigParser()
config.read(args.propsfile)

current_time=str(datetime.datetime.now())

# Initialize Toolkit Variables
user_dir = "/cd3user"

safe_file = user_dir + "/tenancies/createTenancyConfig.safe"
auto_keys_dir = user_dir + "/tenancies/keys"
toolkit_dir = os.path.dirname(os.path.abspath(__file__))+"/.."
#toolkit_dir = user_dir +"/oci_tools/cd3_automation_toolkit"
terraform_dir = toolkit_dir + "/user-scripts/terraform"
variables_example_file = terraform_dir + "/variables_example.tf"
setupoci_props_toolkit_file_path = toolkit_dir + "/setUpOCI.properties"

jenkins_install = toolkit_dir + "/../jenkins_install"
#if hasattr(os.environ,'JENKINS_INSTALL'):
if environ.get('JENKINS_INSTALL') is not None:
    jenkins_install = os.environ['JENKINS_INSTALL']

prefix = config.get('Default', 'prefix').strip()
if prefix == "" or prefix == "\n":
    print("Invalid Prefix. Please try again......Exiting !!")
    exit(1)

prefixes=[]
if os.path.exists(safe_file):
    f=open(safe_file,"r")
    safe_file_lines = f.readlines()
    for l in safe_file_lines:
        if "SUCCESS" in l:
            prefixes.append(l.split("\t")[0])

if prefixes !=[]:
    if prefix in prefixes:
        print("WARNING!!! Container has already been successfuly connected to the tenancy with same prefix. Please proceed only if you are re-running the script for new region subscription")
    #else:
        #print("WARNING!!! Container has already been successfully connected to the tenancy with these values of prefixes: "+str(list(set(prefixes))))
        #print("WARNING!!! Toolkit usage with Jenkins has not been tested with running this script multiple times with different values of prefix in the properties file")
        #print("Jenkins is configured for the prefix used for the first successful execution of the script.")
        inp = input("\nDo you want to proceed (y/n):")
        if inp.lower()=="n":
            exit(1)

# Initialize Tenancy Variables
customer_tenancy_dir = user_dir + "/tenancies/" + prefix
config_files= user_dir + "/tenancies/" + prefix +"/.config_files"
config_file_path = config_files + "/" + prefix + "_oci_config"

terraform_files = customer_tenancy_dir + "/terraform_files/"
outdir_safe=terraform_files+"/.safe"
setupoci_props_file_path = customer_tenancy_dir + "/" + prefix + "_setUpOCI.properties"

# Read Config file Variables
try:
    user=''
    _key_path=''
    fingerprint=''
    cloud_domain=''

    tenancy = config.get('Default', 'tenancy_ocid').strip()
    if tenancy == "" or tenancy == "\n":
        print("Tenancy ID cannot be left empty...Exiting !!")
        exit(1)
    if ("ocid1.tenancy.oc1" in tenancy):
        cloud_domain=".oraclecloud.com"
    else:
        cloud_domain=".oraclegovcloud.com"


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

    outdir_structure_file = config.get('Default', 'outdir_structure_file').strip()
    ssh_public_key = config.get('Default', 'ssh_public_key').strip()

    tf_or_tofu = config.get('Default', 'tf_or_tofu').strip().lower()
    if tf_or_tofu == "" or tf_or_tofu == "\n":
        tf_or_tofu = "terraform"

    ## Advanced parameters ##
    remote_state = config.get('Default', 'use_remote_state').strip().lower()
    remote_state_bucket = config.get('Default', 'remote_state_bucket_name').strip()

    use_devops = config.get('Default', 'use_oci_devops_git').strip().lower()
    devops_repo = config.get('Default', 'oci_devops_git_repo_name').strip()
    devops_user = config.get('Default', 'oci_devops_git_user').strip()
    devops_user_key = config.get('Default', 'oci_devops_git_key').strip()

    # Check if Jenkins was installed during image build

    if environ.get('USE_DEVOPS') is None:
        use_devops_docker = "yes"
    else:
        use_devops_docker = os.environ['USE_DEVOPS']
        use_devops_docker=use_devops_docker.lower()


    if use_devops_docker != use_devops:
        use_devops = "no"

    if use_devops == 'yes':
        import git

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

    compartment_ocid = config.get('Default', 'compartment_ocid').strip()
    if compartment_ocid == '' or compartment_ocid == '\n':
        compartment_ocid = tenancy


except Exception as e:
    print(e)
    print('Check if input properties exist and try again..exiting...')
    exit(1)


if not os.path.exists(customer_tenancy_dir):
    os.makedirs(customer_tenancy_dir)
if not os.path.exists(config_files):
    os.makedirs(config_files)
if not os.path.exists(outdir_safe):
    os.makedirs(outdir_safe)
if not os.path.exists(customer_tenancy_dir+'/othertools_files'):
    os.makedirs(customer_tenancy_dir+'/othertools_files')

dir_values = []

# Copy input properties file to customer_tenancy_dir
shutil.copy(args.propsfile,config_files+"/"+prefix+"_"+os.path.basename(args.propsfile))

# 1. Copy outdir_structure_file

# Copy default outdir_structure_file
shutil.copy(toolkit_dir+'/user-scripts/outdir_structure_file.properties', toolkit_dir+'/user-scripts/.outdir_structure_file.properties')

_outdir_structure_file = ''
if (outdir_structure_file != '' and outdir_structure_file != "\n"):
    if not os.path.isfile(outdir_structure_file):
        print("Invalid outdir_structure_file. Please provide correct file path......Exiting !!")
        exit(1)
    else:
        outdir_config = configparser.RawConfigParser()
        outdir_config.read(outdir_structure_file)
        for key, value in outdir_config.items("Default"):
            if value == '':
                print("Out Directory is missing for one or more parameters, for eg. " + key)
                print("Please check " + outdir_structure_file)
                exit(1)
            if value not in dir_values:
                dir_values.append(str(value))

        _outdir_structure_file = customer_tenancy_dir + "/" + prefix + "_outdir_structure_file.properties"
        #if not os.path.exists(_outdir_structure_file):
        shutil.copyfile(outdir_structure_file, _outdir_structure_file)
    print("\nUsing different directories for OCI services as per the input outdir_structure_file..........")
else:
    print("\nUsing single out directory for resources..........")

# 2. Move Private PEM key and Session Token file
_session_token_file=''
_key_path = ''
if auth_mechanism=='api_key': # or auth_mechanism=='session_token':
    print("\nCopying Private Key File..........")
    # Move Private PEM Key File
    filename = os.path.basename(key_path)
    #shutil.copy(key_path, key_path + "_backup_"+ datetime.datetime.now().strftime("%d-%m-%H%M%S").replace('/', '-'))
    shutil.copy(key_path, config_files + "/" + filename)
    _key_path = config_files + "/" + filename
    os.chmod(_key_path,0o600)

# 3. Create config file
#if not os.path.isfile(config_file_path):
print("\nCreating Tenancy specific config.................")#, terraform provider , variables and properties files.................")

if auth_mechanism=='api_key':
    file = open(config_file_path, "w")
    file.write("[DEFAULT]\n"
               "tenancy = "+tenancy+"\n"
                                    "fingerprint = "+fingerprint+"\n"
                                                                 "user = "+user+"\n"
                                                                                "key_file = "+_key_path+"\n"
                                                                                                        "region = "+region+"\n")
    file.close()
elif auth_mechanism=='session_token':
    '''
    file.write("[DEFAULT]\n"
               "tenancy = "+tenancy+"\n"
                                    "fingerprint = "+fingerprint+"\n"
                                                                 "security_token_file = "+_session_token_file+"\n"
                                                                                                              "key_file = "+_key_path+"\n"
                                                                                                                                                  "region = "+region+"\n")
    '''
    # copy config file to prefix specific directory and create symlink for TF execution
    config_file_path_user_home = user_dir + "/.oci/config"
    # To take care of multiple executions of createTenancyConfig,py
    if not os.path.islink(config_file_path_user_home):
        #shutil.copy(config_file_path_user_home,config_file_path_user_home + "_backup_" + datetime.datetime.now().strftime("%d-%m-%H%M%S").replace('/', '-'))
        shutil.copy(config_file_path_user_home, config_file_path)
        src = config_file_path
        dst = config_file_path_user_home
        try:
            os.symlink(src,dst)
        except FileExistsError as e:
            os.unlink(dst)
            os.symlink(src,dst)

elif auth_mechanism=='instance_principal':
    file = open(config_file_path, "w")
    file.write("[DEFAULT]\n"
               "tenancy = "+tenancy+"\n"
                                    "region = "+region+"\n")
    file.close()


tenancy_id=tenancy

## Authenticate
ct = commonTools()
config, signer = ct.authenticate(auth_mechanism, config_file_path)
## Fetch OCI_regions
cd3service = cd3Services()
cd3service.fetch_regions(config, signer)

#This is needed to be initialised again
ct = commonTools()
try:
    ct.get_subscribedregions(config,signer)
except Exception as e:
    print(str(e))
    f = open(safe_file, "a")
    data = prefix + "\t" + "FAIL\t" + current_time + "\n"
    f.write(data)
    f.close()
    exit(1)

home_region = ct.home_region


## Check the remote state requirements
backend_file = open(terraform_dir + "/backend.tf", 'r')
backend_file_data = backend_file.readlines()
global_backend_file_data = ""

if remote_state == "yes":
    #fetch compartment ocid from compartment name
    if "ocid1.compartment.oc" not in compartment_ocid and "ocid1.tenancy.oc" not in compartment_ocid:
        print("Fetching existing Compartments from Tenancy...")
        ct.get_network_compartment_ids(config['tenancy'], "root", config, signer)
        compartment_ocid = ct.ntk_compartment_ids[compartment_ocid]

    print("\nCreating Tenancy specific remote tfstate Items - bucket, S3 credentials.................")
    s3_credential_file_path = config_files + "/" + prefix + "_s3_credentials"
    buckets_client = ObjectStorageClient(config=config,
                                         retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY,
                                         signer=signer)
    namespace = buckets_client.get_namespace().data
    bucket_region,bucket_name=create_bucket(config,signer)
    try:
        # Generate customer_secret_keys for remote state credentials
        new_config = deepcopy(config)
        new_config.__setitem__("region", ct.region_dict[home_region])

        identity_client = oci.identity.IdentityClient(config=new_config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY,signer=signer)
        cred_name = prefix+"-automation-toolkit-csk"

        # Get user ocid for DevOps User Name
        if "ocid1.user.oc" not in remote_state_user:
            if '@' in remote_state_user:
                remote_state_user = remote_state_user.rsplit("@",1)[0]

            identity_client = oci.identity.IdentityClient(config=new_config,
                                                          retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY,
                                                          signer=signer)
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


        # check if S3 credential exists
        customer_secret_key_id=''
        credential_file_data=''
        list_customer_secret_key_response = identity_client.list_customer_secret_keys(user_id=remote_state_user).data
        for keys in list_customer_secret_key_response:
            if keys.display_name == cred_name:
                customer_secret_key_id=keys.id
                break

        if customer_secret_key_id!='':
            # Delete existing key with same name from user profile if S3 credential file is missing and create new one
            if not os.path.exists(s3_credential_file_path):
                identity_client.delete_customer_secret_key(user_id=remote_state_user,
                                                   customer_secret_key_id=customer_secret_key_id)

                create_customer_secret_key_response = identity_client.create_customer_secret_key(create_customer_secret_key_details=oci.identity.models.CreateCustomerSecretKeyDetails(display_name=cred_name),user_id=remote_state_user).data
                credential_file_data="[default]\naws_access_key_id="+str(create_customer_secret_key_response.id)+"\naws_secret_access_key="+create_customer_secret_key_response.key+"\n"
            # If S3 Crednetials file exists, check if it's the same key
            elif os.path.exists(s3_credential_file_path):
                text = "aws_access_key_id="+customer_secret_key_id+""
                f = open(f"{s3_credential_file_path}", "r")
                same_key=0
                existing_credential_file_lines = f.readlines()
                for line in existing_credential_file_lines:
                    if text == line.strip():
                        same_key=1
                        break

                #If Access Key id is different then delete the existing key and create new one
                if same_key == 0 :
                    identity_client.delete_customer_secret_key(user_id=remote_state_user,
                                                           customer_secret_key_id=customer_secret_key_id)

                    create_customer_secret_key_response = identity_client.create_customer_secret_key(
                    create_customer_secret_key_details=oci.identity.models.CreateCustomerSecretKeyDetails(
                        display_name=cred_name), user_id=remote_state_user).data
                    credential_file_data = "[default]\naws_access_key_id=" + str(
                    create_customer_secret_key_response.id) + "\naws_secret_access_key=" + create_customer_secret_key_response.key + "\n"
                else:
                    print("Continuing to use existing customer secret key\n")

        #Create New Key
        if customer_secret_key_id == '':
            if (len(list_customer_secret_key_response) > 1):
                print("\nUser (" + remote_state_user + ") already has max customer secret keys created. Cannot create a new one to be used with toolkit for tfstate remote management.  Please clear the existing keys or use different user. Exiting...")
                exit(1)
            create_customer_secret_key_response = identity_client.create_customer_secret_key(
                create_customer_secret_key_details=oci.identity.models.CreateCustomerSecretKeyDetails(
                    display_name=cred_name), user_id=remote_state_user).data
            credential_file_data = "[default]\naws_access_key_id=" + str(create_customer_secret_key_response.id) + "\naws_secret_access_key=" + create_customer_secret_key_response.key + "\n"

    except Exception as e:
        print(str(e))
        exit(1)
        # Add code to ask domain name/url and generate creds

    if credential_file_data!='':
        print("Creating new customer secret key\n")
        f = open(f"{s3_credential_file_path}", "w+")
        f.write(credential_file_data)
        f.close()

    for line in backend_file_data:
        if line.__contains__("This line will be removed when using remote state"):
            continue
        elif line.__contains__("key      = "):
            global_backend_file_data += "    key      = \"" +  "global/terraform.tfstate\"\n"
        elif line.__contains__("bucket   = "):
            global_backend_file_data += "    bucket   = \"" + bucket_name + "\"\n"
        elif line.__contains__("region   = "):
            global_backend_file_data += "    region   = \"" + bucket_region + "\"\n"
        elif line.__contains__("endpoint = "):
            global_backend_file_data += "    endpoint = \"https://" + namespace + ".compat.objectstorage." + bucket_region + cloud_domain + "\"\n"
        elif line.__contains__("shared_credentials_file     = "):
            global_backend_file_data += "    shared_credentials_file     = \"" + s3_credential_file_path + "\"\n"
        else:
            global_backend_file_data += line
else:
    for line in backend_file_data:
        global_backend_file_data += line


'''
# 3. Fetch AD Names and write to config file
print('Fetching AD names from tenancy and writing to config file if it does not exist.............')
identity_client = oci.identity.IdentityClient(config=config,signer=signer)
conf_file = open(config_file_path, "a")
tenancy_id = tenancy
i = 1
for ad in paginate(identity_client.list_availability_domains, compartment_id=tenancy_id):
    ad_name = "ad_" + str(i)
    if not ad_name in config:
        conf_file.write("ad_" + str(i) + "=" + ad.name + "\n")
    i = i + 1
conf_file.close()
'''

# 4. Generate setUpOCI.properties file
#if not os.path.isfile(setupoci_props_file_path):
print("Creating Tenancy specific setUpOCI.properties.................")
with open(setupoci_props_toolkit_file_path, 'r+') as setUpOci_file:
    setupoci_props_toolkit_file_data = setUpOci_file.read().rstrip()

setupoci_props_toolkit_file_data = setupoci_props_toolkit_file_data.replace("outdir=", "outdir="+terraform_files)
setupoci_props_toolkit_file_data = setupoci_props_toolkit_file_data.replace("prefix=", "prefix="+prefix)
setupoci_props_toolkit_file_data = setupoci_props_toolkit_file_data.replace("auth_mechanism=", "auth_mechanism=" + auth_mechanism)
setupoci_props_toolkit_file_data = setupoci_props_toolkit_file_data.replace("config_file=", "config_file="+config_file_path)
setupoci_props_toolkit_file_data = setupoci_props_toolkit_file_data.replace("outdir_structure_file=", "outdir_structure_file="+_outdir_structure_file)
setupoci_props_toolkit_file_data = setupoci_props_toolkit_file_data.replace("tf_or_tofu=", "tf_or_tofu="+tf_or_tofu)

f = open(setupoci_props_file_path, "w+")
f.write(setupoci_props_toolkit_file_data)
f.close()

# 5. Fetch Subscribed regions and create the TF related files for each region
if not os.path.exists(terraform_files):
    os.makedirs(terraform_files)

# Copy modules dir to terraform_files folder
try:
    shutil.copytree(terraform_dir + "/modules", terraform_files + "/modules")
except FileExistsError as fe:
    pass

print("Creating Tenancy specific region directories, terraform provider , variables files.................")
regions_file_data = ""

# 6. Read variables.tf from examples folder and copy the variables as string

for region in ct.all_regions:
    regions_file_data = regions_file_data + region.title() + "\n"

    with open(variables_example_file, 'r+') as var_eg_file:
        variables_example_file_data = var_eg_file.read().rstrip()

    variables_example_file_data = variables_example_file_data.replace("<TENANCY OCID HERE>", tenancy)
    variables_example_file_data = variables_example_file_data.replace("<USER OCID HERE>", user)
    variables_example_file_data = variables_example_file_data.replace("<SSH KEY FINGERPRINT HERE>", fingerprint)
    variables_example_file_data = variables_example_file_data.replace("<SSH PRIVATE KEY FULL PATH HERE>", _key_path)
    variables_example_file_data = variables_example_file_data.replace("<SSH PUB KEY STRING HERE>", ssh_public_key)
    variables_example_file_data = variables_example_file_data.replace(
        "<OCI TENANCY REGION HERE eg: us-phoenix-1 or us-ashburn-1>", ct.region_dict[region])

    # Global dir for RPC related
    if region == ct.home_region:

        if not os.path.exists(f"{terraform_files}/global/rpc"):
            os.makedirs(f"{terraform_files}/global/rpc")

            shutil.copyfile(terraform_dir + "/provider.tf", f"{terraform_files}/global/rpc/provider.tf")

            with open(f"{terraform_files}/global/rpc/provider.tf", 'r+') as provider_file:
                provider_file_data = provider_file.read().rstrip()
            if auth_mechanism == 'instance_principal':
                provider_file_data = provider_file_data.replace("provider \"oci\" {",
                                                                "provider \"oci\" {\nauth = \"InstancePrincipal\"")
            if auth_mechanism == 'session_token':
                provider_file_data = provider_file_data.replace("provider \"oci\" {",
                                                                "provider \"oci\" {\nauth = \"SecurityToken\"\nconfig_file_profile = \"DEFAULT\"")

            f = open(f"{terraform_files}/global/rpc/provider.tf", "w+")
            f.write(provider_file_data)
            f.close()

            f = open(f"{terraform_files}/global/rpc/variables_global.tf", "w+")
            f.write(variables_example_file_data)
            f.close()

            f = open(f"{terraform_files}/global/rpc/backend.tf", "w+")
            f.write(global_backend_file_data)
            f.close()


    # Rerunning createTenancy for any new region subscription. Process only new region directories else continue
    if os.path.exists(terraform_files+region):
        continue

    #os.mkdir(terraform_files+region)

    # 7. Copy terraform modules and variables file to outdir
    '''
    if modules_source+"/" == terraform_files:
        try:
            shutil.copytree(terraform_dir + "/modules", terraform_files+"/modules")
        except FileExistsError as fe:
            pass

    shutil.copytree(terraform_dir, terraform_files + "/" + region + "/", ignore=shutil.ignore_patterns("modules"))
    '''
    #shutil.copytree(terraform_dir, terraform_files + "/" + region + "/")
    shutil.copytree(terraform_dir, terraform_files + "/" + region + "/", ignore=shutil.ignore_patterns("modules"))

    #Prepare variables file
    linux_image_id = ''
    windows_image_id = ''

    new_config = deepcopy(config)
    new_config.__setitem__("region", ct.region_dict[region])
    cc = oci.core.ComputeClient(config=new_config,signer=signer)

    # fetch latest image ocids
    try:
        for image in paginate(cc.list_images, compartment_id=tenancy_id, operating_system='Oracle Linux',
                              sort_by='TIMECREATED'):

            if ("Gen2-GPU" not in image.display_name and "aarch" not in image.display_name and "Minimal" not in image.display_name):
                linux_image_id = image.id
                break

        for image in paginate(cc.list_images, compartment_id=tenancy_id, operating_system='Windows',
                              sort_by='TIMECREATED'):
            if ("Gen2" not in image.display_name and "Datacenter" not in image.display_name):
                windows_image_id= image.id
                break

    except Exception as e:
        print(e)
        print("!!! Could not fetch the list of images for Windows and Oracle Linux to write to variables_"+region+".tf file!!!\n"
                                                                                                                  "Please make sure to have Read Access to the Tenancy at the minimum !!!")
        print("\nContinuing without fetching Image OCIDs........!!!")

    if (windows_image_id != ''):
        variables_example_file_data = variables_example_file_data.replace("<LATEST WINDOWS OCID HERE>", windows_image_id)

    if (linux_image_id != ''):
        variables_example_file_data = variables_example_file_data.replace("<LATEST LINUX OCID HERE>", linux_image_id)

    f = open(terraform_files+"/"+region+"/variables_" + region + ".tf", "w+")
    f.write(variables_example_file_data)
    f.close()


    with open(terraform_files +"/" + region + "/provider.tf", 'r+') as provider_file:
        provider_file_data = provider_file.read().rstrip()
    if auth_mechanism == 'instance_principal':
        provider_file_data = provider_file_data.replace("provider \"oci\" {",
                                                        "provider \"oci\" {\nauth = \"InstancePrincipal\"")
    if auth_mechanism == 'session_token':
        provider_file_data = provider_file_data.replace("provider \"oci\" {",
                                                        "provider \"oci\" {\nauth = \"SecurityToken\"\nconfig_file_profile = \"DEFAULT\"")
    f = open(terraform_files +"/" + region + "/provider.tf", "w+")
    f.write(provider_file_data)
    f.close()

    reg_backend = open(terraform_files +"/" + region + "/backend.tf",'w+')
    reg_backend.write(global_backend_file_data)
    reg_backend.close()
    reg_backend = open(terraform_files + "/" + region + "/backend.tf", 'r+')
    new_backend_data = ""

    for line in reg_backend.readlines():
        if line.__contains__("key      = "):
            new_backend_data += "    key      = \"" + region + "/terraform.tfstate\"\n"
        else:
            new_backend_data += line
    reg_backend.close()
    rewrite_backend = open(terraform_files + "/" + region + "/backend.tf", 'w')
    rewrite_backend.write(new_backend_data)
    rewrite_backend.close()

    # Manage single and multiple outdir
    if (outdir_structure_file == '' or outdir_structure_file == "\n"):
        #remove depends_on for single outdir
        region_dir = terraform_files + "/" + region + "/"
        single_outdir_config = configparser.RawConfigParser()
        outdir_config_file = os.path.dirname(os.path.abspath(__file__)) + "/.outdir_structure_file.properties"

        single_outdir_config.read(outdir_config_file)
        keys = []
        for key, val in single_outdir_config.items("Default"):
            keys.append(key)
        for file in os.listdir(region_dir):
            #name=file.removesuffix(".tf")
            name = file[:-len(".tf")]
            if name in keys:
                file=region_dir+"/"+file
                with open(file, 'r+') as tf_file:
                    module_data = tf_file.read().rstrip()
                    module_data = module_data.replace("# depends_on", "depends_on")
                    module_data = module_data.replace("\"./modules", "\"../modules")

                tf_file.close()
                f = open(file, "w+")
                f.write(module_data)
                f.close()
    else:
        region_dir = terraform_files + "/" + region + "/"
        for service, service_dir in outdir_config.items("Default"):
            service = service.strip().lower()
            service_dir = service_dir.strip()

            # Keep the .tf file in default region directory if directory name is empty
            if service_dir=="" or service_dir == "\n":
                continue
            #if (service != 'identity' and service != 'tagging') or ((service == 'identity' or service == 'tagging') and region == home_region):
            home_region_services = ['identity', 'tagging', 'budget','quota']
            if (region != home_region) and (service in home_region_services):
                os.remove(region_dir + service + ".tf")

            if (service not in home_region_services) or ((service in home_region_services) and region == home_region):
                region_service_dir = region_dir + service_dir
                if not os.path.exists(region_service_dir):
                    os.mkdir(region_service_dir)
                if (service == 'instance'):
                    if(os.path.isdir(region_service_dir+'/scripts')):
                        shutil.rmtree(region_service_dir+'/scripts')
                    shutil.move(region_dir + 'scripts',region_service_dir+'/')
                with open(region_dir + service + ".tf", 'r+') as tf_file:
                    module_data = tf_file.read().rstrip()
                    module_data = module_data.replace("\"./modules", "\"../../modules")

                f = open(region_service_dir + "/" + service + ".tf", "w+")
                f.write(module_data)
                f.close()
                os.remove(region_dir + service + ".tf")

                shutil.copyfile(region_dir + "variables_" + region + ".tf", region_service_dir + "/" + "variables_" + region + ".tf")
                shutil.copyfile(region_dir + "provider.tf", region_service_dir + "/" + "provider.tf")
                shutil.copyfile(region_dir + "oci-data.tf", region_service_dir + "/" + "oci-data.tf")

                # write backend.tf to respective directories
                reg_service_backend = open(region_service_dir + "/backend.tf", 'w+')
                reg_service_backend.write(global_backend_file_data)
                reg_service_backend.close()
                reg_service_backend = open(region_service_dir + "/backend.tf", 'r+')
                new_backend_data = ""

                for line in reg_service_backend.readlines():
                    if line.__contains__("key      = "):
                        new_backend_data += "    key      = \"" + region+"/"+service_dir + "/terraform.tfstate\"\n"
                    else:
                        new_backend_data += line
                reg_service_backend.close()
                rewrite_backend = open(terraform_files + "/" + region+"/"+service_dir + "/backend.tf", 'w')
                rewrite_backend.write(new_backend_data)
                rewrite_backend.close()


        os.remove(terraform_files + "/" + region + "/" + "variables_" + region + ".tf")
        os.remove(terraform_files + "/" + region + "/" + "provider.tf")
        os.remove(terraform_files + "/" + region + "/" + "oci-data.tf")
        os.remove(terraform_files + "/" + region + "/" + "backend.tf")

    # 8. Remove terraform example variable file from outdir
    os.remove(terraform_files + "/" + region + "/variables_example.tf")
# 9. Update DevOps files and configurations
if use_devops == 'yes':
    print("\nCreating Tenancy specific DevOps Items - Topic, Project and Repository.................")
    # create subscribed regions file
    f = open(customer_tenancy_dir + "/.config_files/regions_file", "w+")
    f.write(regions_file_data[:-1])
    f.close()
    # create all compartments_file
    if ct.ntk_compartment_ids == {}:
        print("Fetching existing Compartments from Tenancy...")
        ct.get_network_compartment_ids(config['tenancy'], "root", config, signer)
    compartments_file_data = ""
    comp_done = []
    for k, v in ct.ntk_compartment_ids.items():
        if v not in comp_done:
            compartments_file_data += k + "\n"
            comp_done.append(v)

    f = open(customer_tenancy_dir + "/.config_files/compartments_file", "w+")
    f.write(compartments_file_data[:-1])
    f.close()

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

    repo_ssh_url,files_in_repo = create_devops_resources(config, signer)
    devops_dir = terraform_files

    jenkins_home = user_dir+"/tenancies/jenkins_home"
    #if hasattr(os.environ, 'JENKINS_HOME'):
    if environ.get('JENKINS_HOME') is not None:
        jenkins_home = os.environ['JENKINS_HOME']

    #git_config_file = config_files + "/" + prefix + "_git_config"

    #Get Username from $user_ocid if $oci_devops_git_user is left empty
    if "ocid1.user.oc" in devops_user:
        identity_client = oci.identity.IdentityClient(config=new_config,
                                                      retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY,
                                                      signer=signer)
        user_data=identity_client.get_user(user_id=user).data
        tenancy_data=identity_client.get_tenancy(tenancy_id=tenancy).data
        devops_user=user_data.name+"@"+tenancy_data.name

    commit_id = update_devops_config(prefix, repo_ssh_url,files_in_repo, dir_values, devops_user, devops_user_key, devops_dir, ct)

del ct, config, signer
# Logging information
outfile = customer_tenancy_dir+'/createTenancyConfig.out'
logging.basicConfig(filename=outfile, format='%(message)s', filemode='w', level=logging.INFO)

print("==================================================================================================================================")
print("\nThe toolkit has been setup successfully. !!!\n")
#print("Customer Specific Working Directory Path: "+customer_tenancy_dir)
#print("Config File Path: "+ config_file_path )
#print("Path to region based directories, terraform provider and the variables files: " + terraform_files)
#print("\nPlease use "+prefix+"_setUpOCI.properties file at "+customer_tenancy_dir +" to proceed with the execution of the SetUpOCI script !!!!")
#print("Update the path of CD3 Excel input file in "+customer_tenancy_dir + "/" +prefix+"_setUpOCI.properties before executing the next command......")
#print("\nCommands to execute: (Alternately, you may also check the cmds.log in outdir for the same information)")
f = open(safe_file, "a")
data=prefix + "\t" + "SUCCESS\t"+current_time+"\n"
f.write(data)
f.close()

logging.info("Prefix Specific Working Directory Path: "+customer_tenancy_dir+"\n")

if remote_state == 'yes':
    logging.info("Remote State Bucket Name: "+ bucket_name+ " in "+rg+".")

if use_devops == "yes":
    logging.info("Common Jenkins Home: " +jenkins_home)
    logging.info("DevOps Project Name and Repo Name: "+project_name+ ", "+repo_name+ " in "+rg+".")
    logging.info("Folder configured for OCI DevOps GIT: "+terraform_files+" Initial Commit ID from createTenancyConfig.py: "+commit_id)
    logging.info("\n#########################################")
    logging.info("Next Steps for using toolkit via Jenkins")
    logging.info("#########################################")
    logging.info("Start Jenkins using  - /usr/share/jenkins/jenkins.sh &")
    logging.info("Access Jenkins using - https://<IP Address of the machine hosting docker container>:8443")

logging.info("\n######################################")
logging.info("Next Steps for using toolkit via CLI")
logging.info("######################################")
logging.info("Modify "+customer_tenancy_dir + "/" +prefix+"_setUpOCI.properties with input values for cd3file and workflow_type")
logging.info("cd "+user_dir+"/oci_tools/cd3_automation_toolkit/")
logging.info("python setUpOCI.py "+customer_tenancy_dir + "/" +prefix+"_setUpOCI.properties")

with open(outfile, 'r') as log_file:
    data = log_file.read().rstrip()
print(data)

print("==================================================================================================================================")

