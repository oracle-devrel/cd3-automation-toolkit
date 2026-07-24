#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI core components
# Instances
#
# Author: Suruchi Singla
# Oracle Consulting
# Modified (TF Upgrade): Shruthi Subramanian
#

import sys
import os
import fnmatch
from oci.config import DEFAULT_LOCATION
from pathlib import Path
sys.path.append(os.getcwd() + "../")
from common.python.commonTools import *
import ocicloud.python.ociCommonTools as ociCommonTools
from jinja2 import Environment, FileSystemLoader




def _secondary_vnic_column_key(columnname):
    return commonTools.check_column_headers(str(columnname))


def _get_secondary_vnic_column(values, columnname):
    return values.get(commonTools.check_column_headers(columnname), "")

def _split_secondary_vnic_values(columnvalue):
    if columnvalue == "" or str(columnvalue).strip().lower() == "nan":
        return []
    return [str(value).strip() for value in str(columnvalue).split(";")]


def _split_secondary_vnic_boolean_values(columnvalue):
    # CD3 exports Excel booleans as TRUE/FALSE, but Terraform requires lowercase boolean literals.
    return [
        value.lower() if value.lower() in ("true", "false") else value
        for value in _split_secondary_vnic_values(columnvalue)
    ]


def _parse_network_details(value, default_compartment_name, row_num, column_label):
    if "ocid1.subnet.oc" in value:
        return {
            "network_compartment_id": "root",
            "vcn_name": "",
            "subnet_id": value,
        }
    if len(value.split("@")) == 2:
        network_compartment_id = commonTools.check_tf_variable(value.split("@")[0].strip())
        vcn_subnet_name = value.split("@")[1].strip()
    else:
        network_compartment_id = commonTools.check_tf_variable(default_compartment_name)
        vcn_subnet_name = value
    if "::" not in vcn_subnet_name:
        print("Invalid " + column_label + " format specified for row " + str(row_num) + ". Exiting!!!")
        exit(1)
    return {
        "network_compartment_id": network_compartment_id,
        "vcn_name": vcn_subnet_name.split("::")[0].strip(),
        "subnet_id": vcn_subnet_name.split("::")[1].strip(),
    }


def _parse_secondary_vnic_network_details(columnvalue, default_network_details, default_compartment_name, count, row_num):
    values = _split_secondary_vnic_values(columnvalue)
    network_details = []
    for index in range(count):
        value = values[index] if index < len(values) else ""
        if value == "":
            value = default_network_details
        network_details.append(_parse_network_details(value, default_compartment_name, row_num, "Secondary VNIC Network Details"))
    return network_details


def _parse_secondary_vnic_nsgs(columnvalue):
    nsg_values = []
    for value in _split_secondary_vnic_values(columnvalue):
        if value == "":
            nsg_values.append([])
        else:
            nsg_values.append([nsg.strip() for nsg in value.split(",") if nsg.strip() != ""])
    return nsg_values


def _parse_secondary_vnic_tags(columnvalue):
    tag_values = []
    for value in _split_secondary_vnic_values(columnvalue):
        if value == "":
            tag_values.append([])
            continue
        tags = []
        for tag_value in value.split(","):
            if "=" in tag_value:
                tags.append([tag_value.split("=", 1)[0].strip(), tag_value.split("=", 1)[1].strip()])
        tag_values.append(tags)
    return tag_values


def _get_secondary_vnic_value(values, index, default=""):
    return values[index] if index < len(values) else default


