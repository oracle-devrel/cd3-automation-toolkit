#!/usr/bin/python3
# Author: Suruchi
# Oracle Consulting
# suruchi.singla@oracle.com


import sys
import argparse
import pandas as pd
import os
import shutil
import datetime

sys.path.append(os.getcwd() + "/../..")
from commonTools import *
from jinja2 import Environment, FileSystemLoader

parser = argparse.ArgumentParser(description="Creates TF files for FSS")
parser.add_argument("inputfile",help="Full Path to the CSV file for creating fss or CD3 excel file. eg fss.csv or CD3-template.xlsx in example folder")
parser.add_argument("outdir", help="directory path for output tf files ")
parser.add_argument("--configFileName", help="Config file name", required=False)

if len(sys.argv) < 2:
    parser.print_help()
    sys.exit(1)

args = parser.parse_args()
filename = args.inputfile
outdir = args.outdir
if args.configFileName is not None:
    configFileName = args.configFileName
else:
    configFileName=""

ct = commonTools()
ct.get_subscribedregions(configFileName)

x = datetime.datetime.now()
date = x.strftime("%f").strip()

ADS = ["AD1", "AD2", "AD3"]
tempStr = {}
tempStr_fss = {}
FSS_names = {}
MT_names = {}
data_mt=''
data_fs=''
data_fs_es=''
mount_target_tf_name = ''
fss_name = ''
tempdict = {}

global value

#Load the template file
file_loader = FileSystemLoader('templates')
env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
export = env.get_template('export-options-template')
mounttarget = env.get_template('mount-target-template')
fss =  env.get_template('fss-template')
fses = env.get_template('export-resource-template')

# fss_multi export logic
def fss_exports(i, df, tempStr):
    global value

    i = i + 1
    try:
        if (str(df.loc[i, 'Path']) == path and str(df.loc[i, 'Region']) == "nan"):
            sourcecidr_1 = df.loc[i, 'Source CIDR']
            access_1 = df.loc[i, 'Access (READ_ONLY|READ_WRITE)']
            gid_1 = df.loc[i, 'GID']
            uid_1 = df.loc[i, 'UID']
            idsquash_1 = df.loc[i, 'IDSquash (NONE|ALL|ROOT)']
            require_ps_port_1 = str(str(df.loc[i, 'Require PS Port (true|false)']))
            if (str(sourcecidr_1).lower() == NaNstr.lower()):
                sourcecidr_1 = "0.0.0.0/0"
            if str(access_1).lower() == NaNstr.lower():
                access_1 = "READ_ONLY"
            elif str(access_1).strip() != "READ_WRITE":
                access_1 = "READ_ONLY"

            if str(gid_1).lower() == NaNstr.lower():
                gid_1 = "65534"
            else:
                gid_1 = int(gid_1)

            if str(uid_1).lower() == NaNstr.lower():
                uid_1 = "65534"
            else:
                uid_1 = int(uid_1)

            if str(idsquash_1).lower() == NaNstr.lower() or (
                    str(idsquash_1).strip() != "ALL" and str(idsquash_1).strip() != "ROOT"):
                idsquash_1 = "NONE"
            if str(require_ps_port_1).lower() == NaNstr.lower():
                require_ps_port_1 = "false"
            elif str(require_ps_port_1).lower() == "true" or require_ps_port_1 == "TRUE" or df.loc[i, 16] == 1.0:
                require_ps_port_1 = "true"
            else:
                require_ps_port_1 = "false"
            sourceCIDR.append(sourcecidr_1)
            access.append(access_1)
            gid.append(gid_1)
            uid.append(uid_1)
            idsquash.append(idsquash_1)
            require_ps_port.append(require_ps_port_1)
            tempStr1={'sourceCIDR' : sourceCIDR,'access': access,'gid' : gid, 'uid':uid, 'idsquash' : idsquash,'require_ps_port' : require_ps_port}
            fss_exports(i, df, tempStr1)
            value = i
        else:
            return "null"
    except Exception as e:
        print(e)


