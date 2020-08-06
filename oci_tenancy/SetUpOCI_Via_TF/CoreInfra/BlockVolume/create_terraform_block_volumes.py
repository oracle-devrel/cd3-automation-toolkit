#!/usr/bin/python3
# Author: Murali Nagulakonda
# Oracle Consulting
# murali.nagulakonda.venkata@oracle.com


import sys
import argparse
import pandas as pd
import os
from jinja2 import Environment, FileSystemLoader

sys.path.append(os.getcwd() + "/../..")
from commonTools import *

parser = argparse.ArgumentParser(description="Creates TF files for Block Volumes")
parser.add_argument("file",help="Full Path to the CSV file for creating block volume or CD3 excel file. eg instance.csv or CD3-template.xlsx in example folder")
parser.add_argument("outdir", help="directory path for output tf files ")
parser.add_argument("--configFileName", help="Config file name", required=False)

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

ADS = ["AD1", "AD2", "AD3"]

#Load the template file
file_loader = FileSystemLoader('templates')
env = Environment(loader=file_loader, keep_trailing_newline=True, trim_blocks=True, lstrip_blocks=True)
template = env.get_template('block-volume-template')

# If input is CD3 excel file
if ('.xls' in filename):
    df = pd.read_excel(filename, sheet_name='BlockVols',skiprows=1, dtype=object)
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    # List of the column headers
    dfcolumns = df.columns.values.tolist()

    reg = df['Region'].unique()

    # Take backup of files
    for eachregion in reg:
        eachregion = str(eachregion).strip().lower()
        resource='BlockVols'
        if (eachregion in commonTools.endNames or eachregion == 'nan'):
            break
        if eachregion not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit()
        srcdir = outdir + "/" + eachregion + "/"
        commonTools.backup_file(srcdir, resource, "_blockvolume.tf")

    for i in df.index:

        region = str(df.loc[i,"Region"])
        region = region.strip().lower()
        if region in commonTools.endNames:
            break
        if region not in ct.all_regions:
            print("\nERROR!!! Invalid Region; It should be one of the regions tenancy is subscribed to..Exiting!")
            exit()

        #temporary dictionary1 and dictionary2
        tempStr = {}
        tempdict = {}

        # Check if values are entered for mandatory fields - to create volumes
        if str(df.loc[i,'Region']).lower() == 'nan' or str(df.loc[i, 'Block Name']).lower() == 'nan' or str(df.loc[i,'Compartment Name']).lower()  == 'nan' or str(df.loc[i,'Availability Domain\n(AD1|AD2|AD3)']).lower()  == 'nan':
            print( " The values for Region, Block Name, Compartment Name and Availability Domain cannot be left empty. Please enter a value and try again !!")
            exit()

        # Check if values are entered for mandatory fields - to attach volumes to instances
        if str(df.loc[i,'Attached To Instance']).lower()  != 'nan' and str(df.loc[i,'Attach Type\n(iscsi|paravirtualized)']).lower()  == 'nan' :
            print("Attach Type cannot be left empty if you want to attach  the volume to instance "+df.loc[i,'Attached  To Instance']+". Please enter a value and try again !!")
            exit()

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

            if columnname in commonTools.tagColumns:
                tempdict = commonTools.split_tag_values(columnname, columnvalue, tempdict)

            if columnname == "Availability Domain\n(AD1|AD2|AD3)":
                columnname = "availability_domain"
                AD = columnvalue.upper()
                ad = ADS.index(AD)
                columnvalue = str(ad)

            if columnname == "Attached To Instance":
                columnvalue = commonTools.check_tf_variable(columnvalue)

            if columnname == "Attach Type\n(iscsi|paravirtualized)":
                columnname = "attach_type"

            if columnname == "Size In GBs":
                if columnvalue != '':
                    columnvalue = int(float(columnvalue))

            columnname = commonTools.check_column_headers(columnname)
            tempStr[columnname] = str(columnvalue).strip()
            tempStr.update(tempdict)


        #Render template
        tempStr = template.render(tempStr)

        outfile = outdir + "/" + region + "/" + blockname_tf + "_blockvolume.tf"
        print("Writing " + outfile)
        oname = open(outfile, "w")
        oname.write(tempStr)
        oname.close()


# If input is a csv file
elif ('.csv' in filename):
    fname = open(filename, "r")
    all_regions = os.listdir(outdir)
    for line in fname:
        if not line.startswith('#'):
            # [block_name,size_in_gb,availability_domain(AD1|AD2|AD3),attached_to_instance,attach_type(iscsi|paravirtualized,compartment_var_name] = line.split(',')
            linearr = line.split(",")
            region = linearr[0].strip().lower()
            if region not in all_regions:
                print("Invalid Region")
                continue

            blockname = linearr[1].strip()
            size = linearr[2].strip()
            AD = linearr[3].strip()
            attacheToInstanceName = linearr[4].strip()
            attachType = linearr[5].strip()
            compartmentVarName = linearr[6].strip()
            ad = ADS.index(AD)
            display_name = blockname

            tempStr = """resource "oci_core_volume"  \"""" + blockname + """"  {
        #Required
        availability_domain = "${data.oci_identity_availability_domains.ADs.availability_domains.""" + str(ad) + """.name}"
        compartment_id = "${var.""" + compartmentVarName + """}"

        #Optional
        display_name = \"""" + blockname + """"
        size_in_gbs = \"""" + size + """"
        ## Defined Tag Info ##
        }

resource "oci_core_volume_attachment" \"""" + blockname + """_volume_attachment" {
        #Required
        instance_id = "${oci_core_instance.""" + attacheToInstanceName + """.id}"
        attachment_type = \"""" + attachType + """"
        volume_id = "${oci_core_volume.""" + blockname + """.id}"

        }
        """
            outfile = outdir + "/" + region + "/" + blockname + ".tf"
            oname = open(outfile, "w")
            oname.write(tempStr)
            oname.close()
    fname.close()
else:
    print("Invalid input file format; Acceptable formats: .xls, .xlsx, .csv")
    exit()