def _build_secondary_vnics(df, row_index, dfcolumns, row_num):
    secondary_vnic_columns = [column for column in dfcolumns if _secondary_vnic_column_key(column).startswith("secondary_vnic_")]
    if len(secondary_vnic_columns) == 0:
        return {}

    values = {}
    max_count = 0
    for columnname in secondary_vnic_columns:
        columnvalue = commonTools.check_columnvalue(str(df[columnname][row_index]).strip())
        values[_secondary_vnic_column_key(columnname)] = columnvalue
        max_count = max(max_count, len(_split_secondary_vnic_values(columnvalue)))

    if max_count == 0:
        return {}

    default_compartment_name = str(df.loc[row_index, 'Compartment Name']).strip()
    default_network_details = str(df.loc[row_index, 'Network Details']).strip()
    networks = _parse_secondary_vnic_network_details(
        _get_secondary_vnic_column(values, "Secondary VNIC Network Details"),
        default_network_details,
        default_compartment_name,
        max_count,
        row_num
    )
    secondary_vnics = {}

    value_lists = {
        "private_ip": _split_secondary_vnic_values(_get_secondary_vnic_column(values, "Secondary VNIC IP Addresses")),
        "nsg_ids": _parse_secondary_vnic_nsgs(_get_secondary_vnic_column(values, "Secondary VNIC NSGs")),
        "skip_source_dest_check": _split_secondary_vnic_boolean_values(_get_secondary_vnic_column(values, "Secondary VNIC Skip Source Dest Check")),
        "assign_public_ip": _split_secondary_vnic_boolean_values(_get_secondary_vnic_column(values, "Secondary VNIC Pub Address")),
        "display_name": _split_secondary_vnic_values(_get_secondary_vnic_column(values, "Secondary VNIC Display Names")),
        "hostname_label": _split_secondary_vnic_values(_get_secondary_vnic_column(values, "Secondary VNIC Hostname Labels")),
        "assign_private_dns_record": _split_secondary_vnic_boolean_values(_get_secondary_vnic_column(values, "Secondary VNIC Private DNS")),
        "physical_nic_index": _split_secondary_vnic_values(_get_secondary_vnic_column(values, "Secondary VNIC Physical NIC Index")),
        "defined_tags": _parse_secondary_vnic_tags(_get_secondary_vnic_column(values, "Secondary VNIC Defined Tags")),
        "freeform_tags": _parse_secondary_vnic_tags(_get_secondary_vnic_column(values, "Secondary VNIC Freeform Tags")),
    }

    for index, network in enumerate(networks):
        vnic = dict(network)
        vnic["display_name"] = _get_secondary_vnic_value(value_lists["display_name"], index)
        vnic["private_ip"] = _get_secondary_vnic_value(value_lists["private_ip"], index)
        vnic["nsg_ids"] = _get_secondary_vnic_value(value_lists["nsg_ids"], index, [])
        vnic["skip_source_dest_check"] = _get_secondary_vnic_value(value_lists["skip_source_dest_check"], index)
        vnic["assign_public_ip"] = _get_secondary_vnic_value(value_lists["assign_public_ip"], index)
        vnic["hostname_label"] = _get_secondary_vnic_value(value_lists["hostname_label"], index)
        vnic["assign_private_dns_record"] = _get_secondary_vnic_value(value_lists["assign_private_dns_record"], index)
        vnic["physical_nic_index"] = _get_secondary_vnic_value(value_lists["physical_nic_index"], index)
        vnic["defined_tags"] = _get_secondary_vnic_value(value_lists["defined_tags"], index, [])
        vnic["freeform_tags"] = _get_secondary_vnic_value(value_lists["freeform_tags"], index, [])
        secondary_vnics["vnic_" + str(index + 1)] = vnic

    return secondary_vnics


