#!/usr/bin/python3
import csv
import sys
import argparse
import re
import pandas as pd
import os
from os import path
sys.path.append(os.getcwd()+"/../..")
from commonTools import *
from jinja2 import Environment, FileSystemLoader

ADS = ["AD1", "AD2", "AD3"]

parser = argparse.ArgumentParser(description="Creates Instances TF file")
parser.add_argument("file", help="Full Path of csv file or CD3 excel file. eg instance.csv or CD3-template.xlsx in example folder")
parser.add_argument("outdir", help="directory path for output tf files ")
parser.add_argument("--configFileName", help="Config file name", required=False)

if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(1)

if len(sys.argv) < 2:
    parser.print_help()
    sys.exit(1)

args = parser.parse_args()
filename = args.file
outdir = args.outdir

if args.configFileName is not None:
    configFileName = args.configFileName
else:
    configFileName=""

ct = commonTools()
ct.get_subscribedregions(configFileName)

#Load the template file
file_loader = FileSystemLoader('templates')
env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
template = env.get_template('instance-template')

#If input is CD3 excel file
if('.xls' in filename):

    df = pd.read_excel(filename, sheet_name='Instances',skiprows=1)
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    # List of column headers
    dfcolumns = df.columns.values.tolist()

    subnet_tf_name=''
    shape=''
    ocpus=''
    host_tf_name=''
    compartment_var_name=''

    reg = df['Region'].unique()

    # Take backup of files
    for eachregion in reg:
        eachregion = str(eachregion).strip().lower()
        resource='Instances'
        if (eachregion in commonTools.endNames):
            break
        if eachregion not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit()
        srcdir = outdir + "/" + eachregion + "/"
        commonTools.backup_file(srcdir, resource, "_instance.tf")

    for i in df.index:
        region = str(df.loc[i, 'Region'])

        region = region.strip().lower()

        if region in commonTools.endNames:
            break

        if region not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit()

        hostname = str(df.loc[i,'Hostname'])
        shapeField = str(df.loc[i,'Shape'])
        shapeField = shapeField.strip()
        shape_error=0

        if(shapeField.lower()!="nan" and ".Flex" in shapeField):
            if("::" not in shapeField):
                shape_error=1
            else:
                shapeField=shapeField.split("::")
                if(shapeField[1].strip()==""):
                    shape_error=1

        if region in ct.all_regions and shape_error==0:
            OS=df.loc[i,'OS']
            if(".Flex" in shapeField[0]):
                OS=OS+"Flex"
            #copy_template_file(df.loc[i,'Hostname'], OS,df.loc[i,'Region'])

        if(shape_error==1):
            print("\nERROR!!! "+ hostname +" is missing ocpus for Flex shape....Exiting!")
            exit()


        # temporary dictionary1 and dictionary2
        tempStr = {}
        tempdict = {}

        # Check if values are entered for mandatory fields
        if (str(df.loc[i, 'Region']).lower() == 'nan' or str(df.loc[i, 'Hostname']).lower() == 'nan' or str(df.loc[i, 'Shape']).lower() == 'nan' or str(df.loc[i, 'Compartment Name']).lower() == 'nan' or str(df.loc[i, 'Pub Address']).lower() == 'nan' or str(
                df.loc[i, 'Availability Domain\n(AD1|AD2|AD3)']).lower() == 'nan' or str(df.loc[i, 'Subnet Name']).lower() == 'nan' or str(df.loc[i, 'OS']).lower() == 'nan'):
            print("\nColumn Region, Shape, Compartment Name, Availability Domain, Hostname, Pub Address, OS and Subnet Name cannot be left empty in Instances sheet of CD3..exiting...")
            exit(1)

        for columnname in dfcolumns:

            # Column value
            columnvalue = str(df[columnname][i]).strip()

            if columnvalue == '1.0' or columnvalue == '0.0':
                if columnvalue == '1.0':
                    columnvalue = "true"
                else:
                    columnvalue = "false"

            if (columnvalue.lower() == 'nan'):
                columnvalue = ""

            if columnname in commonTools.tagColumns:
                tempdict = commonTools.split_tag_values(columnname, columnvalue, tempdict)

            if "::" in columnvalue:
                if ".Flex" in columnvalue:
                    columnname = commonTools.check_column_headers(columnname)
                    multivalues = columnvalue.split("::")
                    multivalues = [str(part).strip() for part in multivalues if part]
                    tempdict = {columnname: multivalues}
                elif columnname != 'Compartment Name':
                    columnname = commonTools.check_column_headers(columnname)
                    multivalues = columnvalue.split("::")
                    multivalues = [str(part).strip() for part in multivalues if part]
                    tempdict = {columnname: multivalues}

            if columnname == 'Shape':
                if ".Flex" not in columnvalue:
                    columnvalue = columnvalue.strip()
                    tempdict = { 'shape' : [columnvalue] }

            if columnname == "Subnet Name":
                subnet_tf_name = commonTools.check_tf_variable(columnvalue.strip())
                tempdict = { 'subnet_tf_name' : subnet_tf_name }

            if columnname == 'Hostname':
                columnvalue = columnvalue.strip()
                host_tf_name = commonTools.check_tf_variable(columnvalue)
                tempdict = {'host_tf_name': host_tf_name}

            if columnname == 'Compartment Name':
                compartment_var_name = columnvalue.strip()
                compartment_var_name = commonTools.check_tf_variable(compartment_var_name)
                tempdict = {'compartment_tf_name': compartment_var_name}

            if columnname == 'Availability Domain\n(AD1|AD2|AD3)':
                columnname = 'availability_domain'
                AD = columnvalue.upper()
                ad = ADS.index(AD)
                columnvalue = str(ad)
                tempdict = {'availability_domain' : columnvalue}

            if columnname == 'Dedicated VM Host':
                if columnvalue.strip() != '' and columnvalue.strip() != 'nan':
                    dedicated_vm_host_tf = "oci_core_dedicated_vm_host."+commonTools.check_tf_variable(columnvalue)+".id"
                else:
                    dedicated_vm_host_tf = "\"\""
                tempdict = {'dedicated_vm_host_tf': dedicated_vm_host_tf}

            if columnname == 'NSGs':
                if columnvalue != '' or columnvalue != 'nan':
                    nsg_str = ""
                    NSGs = columnvalue.split(",")
                    k=0
                    while k < len(NSGs):
                        nsg_str = nsg_str + "oci_core_network_security_group." + commonTools.check_tf_variable(NSGs[k].strip()) + ".id"
                        if (k != len(NSGs) - 1):
                            nsg_str = nsg_str + ","
                        k += 1
                continue

            if columnname == "SSH Key Var Name":
                if columnvalue.strip() != '' and  columnvalue.strip().lower() != 'nan':
                    ssh_key_var_name = "var."+columnvalue.strip()
                else:
                    ssh_key_var_name = "\"\""
                tempdict = {'ssh_key_var_name': ssh_key_var_name}

            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)

        # Write all info to TF string; Render template
        hostStr = template.render(tempStr)

        file = outdir + "/" + region + "/" + host_tf_name + "_instance.tf"
        oname = open(file, "w+")
        print("Writing... " + file)
        oname.write(hostStr)
        oname.close()

