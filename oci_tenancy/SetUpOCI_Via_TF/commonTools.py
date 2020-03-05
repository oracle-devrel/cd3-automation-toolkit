import pandas as pd
import os
import shutil
import datetime
import configparser
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
from openpyxl.styles import Alignment
from openpyxl.styles import Font
from openpyxl.styles import Border
from openpyxl.styles import Side
import re

class commonTools():
    region_dict = {'ashburn':'us-ashburn-1','phoenix':'us-phoenix-1','london':'uk-london-1','frankfurt':'eu-frankfurt-1','toronto':'ca-toronto-1','tokyo':'ap-tokyo-1','seoul':'ap-seoul-1','mumbai':'ap-mumbai-1','sydney':'ap-sydney-1','saopaulo':'sa-saopaulo-1','zurich':'eu-zurich-1'}
    endNames = {'<END>', '<end>', '<End>'}
    tfname = re.compile('[^a-zA-Z0-9_-]')

    #Write exported  rows to cd3
    def write_to_cd3(rows, cd3file, sheet_name):
        book = load_workbook(cd3file)
        sheet = book[sheet_name]

        if(sheet_name=="VCN Info"):
            onprem_destinations=""
            ngw_destinations = ""
            igw_destinations = ""
            for destination in rows[0]:
                onprem_destinations=destination+","+onprem_destinations
            for destination in rows[1]:
                ngw_destinations = destination + "," + ngw_destinations
            for destination in rows[2]:
                igw_destinations = destination + "," + igw_destinations
            #regions is not empty (from export_network_nonGreenField)
            if(len(rows)==4):
                regions = ""
                for r in rows[3]:
                    regions=r+","+regions
                if (regions != "" and regions[-1] == ','):
                    regions = regions[:-1]
                #Put n for subnet_name_attach_cidr
                sheet.cell(6,2).value = 'n'
                #Put regions value
                sheet.cell(7, 2).value = regions

            if (onprem_destinations != "" and onprem_destinations[-1] == ','):
                onprem_destinations = onprem_destinations[:-1]
            if (ngw_destinations != "" and ngw_destinations[-1] == ','):
                ngw_destinations = ngw_destinations[:-1]
            if (igw_destinations != "" and igw_destinations[-1] == ','):
                igw_destinations = igw_destinations[:-1]

            sheet.cell(3,2).value=onprem_destinations
            sheet.cell(4,2).value = ngw_destinations
            sheet.cell(5,2).value = igw_destinations
            book.save(cd3file)
            book.close()
            return

        rows_len=len(rows)

        #If no rows exported from OCI, remove the sample data as well
        if(rows_len == 0):
            print("0 rows exported; Nothing to write to CD3 excel; Sheet "+sheet_name +" will be empty in CD3 excel!!")
            for i in range(0, sheet.max_row):
                for j in range(0, sheet.max_column):
                    sheet.cell(row=i + 3, column=j + 1).value = ""

            book.save(cd3file)
            book.close()
            return

        sheet_max_rows = sheet.max_row
        if (rows_len > sheet_max_rows):
            large = rows_len
        else:
            large = sheet_max_rows

        #Put Data
        for i in range(0,large):
            for j in range(0,len(rows[0])):
                if(i>=rows_len):
                    sheet.cell(row=i+3, column=j+1).value = ""
                else:
                    sheet.cell(row=i+3, column=j+1).value = rows[i][j]
                sheet.cell(row=i+3, column=j+1).alignment = Alignment(wrap_text=True)

        #Add color for exported sec rules and route rules
        if (sheet_name == "RouteRulesinOCI" or sheet_name == "SecRulesinOCI"):
            names = []
            brdr = Border(left=Side(style='thin'),
                          right=Side(style='thin'),
                          top=Side(style='thin'),
                          bottom=Side(style='thin'),
                          )
            # Add color coding to exported rules
            for row in sheet.iter_rows(min_row=3):
                c = 0
                region = ""
                name = ""
                for cell in row:
                    c = c + 1
                    if (c == 1):
                        region = cell.value
                        continue
                    elif (c == 4):
                        name = cell.value
                        break

                vcn_name = region + "_" + name
                if (vcn_name not in names):
                    names.append(vcn_name)
                    for cellnew in row:
                        if (len(names) % 2 == 0):
                            cellnew.fill = PatternFill(start_color="94AFAF", end_color="94AFAF", fill_type="solid")
                            cellnew.border = brdr
                        else:
                            cellnew.fill = PatternFill(start_color="E5DBBE", end_color="E5DBBE", fill_type="solid")
                            cellnew.border = brdr
                else:
                    for cellnew in row:
                        if (len(names) % 2 == 0):
                            cellnew.fill = PatternFill(start_color="94AFAF", end_color="94AFAF", fill_type="solid")
                            cellnew.border = brdr
                        else:
                            cellnew.fill = PatternFill(start_color="E5DBBE", end_color="E5DBBE", fill_type="solid")
                            cellnew.border = brdr

        book.save(cd3file)
        book.close()

    """def write_to_cd3_old(df, cd3file,sheet_name):
        book = load_workbook(cd3file)
        if (sheet_name in book.sheetnames):
            book.remove(book[sheet_name])

        writer = pd.ExcelWriter(cd3file, engine='openpyxl')
        writer.book = book
        writer.save()

        book = load_workbook(cd3file)
        writer = pd.ExcelWriter(cd3file, engine='openpyxl')
        writer.book = book
        df.to_excel(writer, sheet_name=sheet_name, index=False)

        # Adjust column widths
        ws = writer.sheets[sheet_name]
        from openpyxl.utils import get_column_letter

        column_widths = []
        for row in ws.iter_rows(min_row=2):
            for i, cell in enumerate(row):
                if len(column_widths) > i:
                    if len(str(cell.value)) > column_widths[i]:
                        column_widths[i] = len(str(cell.value))
                else:
                    column_widths += [len(str(cell.value))]

        for i, column_width in enumerate(column_widths):
            ws.column_dimensions[get_column_letter(i + 1)].width = column_width

        # Header Row
        for row in ws.iter_rows(min_row=1, max_row=1):
            for cell in row:
                cell.fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
                cell.font = Font(bold=True)
                cell.alignment = Alignment(wrap_text=True)

        # Move the sheet near Networking sheets
        book._sheets.remove(ws)
        if (sheet_name == "VCNs"):
            book._sheets.insert(5, ws)
        elif (sheet_name == "DHCP"):
            book._sheets.insert(6, ws)
        elif (sheet_name == "Subnets"):
            book._sheets.insert(7, ws)

        elif(sheet_name == "RouteRulesinOCI" or sheet_name == "SecRulesinOCI"):
            names = []
            brdr = Border(left=Side(style='thin'),
                          right=Side(style='thin'),
                          top=Side(style='thin'),
                          bottom=Side(style='thin'),
                          )
            # Add color coding to exported rules
            for row in ws.iter_rows(min_row=2):
                c = 0
                region = ""
                name = ""
                for cell in row:
                    c = c + 1
                    if (c == 1):
                        region = cell.value
                        continue
                    elif (c == 4):
                        name = cell.value
                        break

                vcn_name = region + "_" + name
                if (vcn_name not in names):
                    names.append(vcn_name)
                    for cellnew in row:
                        if (len(names) % 2 == 0):
                            cellnew.fill = PatternFill(start_color="94AFAF", end_color="94AFAF", fill_type="solid")
                            cellnew.border = brdr
                        else:
                            cellnew.fill = PatternFill(start_color="E5DBBE", end_color="E5DBBE", fill_type="solid")
                            cellnew.border = brdr
                else:
                    for cellnew in row:
                        if (len(names) % 2 == 0):
                            cellnew.fill = PatternFill(start_color="94AFAF", end_color="94AFAF", fill_type="solid")
                            cellnew.border = brdr
                        else:
                            cellnew.fill = PatternFill(start_color="E5DBBE", end_color="E5DBBE", fill_type="solid")
                            cellnew.border = brdr

            # Move the sheet near Networking sheets
            if(sheet_name=="RouteRulesinOCI"):
                book._sheets.insert(9, ws)
            elif(sheet_name=="SecRulesinOCI"):
                book._sheets.insert(8, ws)

        writer.save()"""

    #def backup_file(src_dir, pattern, overwrite):
    def backup_file(src_dir, pattern):
        x = datetime.datetime.now()
        date = x.strftime("%f").strip()
        if("_routetable.tf" in pattern):
            dest_dir = src_dir + "/backup_RTs_" + date
            print("Back up Directory: " + dest_dir)
        elif("_seclist.tf" in pattern):
            dest_dir = src_dir + "/backup_SLs_" + date
            print("Back up Directory: " + dest_dir)
        else:
            dest_dir = src_dir + "/backup_"+date
            print("Backing up existing "+pattern + " to "+ dest_dir)
        for f in os.listdir(src_dir):
            if f.endswith(pattern):
                if not os.path.exists(dest_dir):
                    #print("\nCreating backup dir " + dest_dir + "\n")
                    os.makedirs(dest_dir)

                src = os.path.join(src_dir, f)
                dest = os.path.join(dest_dir, f)
                #print("backing up ....." + src +"   to  "+dest)
                shutil.move(src, dest_dir)
                """if (overwrite == 'yes'):
                    shutil.move(src, dest_dir)
                elif (overwrite == 'no'):
                    shutil.copyfile(src, dest)
                """

