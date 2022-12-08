#!/usr/bin/python3
# Copyright (c) 2016, 2019, Oracle and/or its affiliates. All rights reserved.
#
# CD3 Parser
#
# Author: Andrew Vuong
# Oracle Consulting
# Modified (TF Upgrade): Shruthi Subramanian
#

import math
import pandas as pd
import re
import os
import sys
sys.path.append(os.getcwd()+"/../../..")
from commonTools import *


"""
Design strategy

Parent class of CD3Parser which parses the CD3 tabs into individual respective dataframes.

Then respective individual class created from CD3Parser class, will perform specialized organization
of data relevant to the tab offering compartmentability and modularity.

!!!!!!!!!!!!! Must include the full CD3 xlsx with all sheets below included!!!!!!!!!!!!!!!!!!
"""


class CD3Parser(object):
    def __init__(self, filename):
        # parsing by tabs
        try:
            self.excel_CD3 = pd.ExcelFile(filename)
        except Exception as e:
            raise NameError("More information: Path does not exist, check correctness of pathname")
        try:
            """ Assuming that all CD3 .xlsx sheet names are correctly spelled and cased, will raise 
            exception otherwise and relist the CD3 .xlsx sheet names """
            #self.compartment = self.excel_CD3.parse("Compartments", skiprows=1)  # another one
            #self.group = self.excel_CD3.parse("Groups")
            #self.policies = self.excel_CD3.parse("Policies")
            #self.vcn = self.excel_CD3.parse("VCNs", skiprows=1)  # another one
            #self.vcn_info = self.excel_CD3.parse("VCN Info", skiprows=1)  # parser
            #self.subnets = self.excel_CD3.parse("Subnets")
            #self.dhcp = self.excel_CD3.parse("DHCP")
            #self.instances = self.excel_CD3.parse("Instances")
            #self.blockvols = self.excel_CD3.parse("BlockVols")
            #self.tags = self.excel_CD3.parse("Tags")
            #self.tagserver = self.excel_CD3.parse("TagServer")
            #self.tagvolume = self.excel_CD3.parse("TagVolume")
            #self.addrouterules = self.excel_CD3.parse("AddRouteRules")
            #self.addsecrules = self.excel_CD3.parse("AddSecRules")
            #self.routerules = self.excel_CD3.parse("RouteRulesinOCI")
            #self.secrules = self.excel_CD3.parse("SecRulesinOCI")
            try:
                self.nsg = self.excel_CD3.parse("NSGs", skiprows=1,dtype=object)
            except Exception as e:
                if ("No sheet named" in str(e)):
                    print("\nTab - \"NSGs\" is missing in the CD3. Please make sure to use the right CD3 in properties file...Exiting!!")
                    exit(1)

        except Exception as e:
            raise NameError(("More information: Check that sheet_names are correct and exact on"
                             "CD3 .xls file.\n{}\n"
                             ).format(self.excel_CD3.sheet_names))

    def getNSG(self):
        return self.NSGParser(self.nsg)

    def getCompartment(self):
        return self.CompartmentParser(self.compartment)

    def getVCN(self):
        return self.VCNParser(self.vcn)

    def getVCN_Info(self):
        return self.VCN_InfoParser(self.vcn_info)

    # many more respective get methods
    """
    Example:
    def getDHCP(self):
        return self.DHCPParser(self.dhcp)
    """

    class AbstractParser(object):
        """Common parser functions; must supply sheet as arg if want to use AbstractParser as
        parent class otherwise use object as parent class.

        Each child class created from AbstractParser must Super().__init__(respective sheet) in
        child class's init to allow common function calls of AbstractParser.
        Not necessary, but strongly recommended to enable full function, and it's simple."""

        def __init__(self, sheet, regions):
            self.sheet = sheet
            self.regions = regions

        def _sheet_to_numpy(self):
            return self.sheet.to_numpy()

        def _getDataFrame(self):
            return self.sheet

        def purge(self, dir, pattern):
            """destroy existing .tf files"""
            for file in os.listdir(dir):
                if re.search(pattern, file):
                    print("Purge ....." + os.path.join(dir, file))
                    os.remove(os.path.join(dir, file))

        def checkOptionalEmpty(self, option):
            return isinstance(option, (int, float)) and math.isnan(option)

        def getRegionSpecificDict(self, regionDict, region):
            return regionDict[region.lower()]

        def getRegions(self):
            return self.regions

        def debug(self):
            print("\n=========DEBUG MODE SET TO TRUE==============\n\n{}\n" \
                  .format(self.sheet))
            print("Regions:\n{}\n".format(self.regions))
            print("All columns list and its indice:\n{}\n" \
                  .format({k: v for v, k in enumerate(self.sheet.columns)}))

    class NSGParser(AbstractParser):
        """NSGParser takes information from the NSG sheet and organize it  in such a way that
        seperates data by region to allow uniqueness, otherwise you could possibly have same
        compartment names, vcn names, and subnets, but the rules wouldn't follow because these
        are two separate regions.
        Additionally, the thought was to group all the relavant rules to a particular NSG.
        NSG cannot be the key directly because another NSG with the same name could reside in a
        different compartment even if they were from the same region. Therefore there must be a
        unique key such as compartment+VCN+NSGname as key, with its rules following as the value.
        The regions are the initial keys to regionspecific dictionaries, so a dict of dict."""

        def __init__(self, nsg):
            working_header = {}
            self.sheet = nsg
            self.nsg = nsg
            nsg = nsg.dropna(how='all')
            nsg = nsg.reset_index(drop=True)
            self.nsg_numpy = nsg.to_numpy()  # makes a list of list
            self.headers = nsg.columns.values.tolist()
            if nsg.Region.isnull().any() :
                print("\nError!! Region cannot be left empty.... Exiting!!")
                exit()
            #self.regions = sorted(list(set(nsg.Region)))
            self.regions = list(nsg.Region)

            self.regions = [x.strip().lower() for x in self.regions]
            unique_headers = tuple(self.headers[1:4])
            working_header[unique_headers] = [(self.headers[3:])]
            self.headersDict = dict((self.headers[0].lower(), working_header) for region in self.regions)

            self.regions = [i for n, i in enumerate(self.regions) if i not in self.regions[:n]]
            #for x in self.regions:
                #if x in commonTools.endNames:
                #    self.regions.remove(x)
            self.regionDict = dict((region.lower(), {}) for region in self.regions)  # robust
            for index in self.nsg_numpy:  # each row on excel
                region = str(index[0]).strip().lower()
                if region in commonTools.endNames:# or region not in parseVCNInfo(filename).all_regions:
                    break
                unique_id = tuple(index[1:4])  # column BCD
                workingdict = self.regionDict[index[0].lower()]
                if unique_id in workingdict.keys():
                    workingdict[unique_id].append(index[3:])
                else:
                    workingdict[unique_id] = [index[3:]]
            super().__init__(nsg, self.regions)

        
        def getRegionDict(self):
            return self.regionDict

        def getHeaderDict(self):
            return self.headersDict

    # many more respective classes
    """
    Example:
    class DHCPParser:
        def __init__(self, dhcp):
            self.dhcpspecific = dhcp
    """

    class CompartmentParser(AbstractParser):
        """Comparment Parser
        {region:{[[compartments,description]]}}
        """

        def __init__(self, compartment):
            self.compartment = compartment
            self.compartment_numpy = compartment.to_numpy()
            self.regions = []
            self.regionDict = {}  # {region:{[[compartments,description]]}}
            for index in self.compartment_numpy:
                region = index[0]
                if self.checkOptionalEmpty(region) or region.lower() == "<end>":
                    break
                else:
                    region = index[0].lower()  # yield uniform capitalized names
                    if not region in self.regionDict:
                        self.regions.append(region.capitalize())
                        self.regionDict[region] = {index[1].lower(): index[2]}
                    else:  # uses latest entry if duplicate exist in CD3
                        self.regionDict[region][index[1].lower()] = index[2]
            super().__init__(compartment, self.regions)

        def getRegionDict(self):
            return self.regionDict

    class VCNParser(AbstractParser):
        """VCN Parser
        {region:{[[vcn_name,[options]]]}}
        """

        def __init__(self, vcn):
            self.vcn = vcn
            self.vcn_numpy = vcn.to_numpy()
            self.regions = []
            self.regionDict = {}
            for index    in self.vcn_numpy:
                region = index[0].lower()
                if self.checkOptionalEmpty(region) or region.lower() == "<end>":
                    break
                else:
                    region = index[0].lower()
                    if not region in self.regionDict:
                        self.regions.append(region.capitalize())
                        self.regionDict[region] = {index[1].lower(): list(index[2:])}
                    else:
                        self.regionDict[region][index[1].lower()] = list(index[2:])
            super().__init__(vcn, self.regions)

        def getRegionDict(self):
            return self.regionDict

    class VCN_InfoParser(AbstractParser):
        """VCN Info Parser
        VCN Info is different in that it's essentially two unrelated structure in one to parse
        The first structure parses separately into a properties file with only one entry to parse.
        The second structure parses a VCN peering dict.

        # DESIGN CHANGES NEEDED. Not specific but how does VCN Peering know which region it is part
        of
        !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        VCN_InfoParser eeds to be cleaned up. Very hacky because I do not know the design decisions
        for this sheet
        """

        def __init__(self, vcn_info):
            self.vcn_info = vcn_info
            self.vcn_info_numpy = vcn_info.to_numpy()
            self.regions = []
            self.propertiesDict = {}
            self.peeringDict = {}
            """first structure, parse properties first
            TODO: not sure if empty value still needed to be included in properties, 
            I assume so and have defaulted to include empty values, as None

            """
            peering_part = False
            for index in self.vcn_info_numpy:
                if index[0].lower() == "vcn peering":
                    peering_part = True
                    pass
                elif not peering_part:
                    value = "" if self.checkOptionalEmpty(index[1]) else index[1]
                    self.propertiesDict[index[0]] = value
                else:
                    self.peeringDict[index[0]] = index[1]

            # creates the self.regions list, strips all stray whitespaces as well.
            [self.regions.append(region.strip().capitalize()) for region in \
             str(self.propertiesDict['regions']).split(",")]
            sorted(self.regions)
            super().__init__(vcn_info, self.regions)

        def getPropertiesDict(self):
            return self.propertiesDict

        def getPeeringDict(self):
            return self.peeringDict
