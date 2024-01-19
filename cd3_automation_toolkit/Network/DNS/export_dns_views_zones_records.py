#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to export OCI core components
# Export DNS views-zones-rrsets
#
import oci
import os
from commonTools import *

importCommands = {}
oci_obj_names = {}


def get_rrset(zone_data,dns_client,record_default):
    r_map = {}
    r_tmp = {}
    zone_records = dns_client.get_zone_records(zone_data.id).data

    for zone_record in zone_records.items:
        if record_default == 'n' and zone_record.is_protected == True:
            continue
        tmpdict = {}
        domain = zone_record.domain
        rtype = zone_record.rtype
        r_key = domain+"_"+rtype
        tmpdict['rtype'] = rtype
        tmpdict['ttl'] = zone_record.ttl
        tmpdict['domain'] = domain
        record_key = str(zone_data.name + "_" + domain + "_" + zone_record.rtype)
        if r_key not in r_tmp.keys():
            r_tmp[r_key] = zone_record.rdata
        else:
            r_tmp[r_key] = str(r_tmp[r_key]) + "\n" + zone_record.rdata

        tmpdict['rdata'] = r_tmp[r_key]

        r_map[record_key] = tmpdict

    return r_map


def print_data(region, ntk_compartment_name, rrset, zone_data, view_data, values_for_column):
    view_tf_name = str(view_data.display_name)
    #zone_tf_name = view_tf_name + "_" + str(zone_data.name).replace(".", "_")
    zone_name = str(zone_data.name).replace(".", "_")
    domain = str(rrset['domain'])
    rtype = str(rrset['rtype'])
    rrset_tf_name = str(view_tf_name + "_" + zone_name + "_" + domain.replace(".", "_") + "_" + rtype).replace(".", "_")
    rrset_id = "zoneNameOrId/"+str(zone_data.id)+"/domain/"+domain+"/rtype/"+rtype+"/scope/PRIVATE/viewId/"+str(
            view_data.id)
    importCommands[region.lower()].write(
        "\nterraform import \"module.dns-rrsets[\\\"" + rrset_tf_name + "\\\"].oci_dns_rrset.rrset\" " + rrset_id)


    for col_header in values_for_column:
        if col_header == 'Region':
            values_for_column[col_header].append(region)
        elif col_header == 'Compartment Name':
            values_for_column[col_header].append(ntk_compartment_name)
        elif col_header == 'View Name':
            values_for_column[col_header].append(view_data.display_name)
        elif col_header == 'Zone':
            values_for_column[col_header].append(zone_data.name)
        elif col_header == 'Domain':
            values_for_column[col_header].append(rrset['domain'])
        elif col_header == 'RType':
            values_for_column[col_header].append(rrset['rtype'])
        elif col_header == 'RDATA':
            values_for_column[col_header].append(rrset['rdata'])
        elif col_header == 'TTL':
            values_for_column[col_header].append(rrset['ttl'])
        elif col_header.lower() in commonTools.tagColumns:
            values_for_column = commonTools.export_tags(view_data, col_header, values_for_column)


def print_empty_view(region, ntk_compartment_name, view_data, values_for_column):
    for col_header in values_for_column:
        if col_header == 'Region':
            values_for_column[col_header].append(region)
        elif col_header == 'Compartment Name':
            values_for_column[col_header].append(ntk_compartment_name)
        elif col_header == 'View Name':
            values_for_column[col_header].append(view_data.display_name)

        elif col_header == 'Zone':
            values_for_column[col_header].append("")
        elif col_header == 'Domain':
            values_for_column[col_header].append("")
        elif col_header == 'RType':
            values_for_column[col_header].append("")
        elif col_header == 'RDATA':
            values_for_column[col_header].append("")
        elif col_header == 'TTL':
            values_for_column[col_header].append("")
        elif col_header.lower() in commonTools.tagColumns:
            values_for_column = commonTools.export_tags(view_data, col_header, values_for_column)

