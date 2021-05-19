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
    parser.add_argument("outdir", help="Output directory for creation of TF files")
    parser.add_argument("prefix", help="customer name/prefix for all file names")
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

    tfStr = ''
    tempStr = {}

    compartmentVarName = commonTools.check_tf_variable(comp_name)
    columnvalue = str(compartmentVarName)

    tempStr['compartment_tf_name'] = columnvalue

    loggroup_name = prefix + "-oss-log-group"
    log_name = prefix + "-oss-log"
    log_group_id= 'oci_logging_log_group.'+prefix+'-oss-log-group.id'
    resource='oci_objectstorage_bucket.'+prefix+'-oss-bucket.name'

    tempStr['loggroup_name'] = loggroup_name
    tempStr['loggroup_tf_name'] = loggroup_name
    tempStr['loggroup_exists'] = 'true'
    tempStr['loggroup_desc']='Log Group for OSS bucket'
    tempStr['log_group_id'] = log_group_id
    tempStr['resource'] = resource
    tempStr['log_name'] = log_name
    tempStr['log_tf_name'] = log_name
    tempStr['category'] = 'write'
    tempStr['service'] = 'objectstorage'

    tfStr = tfStr + template.render(tempStr)

    # Write TF string to the file in respective region directory
    reg_out_dir = outdir + "/" + region_name
    if not os.path.exists(reg_out_dir):
        os.makedirs(reg_out_dir)

    outfile = reg_out_dir + "/cis-oss-logging.tf"

    if(tfStr!=''):
        oname=open(outfile,'w')
        oname.write(tfStr)
        oname.close()
        print(outfile + " containing TF for OSS Logging has been created for region "+region_name)


def enable_cis_vcnflow_logging(filename, outdir, prefix, config=DEFAULT_LOCATION):

    # Declare variables
    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, "Subnets")

    # Remove empty rows
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    template = env.get_template('logging-template')

    tfStr = {}
    tempStr = {}
    outfile={}
    vcns_list = []
    for i in df.index:
        region = str(df.loc[i, 'Region'])

        if (region in commonTools.endNames):
            break

        region = region.strip().lower()
        tfStr[region]=''

    for i in df.index:
        region = str(df.loc[i, 'Region'])

        if (region in commonTools.endNames):
            break

        region = region.strip().lower()
        compartment_var_name = str(df.loc[i, 'Compartment Name']).strip()
        vcn_name = str(df['VCN Name'][i]).strip()
        subnet_name = str(df['Subnet Name'][i]).strip()


        compartmentVarName = commonTools.check_tf_variable(compartment_var_name)
        columnvalue = str(compartmentVarName)

        tempStr['compartment_tf_name'] =  columnvalue

        loggroup_name = commonTools.check_tf_variable(vcn_name)+"-flow-log-group"
        log_name = commonTools.check_tf_variable(subnet_name)+"-flow-log"
        log_group_id= 'oci_logging_log_group.'+loggroup_name+'.id'
        resource='oci_core_subnet.'+commonTools.check_tf_variable(vcn_name+"_"+subnet_name)+'.id'

        if vcn_name not in vcns_list:
            tempStr['loggroup_exists'] = 'false'
            tempStr['loggroup_name'] = loggroup_name
            tempStr['loggroup_tf_name'] = loggroup_name
            tempStr['loggroup_desc'] = 'Log Group for VCN'
            tfStr[region] = tfStr[region] + template.render(tempStr)
            vcns_list.append(vcn_name)

        tempStr['loggroup_exists'] = 'true'
        tempStr['log_group_id'] = log_group_id
        tempStr['resource'] = resource
        tempStr['log_name'] = log_name
        tempStr['log_tf_name'] = log_name
        tempStr['category'] = 'all'
        tempStr['service'] = 'flowlogs'

        tfStr[region] = tfStr[region] + template.render(tempStr)

    # Write TF string to the file in respective region directory
    for reg in tfStr.keys():
        reg_out_dir = outdir + "/" + reg
        if not os.path.exists(reg_out_dir):
            os.makedirs(reg_out_dir)

        outfile[reg] = reg_out_dir + "/cis-vcnflow-logging.tf"
        if(tfStr[reg]!=''):
            oname=open(outfile[reg],'w')
            oname.write(tfStr[reg])
            oname.close()
            print(outfile[reg] + " containing TF for VCN Flow Logs has been created for region "+reg)


if __name__ == '__main__':
    # Execution of the code begins here
    args = parse_args()
    enable_cis_oss_logging(args.outdir, args.prefix, args.config, args.region_name, args.comp_name)
