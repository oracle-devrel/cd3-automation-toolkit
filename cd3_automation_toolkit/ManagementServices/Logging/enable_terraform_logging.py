#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI Management components
# Logging
#
# Author: Suruchi Singla
# Oracle Consulting
# Modified (TF Upgrade): Shruthi Subramanian
#

import os
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from oci.config import DEFAULT_LOCATION
from commonTools import *

######
# Required Inputs- Config file, prefix AND outdir
######
# Execution of the code begins here
def enable_cis_oss_logging(filename, outdir, service_dir, prefix, config=DEFAULT_LOCATION):

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, "Buckets")

    # Remove empty rows
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    # List of the column headers
    dfcolumns = df.columns.values.tolist()

    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    template = env.get_template('logging-template')
    auto_tfvars_filename = prefix+'_buckets-logging.auto.tfvars'

    tfStrLogs = {}
    tempStr = {}
    outfile = {}
    buckets_list = {}
    tfStrLogGroups = {}
    tempdict = {}


    for i in df.index:
        region = str(df.loc[i, 'Region'])

        if (region in commonTools.endNames):
            break

        region = region.strip().lower()
        tfStrLogs[region] = ''
        tfStrLogGroups[region] = ''
        buckets_list[region] = []

    for i in df.index:
        region = str(df.loc[i, 'Region'])
        if (region in commonTools.endNames):
            break

        region_name = region.strip().lower()
        compartment_var_name = str(df.loc[i, 'Compartment Name']).strip()
        bucket_name = str(df['Bucket Name'][i]).strip()
        bucket_tf_name = commonTools.check_tf_variable(bucket_name)

        for columnname in dfcolumns:
            if columnname.lower() in commonTools.tagColumns:
                columnvalue = str(df[columnname][i]).strip()
                if columnvalue != 'nan' and columnvalue != '':
                    tempdict = commonTools.split_tag_values(columnname, columnvalue, tempdict)
                    tempStr.update(tempdict)

        compartmentVarName = commonTools.check_tf_variable(compartment_var_name)
        columnvalue = str(compartmentVarName)

        tempStr['compartment_tf_name'] = columnvalue
        tempStr['region'] = region_name
        tempStr['oci_service'] = 'oss'

        loggroup_name = bucket_name+"-bucket-log-group"
        loggroup_tf_name = commonTools.check_tf_variable(bucket_name)+"-bucket-log-group"
        log_name = bucket_name+"-write-log"
        log_tf_name = commonTools.check_tf_variable(bucket_name)+"-write-log"
        log_group_id= loggroup_tf_name
        resource=bucket_name

        if bucket_name not in buckets_list[region_name]:
            tempStr['loggroup_name'] = loggroup_name
            tempStr['loggroup_tf_name'] = loggroup_tf_name
            tempStr['loggroup_desc']='Log Group for OSS bucket'
            tfStrLogGroups[region_name] = tfStrLogGroups[region_name] + template.render(tempStr, loggroup='true')
            buckets_list[region_name].append(bucket_name)

            tempStr['loggroup'] = 'false'
            tempStr['log_group_id'] = log_group_id
            tempStr['resource'] = resource
            tempStr['log_name'] = log_name
            tempStr['log_tf_name'] = log_tf_name
            tempStr['category'] = 'write'
            tempStr['service'] = 'objectstorage'
            tfStrLogs[region_name] = tfStrLogs[region_name] + template.render(tempStr)

    # Write TF string to the file in respective region directory
    for reg in tfStrLogs.keys():
        reg_out_dir = outdir + "/" + reg +"/" + service_dir
        if not os.path.exists(reg_out_dir):
            os.makedirs(reg_out_dir)

        outfile[reg] = reg_out_dir + "/"+auto_tfvars_filename
        srcdir = reg_out_dir + "/"
        resource = 'osslog'
        commonTools.backup_file(srcdir, resource, auto_tfvars_filename)

        srcStr = "##Add New Logs for " + reg + " here##"
        tfStrLogs[reg] = template.render(tempStr, count=0, region=reg).replace(srcStr, tfStrLogs[reg] + "\n" + srcStr)

        srcStr = "##Add New Log Groups for " + reg + " here##"
        tfStrLogGroups[reg] = template.render(tempStr, loggroup= 'true', count=0, region=reg).replace(srcStr, tfStrLogGroups[reg] + "\n" + srcStr)

        tfStrLogs[reg] = tfStrLogs[reg] +"\n"+ tfStrLogGroups[reg]

        if(tfStrLogs[reg]!=''):
            oname=open(outfile[reg],'w')
            tfStrLogs[reg] = "".join([s for s in tfStrLogs[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
            oname.write(tfStrLogs[reg])
            oname.close()
            print(outfile[reg] + " for OSS Bucket Logs has been created for region "+reg)

def enable_cis_vcnflow_logging(filename, outdir, service_dir, prefix, config=DEFAULT_LOCATION):

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, "SubnetsVLANs")

    # Remove empty rows
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    # List of the column headers
    dfcolumns = df.columns.values.tolist()

    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    template = env.get_template('logging-template')
    auto_tfvars_filename = prefix+'_vcnflow-logging.auto.tfvars'

    tfStrLogs = {}
    tempStr = {}
    outfile={}
    vcns_list = {}
    tfStrLogGroups = {}
    tempdict = {}

    for i in df.index:
        region = str(df.loc[i, 'Region'])

        if (region in commonTools.endNames):
            break

        region = region.strip().lower()
        tfStrLogs[region]=''
        tfStrLogGroups[region] = ''
        vcns_list[region] = []

    for i in df.index:
        region = str(df.loc[i, 'Region'])

        if (region in commonTools.endNames):
            break

        subnet_vlan_in_excel = str(df.loc[i, 'Subnet or VLAN']).strip()
        if subnet_vlan_in_excel.lower().startswith('vlan'):
            continue

        region = region.strip().lower()
        compartment_var_name = str(df.loc[i, 'Compartment Name']).strip()
        vcn_name = str(df['VCN Name'][i]).strip()
        name = str(df['Display Name'][i]).strip()

        for columnname in dfcolumns:
            if columnname.lower() in commonTools.tagColumns:
                columnvalue = str(df[columnname][i]).strip()
                if columnvalue !='nan' and columnvalue!='':
                    tempdict = commonTools.split_tag_values(columnname, columnvalue, tempdict)
                    tempStr.update(tempdict)

        display_name = name

        subnet_tf_name=vcn_name+"_"+display_name
        subnet_tf_name = commonTools.check_tf_variable(subnet_tf_name)

        compartmentVarName = commonTools.check_tf_variable(compartment_var_name)
        columnvalue = str(compartmentVarName)

        tempStr['compartment_tf_name'] =  columnvalue

        resource = subnet_tf_name
        loggroup_name = commonTools.check_tf_variable(vcn_name)+"-flow-log-group"
        log_name = commonTools.check_tf_variable(display_name)+"-flow-log"
        log_tf_name = commonTools.check_tf_variable(resource) + "-flow-log"
        log_group_id= loggroup_name


        tempStr['oci_service'] = 'vcn'

        if vcn_name not in vcns_list[region]:
            tempStr['loggroup_name'] = loggroup_name
            tempStr['loggroup_tf_name'] = loggroup_name
            tempStr['loggroup_desc'] = 'Log Group for VCN'
            tfStrLogGroups[region] = tfStrLogGroups[region] + template.render(tempStr,loggroup='true')
            vcns_list[region].append(vcn_name)

        tempStr['loggroup'] = 'false'
        tempStr['log_group_id'] = log_group_id
        tempStr['resource'] = resource
        tempStr['log_name'] = log_name
        tempStr['log_tf_name'] = log_tf_name
        tempStr['category'] = 'all'
        tempStr['service'] = 'flowlogs'

        tfStrLogs[region] = tfStrLogs[region] + template.render(tempStr)

    # Write TF string to the file in respective region directory
    for reg in tfStrLogs.keys():
        reg_out_dir = outdir + "/" + reg +"/" + service_dir
        if not os.path.exists(reg_out_dir):
            os.makedirs(reg_out_dir)

        outfile[reg] = reg_out_dir + "/" + auto_tfvars_filename

        srcdir = reg_out_dir + "/"
        resource = 'vcnflowlog'
        commonTools.backup_file(srcdir, resource, auto_tfvars_filename)

        srcStr = "##Add New Logs for " + reg + " here##"
        tfStrLogs[reg] = template.render(tempStr, count=0, region=reg).replace(srcStr, tfStrLogs[reg] + "\n" + srcStr)

        srcStr = "##Add New Log Groups for " + reg + " here##"
        tfStrLogGroups[reg] = template.render(tempStr, loggroup= 'true', count=0, region=reg).replace(srcStr, tfStrLogGroups[reg] + "\n" + srcStr)

        tfStrLogs[reg] = tfStrLogs[reg] +"\n"+ tfStrLogGroups[reg]

        if(tfStrLogs[reg]!=''):
            oname=open(outfile[reg],'w')
            tfStrLogs[reg] = "".join([s for s in tfStrLogs[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
            oname.write(tfStrLogs[reg])
            oname.close()
            print(outfile[reg] + " for VCN Flow Logs has been created for region "+reg)

def enable_load_balancer_logging(filename, outdir, service_dir, prefix, config=DEFAULT_LOCATION):

    # Declare variables
    configFileName = config

    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    template = env.get_template('logging-template')
    auto_tfvars_filename = prefix+"_load-balancers-logging.auto.tfvars"

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, "LB-Hostname-Certs")

    # Remove empty rows
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    # List of the column headers
    dfcolumns = df.columns.values.tolist()

    ct = commonTools()
    ct.get_subscribedregions(configFileName)

    tfStrLogs = {}
    tempStr = {}
    outfile={}
    lbr_list = {}
    tfStrLogGroups = {}
    tempdict = {}

    for i in df.index:
        region = str(df.loc[i, 'Region'])

        if (region in commonTools.endNames):
            break

        region = region.strip().lower()
        tfStrLogs[region]=''
        tfStrLogGroups[region] = ''
        lbr_list[region] = []

    for i in df.index:
        region = str(df.loc[i, 'Region'])

        if (region in commonTools.endNames):
            break

        region = region.strip().lower()
        compartment_var_name = str(df.loc[i, 'Compartment Name']).strip()
        description = "Log Group for "+str(df['LBR Name'][i]).strip()
        name = str(df['LBR Name'][i]).strip()

        for columnname in dfcolumns:
            if columnname.lower() in commonTools.tagColumns:
                columnvalue = str(df[columnname][i]).strip()
                if columnvalue !='nan' and columnvalue!='':
                    tempdict = commonTools.split_tag_values(columnname, columnvalue, tempdict)
                    tempStr.update(tempdict)

        compartmentVarName = commonTools.check_tf_variable(compartment_var_name)
        columnvalue = str(compartmentVarName)

        tempStr['compartment_tf_name'] =  columnvalue

        loggroup_name = commonTools.check_tf_variable(name)+"-log-group"
        lb_tf_name = commonTools.check_tf_variable(name)
        tempStr['oci_service'] = 'loadbalancer'

        if loggroup_name not in lbr_list[region]:
            tempStr['loggroup_name'] = loggroup_name
            tempStr['loggroup_tf_name'] = loggroup_name
            tempStr['loggroup_desc'] = description
            tfStrLogGroups[region] = tfStrLogGroups[region] + template.render(tempStr,loggroup='true')
            lbr_list[region].append(loggroup_name)

        tempStr['loggroup'] = 'false'
        tempStr['log_group_id'] = loggroup_name
        tempStr['resource'] = lb_tf_name
        tempStr['log_name'] = name
        tempStr['lb_log_tf_name'] = lb_tf_name
        tempStr['service'] = 'loadbalancer'
        tempStr['logtype'] = ['access','error']

        tfStrLogs[region] = tfStrLogs[region] + template.render(tempStr)

    # Write TF string to the file in respective region directory
    for reg in tfStrLogs.keys():
        reg_out_dir = outdir + "/" + reg + "/" + service_dir
        if not os.path.exists(reg_out_dir):
            os.makedirs(reg_out_dir)

        outfile[reg] = reg_out_dir + "/" + auto_tfvars_filename

        srcdir = reg_out_dir + "/"
        resource = 'loadbalancerlog'
        commonTools.backup_file(srcdir, resource, auto_tfvars_filename)

        srcStr = "##Add New Logs for " + reg + " here##"
        tfStrLogs[reg] = template.render(tempStr, count=0, region=reg).replace(srcStr, tfStrLogs[reg] + "\n" + srcStr)

        srcStr = "##Add New Log Groups for " + reg + " here##"
        tfStrLogGroups[reg] = template.render(tempStr, loggroup= 'true', count=0, region=reg).replace(srcStr, tfStrLogGroups[reg] + "\n" + srcStr)

        tfStrLogs[reg] = tfStrLogs[reg] +"\n"+ tfStrLogGroups[reg]

        if(tfStrLogs[reg]!=''):
            oname=open(outfile[reg],'w+')
            tfStrLogs[reg] = "".join([s for s in tfStrLogs[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
            oname.write(tfStrLogs[reg])
            oname.close()
            print(outfile[reg] + " containing TF for Load Balancer Logging has been created for region "+reg)