# Execution of the code begins here
def export_dns_views_zones_rrsets(inputfile, outdir, service_dir, config, signer, ct, dns_filter, export_compartments=[], export_regions=[]):
    global tf_import_cmd
    global sheet_dict
    global importCommands
    global values_for_vcninfo
    global cd3file
    global reg
    global values_for_column

    cd3file = inputfile
    if ('.xls' not in cd3file):
        print("\nAcceptable cd3 format: .xlsx")
        exit()

    view_default = dns_filter
    zone_default = dns_filter
    record_default = dns_filter

    sheetName = "DNS-Views-Zones-Records"

    # Read CD3
    df, values_for_column= commonTools.read_cd3(cd3file,sheetName)

    # Get dict for columns from Excel_Columns
    sheet_dict=ct.sheet_dict[sheetName]

    print("\nCD3 excel file should not be opened during export process!!!")
    print("Tabs- DNS-ViewsZonesRecords  will be overwritten during export process!!!\n")

    # Create backups
    resource = 'tf_import_' + sheetName.lower()
    file_name = 'tf_import_commands_' + sheetName.lower() + '_nonGF.sh'
    for reg in export_regions:
        script_file = f'{outdir}/{reg}/{service_dir}/' + file_name
        if (os.path.exists(script_file)):
            commonTools.backup_file(outdir + "/" + reg +"/" + service_dir, resource, file_name)
        importCommands[reg] = open(script_file, "w")
        importCommands[reg].write("#!/bin/bash")
        importCommands[reg].write("\n")
        importCommands[reg].write("terraform init")

    # Fetch Views/Zones/rrsets Details
    print("\nFetching details of DNS Views/Zones/Records...")

    for reg in export_regions:
        importCommands[reg].write("\n\n######### Writing import for DNS Views/Zones/RRsets #########\n\n")
        config.__setitem__("region", ct.region_dict[reg])
        region = reg.capitalize()
        dns_client = oci.dns.DnsClient(config=config, retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY, signer=signer)
        # Same compartment will be used to export view/zones
        for ntk_compartment_name in export_compartments:
            views = oci.pagination.list_call_get_all_results(dns_client.list_views, compartment_id=ct.ntk_compartment_ids[ntk_compartment_name], lifecycle_state="ACTIVE")
            for view_data in views.data:
                if view_default == 'n' and view_data.is_protected == True:
                    continue
                #view_data = dns_client.get_view(view.id).data
                view_tf_name = str(view_data.display_name)
                zones = oci.pagination.list_call_get_all_results(dns_client.list_zones,
                                                                 compartment_id=ct.ntk_compartment_ids[
                                                                     ntk_compartment_name], lifecycle_state="ACTIVE",
                                                                 scope="PRIVATE", view_id=view_data.id).data
                if zones:
                ## Add if empty view
                    for zone_data in zones:
                        if zone_default == 'n' and zone_data.is_protected == True:
                            continue
                        zone_tf_name = view_tf_name + "_" + str(zone_data.name).replace(".", "_")
                        rrsets = get_rrset(zone_data, dns_client, record_default)
                        if rrsets:
                            for rrset in rrsets.values():
                                print_data(region, ntk_compartment_name, rrset, zone_data, view_data, values_for_column)
                            importCommands[region.lower()].write(
                                "\nterraform import \"module.dns-zones[\\\"" + zone_tf_name + "\\\"].oci_dns_zone.zone\" " + str(
                                    zone_data.id))
                        else:
                            print_empty_view(region, ntk_compartment_name, view_data, values_for_column)
                else:
                    print_empty_view(region, ntk_compartment_name, view_data, values_for_column)

                importCommands[region.lower()].write(
                    "\nterraform import \"module.dns-views[\\\"" + view_tf_name + "\\\"].oci_dns_view.view\" " + str(
                        view_data.id))

                #print_data(region, view_data)


    commonTools.write_to_cd3(values_for_column, cd3file, sheetName)
    print("DNS Views/Zones/Records are exported to CD3\n")

    # writing data
    for reg in export_regions:
        script_file = f'{outdir}/{reg}/{service_dir}/' + file_name
        with open(script_file, 'a') as importCommands[reg]:
            importCommands[reg].write('\n\nterraform plan\n')