# If input is CD3 excel file
# Execution of the code begins here
def create_terraform_instances(inputfile, outdir, service_dir, prefix, ct):
    boot_policy_tfStr = {}
    tfStr = {}
    ADS = ["AD1", "AD2", "AD3"]

    filename = inputfile

    sheetName = "Instances"
    auto_tfvars_filename = prefix + '_' + sheetName.lower() + '.auto.tfvars'

    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    template = env.get_template('instances-template')

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, sheetName)
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    # List of column headers
    dfcolumns = df.columns.values.tolist()

    # Take backup of files
    for eachregion in ct.all_regions:
        resource = sheetName.lower()
        srcdir = outdir + "/" + eachregion + "/" + service_dir + "/"
        commonTools.backup_file(srcdir, resource, auto_tfvars_filename)
        tfStr[eachregion] = ''
        boot_policy_tfStr[eachregion] = ''

    #subnets = parseSubnets(filename)

    for i in df.index:
        region = str(df.loc[i, 'Region'])
        region = region.strip().lower()

        if region in commonTools.endNames:
            break

        if region not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit(1)

        display_name = str(df.loc[i, 'Display Name'])
        shapeField = str(df.loc[i, 'Shape'])
        shapeField = shapeField.strip()
        shape_error = 0

        if (shapeField.lower() != "nan"):
            if ".Micro" in shapeField or ".Flex" in shapeField:
                if ("::" not in shapeField):
                    shape_error = 1
                else:
                    shapeField = shapeField.split("::")
                    if (shapeField[1].strip() == ""):
                        shape_error = 1

        if (shape_error == 1):
            print("\nERROR!!! " + display_name + " is missing ocpus for Flex/Micro shape....Exiting!")
            exit(1)

        # temporary dictionary1 and dictionary2
        tempStr = {}
        tempdict = {}
        secondary_vnics = _build_secondary_vnics(df, i, dfcolumns, i + 3)
        if secondary_vnics != {}:
            tempStr.update({'secondary_vnics': secondary_vnics})

        # Check if values are entered for mandatory fields
        if (str(df.loc[i, 'Region']).lower() == 'nan' or str(df.loc[i, 'Display Name']).lower() == 'nan' or str(
                df.loc[i, 'Shape']).lower() == 'nan' or str(df.loc[i, 'Compartment Name']).lower() == 'nan' or str(
            df.loc[i, 'Pub Address']).lower() == 'nan' or str(
            df.loc[i, 'Availability Domain(AD1|AD2|AD3)']).lower() == 'nan' or str(
            df.loc[i, 'Network Details']).lower() == 'nan' or str(df.loc[i, 'Source Details']).lower() == 'nan'):
            print(
                "\nOne/All of the Column/Columns from Region, Shape, Compartment Name, Availability Domain, Display Name, Pub Address, Source Details and Network Details is empty in Instances sheet of CD3..exiting...Please check.")
            exit(1)

        # Perform the plugin match
        plugin_match = None
        plugin_column = fnmatch.filter(df.columns.tolist(), 'Plugin*')

        source_details=[]
        for columnname in dfcolumns:
            if _secondary_vnic_column_key(columnname).startswith("secondary_vnic_"):
                continue

            # Column value
            columnvalue = str(df[columnname][i]).strip()

            # Check for boolean/null in column values
            columnvalue = commonTools.check_columnvalue(columnvalue)

            # Check for multivalued columns
            tempdict = commonTools.check_multivalues_columnvalue(columnvalue, columnname, tempdict)

            # Process Defined and Freeform Tags
            if columnname.lower() in ociCommonTools.tagColumns:
                tempdict = ociCommonTools.split_tag_values(columnname, columnvalue, tempdict)

            if columnname in plugin_column:
                columnvalue = columnvalue.strip()
                if columnvalue != "":
                    plugin_match = True
                    tempdict = {'plugin_match': plugin_match}

            if columnname == 'Network Type':
                network_type = columnvalue.strip()
                tempdict = {'network_type': network_type}

            if columnname == 'Platform Config Type':
                network_type = columnvalue.strip()
                tempdict = {'platform_config_type': network_type}

            if columnname == 'Shape':
                if ".Flex" not in columnvalue and ".Micro" not in columnvalue:
                    columnvalue = columnvalue.strip()
                    tempdict = {'shape': [columnvalue]}

            subnet_id = ''
            network_compartment_id = ''
            vcn_name = ''
            if columnname == "Network Details":
                columnvalue = columnvalue.strip()
                if ("ocid1.subnet.oc" in columnvalue):
                    network_compartment_id = "root"
                    vcn_name = ""
                    subnet_id = columnvalue
                elif columnvalue.lower() != 'nan' and columnvalue.lower() != '':
                    if len(columnvalue.split("@")) == 2:
                        network_compartment_id = commonTools.check_tf_variable(columnvalue.split("@")[0].strip())
                        vcn_subnet_name = columnvalue.split("@")[1].strip()
                    else:
                        network_compartment_id = commonTools.check_tf_variable(
                            str(df.loc[i, 'Compartment Name']).strip())
                        vcn_subnet_name = columnvalue
                    if ("::" not in vcn_subnet_name):
                        print("Invalid Network Details format specified for row " + str(i + 3) + ". Exiting!!!")
                        exit(1)
                    else:
                        vcn_name = vcn_subnet_name.split("::")[0].strip()
                        subnet_id = vcn_subnet_name.split("::")[1].strip()
                tempdict = {'network_compartment_id': network_compartment_id, 'vcn_name': vcn_name,
                            'subnet_id': subnet_id}

            if columnname == 'Display Name':
                columnvalue = columnvalue.strip()
                display_tf_name = commonTools.check_tf_variable(columnvalue)
                tempdict = {'display_tf_name': display_tf_name}

            if columnname == 'Compartment Name':
                compartment_var_name = columnvalue.strip()
                compartment_var_name = commonTools.check_tf_variable(compartment_var_name)
                tempdict = {'compartment_tf_name': compartment_var_name}

            if columnname == 'Remote Execute':
                if columnvalue != "":
                    if ("@" in columnvalue):
                        remote_execute = columnvalue.strip().split("@")
                        tempdict = {'remote_execute': remote_execute[1],
                                    'bastion_ip': remote_execute[0]}
                    else:
                        tempdict = {'remote_execute': columnvalue.strip()}

            if columnname == 'Custom Policy Compartment Name':
                if columnvalue != "":
                    custom_policy_compartment_name = columnvalue.strip()
                    custom_policy_compartment_name = commonTools.check_tf_variable(custom_policy_compartment_name)
                    tempdict = {'custom_policy_compartment_name': custom_policy_compartment_name}

            if columnname == 'Availability Domain(AD1|AD2|AD3)':
                columnname = 'availability_domain'
                AD = columnvalue.upper()
                ad = ADS.index(AD)
                columnvalue = str(ad)
                tempdict = {'availability_domain': columnvalue}

            if columnname == 'Dedicated VM Host':
                if columnvalue.strip() != '' and columnvalue.strip() != 'nan':
                    dedicated_vm_host_tf = columnvalue
                    tempdict = {'dedicated_vm_host_tf': dedicated_vm_host_tf}

            if columnname == 'NSGs':
                if columnvalue != '' and columnvalue.strip().lower() != 'nan':
                    nsg_str = ""
                    nsg = ""
                    NSGs = columnvalue.split(",")
                    k = 0
                    while k < len(NSGs):
                        nsg = "\"" + NSGs[k].strip() + "\""
                        nsg_str = nsg_str + str(nsg)
                        if (k != len(NSGs) - 1):
                            nsg_str = nsg_str + ","
                        k += 1
                    tempdict = {'nsg_ids': nsg_str}
                    tempStr.update(tempdict)
                continue

            if columnname == "SSH Key Var Name":
                if columnvalue.strip() != '' and columnvalue.strip().lower() != 'nan':
                    ssh_key_var_name = columnvalue.strip()
                    tempdict = {'ssh_key_var_name': ssh_key_var_name}

            if columnname == "Source Details":
                if columnvalue.strip() != '' and columnvalue.strip().lower() != 'nan':
                    if "ocid1.image.oc" in columnvalue.strip():
                        ocid = columnvalue.strip()
                        type = "image"
                        source_details.append(type)
                        source_details.append(ocid)
                    elif "ocid1.bootvolume.oc" in columnvalue.strip():
                        ocid = columnvalue.strip()
                        type = "bootVolume"
                        source_details.append(type)
                        source_details.append(ocid)
                    elif "::" in columnvalue.strip():
                        source_details = columnvalue.strip().split("::")
                    tempdict = {'source_details': source_details}

            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)

        # Write all info to TF string
        tfStr[region] = tfStr[region] + template.render(tempStr)

    # Write TF string to the file in respective region directory
    for reg in ct.all_regions:

        reg_out_dir = outdir + "/" + reg + "/" + service_dir
        if not os.path.exists(reg_out_dir):
            os.makedirs(reg_out_dir)

        if tfStr[reg] != '':
            # Generate Instances String
            src = "##Add New Instances for " + reg.lower() + " here##"
            tfStr[reg] = template.render(count=0, region=reg).replace(src, tfStr[reg] + "\n" + src)
            tfStr[reg] = "".join([s for s in tfStr[reg].strip().splitlines(True) if s.strip("\r\n").strip()])

            # Write to TF file
            outfile = reg_out_dir + "/" + auto_tfvars_filename
            tfStr[reg] = "".join([s for s in tfStr[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
            oname = open(outfile, "w+")
            print(outfile + " for instances and boot volume backup policy has been created for region " + reg)
            oname.write(tfStr[reg])
            oname.close()
