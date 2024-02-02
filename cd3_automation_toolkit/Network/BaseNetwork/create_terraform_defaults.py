#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI core components
# Create all the Gateways and VCN
#
# Author: Divya Das and Shruthi Subramanian
# Oracle Consulting
#
import json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from commonTools import *

######
# Required Files
# input file containing VCN info - CD3 excel
# Create the default seclist terraform objects - DRG, IGW, NGW, SGW, LPGs for the VCN
# Outdir
# Modify Network
# prefix
######

def create_default_routetable(inputfile, outdir, service_dir, prefix, ct, non_gf_tenancy, modify_network):

    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)

    filename = inputfile
    vcnsheetName = "VCNs"

    default_routetable_auto_tfvars_filename = "_default-routetables.auto.tfvars"

    # routetable templates
    routerule = env.get_template('route-rule-template')
    defaultrt = env.get_template('default-route-table-template')
    routetable = env.get_template('route-table-template')

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, vcnsheetName)
    # Remove empty rows
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    # List of the column headers
    dfcolumns = df.columns.values.tolist()
    region_included = []
    defRTs_from_subnet_sheet = []

    defrt = {}
    default_rt_tempSkeleton = {}

    for reg in ct.all_regions:
        defrt[reg] = ''
        default_rt_tempSkeleton[reg] = ''


    def generate_route_table_string(region_rt_name, region, routetableStr, tempStr, common_rt):
        if (region_rt_name not in common_rt and region_rt_name not in routetableStr[region]):
            routetableStr[region] = routetableStr[region] + routetable.render(tempStr,
                                                                              route_rules_igw="####ADD_NEW_IGW_RULES " + region_rt_name + " ####",
                                                                              route_rules_ngw="####ADD_NEW_NGW_RULES " + region_rt_name + " ####",
                                                                              route_rules_sgw="####ADD_NEW_SGW_RULES " + region_rt_name + " ####",
                                                                              route_rules_drg="####ADD_NEW_DRG_RULES " + region_rt_name + " ####",
                                                                              route_rules_lpg="####ADD_NEW_LPG_RULES " + region_rt_name + " ####",
                                                                              route_rules_ip="####ADD_NEW_IP_RULES " + region_rt_name + " ####", )


        common_rt.append(region_rt_name)
        return routetableStr[region]

    for i in df.index:
        region = str(df['Region'][i])
        if (region in commonTools.endNames):
            break
        region = region.strip().lower()
        if region not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit(1)

        # temporary dictionary1 and dictionary2
        tempStr = {}
        tempdict = {}

        tempStr.update({'count': 1})
        if region not in region_included:
            tempStr.update({'count': 0})
            region_included.append(region)
            default_rt_tempSkeleton[region] = defaultrt.render(tempStr, skeleton=True, region=region)

        for columnname in dfcolumns:

            # Column value
            columnvalue = str(df[columnname][i]).strip()

            # Check for boolean/null in column values
            columnvalue = commonTools.check_columnvalue(columnvalue)

            # Check for multivalued columns
            tempdict = commonTools.check_multivalues_columnvalue(columnvalue, columnname, tempdict)

            # Process Defined and Freeform Tags
            if columnname.lower() in commonTools.tagColumns:
                tempdict = commonTools.split_tag_values(columnname, columnvalue, tempdict)
                tempStr.update(tempdict)

            if columnname == 'Compartment Name':
                compartment_tf_name = commonTools.check_tf_variable(columnvalue)
                tempdict = {'compartment_tf_name': compartment_tf_name}
                tempStr.update(tempdict)

            if columnname == 'VCN Name':
                vcn_name = columnvalue
                display_name = "Default Route Table for " + vcn_name

                vcn_tf_name = commonTools.check_tf_variable(vcn_name)
                tempdict = {'vcn_tf_name': vcn_tf_name, 'display_name': display_name, 'vcn_name': vcn_name}
                tempStr.update(tempdict)

            # Check this code once
            if columnname == 'Route Table Name':
                if columnvalue == '':
                    continue
                else:
                    columnvalue = vcn_tf_name + "_" + commonTools.check_tf_variable(str(columnvalue).strip())
                    tempdict = {'rt_tf_name': columnvalue}
                    add_rules_tf_name = columnvalue
                    tempStr.update(tempdict)

            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)

        region = tempStr['region'].lower().strip()
        vcn_name = tempStr['vcn_name'].strip()
        vcn_tf_name = commonTools.check_tf_variable(vcn_name)
        tempStr['vcn_tf_name'] = vcn_tf_name
        compartment_var_name = str(tempStr['compartment_name']).strip()
        routetablename = vcn_tf_name + "_" + display_name
        routetable_tf_name = commonTools.check_tf_variable(routetablename)
        rt_var = vcn_tf_name + "_" + display_name
        rt_tf_name = commonTools.check_tf_variable(rt_var)

        region_rt_name = "#" + region.lower() + "_" + rt_tf_name + "#"
        tempdict = {'region_rt_name': region_rt_name}
        tempStr.update(tempdict)

        defRTs_from_subnet_sheet.append(region_rt_name)

        # Added to check if compartment name is compatible with TF variable name syntax
        compartment_var_name = commonTools.check_tf_variable(compartment_var_name)

        tempdict = {'vcn_tf_name': vcn_tf_name, 'compartment_tf_name': compartment_var_name,
                    'routetable_tf_name': routetable_tf_name,
                    'region': region, 'display_name': display_name, 'rt_var': rt_var, 'rt_tf_name': rt_tf_name}
        tempStr.update(tempdict)
        common_rt = []

        if not modify_network:
            defrt[region] = generate_route_table_string(region_rt_name=region_rt_name, region=region,
                                                       routetableStr=defrt, tempStr=tempStr, common_rt=common_rt)
        else:

            default_outfile = outdir + "/" + region + "/" + service_dir +"/" +prefix + default_routetable_auto_tfvars_filename

            # Read the file if it exists
            if os.path.exists(default_outfile):
                # Read the contents of file in outdir
                with open(default_outfile, 'r+') as file:
                    filedata = file.read()
                file.close()

                # for the RTs in Subnet sheet, see if the start string is there in filedata, if yes, retain it
                for defSLs in defRTs_from_subnet_sheet:
                    if "# Start of " + defSLs + " #" in filedata and "# Start of " + defSLs + " #" not in defrt[region]:
                        defrt[region] = ct.copy_data_from_file(default_outfile, defSLs, defrt[region])

            # Check if the defSL from Subnets sheet is there in deftfStr once the data form previous auto.tfvars are copied;
            # render template and add only new ones.
            for defSLs in defRTs_from_subnet_sheet:
                if "# Start of " + defSLs + " #" not in defrt[region]:
                    defrt[region] = generate_route_table_string(region_rt_name=region_rt_name, region=region,
                                                                routetableStr=defrt, tempStr=tempStr,
                                                                common_rt=common_rt)
    for reg in ct.all_regions:

        defaultTextToAddSeclistSearch = "##Add New Default Route Tables for " + reg + " here##"
        default_outfile = outdir + "/" + reg + "/" + service_dir + "/" + prefix + default_routetable_auto_tfvars_filename

        if defrt[reg] != '':
            # Backup existing seclist files in ash and phx dir
            resource = "RTs"
            commonTools.backup_file(outdir + "/" + reg + "/" + service_dir, resource, prefix + default_routetable_auto_tfvars_filename)

            default_rt_tempSkeleton[reg] = default_rt_tempSkeleton[reg].replace(defaultTextToAddSeclistSearch,defrt[reg] + "\n" + defaultTextToAddSeclistSearch)
            default_rt_tempSkeleton[reg] = "".join([s for s in default_rt_tempSkeleton[reg].strip().splitlines(True) if s.strip("\r\n").strip()])

            oname = open(default_outfile, "w+")
            oname.write(default_rt_tempSkeleton[reg])
            oname.close()
            print(default_outfile + " for default route tables has been created for region " + reg)

