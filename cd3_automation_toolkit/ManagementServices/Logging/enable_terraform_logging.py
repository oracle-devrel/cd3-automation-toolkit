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


def enable_service_logging(filename, outdir, prefix, ct, service_dir, option=''):

     # Load the template file
     file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
     env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
     template = env.get_template('logging-template')

     tfStrLogs = {}
     tempStr = {}
     outfile = {}
     tfStrLogGroups = {}
     tempdict = {}
     obj_list = {}

     if option.lower().__contains__("buckets"):
         sheet_name = "Buckets"
         column_name = "Bucket Name"
         auto_tfvars_filename = prefix + '_buckets-logging.auto.tfvars'
         oci_service = 'oss'
         service = 'objectstorage'
         log_types = ['read', 'write']
         backup_resource = 'osslog'

     elif option.lower().__contains__("lbaas"):
         sheet_name = "LB-Hostname-Certs"
         column_name = "LBR Name"
         auto_tfvars_filename = prefix + '_load-balancers-logging.auto.tfvars'
         oci_service = 'loadbalancer'
         service = 'loadbalancer'
         log_types = ['access','error']
         backup_resource = 'loadbalancerlog'

     elif option.lower().__contains__("vcn"):
         sheet_name = "SubnetsVLANs"
         column_name = "VCN Name"
         auto_tfvars_filename = prefix + '_vcnflow-logging.auto.tfvars'
         oci_service = 'vcn'
         service = 'flowlogs'
         log_types = ['flow']
         backup_resource = 'vcnflowlog'

     elif option.lower().__contains__("file"):
         sheet_name = "FSS"
         column_name = "MountTarget Name"
         auto_tfvars_filename = prefix + '_nfs-logging.auto.tfvars'
         oci_service = 'nfs'
         service = 'filestorage'
         log_types = ['nfslogs']
         backup_resource = 'nfslog'

     elif option.lower().__contains__("firewall"):
         sheet_name = "Firewall"
         column_name = "Firewall Name"
         auto_tfvars_filename = prefix + '_fw-logging.auto.tfvars'
         oci_service = 'fw'
         service = 'ocinetworkfirewall'
         log_types = ['threatlog','trafficlog']
         backup_resource = 'fwlog'

     else:
         print("Invalid Option for Logging")
         exit(1)

     # Read cd3 using pandas dataframe
     df, col_headers = commonTools.read_cd3(filename, sheet_name)

     # Remove empty rows
     df = df.dropna(how='all')
     df = df.reset_index(drop=True)

     # List of the column headers
     dfcolumns = df.columns.values.tolist()

     for i in df.index:
         region = str(df.loc[i, 'Region'])

         if (region in commonTools.endNames):
             break

         region = region.strip().lower()
         tfStrLogs[region] = ''
         tfStrLogGroups[region] = ''
         obj_list[region] = []

     for i in df.index:
         region = str(df.loc[i, 'Region'])
         if (region in commonTools.endNames):
             break


         region_name = region.strip().lower()
         compartment_name = str(df.loc[i, 'Compartment Name']).strip()

         obj_name = str(df[column_name][i]).strip()
         obj_tf_name = commonTools.check_tf_variable(obj_name)

         loggroup_tf_name = obj_tf_name + "_" + oci_service + "-log-group"

         log_tf_name = obj_tf_name

         if obj_name.lower()=='nan':
             continue

         #VCN Flow Logs
         if (option.lower().__contains__("vcn")):
             subnet_vlan_in_excel = str(df.loc[i, 'Subnet or VLAN']).strip()
             if subnet_vlan_in_excel.lower().startswith('vlan'):
                 continue
             subnet_name = str(df['Display Name'][i]).strip()
             obj_tf_name = commonTools.check_tf_variable(obj_name+"_"+subnet_name)
             log_tf_name = obj_tf_name
             loggroup_tf_name = commonTools.check_tf_variable(obj_name) + "_"  + "flow-log-group"

         for columnname in dfcolumns:
             if columnname.lower() in commonTools.tagColumns:
                 columnvalue = str(df[columnname][i]).strip()
                 if columnvalue != 'nan' and columnvalue != '':
                     tempdict = commonTools.split_tag_values(columnname, columnvalue, tempdict)
                     tempStr.update(tempdict)

         tempStr['compartment_tf_name'] = commonTools.check_tf_variable(compartment_name)
         tempStr['region'] = region_name
         tempStr['oci_service'] = oci_service


         if obj_name not in obj_list[region_name]:
             tempStr['loggroup_tf_name'] = loggroup_tf_name
             tempStr['loggroup_desc'] = 'Log Group for ' + obj_name
             tfStrLogGroups[region_name] = tfStrLogGroups[region_name] + template.render(tempStr, loggroup='true')
             obj_list[region_name].append(obj_name)

         tempStr['loggroup'] = 'false'
         tempStr['resource'] = obj_tf_name
         tempStr['log_tf_name'] = log_tf_name
         tempStr['logtype'] = log_types
         tempStr['service'] = service
         tempStr['oci_service'] = oci_service
         tfStrLogs[region_name] = tfStrLogs[region_name] + template.render(tempStr)

     # Write TF string to the file in respective region directory
     for reg in tfStrLogs.keys():
         reg_out_dir = outdir + "/" + reg + "/" + service_dir
         if not os.path.exists(reg_out_dir):
             os.makedirs(reg_out_dir)

         outfile[reg] = reg_out_dir + "/" + auto_tfvars_filename
         srcdir = reg_out_dir + "/"
         commonTools.backup_file(srcdir, backup_resource, auto_tfvars_filename)

         srcStr = "##Add New Logs for " + reg + " here##"
         tfStrLogs[reg] = template.render(tempStr, count=0, region=reg).replace(srcStr,
                                                                                tfStrLogs[reg] + "\n" + srcStr)

         srcStr = "##Add New Log Groups for " + reg + " here##"
         tfStrLogGroups[reg] = template.render(tempStr, loggroup='true', count=0, region=reg).replace(srcStr,
                                                                                                      tfStrLogGroups[
                                                                                                          reg] + "\n" + srcStr)

         tfStrLogs[reg] = tfStrLogs[reg] + "\n" + tfStrLogGroups[reg]

         if (tfStrLogs[reg] != ''):
             oname = open(outfile[reg], 'w')
             tfStrLogs[reg] = "".join(
                 [s for s in tfStrLogs[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
             oname.write(tfStrLogs[reg])
             oname.close()
             print(outfile[reg] + " for "+oci_service.upper()+" Logs has been created for region " + reg)