class parseVCNs():
    peering_dict = dict()
    objs_peering_dict = dict()

    vcn_region = {}
    vcn_drgs = {}
    vcn_compartment = {}
    vcn_lpg_names= {}
    vcn_lpg_names1 = {}
    vcn_lpg_names2 = {}
    vcn_lpg_names3 = {}
    hub_vcn_names = []
    spoke_vcn_names = []
    vcn_lpg_rules = {}
    vcn_igws = {}
    vcn_ngws = {}
    vcn_sgws = {}
    vcn_hub_spoke_peer_none = {}
    vcn_compartment = {}
    vcn_names = []
    def __init__(self, filename):
        if(".xls" in filename):
            df_vcn = pd.read_excel(filename, sheet_name='VCNs', skiprows=1)
            df_vcn = df_vcn.dropna(how='all')
            df_vcn = df_vcn.reset_index(drop=True)

            # Create VCN details Dicts and Hub and Spoke VCN Names
            for i in df_vcn.index:
                region = df_vcn['Region'][i]
                if (region in commonTools.endNames or str(region).lower() == 'nan'):
                    break
                vcn_name = df_vcn['vcn_name'][i]
                self.vcn_names.append(vcn_name)

                # Check to see if vcn_name is empty in VCNs Sheet
                if (str(vcn_name).lower() == 'nan'):
                    print("ERROR!!! vcn_name/row cannot be left empty in VCNs sheet in CD3..exiting...")
                    exit(1)
                vcn_name = vcn_name.strip()
                if str(df_vcn['hub_spoke_peer_none'][i]).strip().split(":")[0].strip().lower() == 'hub':
                    self.peering_dict[vcn_name]=""
                    self.objs_peering_dict[vcn_name]=""


            for i in df_vcn.index:
                region = df_vcn['Region'][i]
                if (region in commonTools.endNames or str(region).lower()=='nan'):
                    break
                vcn_name = df_vcn['vcn_name'][i]
                self.vcn_names.append(vcn_name)

                # Check to see if vcn_name is empty in VCNs Sheet
                if (str(vcn_name).lower() == 'nan'):
                    print("ERROR!!! vcn_name/row cannot be left empty in VCNs sheet in CD3..exiting...")
                    exit(1)
                vcn_name=vcn_name.strip()
                region = region.strip().lower()
                self.vcn_region[vcn_name] = region

                self.vcn_lpg_names[vcn_name] = str(df_vcn['lpg_required'][i]).strip().split(",")
                self.vcn_lpg_names[vcn_name] = [x.strip() for x in self.vcn_lpg_names[vcn_name]]

                j=0
                for lpg in self.vcn_lpg_names[vcn_name]:
                    if lpg=='y':
                        self.vcn_lpg_names[vcn_name][j]=vcn_name+"_lpg"+str(j)
                        j=j+1
                self.vcn_lpg_names1[vcn_name] = str(df_vcn['lpg_required'][i]).strip().split(",")
                self.vcn_lpg_names1[vcn_name] = [x.strip() for x in self.vcn_lpg_names1[vcn_name]]

                j = 0
                for lpg in self.vcn_lpg_names1[vcn_name]:
                    if lpg == 'y':
                        self.vcn_lpg_names1[vcn_name][j] = vcn_name + "_lpg" + str(j)
                        j = j + 1

                self.vcn_lpg_names2[vcn_name] = str(df_vcn['lpg_required'][i]).strip().split(",")
                self.vcn_lpg_names2[vcn_name] = [x.strip() for x in self.vcn_lpg_names2[vcn_name]]

                j = 0
                for lpg in self.vcn_lpg_names2[vcn_name]:
                    if lpg == 'y':
                        self.vcn_lpg_names2[vcn_name][j] = vcn_name + "_lpg" + str(j)
                        j = j + 1

                self.vcn_lpg_names3[vcn_name] = str(df_vcn['lpg_required'][i]).strip().split(",")
                self.vcn_lpg_names3[vcn_name] = [x.strip() for x in self.vcn_lpg_names3[vcn_name]]

                j = 0
                for lpg in self.vcn_lpg_names3[vcn_name]:
                    if lpg == 'y':
                        self.vcn_lpg_names3[vcn_name][j] = vcn_name + "_lpg" + str(j)
                        j = j + 1

                self.vcn_drgs[vcn_name]=str(df_vcn['drg_required'][i]).strip()
                self.vcn_igws[vcn_name] = str(df_vcn['igw_required'][i]).strip()
                self.vcn_ngws[vcn_name] = str(df_vcn['ngw_required'][i]).strip()
                self.vcn_sgws[vcn_name] = str(df_vcn['sgw_required'][i]).strip()
                self.vcn_hub_spoke_peer_none[vcn_name] = str(df_vcn['hub_spoke_peer_none'][i]).strip().split(":")
                self.vcn_compartment[vcn_name]=str(df_vcn['compartment_name'][i]).strip()

                self.vcn_lpg_rules.setdefault(vcn_name, '')

                if (self.vcn_hub_spoke_peer_none[vcn_name][0].strip().lower() == 'hub'):
                    self.hub_vcn_names.append(vcn_name)
                    #self.peering_dict[vcn_name]=''


                if (self.vcn_hub_spoke_peer_none[vcn_name][0].strip().lower() == 'spoke' or self.vcn_hub_spoke_peer_none[vcn_name][0].strip().lower() == 'exportedspoke'):
                    hub_name=self.vcn_hub_spoke_peer_none[vcn_name][1].strip()
                    self.spoke_vcn_names.append(vcn_name)
                    try:
                        self.peering_dict[hub_name] = self.peering_dict[hub_name]+vcn_name+","
                    except KeyError:
                        print("ERROR!!! "+hub_name +" not marked as Hub. Verify hub_spoke_peer_none column again..Exiting!")
                        exit(1)
                #prepare seperate peering dict for establishing peering between LPGs
                if (self.vcn_hub_spoke_peer_none[vcn_name][0].strip().lower() == 'spoke'):
                    hub_name=self.vcn_hub_spoke_peer_none[vcn_name][1].strip()
                    try:
                        self.objs_peering_dict[hub_name] = self.objs_peering_dict[hub_name]+vcn_name+","
                    except KeyError:
                        print("ERROR!!! "+hub_name +" not marked as Hub. Verify hub_spoke_peer_none column again..Exiting!")
                        exit(1)


                if (self.vcn_hub_spoke_peer_none[vcn_name][0].strip().lower() == 'peer'):
                    self.peering_dict[vcn_name]=self.vcn_hub_spoke_peer_none[vcn_name][1].strip()
                    self.objs_peering_dict[vcn_name] = self.vcn_hub_spoke_peer_none[vcn_name][1].strip()

            for k,v in self.peering_dict.items():
                if(v!="" and v[-1]==','):
                    v=v[:-1]
                    self.peering_dict[k]=v
            for k,v in self.objs_peering_dict.items():
                if(v!="" and v[-1]==','):
                    v=v[:-1]
                    self.objs_peering_dict[k]=v
        if(".csv" in filename):
            config = configparser.RawConfigParser()
            config.optionxform = str
            file_read = config.read(filename)
            sections = config.sections()

            # Get Global Properties from Default Section
            all_regions = config.get('Default', 'regions')
            all_regions = all_regions.split(",")
            all_regions = [x.strip().lower() for x in all_regions]

