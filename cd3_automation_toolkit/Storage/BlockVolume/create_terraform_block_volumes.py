#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI core components
# Block Volumes
#
# Author: Murali N V
# Oracle Consulting
# Modified (TF Upgrade): Shruthi Subramanian
#

import sys
import os
from oci.config import DEFAULT_LOCATION
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
sys.path.append(os.getcwd() + "/../..")
from commonTools import *

######
# Required Inputs-CD3 excel file, Config file, prefix AND outdir
######
# Execution of the code begins here
def create_terraform_block_volumes(inputfile, outdir, service_dir, prefix,ct):
    filename = inputfile
    tfStr = {}

    sheetName="BlockVolumes"
    auto_tfvars_filename = prefix + '_' + sheetName.lower() + '.auto.tfvars'

    ADS = ["AD1", "AD2", "AD3"]

    # Load the template file
    file_loader = FileSystemLoader(f'{Path(__file__).parent}/templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
    template = env.get_template('blockvolumes-template')

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, sheetName)

    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    # List of the column headers
    dfcolumns = df.columns.values.tolist()

    # Take backup of files
    for eachregion in ct.all_regions:
        tfStr[eachregion] = ''
        reg_out_dir = outdir + "/" + eachregion + "/" + service_dir
        resource = sheetName.lower()
        commonTools.backup_file(reg_out_dir + "/", resource, auto_tfvars_filename)

    for i in df.index:

        region = str(df.loc[i,"Region"])
        region = region.strip().lower()
        if region in commonTools.endNames:
            break
        if region not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit(1)

        #temporary dictionary1 and dictionary2
        tempStr = {}
        tempdict = {}
        source_details = []
        block_volume_replicas = []
        autotune_policies = []

        # Check if values are entered for mandatory fields - to create volumes
        if str(df.loc[i,'Region']).lower() == 'nan' or str(df.loc[i, 'Block Name']).lower() == 'nan' or str(df.loc[i,'Compartment Name']).lower()  == 'nan' or str(df.loc[i,'Availability Domain(AD1|AD2|AD3)']).lower()  == 'nan':
            print( "The values for Region, Block Name, Compartment Name and Availability Domain cannot be left empty. Please enter a value and try again !!")
            exit(1)

        # Check if values are entered for mandatory fields - to attach volumes to instances
        if str(df.loc[i,'Attached To Instance']).lower()  != 'nan' and str(df.loc[i,'Attach Type(iscsi|paravirtualized)']).lower()  == 'nan' :
            print("Attach Type cannot be left empty if you want to attach  the volume to instance "+df.loc[i,'Attached To Instance']+". Please enter a value and try again !!")
            exit(1)
        elif str(df.loc[i,'Attach Type(iscsi|paravirtualized)']).lower()  != 'nan' and str(df.loc[i,'Attached To Instance']).lower()  == 'nan' :
            print("Attached To Instance cannot be left empty if Attachment Type is "+df.loc[i,'Attach Type(iscsi|paravirtualized)']+". Please enter a value and try again !!")
            exit(1)

        blockname_tf = commonTools.check_tf_variable(df.loc[i, 'Block Name'])
        tempStr['block_tf_name'] = blockname_tf

        # Fetch data; loop through columns
        for columnname in dfcolumns:
            # Column value
            columnvalue = str(df.loc[i, columnname]).strip()

            #Check for boolean/null in column values
            columnvalue = commonTools.check_columnvalue(columnvalue)

            #Check for multivalued columns
            tempdict = commonTools.check_multivalues_columnvalue(columnvalue,columnname,tempdict)

            if columnname == "Compartment Name":
                compartmentVarName = columnvalue.strip()
                columnname = commonTools.check_column_headers(columnname)
                compartmentVarName = commonTools.check_tf_variable(compartmentVarName)
                columnvalue = str(compartmentVarName)
                tempdict = {'compartment_tf_name': columnvalue}

            if columnname == 'Custom Policy Compartment Name':
                if columnvalue != "":
                    custom_policy_compartment_name = columnvalue.strip()
                    custom_policy_compartment_name = commonTools.check_tf_variable(custom_policy_compartment_name)
                    tempdict = {'custom_policy_compartment_name': custom_policy_compartment_name}


            # Process Freeform Tags and Defined Tags
            if columnname.lower() in commonTools.tagColumns:
                tempdict = commonTools.split_tag_values(columnname, columnvalue, tempdict)

            if columnname == "Availability Domain(AD1|AD2|AD3)":
                columnname = "availability_domain"
                AD = columnvalue.upper()
                ad = ADS.index(AD)
                columnvalue = str(ad)

            if columnname == "Attached To Instance":
                if str(columnvalue).strip() != '':
                    columnvalue = commonTools.check_tf_variable(columnvalue)

            if (columnname == 'Backup Policy'):
                columnname = 'backup_policy'
                columnvalue = str(columnvalue).strip()

            if columnname == "Attach Type(iscsi|paravirtualized)":
                columnname = "attach_type"

            if columnname == "Size In GBs":
                if columnvalue != '':
                    columnvalue = int(float(columnvalue))
            if columnname == "Source Details":
                if columnvalue.strip() != '' and columnvalue.strip().lower() != 'nan':
                    if "ocid1.volume.oc" in columnvalue.strip():
                        ocid = columnvalue.strip()
                        type = "volume"
                        source_details.append(type)
                        source_details.append(ocid)
                    elif "ocid1.volumebackup.oc" in columnvalue.strip():
                        ocid = columnvalue.strip()
                        type = "volumeBackup"
                        source_details.append(type)
                        source_details.append(ocid)
                    elif "ocid1.blockvolumereplica.oc" in columnvalue.strip():
                        ocid = columnvalue.strip()
                        type = "blockVolumeReplica"
                        source_details.append(type)
                        source_details.append(ocid)
                    elif "::" in columnvalue.strip():
                        source_details = columnvalue.strip().split("::")
                    tempdict = {'source_details': source_details}
            if columnname == "Block Volume Replica (Region::AD::Name)":
                columnname = "Block Volume Replicas"
                if columnvalue.strip() != '' and columnvalue.strip().lower() != 'nan':
                    if "::" in columnvalue.strip():
                        if columnvalue.strip().count("::") == 2:
                            block_volume_replicas_ads = columnvalue.strip().split("::")
                            block_volume_replicas_region = (block_volume_replicas_ads[0]).lower()
                            block_volume_replicas_ad = (block_volume_replicas_ads[1]).upper()
                            block_volume_replicas_name = (block_volume_replicas_ads[2])
                            if block_volume_replicas_region == str(df.loc[i,'Region']).strip().lower() and block_volume_replicas_ad == str(df.loc[i,'Availability Domain(AD1|AD2|AD3)']).strip().upper():
                                print("Volume replication Region and AD can not be same as volume Region and AD - column 'Block Volume Replica (Region::AD::Name)'")
                                exit(1)
                            if (block_volume_replicas_region in ct.all_regions) and (block_volume_replicas_ad in ADS):
                                region_ads = ct.region_ad_dict[block_volume_replicas_region]
                                if len(region_ads) >= int(block_volume_replicas_ad.split("AD")[1]):
                                    block_volume_replicas_ad = region_ads[(int(block_volume_replicas_ad.split("AD")[1]) -1)]
                                    block_volume_replicas.append(block_volume_replicas_ad)
                                    if block_volume_replicas_name != '' or block_volume_replicas_name != 'nan':
                                        block_volume_replicas.append(block_volume_replicas_name)
                                    else:
                                        rep_name = str(df.loc[i, 'Block Name']).strip() + "-replica"
                                        block_volume_replicas.append(rep_name)
                                else:
                                    print("AD is not present in Replication Region. " + columnname)
                                    exit(1)
                            else:
                                print("Replication Region is not subscribed or AD is in incorrect format. " +columnname)
                                exit(1)
                        elif columnvalue.strip().count("::") == 1:
                            block_volume_replicas_ads = columnvalue.strip().split("::")
                            block_volume_replicas_region = (block_volume_replicas_ads[0]).lower()
                            block_volume_replicas_ad = (block_volume_replicas_ads[1]).upper()
                            if block_volume_replicas_region == str(df.loc[i,'Region']).strip().lower() and block_volume_replicas_ad == str(df.loc[i,'Availability Domain(AD1|AD2|AD3)']).strip().upper():
                                print("Volume replication Region and AD can not be same as volume Region and AD - column 'Block Volume Replica (Region::AD::Name)'")
                                exit(1)
                            if (block_volume_replicas_region in ct.all_regions) and (block_volume_replicas_ad in ADS):
                                region_ads = ct.region_ad_dict[block_volume_replicas_region]
                                if len(region_ads) >= int(block_volume_replicas_ad.split("AD")[1]):
                                    block_volume_replicas_ad = region_ads[(int(block_volume_replicas_ad.split("AD")[1]) - 1)]
                                    block_volume_replicas.append(block_volume_replicas_ad)
                                    rep_name = str(df.loc[i, 'Block Name']).strip() + "-replica"
                                    block_volume_replicas.append(rep_name)
                                else:
                                    print("AD is not present in Replication Region. " + columnname)
                                    exit(1)
                            else:
                                print("Replication Region is not subscribed or AD is in incorrect format. " + columnname)
                                exit(1)

                        tempdict = {'block_volume_replicas': block_volume_replicas}
                    else:
                        print("Value is not in correct format. " + columnname)
                        exit(1)
            if columnname == "Cross Region Replication":
                val=''
                if columnvalue.lower()=="off":
                    val = 'true'
                if columnvalue.lower() !='on':
                    tempdict = {'block_volume_replicas': ''}
                    tempStr.update(tempdict)

                tempdict = {'block_volume_replicas_deletion': val}
            if columnname == "Autotune Type":
                if columnvalue.strip() != '' and columnvalue.strip().lower() != 'nan':
                    if columnvalue.strip().upper() == "PERFORMANCE_BASED":
                        if "Max VPUS Per GB" not in dfcolumns:
                            print("column 'Max VPUS Per GB' must be present in sheet and can not be left blank if Autotune type is PERFORMANCE_BASED.")
                            exit(1)
                        if str(df.loc[i,'Max VPUS Per GB']) != 'nan':
                            perf = {'autotune_type':'PERFORMANCE_BASED','max_vpus_per_gb':str(df.loc[i,'Max VPUS Per GB']).strip()}
                            autotune_policies.append(perf)
                        else:
                            print("column 'Max VPUS Per GB' can not be left blank if Autotune type is PERFORMANCE_BASED.")
                            exit(1)
                    elif columnvalue.strip().upper() == "DETACHED_VOLUME":
                        max_vpus_per_gb = 'null'
                        detach = {'autotune_type': 'DETACHED_VOLUME','max_vpus_per_gb': max_vpus_per_gb}
                        autotune_policies.append(detach)
                    elif columnvalue.strip().upper() == "BOTH":
                        if "Max VPUS Per GB" not in dfcolumns:
                            print("column 'Max VPUS Per GB' must be present in sheet and can not be left blank if Autotune type is PERFORMANCE_BASED.")
                            exit(1)
                        if str(df.loc[i, 'Max VPUS Per GB']) != 'nan':
                            perf = {'autotune_type':'PERFORMANCE_BASED','max_vpus_per_gb':str(df.loc[i,'Max VPUS Per GB']).strip()}
                            detach = {'autotune_type': 'DETACHED_VOLUME', 'max_vpus_per_gb': 'null'}
                            autotune_policies.append(detach)
                            autotune_policies.append(perf)
                        else:
                            print("Column 'Max VPUS Per GB' can not be left blank if Autotune type is PERFORMANCE_BASED/BOTH.")
                            exit(1)
                    else:
                        print("Value is not in correct format. " + columnname)
                        exit(1)
                    tempdict = {'autotune_policies': autotune_policies}

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
            # Generate Final String
            src = "##Add New Block Volumes for "+reg.lower()+" here##"
            tfStr[reg] = template.render(count=0, region=reg).replace(src,tfStr[reg])
            tfStr[reg] = "".join([s for s in tfStr[reg].strip().splitlines(True) if s.strip("\r\n").strip()])

            # Write to TF file
            tfStr[reg] = "".join([s for s in tfStr[reg].strip().splitlines(True) if s.strip("\r\n").strip()])
            outfile = reg_out_dir+ "/" + auto_tfvars_filename
            oname = open(outfile, "w+")
            print(outfile + " for Block Volume and its Backup Policy has been created for region " + reg)
            oname.write(tfStr[reg])
            oname.close()