def create_default_seclist(inputfile, outdir, service_dir, prefix, ct, non_gf_tenancy, modify_network):

    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)

    filename = inputfile
    vcnsheetName = "VCNs"

    # seclist templates
    default_seclist = env.get_template('default-seclist-template')
    secrule = env.get_template('sec-rule-template')
    seclist = env.get_template('seclist-template')

    default_seclist_auto_tfvars_filename = "_default-seclists.auto.tfvars"

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, vcnsheetName)
    # Remove empty rows
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    region_included = []
    deftfStr = {}
    default_seclist_tempSkeleton = {}

    def generate_security_rules(region_seclist_name, processed_seclist, tfStr, region, tempStr, ingress_rule,
                                tempdict2, egress_rule):
        if region_seclist_name not in processed_seclist:
            tfStr[region] = tfStr[region] + seclist.render(tempStr,
                                                           ingress_sec_rules="####ADD_NEW_INGRESS_SEC_RULES " + region_seclist_name + " ####",
                                                           egress_sec_rules="####ADD_NEW_EGRESS_SEC_RULES " + region_seclist_name + " ####")
            processed_seclist.append(region_seclist_name)
        if tempStr['rule_type'] == 'ingress':
            new_ingress_sec_rule = ct.create_ingress_rule_string(secrule, tempStr, ingress_rule, tempdict2, region_seclist_name)
            try:
                tfStr[region] = tfStr[region].replace(
                    "####ADD_NEW_INGRESS_SEC_RULES " + region_seclist_name + " ####", new_ingress_sec_rule)
            except Exception as err:
                raise err
        if tempStr['rule_type'] == 'egress':
            new_egress_sec_rule = ct.create_egress_rule_string(secrule, tempStr, egress_rule, tempdict2, region_seclist_name)
            tfStr[region] = tfStr[region].replace("####ADD_NEW_EGRESS_SEC_RULES " + region_seclist_name + " ####",
                                                  new_egress_sec_rule)

        return tfStr[region]

    for reg in ct.all_regions:
        deftfStr[reg] = ''
        default_seclist_tempSkeleton[reg] = ''

    for i in df.index:
        region = str(df['Region'][i])
        if (region in commonTools.endNames):
            break
        region = region.strip().lower()
        if region not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit(1)

        # temporary dictionary1 and dictionary2
        tempStr = {}

        tempStr.update({'count': 1})
        if region not in region_included:
            tempStr.update({'count': 0})
            region_included.append(region)
            defSLs_from_subnet_sheet = []
            default_seclist_tempSkeleton[region] = default_seclist.render(tempStr, skeleton=True, region=region)

        cidr_blocks = str(df['CIDR Blocks'][i]).lower().strip()
        cidr_blocks = [x.strip() for x in cidr_blocks.split(',')]
        # reverses the order while exporting into excel so use reverse to avoid terraform change
        if (non_gf_tenancy):
            cidr_blocks.reverse()
            cidr_blocks = json.dumps(cidr_blocks)

        default_ingress = {}
        for x in list(cidr_blocks):
            default_ingress.update({'default_ingress' + x: {
                'protocol': 'icmp',
                'source': x,
                'rule_description': '',
                'rule_type': 'ingress',
                'icmptype': '',
                'icmpcode': ''
            }})
        defaults = {
            'default_ingress2': {
                'protocol': 'icmp',
                'source': '0.0.0.0/0',
                'rule_description': '',
                'rule_type': 'ingress',
                'icmptype': '',
                'icmpcode': ''
            },
            'default_ingress3': {
                'protocol': 'tcp',
                'source': '0.0.0.0/0',
                'rule_description': '',
                'rule_type': 'ingress',
                'dportmax': "22",
                'dportmin': "22"
            },
            'default_egress1': {
                'protocol': 'all',
                'destination': '0.0.0.0/0',
                'rule_description': '',
                'rule_type': 'egress',
                'options': {
                    'all': []
                }
            }
        }
        defaults.update(default_ingress)

        vcn_name = str(df['VCN Name'][i]).strip()
        vcn_tf_name = commonTools.check_tf_variable(vcn_name)
        compartment_var_name = str(df['Compartment Name'][i]).strip()
        compartment_var_name = commonTools.check_tf_variable(compartment_var_name)

        # Create TF object for default seclist options
        display_name = 'Default Security List for ' + vcn_name
        seclistname = vcn_name + "_" + display_name
        seclist_tf_name = commonTools.check_tf_variable(seclistname)

        tempdict = {'vcn_tf_name': vcn_tf_name, 'compartment_tf_name': compartment_var_name,
                    'seclist_tf_name': seclist_tf_name,
                    'isstateless': 'false', 'region': region, 'display_name': display_name}

        tempStr.update(tempdict)
        tempStr.update({'destination': ''})

        region_seclist_name = "#" + region + "_" + tempStr['seclist_tf_name'] + "#"
        processed_seclist = []
        ingress_rule = ''
        tempdict2 = {}
        egress_rule = ''

        defSLs_from_subnet_sheet.append(region_seclist_name)

        if not modify_network:
            for rule in defaults.keys():
                tempStr.update(defaults[rule])
                deftfStr[region] = generate_security_rules(region_seclist_name=region_seclist_name,
                                                           processed_seclist=processed_seclist, tfStr=deftfStr,
                                                           region=region, tempStr=tempStr,
                                                           ingress_rule=ingress_rule, tempdict2=tempdict2,
                                                           egress_rule=egress_rule)
        else:
            default_outfile = outdir + "/" + region + "/" + service_dir + "/" +prefix + default_seclist_auto_tfvars_filename

            # Read the file if it exists
            if os.path.exists(default_outfile):
                # Read the contents of file in outdir
                with open(default_outfile, 'r+') as file:
                    filedata = file.read()
                file.close()

                # for the this SL, see if the start string is there in filedata, if yes, retain seclist as is
                if "# Start of " + region_seclist_name + " #" in filedata and "# Start of " + region_seclist_name + " #" not in deftfStr[region]:
                    deftfStr[region] = ct.copy_data_from_file(default_outfile, region_seclist_name, deftfStr[region])


            # Check if the defSL from Subnets sheet is there in deftfStr once the data form previous auto.tfvars are copied;
            # render template and add only new ones.

            for defSLs in defSLs_from_subnet_sheet:
                if "# Start of " + defSLs + " #" not in deftfStr[region]:
                    for rule in defaults.keys():
                        tempStr.update(defaults[rule])
                        deftfStr[region] = generate_security_rules(region_seclist_name=region_seclist_name,
                                                                   processed_seclist=processed_seclist,
                                                                   tfStr=deftfStr,
                                                                   region=region, tempStr=tempStr,
                                                                   ingress_rule=ingress_rule, tempdict2=tempdict2,
                                                                   egress_rule=egress_rule)

    for reg in ct.all_regions:
        defaultTextToAddSeclistSearch = "##Add New Default Seclists for " + reg + " here##"
        default_outfile = outdir + "/" + reg + "/" + service_dir +"/"+ prefix + default_seclist_auto_tfvars_filename

        if deftfStr[reg] != '':
            # Backup existing seclist files in ash and phx dir
            resource = "SLs"
            commonTools.backup_file(outdir + "/" + reg + "/" + service_dir, resource, prefix + default_seclist_auto_tfvars_filename)

            default_seclist_tempSkeleton[reg] = default_seclist_tempSkeleton[reg].replace(
                defaultTextToAddSeclistSearch, deftfStr[reg] + "\n" + defaultTextToAddSeclistSearch)
            default_seclist_tempSkeleton[reg] = "".join(
                [s for s in default_seclist_tempSkeleton[reg].strip().splitlines(True) if s.strip("\r\n").strip()])

            oname = open(default_outfile, "w+")
            oname.write(default_seclist_tempSkeleton[reg])
            oname.close()
            print(default_outfile + " for default seclist has been created for region " + reg)

# Code execution starts here
def create_terraform_defaults(inputfile, outdir, service_dir, prefix, ct, non_gf_tenancy, modify_network):

    create_default_seclist(inputfile, outdir, service_dir, prefix, ct, non_gf_tenancy, modify_network)
    create_default_routetable(inputfile, outdir, service_dir, prefix, ct, non_gf_tenancy, modify_network)