class parseVCNInfo():
    all_regions = []
    subnet_name_attach_cidr = ''
    add_ping_secrules_onprem=''
    add_ping_secrules_vcnpeering=''
    onprem_destinations = []
    ngw_destinations = []
    igw_destinations = []


    def __init__(self,filename):

        df_info = pd.read_excel(filename, sheet_name='VCN Info', skiprows=1)

        # Get Property Values
        values = df_info['Value']

        onprem_destinations = str(values[0]).strip()
        if (onprem_destinations.lower() == 'nan'):
            print("\ndrg_subnet should not be left empty.. It will create empty route tables")
            self.onprem_destinations.append('')
        else:
            self.onprem_destinations = onprem_destinations.split(",")

        ngw_destinations = str(values[1]).strip()
        if (ngw_destinations.lower() == 'nan'):
            self.ngw_destinations.append('0.0.0.0/0')
        else:
            self.ngw_destinations = ngw_destinations.split(",")

        igw_destinations = str(values[2]).strip()
        if (igw_destinations.lower() == 'nan'):
            self.igw_destinations.append('0.0.0.0/0')
        else:
            self.igw_destinations = igw_destinations.split(",")

        self.subnet_name_attach_cidr = str(values[3]).strip()
        if (self.subnet_name_attach_cidr.lower() == 'nan'):
            self.subnet_name_attach_cidr = 'n'
        else:
            self.subnet_name_attach_cidr=self.subnet_name_attach_cidr.strip().lower()

        all_regions_excel = str(values[4]).strip()
        if(all_regions_excel.lower()=="nan"):
            print("\nERROR!!! regions field in VCN Info tab cannot be left empty..Exiting!!")
            exit(1)
        all_regions_excel = all_regions_excel.split(",")
        self.all_regions = [x.strip().lower() for x in all_regions_excel]





