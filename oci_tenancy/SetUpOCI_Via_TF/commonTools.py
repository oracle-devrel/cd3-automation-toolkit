import pandas as pd
import os
import shutil
import datetime
import configparser


class commonTools():
    region_dict = {'ashburn':'us-ashburn-1','phoenix':'us-phoenix-1','london':'uk-london-1','frankfurt':'eu-frankfurt-1','toronto':'ca-toronto-1','tokyo':'ap-tokyo-1','seoul':'ap-seoul-1','mumbai':'ap-mumbai-1','sydney':'ap-sydney-1','saopaulo':'sa-saopaulo-1','zurich':'eu-zurich-1'}
    endNames = {'<END>', '<end>', '<End>'}

    #def backup_file(src_dir, pattern, overwrite):
    def backup_file(src_dir, pattern):
        x = datetime.datetime.now()
        date = x.strftime("%f").strip()
        if("_routetable.tf" in pattern):
            dest_dir = src_dir + "/backup_RTs_" + date
        elif("_seclist.tf" in pattern):
            dest_dir = src_dir + "/backup_SLs_" + date

        for f in os.listdir(src_dir):
            if f.endswith(pattern):
                if not os.path.exists(dest_dir):
                    print("\nCreating backup dir " + dest_dir + "\n")
                    os.makedirs(dest_dir)

                src = os.path.join(src_dir, f)
                print("backing up ....." + src)
                dest = os.path.join(dest_dir, f)
                shutil.move(src, dest_dir)
                """if (overwrite == 'yes'):
                    shutil.move(src, dest_dir)
                elif (overwrite == 'no'):
                    shutil.copyfile(src, dest)
                """

class parseVCNs():
    peering_dict = dict()

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
            df_vcn.dropna(how='all')

            # Create VCN details Dicts and Hub and Spoke VCN Names
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
                j=0
                for lpg in self.vcn_lpg_names[vcn_name]:
                    if lpg=='y':
                        self.vcn_lpg_names[vcn_name][j]=vcn_name+"_lpg"+str(j)
                        j=j+1

                self.vcn_lpg_names1[vcn_name] = str(df_vcn['lpg_required'][i]).strip().split(",")
                j = 0
                for lpg in self.vcn_lpg_names1[vcn_name]:
                    if lpg == 'y':
                        self.vcn_lpg_names1[vcn_name][j] = vcn_name + "_lpg" + str(j)
                        j = j + 1

                self.vcn_lpg_names2[vcn_name] = str(df_vcn['lpg_required'][i]).strip().split(",")
                j = 0
                for lpg in self.vcn_lpg_names2[vcn_name]:
                    if lpg == 'y':
                        self.vcn_lpg_names2[vcn_name][j] = vcn_name + "_lpg" + str(j)
                        j = j + 1

                self.vcn_lpg_names3[vcn_name] = str(df_vcn['lpg_required'][i]).strip().split(",")
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


                if (self.vcn_hub_spoke_peer_none[vcn_name][0].lower() == 'hub'):
                    self.hub_vcn_names.append(vcn_name)
                    self.peering_dict[vcn_name]=''


                if (self.vcn_hub_spoke_peer_none[vcn_name][0].lower() == 'spoke'):
                    hub_name=self.vcn_hub_spoke_peer_none[vcn_name][1]
                    self.spoke_vcn_names.append(vcn_name)
                    self.peering_dict[hub_name] = self.peering_dict[hub_name]+vcn_name+","

                if (self.vcn_hub_spoke_peer_none[vcn_name][0].lower() == 'peer'):
                    self.peering_dict[vcn_name]=self.vcn_hub_spoke_peer_none[vcn_name][1]

            for k,v in self.peering_dict.items():
                if(v[-1]==','):
                    v=v[:-1]
                    self.peering_dict[k]=v
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
        all_regions_excel = all_regions_excel.split(",")
        self.all_regions = [x.strip().lower() for x in all_regions_excel]





