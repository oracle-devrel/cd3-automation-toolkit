#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI Network components
# DNS-Resolvers
#

import os
from jinja2 import Environment, FileSystemLoader
from oci.config import DEFAULT_LOCATION
from pathlib import Path
from commonTools import *


######
# Required Inputs- CD3 excel file, Config file, prefix AND outdir
######
# Execution of the code begins here
def create_terraform_dns_resolvers(inputfile, outdir, service_dir, prefix, ct):
    filename = inputfile
    sheetName = "DNS-Resolvers"
    auto_tfvars_filename = prefix + "_"+sheetName.lower()+".auto.tfvars"
    no_strip_columns = ["Display Name"]

    outfile = {}
    oname = {}
    tfStr = {}
    endpoints = {}
    rules = {}

    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    template = env.get_template('dns-resolvers-template')

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, sheetName)

    # Remove empty rows
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    # List of the column headers
    dfcolumns = df.columns.values.tolist()

    # Initialise empty TF string for each region
    for reg in ct.all_regions:
        tfStr[reg] = ''
        srcdir = outdir + "/" + reg + "/" + service_dir + "/"
        resource = sheetName.lower()
        commonTools.backup_file(srcdir, resource, auto_tfvars_filename)


    vcndone = []
    prevregion = ""
    e_done = []

    # Iterate over rows
    # Loop to get rules for each vcn
    for r in df.index:
        r_region = str(df.loc[r, 'Region']).strip()
        # Encountered <End>
        if (r_region in commonTools.endNames):
            break
        r_region = r_region.strip().lower()

        # If some invalid region is specified in a row
        if r_region not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit(1)
        r_vcn = str(df.loc[r, 'VCN Name']).lower().replace("\ ", "_")
        e_name = str(df.loc[r, 'Endpoint Display Name'])
        e_type = str(df.loc[r, 'Endpoint Type:IP Address']).split(':')[0].lower()
        res_key = r_region + "_" + r_vcn
        temprule = []
        if (r_region != prevregion) or (r_vcn != prevvcn):
            e_done = []
        prevregion = r_region
        prevvcn = r_vcn

        rules_data = str(df.loc[r, 'Rules']).strip().split('\n')
        r_index = 1
        for rule in (rule for rule in rules_data if rule != 'nan'):
            client_address_conditions = []
            qname_cover_conditions = []
            clients = []
            rule_id = "rule"+str(r_index)
            client_type = (str(rule).split('::')[0]).strip()
            conditions = (str(rule).split('::')[1]).strip()
            destination_addresses = [(str(rule).split('::')[2].strip())]
            conditions = conditions.split(',')
            for condition in conditions:
                clients.append(condition.strip())
            if client_type.lower() == 'domains':
                qname_cover_conditions = clients
            elif client_type.lower() == 'cidrs':
                client_address_conditions = clients
            elif client_type.lower() == 'none':
                client_address_conditions = []
                qname_cover_conditions = []

            temp_rdict = {'rule_id': rule_id, 'client_address_conditions': client_address_conditions,
                        'destination_addresses': destination_addresses,
                        'qname_cover_conditions': qname_cover_conditions, 'source_endpoint_name': e_name.strip()}
            temprule.append(temp_rdict)
            r_index += 1

        if e_type == 'forwarding':
            rules[res_key] = temprule

    # Loop to get endpoint map
    for e in df.index:
        e_region = str(df.loc[e, 'Region']).lower().strip()
        # Encountered <End>
        if (e_region in commonTools.endNames):
            break
        # If some invalid region is specified in a row
        if e_region not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit(1)

        e_vcn = str(df.loc[e, 'VCN Name'])
        vcn_key = e_region + "_" + str(e_vcn.replace("\ ", "_")).lower()

        tmp_edict = {}
        endpointdict = {}
        endpoint_list = []
        if (e_region != prevregion):
            vcndone = []

        prevregion = e_region

        for columnname in dfcolumns:
            if columnname not in no_strip_columns:
                columnvalue = str(df[columnname][e]).strip()
            else:
                columnvalue = str(df[columnname][e])

            if columnname == "Endpoint Display Name":
                endpoint_name = columnvalue
                tmp_edict = {'name': endpoint_name}

            if columnname == "Endpoint Subnet Name":
                endpoint_subnet = str(columnvalue).strip()
                tmp_edict = {'subnet_name': endpoint_subnet}

            if columnname == "Endpoint Type:IP Address":
                endpoint_type_ip = str(columnvalue).strip()
                if endpoint_type_ip != 'nan':
                    if (":" in str(endpoint_type_ip)):
                        e_type = str(endpoint_type_ip.split(':')[0]).lower()
                        ip = str(endpoint_type_ip.split(':')[1]).lower()
                    else:
                        e_type = str(endpoint_type_ip.split(':')[0]).lower()
                        ip = ''
                    e_type = e_type.strip()
                    ip = ip.strip()
                    if e_type == 'forwarding':
                        forwarding = 'true'
                        listening = 'false'
                        tmp_edict = {'is_forwarding': forwarding, 'is_listening': listening, 'forwarding_address': ip, 'e_type': 'yes'}

                    elif e_type == 'listening':
                        listening = 'true'
                        forwarding = 'false'
                        tmp_edict = {'is_forwarding': forwarding, 'is_listening': listening, 'listening_address': ip, 'e_type': 'yes'}
                    else:
                        tmp_edict = {'e_type': 'no'}
                else:
                    tmp_edict = {'e_type': 'no'}

            if columnname == 'Endpoint NSGs':
                if columnvalue != '' and columnvalue.strip().lower() != 'nan':
                    nsg_str = []
                    NSGs = columnvalue.split(",")
                    k = 0
                    while k < len(NSGs):
                        nsg = NSGs[k].strip()
                        nsg_str.append(str(nsg))
                        k += 1
                    tmp_edict = {'nsg_ids': nsg_str}

            endpointdict.update(tmp_edict)

        if endpointdict["name"] != 'nan' and endpointdict["subnet_name"] != 'nan' and endpointdict["e_type"] == 'yes':

            if vcn_key not in vcndone:
                endpoint_list.append(endpointdict)
                vcndone.append(vcn_key)
                endpoints[vcn_key] = endpoint_list
            else:
                endpoints[vcn_key].append(endpointdict)

    # Main loop to generate tfvars
    for i in df.index:
        region = str(df.loc[i, 'Region']).strip()

        # Encountered <End>
        if (region in commonTools.endNames):
            break
        region = region.strip().lower()

        # If some invalid region is specified in a row
        if region not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit(1)

        tempStr = {}
        tempdict = {}

        if (region != prevregion):
            vcndone = []
        prevregion = region
        # Check if values are entered for mandatory fields
        if str(df.loc[i, 'Region']).lower() == 'nan' or \
                str(df.loc[i, 'Compartment Name']).lower() == 'nan' or \
                str(df.loc[i, 'VCN Name']).lower() == 'nan':
            print(
                "\nRegion, Compartment Name, VCN Name fields are mandatory. Please enter a value and try again !!")
            print("\n** Exiting **")
            exit(1)

        # set key for template items
        vcn_name = str(df["VCN Name"][i])
        endpoint_type_ip = str(df["Endpoint Type:IP Address"][i]).lower()
        e_type = ""
        if endpoint_type_ip != 'nan':
            e_type = str(endpoint_type_ip.split(':')[0]).lower()
            e_type = e_type.strip()

        tempStr['resolver_tf_name'] = vcn_name
        vcn_key = region.lower() + "_" + str(vcn_name.replace("\ ", "_")).lower()

        for columnname in dfcolumns:
            # Column value
            if columnname not in no_strip_columns:
                columnvalue = str(df[columnname][i]).strip()
            else:
                columnvalue = str(df[columnname][i])

            # Check for boolean/null in column values
            columnvalue = commonTools.check_columnvalue(columnvalue)

            # Check for multivalued columns
            tempdict = commonTools.check_multivalues_columnvalue(columnvalue, columnname, tempdict)

            if columnname == "VCN Name":
                tempdict = {'res_vcn_name': vcn_name}

            if columnname == "Compartment Name":
                compartmentVarName = columnvalue.strip()
                columnname = commonTools.check_column_headers(columnname)
                compartmentVarName = commonTools.check_tf_variable(compartmentVarName)
                columnvalue = str(compartmentVarName)
                tempdict = {'net_compartment_name': columnvalue}

            if columnname == "Display Name":
                tempdict = {'res_display_name': columnvalue}

            if columnname == 'Associated Private Views':
                views = str(columnvalue).split('\n')
                tempview = []
                for view in (view for view in views if view != ''):
                    view_comp = str(view).split('@')[0]
                    compartmentVarName = view_comp.strip()
                    compartmentVarName = commonTools.check_tf_variable(compartmentVarName)
                    view_comp = str(compartmentVarName)
                    view_name = str(view).split('@')[1]
                    view_map = {'view_id': view_name, 'compartment_id': view_comp}
                    tempview.append(view_map)
                tempdict = {'res_views': tempview}

            if columnname == 'Endpoint Display Name':
                try:
                    res_endpoints = endpoints[vcn_key]
                except:
                    res_endpoints = []
                tempdict = {'res_endpoints': res_endpoints}

            if columnname == 'Rules':
                try:
                    res_rules = rules[vcn_key]
                except:
                    res_rules = []
                tempdict = {'res_resolver_rules': res_rules}

            # Process Defined and Freeform Tags
            if columnname.lower() in commonTools.tagColumns:
                tempdict = commonTools.split_tag_values(columnname, columnvalue, tempdict)

            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)
        if vcn_name not in vcndone:
            tfStr[region] = tfStr[region] + template.render(tempStr)
            vcndone.append(vcn_name)

 # Write TF string to the file in respective region directory
    for reg in ct.all_regions:
        reg_out_dir = outdir + "/" + reg + "/" + service_dir
        if not os.path.exists(reg_out_dir):
            os.makedirs(reg_out_dir)
        outfile[reg] = reg_out_dir + "/" +  auto_tfvars_filename

        if (tfStr[reg] != ''):
            src = "##Add New resolvers for " + reg.lower() + " here##"
            tfStr[reg] = template.render(count=0, region=reg).replace(src, tfStr[reg] + "\n" + src)
            tfStr[reg] = "".join([s for s in tfStr[reg].strip().splitlines(True) if s.strip("\r\n").strip()])

            oname[reg] = open(outfile[reg], 'w')
            oname[reg].write(tfStr[reg])
            oname[reg].close()
            print(outfile[reg] + " containing TF for DNS Resolvers has been created for region " + reg)

