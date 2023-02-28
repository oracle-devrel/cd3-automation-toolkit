#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI core components
# Groups
#
# Author: Suruchi Singla
# Oracle Consulting
# Modified (TF Upgrade): Shruthi Subramanian
#

import argparse
import os
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from oci.config import DEFAULT_LOCATION
from commonTools import *

######
# Required Inputs- Config file, prefix AND outdir
######

def parse_args():

    # Read the arguments
    parser = argparse.ArgumentParser(description="Create Groups terraform file")
    parser.add_argument('outdir', help='Output directory for creation of TF files')
    parser.add_argument('prefix', help='TF files prefix')
    parser.add_argument("service_dir",help="subdirectory under region directory in case of separate out directory structure")
    parser.add_argument("comp_name", help="compartment name")
    parser.add_argument("region_name", help="region name")
    parser.add_argument("--configFileName", help="Config file name", required=False)

def enable_cis_oss_logging(outdir, prefix, region_name, comp_name, config=DEFAULT_LOCATION):

    # Declare variables
    configFileName = config
    region_name=region_name.strip().lower()
    comp_name = comp_name.strip()

    ct = commonTools()
    ct.get_subscribedregions(configFileName)

    if region_name not in ct.all_regions:
        print("Invalid Region!! Tenancy is not subscribed to this region. Please try again")
        exit()


    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    template = env.get_template('logging-template')
    auto_tfvars_filename = "cis-oss-logging.auto.tfvars"

    tfStr = ''
    tempStr = {}

    compartmentVarName = commonTools.check_tf_variable(comp_name)
    columnvalue = str(compartmentVarName)

    tempStr['compartment_tf_name'] = columnvalue
    tempStr['region'] = region_name
    tempStr['oci_service'] = 'oss'

    loggroup_name = prefix+"-"+region_name+"-oss-log-group"
    log_name = prefix+"-"+region_name+"-oss-log"
    log_group_id= loggroup_name
    resource=prefix+"-"+region_name+"-oss-bucket"

    tempStr['loggroup_name'] = loggroup_name
    tempStr['loggroup_tf_name'] = loggroup_name
    tempStr['loggroup_desc']='Log Group for OSS bucket'
    srcStr = "##Add New Log Groups for "+region_name+" here##"
    logstfStr = template.render(tempStr, count = 0, loggroup = 'true').replace(srcStr, template.render(tempStr, loggroup = 'true')+"\n"+srcStr)

    tempStr['log_group_id'] = log_group_id
    tempStr['resource'] = resource
    tempStr['log_name'] = log_name
    tempStr['log_tf_name'] = log_name
    tempStr['category'] = 'write'
    tempStr['service'] = 'objectstorage'
    srcStr = "##Add New Logs for "+region_name+" here##"
    loggrouptfStr = template.render(tempStr, count = 0, logs = 'true', loggroup = 'false').replace(srcStr, template.render(tempStr, logs = 'true')+"\n"+srcStr)

    # Write TF string to the file in respective region directory
    reg_out_dir = outdir + "/" + region_name
    if not os.path.exists(reg_out_dir):
        os.makedirs(reg_out_dir)

    outfile = reg_out_dir + "/"+auto_tfvars_filename
    srcdir = reg_out_dir + "/"
    resource = 'osslog'
    commonTools.backup_file(srcdir, resource, auto_tfvars_filename)

    if(logstfStr + loggrouptfStr!=''):
        oname=open(outfile,'w')
        finalStr = logstfStr + loggrouptfStr
        finalStr = "".join([s for s in finalStr.strip().splitlines(True) if s.strip("\r\n").strip()])
        oname.write(finalStr)
        oname.close()
        print(outfile + " containing TF for OSS Logging has been created for region "+region_name)


def enable_cis_vcnflow_logging(filename, outdir, service_dir, prefix, config=DEFAULT_LOCATION):

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, "Subnets")

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

        region = region.strip().lower()
        compartment_var_name = str(df.loc[i, 'Compartment Name']).strip()
        vcn_name = str(df['VCN Name'][i]).strip()
        name = str(df['Subnet Name'][i]).strip()
        subnet = str(df['CIDR Block'][i]).strip()
        AD = str(df['Availability Domain(AD1|AD2|AD3|Regional)'][i]).strip()

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


if __name__ == '__main__':
    # Execution of the code begins here
    args = parse_args()
    enable_cis_oss_logging(args.outdir, args.prefix, args.config, args.service_dir, args.region_name, args.comp_name)
