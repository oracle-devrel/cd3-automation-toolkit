#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# This script will produce a Terraform file that will be used to set up OCI core components
# Create Rule Set
#
# Author: Shruthi Subramanian
# Oracle Consulting
#

import json
import sys
import argparse
import os
import pandas as pd
sys.path.append(os.getcwd()+"/../../..")
from commonTools import *
from jinja2 import Environment, FileSystemLoader

######
# Required Inputs-CD3 excel file, Config file AND outdir
######

# If input file is CD3
def main():

    # Read the input arguments
    parser = argparse.ArgumentParser(description="Creates Rule Set TF files for LBR")
    parser.add_argument("inputfile",help="Full Path to the CD3 excel file. eg CD3-template.xlsx in example folder")
    parser.add_argument("outdir", help="directory path for output tf files ")
    parser.add_argument("--configFileName", help="Config file name", required=False)

    # Load the template file
    file_loader = FileSystemLoader('templates')
    env = Environment(loader=file_loader, keep_trailing_newline=True)
    rs = env.get_template('rule-set-template')
    method = env.get_template('access-method-rules-template')
    acl = env.get_template('access-control-rules-template')
    header = env.get_template('http-header-rules-template')
    request = env.get_template('request-response-header-rules-template')
    uri = env.get_template('uri-redirect-rules-template')

    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()
    filename = args.inputfile
    outdir = args.outdir
    if args.configFileName is not None:
        configFileName = args.configFileName
    else:
        configFileName = ""

    ct = commonTools()
    ct.get_subscribedregions(configFileName)

    # Read cd3 using pandas dataframe
    df, col_headers = commonTools.read_cd3(filename, "RuleSet")

    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    #DF with just the load balancer names and the Region details

    # fill the empty values with that in previous row.
    dffill = df[['Region','LBR Name','Rule Set Name','Action']]
    dffill = dffill.fillna(method='ffill')

    #Drop unnecessary columns
    dfdrop = df[['Region','LBR Name','Rule Set Name','Action']]
    dfdrop = df.drop(dfdrop, axis=1)

    #dfcert with required details
    df = pd.concat([dffill, dfdrop], axis=1)

    pd.set_option('display.max_columns', 500)

    unique_region = df['Region'].unique()

    # Make a dictionary - { Region :{ Rule Set : [Methods] } }
    d = {k: f.groupby(df['Rule Set Name'])['Allowed Methods'].apply(list).to_dict()
         for k, f in df.groupby(df['Region'])}
    d = dict((k.lower(), v) for k, v in d.items())

    # Take backup of files
    for eachregion in unique_region:
        eachregion = str(eachregion).strip().lower()
        if (eachregion in commonTools.endNames):
            break
        if eachregion == 'nan':
            continue
        if eachregion not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit()

        resource='RuleSet'
        srcdir = outdir + "/" + eachregion + "/"
        commonTools.backup_file(srcdir, resource, "-ruleset-lb.tf")

    # List of the column headers
    dfcolumns = df.columns.values.tolist()

    rule_set_list = []
    rs_str = ''
    region_list = []
    lbr_list = []

    def add_rules(df,rs_str,tempStr,count):

        if str(df.loc[i, 'Action']).upper() == 'CONTROL_ACCESS_USING_HTTP_METHODS':
            if count == 0:
                method_str = method.render(tempStr)
                rs_str = rs_str.replace(srcStr, method_str)
            else:
                pass

        if str(df.loc[i, 'Action']).upper() == 'HTTP_HEADER':
            header_str = header.render(tempStr)
            rs_str = rs_str.replace(srcStr, header_str)

        if str(df.loc[i, 'Action']).upper() == 'ALLOW':
            if str(df.loc[i,'Attribute Name'].upper() == 'SOURCE_VCN_IP_ADDRESS') or str(df.loc[i,'Attribute Name'].upper() == 'SOURCE_IP_ADDRESS') or str(df.loc[i,'Attribute Name'].upper() == 'SOURCE_VCN_ID'):
                acl_str = acl.render(tempStr)
                rs_str = rs_str.replace(srcStr, acl_str)

        if str(df.loc[i, 'Action']).upper() == 'REDIRECT':
            if str(df.loc[i,'Attribute Name'].upper() == 'PATH'):
                uri_str = uri.render(tempStr)
                rs_str = rs_str.replace(srcStr,uri_str)

        if str(df.loc[i,'Action']).upper() == 'EXTEND_HTTP_REQUEST_HEADER_VALUE' or str(df.loc[i,'Action']).upper() == 'EXTEND_HTTP_RESPONSE_HEADER_VALUE' \
                or  str(df.loc[i,'Action']).upper() == 'ADD_HTTP_REQUEST_HEADER' or str(df.loc[i,'Action']).upper() == 'ADD_HTTP_RESPONSE_HEADER' \
                or str(df.loc[i,'Action']).upper() == 'REMOVE_HTTP_REQUEST_HEADER'  or str(df.loc[i,'Action']).upper() == 'REMOVE_HTTP_RESPONSE_HEADER':
            request_str = request.render(tempStr)
            rs_str = rs_str.replace(srcStr,request_str)

        return rs_str

    for i in df.index:
        region = str(df.loc[i, 'Region'])

        if region.lower() == 'nan':
            continue

        region = region.strip().lower()

        if region in commonTools.endNames:
            break

        if region not in ct.all_regions:
            print("\nInvalid Region; It should be one of the values mentioned in VCN Info tab...Exiting!!")
            exit()

        # temporary dictionaries
        tempStr= {}
        tempdict= {}
        suffix=''
        method_list = ''
        prefix=''
        host=''
        port=''
        protocol = ''
        path=''
        lbr_tf_name = ''
        rule_set_tf_name = ''
        srcStr="## Add_rules_here ##"

        #Check if mandatory field is empty
        if (str(df.loc[i,'Action']).upper() == 'CONTROL_ACCESS_USING_HTTP_METHODS') and (str(df.loc[i,'Allowed Methods']).lower() == 'nan'):
            print("\nAllowed Methods cannot be left empty when Action is CONTROL_ACCESS_USING_HTTP_METHODS.....Exiting!")
            exit(1)

        if (str(df.loc[i,'Action']).upper() == 'ALLOW') or (str(df.loc[i,'Action']).upper() == 'REDIRECT'):
            if (str(df.loc[i,'Attribute Name']).lower() == 'nan') :
                print("\nAttribute Name cannot be left empty if Action is ALLOW|REDIRECT. Enter required values based on Action and try again......Exiting!!")
                exit(1)

            if (str(df.loc[i,'Attribute Name']).upper() == 'PATH') and (str(df.loc[i, 'Operator']).lower() == 'nan'):
                print("\nOperator cannot be left empty if Attribute Name is Path.......Exiting!!")
                exit(1)

            if (str(df.loc[i,'Attribute Name']).upper() == 'SOURCE_IP_ADDRESS') or (str(df.loc[i,'Attribute Name']).upper() == 'SOURCE_VCN_IP_ADDRESS') or (str(df.loc[i,'Attribute Name']).upper() == 'SOURCE_VCN_ID') :
                if (str(df.loc[i,'Attribute Value']).lower() == 'nan'):
                    print("\nAttribute Value cannot be left empty if Attribute Name is SOURCE_IP_ADDRESS|SOURCE_VCN_IP_ADDRESS|SOURCE_VCN_ID.......Exiting!!")
                    exit(1)

        if (str(df.loc[i,'Action']).upper() == 'ADD_HTTP_REQUEST_HEADER') or (str(df.loc[i,'Action']).upper() == 'ADD_HTTP_RESPONSE_HEADER') or (str(df.loc[i,'Action']).upper() == 'EXTEND_HTTP_REQUEST_HEADER_VALUE'):
            if (str(df.loc[i,'Header']).lower() == 'nan'):
                print("\nHeader cannot be left empty if Action is ADD_HTTP_REQUEST_HEADER | ADD_HTTP_RESPONSE_HEADER | EXTEND_HTTP_REQUEST_HEADER_VALUE.\nEnter required values based on Action and try again......Exiting!!")
                exit(1)

        if (str(df.loc[i, 'Action']).upper() == 'EXTEND_HTTP_RESPONSE_HEADER_VALUE') or (str(df.loc[i,'Action']).upper() == 'REMOVE_HTTP_REQUEST_HEADER') or (str(df.loc[i,'Action']).upper() == 'REMOVE_HTTP_RESPONSE_HEADER') :
            if (str(df.loc[i,'Header']).lower() == 'nan'):
                print("\nHeader cannot be left empty if Action is EXTEND_HTTP_RESPONSE_HEADER_VALUE | REMOVE_HTTP_REQUEST_HEADER | REMOVE_HTTP_RESPONSE_HEADER.\nEnter required values based on Action and try again......Exiting!!")
                exit(1)

        if (str(df.loc[i,'Action']).upper() == 'ADD_HTTP_REQUEST_HEADER') and (str(df.loc[i,'Value']).lower() == 'nan'):
            print("\nValue cannot be left empty if Action is ADD_HTTP_REQUEST_HEADER.......Exiting!!")
            exit(1)


        # Fetch data; loop through columns
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

            if columnname == 'Allow Invalid Characters(TRUE|FALSE)':
                columnname = 'allow_invalid_characters'

            if columnname == 'HTTP Header Size(in kB)':
                columnname = 'http_header_size'

            if columnname == 'Description of Access Control Rule':
                columnname = 'description'

            if columnname == 'LBR Name':
                if columnvalue != '':
                    lbr_tf_name = commonTools.check_tf_variable(columnvalue)
                    tempdict = {'lbr_tf_name': lbr_tf_name}

            if columnname == 'Rule Set Name':
                if columnvalue != '':
                    rule_set_tf_name = commonTools.check_tf_variable(columnvalue)
                    tempdict = {'rule_set_tf_name': rule_set_tf_name}
                    tempStr.update(tempdict)

            if columnname == 'Redirect URI Host:Port':
                if columnvalue != '':
                    columnname = 'redirect_uri_host_port'
                    columnvalue = str(columnvalue).strip().split(':')
                    host = columnvalue[0]
                    port = columnvalue[1]
                tempdict = {'host':host, 'port':port}
                tempStr.update(tempdict)

            if columnname == 'Redirect URI Protocol:Path':
                columnname = 'redirect_uri_protocol_path'
                if columnvalue != '':
                    columnvalue = str(columnvalue).strip().split(':')
                    protocol = columnvalue[0]
                    path = columnvalue[1]
                tempdict = {'protocol':protocol, 'path':path}
                tempStr.update(tempdict)


            if columnname == 'Suffix or Prefix (suffix:<value>|prefix:<value>)':
                columnname = 'suffix_or_prefix'
                if columnvalue != '':
                    columnvalue = str(columnvalue).strip().split(',')
                    for values in columnvalue:
                        values = values.split(':')
                        if values[0].lower() == 'suffix':
                            suffix = values[1]
                        if values[0].lower() == 'prefix':
                            prefix = values[1]
                        tempdict = {'suffix':suffix,'prefix':prefix}
                        tempStr.update(tempdict)

            if columnname == 'Attribute Value':
                attribute_name = str(df.loc[i,'Attribute Name']).strip()
                if attribute_name == 'SOURCE_VCN_IP_ADDRESS' or attribute_name == 'SOURCE_IP_ADDRESS' or attribute_name == 'SOURCE_VCN_ID':
                    if str(columnvalue) != '':
                        columnvalue = str(columnvalue).strip()
                        if '.' not in columnvalue:
                            columnvalue = commonTools.check_tf_variable(columnvalue)
                            columnvalue  = 'oci_core_vcn.'+columnvalue+'.id'
                        else:
                            columnvalue = "\"" +columnvalue +"\""

            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()

            # To process the methods - remove 'nan' from list and add it to tempStr
            if rule_set_tf_name != '':
                method_list = [x for x in d[region][rule_set_tf_name] if str(x).lower() != 'nan']
                for k, v in d.items():
                    if rule_set_tf_name in v.keys():
                        tempdict = {'method_list' : json.dumps(method_list)}

            tempStr.update(tempdict)

        outfile = outdir + "/" + region + "/" + lbr_tf_name + rule_set_tf_name + "-ruleset-lb.tf"

        if str(df.loc[i, 'Region']) not in region_list:
            region_list.append(str(df.loc[i, 'Region']))
            lbr_list = []
            rule_set_list = []
            if str(df.loc[i, 'Rule Set Name']) not in rule_set_list and str(df.loc[i, 'Rule Set Name'])  != 'nan':
                lbr_list.append(str(df.loc[i, 'LBR Name']))
                rule_set_list.append(str(df.loc[i, 'Rule Set Name']))
                rs_str = rs.render(tempStr)
                count = 0
                rs_str = add_rules(df,rs_str,tempStr, count)
                print("Writing to ..." + outfile)
            else:
                count = 1
                rs_str = add_rules(df, rs_str, tempStr, count)
        else:
            if str(df.loc[i, 'Rule Set Name']) not in rule_set_list and str(df.loc[i, 'Rule Set Name'])  != 'nan':
                rule_set_list.append(str(df.loc[i, 'Rule Set Name']))
                rs_str = rs.render(tempStr)
                count = 0
                rs_str = add_rules(df,rs_str,tempStr, count)
                print("Writing to ..." + outfile)
            else:
                count = 1
                rs_str = add_rules(df, rs_str, tempStr, count)

    
        # Write to TF file
        oname = open(outfile, "w+")
        oname.write(rs_str)
        oname.close()

if __name__ == '__main__':
    # Execution of the code begins here
    main()