#If input is a csv file
elif('.csv' in filename):
    all_regions = os.listdir(outdir)
    with open(filename) as csvfile:
        reader = csv.DictReader(skipCommentedLine(csvfile))
        columns = reader.fieldnames
        for row in reader:
            region = row['Region']
            region = region.strip().lower()
            if region not in all_regions:
                print("Invalid Region")
                exit(1)
        for row in reader:
            copy_template_file(row['Hostname'], row['OS'],row['Region'])
            for column in columns:
                if (row['Region'] in endNames):
                    exit()

                if (re.match('DedicatedVMHost', column, flags=re.IGNORECASE)):
                    dedicated_host = row[column]
                    if (dedicated_host != 'nan'):
                        dedicated_host_str = """dedicated_vm_host_id = "${oci_core_dedicated_vm_host.""" + dedicated_host + """.id}" """
                        replaceAllplaceholders(outdir + '/' + row['Region'].strip().lower() + '/' + row['Hostname'] + '.tf','##' + column + '##', dedicated_host_str)
                    continue

                if (re.match('NSGs', column, flags=re.IGNORECASE)):
                    NSG_col = row[column]
                    if NSG_col != '':
                        nsg_str = "nsg_ids=""[ "
                        NSGs = NSG_col.split(":")
                        k = 0
                        while k < len(NSGs):
                            nsg_str = nsg_str + """"${oci_core_network_security_group.""" + NSGs[
                                k].strip() + """.id}" """
                            if (k != len(NSGs) - 1):
                                nsg_str = nsg_str + ","
                            else:
                                nsg_str = nsg_str + " ]"
                            k += 1
                        replaceAllplaceholders(outdir + '/' + row['Region'].strip().lower() + '/' + row['Hostname'] + '.tf','##' + column + '##', nsg_str)

                if(re.match('Availability domain',column,flags=re.IGNORECASE)):
                    if ('AD1' in row[column]):
                        row[column]='0'
                    if ('AD2' in row[column]):
                        row[column] = '1'
                    if ('AD3' in row[column]):
                        row[column] = '2'
                if(re.match('Pub Address',column,flags=re.IGNORECASE)):
                    if (row[column].lower() == "true"):
                        row[column] = 'true'
                    if (row[column].lower() == "false"):
                        row[column] = 'false'
                replaceAllplaceholders(outdir + '/' + row['Region'].strip().lower()+'/'+row['Hostname'] + '.tf', '##' + column + '##', row[column])

else:
    print("Invalid input file format; Acceptable formats: .xls, .xlsx, .csv")
    exit()