# If input is csv file; convert to excel
if ('.csv' in filename):
    df = pd.read_csv(filename)
    excel_writer = pd.ExcelWriter('tmp_to_excel.xlsx', engine='xlsxwriter')
    df.to_excel(excel_writer, 'FSS')
    excel_writer.save()
    filename = 'tmp_to_excel.xlsx'

df = pd.read_excel(filename, sheet_name='FSS', skiprows=1)
df = df.dropna(how='all')
df = df.reset_index(drop=True)

endNames = {'<END>', '<end>', '<End>'}
NaNstr = 'NaN'

for r in ct.all_regions:
    tempStr_fss[r] = ''
    MT_names[r] = []
    FSS_names[r] = []

for i in df.index:

    exports = []
    sourceCIDR = []
    access = []
    gid = []
    uid = []
    idsquash = []
    require_ps_port = []
    path = ''
    fss_tf_name=''

    region = str(df.loc[i, 'Region'])
    if region == "nan":
        continue

    if region in endNames:
        break
    region = str(region).lower().strip()


    if region not in ct.all_regions:
        print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
        exit(1)

    # Check if values are entered for mandatory fields - to create fss
    if (str(df.loc[i, 'Path']).lower() == 'nan' or str(
            df.loc[i, 'FSS Name']).lower() == 'nan'
            or str(df.loc[i, 'Compartment Name']).lower() == 'nan' or str(
                df.loc[i, 'Availability Domain\n(AD1|AD2|AD3)']).lower() == 'nan' or str(
                df.loc[i, 'MountTarget Name']).lower() == 'nan'):
        print("Columns Region, Compartment Name, Availability Domain, MountTarget Name, MountTarget SubnetName, Max FSS Capacity, Max FSS Inodes, FSS Name and path cannot be left blank..Exiting!")
        exit()

    # List of the column headers
    dfcolumns = df.columns.values.tolist()

    for columnname in dfcolumns:

        # Column value
        columnvalue = str(df[columnname][i]).strip()

        if columnvalue == '1.0' or columnvalue == '0.0':
            if columnname != "IDSquash (NONE|ALL|ROOT)":
                if columnvalue == '1.0':
                    columnvalue = "true"
                else:
                    columnvalue = "false"

        if (columnvalue.lower() == 'nan'):
            columnvalue = ""

        if columnname in commonTools.tagColumns:
            tempdict = commonTools.split_tag_values(columnname, columnvalue, tempdict)
            tempStr.update(tempdict)

        if "::" in columnvalue:
            if columnname != 'Compartment Name':
                columnname = commonTools.check_column_headers(columnname)
                multivalues = columnvalue.split("::")
                multivalues = [str(part).strip() for part in multivalues if part]
                tempdict = {columnname: multivalues}

        if columnname == 'Compartment Name':
            compartment_tf_name = commonTools.check_tf_variable(columnvalue)
            tempdict = {'compartment_tf_name': compartment_tf_name}
            tempStr.update(tempdict)

        if columnname == 'Availability Domain\n(AD1|AD2|AD3)':
            columnname = 'availability_domain'
            if columnvalue != '':
                AD = columnvalue.upper()
                ad = ADS.index(AD)
                columnvalue = str(ad)
            tempdict = {'availability_domain': columnvalue}

        if columnname == 'MountTarget Subnet Name':
            mount_target_subnet = commonTools.check_tf_variable(columnvalue.strip())
            tempdict = {'mount_target_subnet' : mount_target_subnet}
            tempStr.update(tempdict)

        if columnname == "Access (READ_ONLY|READ_WRITE)":
            columnname = "access"
            if str(columnvalue).lower() == "nan" or str(columnvalue) == "":
                columnvalue = "READ_ONLY"
            if str(columnvalue).strip() != "READ_WRITE":
                columnvalue = "READ_ONLY"
            access.append(columnvalue)
            tempdict = {'access': columnvalue}

        if columnname == "Source CIDR":
            columnname = commonTools.check_column_headers(columnname)
            if str(columnvalue).lower() == "nan" or str(columnvalue) == "":
                columnvalue = "0.0.0.0/0"
            sourceCIDR.append(columnvalue)
            tempdict = {'source_cidr': columnvalue}
            tempStr.update(tempdict)

        if columnname == "GID":
            columnname = commonTools.check_column_headers(columnname)
            if str(columnvalue).lower() == "nan" or str(columnvalue) == "":
                columnvalue = "65534"
            else:
                columnvalue = int(columnvalue)
            gid.append(columnvalue)


        if columnname == "UID":
            columnname = commonTools.check_column_headers(columnname)
            if str(columnvalue).lower() == "nan" or str(columnvalue) == "":
                columnvalue = "65534"
            else:
                columnvalue = int(columnvalue)
            uid.append(columnvalue)

        if columnname == "IDSquash (NONE|ALL|ROOT)":
            columnname = "idsquash"
            if str(columnvalue).lower() == "nan" or str(columnvalue) != "ALL" or str(columnvalue) != "ROOT" or str(columnvalue) == "":
                columnvalue = "NONE"
            idsquash.append(columnvalue)
            tempdict = {'idsquash': columnvalue}


        if columnname == "Require PS Port (true|false)":
            columnname = "require_ps_port"
            if str(columnvalue).lower() == "nan" or str(columnvalue).lower() != "true" or str(columnvalue) == "" or str(columnvalue) != 1.0:
                columnvalue = "false"
            require_ps_port.append(columnvalue)
            tempdict = {'require_ps_port': columnvalue}

        if columnname == "MountTarget Name":
            if columnvalue != '':
                mount_target_tf_name = commonTools.check_tf_variable(str(columnvalue).strip())
            tempdict = {'mount_target_tf_name': mount_target_tf_name}
            tempStr.update(tempdict)

        if columnname == 'FSS Name':
            if columnvalue != '':
                fss_name = str(columnvalue).strip()
                fss_tf_name = commonTools.check_tf_variable(fss_name.strip())
            tempdict = {'fss_tf_name' : fss_tf_name,'fss_name' : fss_name}
            tempStr.update(tempdict)

        path = str(df.loc[i,'Path']).strip()

        columnname = commonTools.check_column_headers(columnname)
        tempStr[columnname] = str(columnvalue).strip()
        tempStr.update(tempdict)

    fss_exports(i, df, tempStr)
    export_set_info = ""

    for j in range(0, len(sourceCIDR)):
        tempStr['source'] = str(sourceCIDR[j]).strip()
        tempStr['access'] = access[j].strip()
        tempStr['gid'] = str(gid[j])
        tempStr['uid'] = str(uid[j])
        tempStr['idsquash'] = idsquash[j].strip()
        tempStr['require_ps_port'] = str(require_ps_port[j]).strip().lower()

        export_set_info = export_set_info + export.render(tempStr)

    tempdict = {'export_set_info' : export_set_info }
    tempStr.update(tempdict)

    if (str(mount_target_tf_name).strip() not in MT_names[region]):
        MT_names[region].append(str(mount_target_tf_name).strip())
        tempStr_fss[region] = tempStr_fss[region] + mounttarget.render(tempStr)

    if (fss_name.strip() not in FSS_names[region]):
        FSS_names[region].append(fss_name.strip())
        tempStr_fss[region] = tempStr_fss[region] + fss.render(tempStr)

    path_tf = path
    if path[-1] == '/':
        path_tf = path[:-1]
    FSE_tf_name = "FSE-" + mount_target_tf_name + "-" + fss_tf_name + "-" + path_tf[1:]
    FSE_tf_name = commonTools.check_tf_variable(FSE_tf_name)

    tempStr['FSE_tf_name'] = FSE_tf_name
    tempStr.update(tempdict)

    # FSE_tf_name=commonTools.check_tf_variable(FSE_name)
    tempStr_fss[region] = tempStr_fss[region] + fses.render(tempStr)

for r in ct.all_regions:
    if (tempStr_fss[r] != ""):
        outfile = outdir + "/" + r + "/FSS.tf"
        if (os.path.exists(outfile)):
            shutil.copy(outfile, outfile + "_backUp" + date)
        oname = open(outfile, "w")
        print("Writing " + outfile)
        oname.write(tempStr_fss[r])
        oname.close()

# Remove temporary file created
if ('tmp_to_excel.xlsx' in filename):
    os.remove(filename)