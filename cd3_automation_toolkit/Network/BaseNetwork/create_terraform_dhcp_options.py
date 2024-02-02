#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI core components
# DHCP
#
# Author: Suruchi Singla
# Oracle Consulting
# Modified (TF Upgrade): Shruthi Subramanian
#

import sys
import datetime
import os
from pathlib import Path
sys.path.append(os.getcwd() + "/../../..")
from jinja2 import Environment, FileSystemLoader
from commonTools import *

######
# Required Files
# input file is cd3 , A prefix for the tf files generated- ex: <prefix>_dhcp.tf
# A Config file
# Modify Network
# Outdir
######
# Execution of the code begins here
def create_terraform_dhcp_options(inputfile, outdir, service_dir, prefix, ct, non_gf_tenancy, modify_network=False):
    outfile = {}
    deffile = {}
    oname = {}
    defname = {}
    tfStr = {}
    custom = {}
    defStr = {}

    filename = inputfile
    modify_network = str(modify_network).lower()

    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    template = env.get_template('custom-dhcp-template')
    defaultdhcp = env.get_template('major-objects-default-dhcp-template')

    vcns = parseVCNs(filename)
    for reg in ct.all_regions:
        tfStr[reg] = ''
        defStr[reg] = ''
        custom[reg] = ''


    def processDHCP(tempStr, template, defaultdhcp):
        defaultdhcpdata = ''
        customdhcpdata = ''

        compartment_var_name = tempStr['compartment_tf_name'].strip()
        region = tempStr['region'].lower().strip()
        vcn_name = tempStr['vcn_name'].strip()
        vcn_tf_name = commonTools.check_tf_variable(vcn_name)

        # Added to check if compartment name is compatible with TF variable name syntax
        compartment_var_name = commonTools.check_tf_variable(compartment_var_name)

        server_type = tempStr['server_type'].strip()
        search_domain = tempStr['search_domain'].strip()
        dhcp_option_name = tempStr['dhcp_option_name'].strip()
        vcn_dhcp = vcn_name + "_" + dhcp_option_name
        vcn_dhcp_tf_name = commonTools.check_tf_variable(vcn_dhcp)

        tempdict = {'vcn_tf_name': vcn_tf_name, 'compartment_tf_name': compartment_var_name,
                    'dhcp_tf_name': vcn_dhcp_tf_name, 'vcn_dhcp': vcn_dhcp,
                    'vcn_name': vcn_name, 'search_domain': search_domain, 'dhcp_option_name': dhcp_option_name,
                    'server_type': server_type}

        tempStr.update(tempdict)

        if ("Default DHCP Options" in dhcp_option_name):
            if region in region_included_for_default_dhcp:
                defaultdhcpdata = defaultdhcp.render(tempStr)[:-1]
            else:
                defaultdhcpdata = defaultdhcp.render(tempStr, count=0)[:-1]
                region_included_for_default_dhcp.append(region)
        else:
            if region in region_included_for_custom_dhcp:
                customdhcpdata = template.render(tempStr,custom=False)
            else:
                customdhcpdata = template.render(tempStr, custom=False, count=0)
                region_included_for_custom_dhcp.append(region)

        defStr[region] = defStr[region]+ defaultdhcpdata
        custom[region] = custom[region] + customdhcpdata

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, "DHCP")

    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    # List of the column headers
    dfcolumns = df.columns.values.tolist()
    region_included_for_custom_dhcp = []
    region_included_for_default_dhcp = []

    for i in df.index:
        region = str(df.loc[i, 'Region'])

        if (region in commonTools.endNames):
            break
        region = region.strip().lower()

        if region not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit(1)

        # temporary dictionary1 and dictionary2
        tempStr = {}
        tempdict = {}

        for columnname in dfcolumns:
            # Column value
            columnvalue = str(df[columnname][i]).strip()

            # Check for boolean/null in column values
            columnvalue = commonTools.check_columnvalue(columnvalue)

            # Check for multivalued columns
            tempdict = commonTools.check_multivalues_columnvalue(columnvalue,columnname,tempdict)

            # Process Defined and Freeform Tags
            if columnname.lower() in commonTools.tagColumns:
                tempdict = commonTools.split_tag_values(columnname, columnvalue, tempdict)

            if columnname == "Compartment Name":
                compartment_var_name = columnvalue.strip()
                tempStr['compartment_tf_name'] = compartment_var_name

            if columnname == "VCN Name":
                vcn_name = columnvalue.strip()
                tempStr['vcn_name'] = vcn_name

                check=vcn_name.strip(),region
                if (check not in vcns.vcn_names):
                    print( "\nERROR!!! " + vcn_name + " specified in DHCP tab has not been declared in VCNs tab..Exiting!")
                    exit(1)

            if columnname == "Server Type(VcnLocalPlusInternet|CustomDnsServer)":
                columnname = 'server_type'
                columnvalue = columnvalue.strip()

            if columnname == 'Custom DNS Server':
                custom_dns_server = str(columnvalue).strip()
                if custom_dns_server != '':
                    custom_dns_server = custom_dns_server.replace(',', '","')
                    custom_dns_server = '"' + custom_dns_server + '"'
                    tempdict = {'custom_dns_server': custom_dns_server}
                tempStr.update(tempdict)

            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)

        processDHCP(tempStr,template,defaultdhcp)


    if (modify_network == 'true'):
        for reg in ct.all_regions:

            reg_out_dir = outdir + "/" + reg + "/" +service_dir
            if not os.path.exists(reg_out_dir):
                os.makedirs(reg_out_dir)

            if custom[reg] != '':
                tfStr[reg] = template.render(custom=True,dhcps=custom[reg])

            custom_dhcp_auto_tfvars_filename = '_custom-dhcp.auto.tfvars'
            outfile[reg] = reg_out_dir + "/" + prefix + custom_dhcp_auto_tfvars_filename
            def_dhcp_auto_tfvars_filename = '_default-dhcp.auto.tfvars'
            deffile[reg] = reg_out_dir + "/" +prefix +def_dhcp_auto_tfvars_filename

            x = datetime.datetime.now()
            date = x.strftime("%f").strip()

            srcdir = outdir + "/" + reg + "/" + service_dir

            if(custom[reg]!=''):
                if (os.path.exists(outfile[reg])):
                    resource = 'custom-dhcp'
                    commonTools.backup_file(srcdir, resource, prefix + custom_dhcp_auto_tfvars_filename)
                tfStr[reg] = "".join([s for s in tfStr[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
                oname[reg] = open(outfile[reg], "w+")
                oname[reg].write(tfStr[reg])
                oname[reg].close()
                print(outfile[reg] + " containing TF for DHCP Options has been updated for region " + reg)
            else:
                if(custom[reg]==''):
                    if (os.path.exists(outfile[reg])):
                        resource = 'custom-dhcp'
                        commonTools.backup_file(srcdir, resource, prefix + custom_dhcp_auto_tfvars_filename)

            # Added this if condition again because modify network was showing tf destroying for Default DHCP Options
            if (defStr[reg] != ''):
                defStr[reg] = defStr[reg] + "\n}"
                if (os.path.exists(deffile[reg])):
                    resource = 'default-dhcp'
                    commonTools.backup_file(srcdir, resource, prefix + def_dhcp_auto_tfvars_filename)
                defStr[reg] = "".join([s for s in defStr[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
                defname[reg] = open(deffile[reg], "w+")
                defname[reg].write(defStr[reg])
                defname[reg].close()
                print(deffile[reg] + " for Default DHCP Options has been updated for region " + reg)
            else:
                if (defStr[reg] == ''):
                    if (os.path.exists(deffile[reg])):
                        resource = 'default-dhcp'
                        commonTools.backup_file(srcdir, resource, prefix + def_dhcp_auto_tfvars_filename)


    elif (modify_network == 'false'):
        for reg in ct.all_regions:
            reg_out_dir = outdir + "/" + reg +"/" +service_dir

            if not os.path.exists(reg_out_dir):
                os.makedirs(reg_out_dir)

            if custom[reg] != '':
                tfStr[reg] = template.render(custom=True,dhcps=custom[reg])

            custom_dhcp_auto_tfvars_filename = '_custom-dhcp.auto.tfvars'
            outfile[reg] = reg_out_dir + "/" + prefix + custom_dhcp_auto_tfvars_filename
            def_dhcp_auto_tfvars_filename = '_default-dhcp.auto.tfvars'
            deffile[reg] = reg_out_dir + "/" +prefix +def_dhcp_auto_tfvars_filename

            srcdir = outdir + "/" + reg + "/" + service_dir

            # Remove the files from other regions if there are any in outdir that is not in CD3.
            if reg not in region_included_for_custom_dhcp:
                resource = 'custom-dhcp'
                commonTools.backup_file(srcdir, resource, prefix + custom_dhcp_auto_tfvars_filename)
            if reg not in region_included_for_default_dhcp:
                resource = 'default-dhcp'
                commonTools.backup_file(srcdir, resource, prefix + def_dhcp_auto_tfvars_filename)

            if (tfStr[reg] != ''):
                if (os.path.exists(outfile[reg])):
                    resource = 'custom-dhcp'
                    commonTools.backup_file(srcdir, resource, prefix + custom_dhcp_auto_tfvars_filename)
                tfStr[reg] = "".join([s for s in tfStr[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
                oname[reg] = open(outfile[reg], 'w+')
                oname[reg].write(tfStr[reg])
                oname[reg].close()
                print(outfile[reg] + " containing TF for DHCP Options has been created for region " + reg)

            if (defStr[reg] != ''):
                defStr[reg] = defStr[reg] + "\n}"
                if (os.path.exists(deffile[reg])):
                    resource = 'default-dhcp'
                    commonTools.backup_file(srcdir, resource, prefix + def_dhcp_auto_tfvars_filename)
                defStr[reg] = "".join([s for s in defStr[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
                defname[reg] = open(deffile[reg], "w+")
                defname[reg].write(defStr[reg])
                defname[reg].close()
                print(deffile[reg] + " for Default DHCP Options has been created for region " + reg)

