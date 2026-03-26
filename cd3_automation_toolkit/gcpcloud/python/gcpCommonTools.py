from common.python.commonTools import *
from typing import Dict, Optional
import os
from google.oauth2 import service_account


class gcpCommonTools():
    tagColumns = {'labels'}

    def authenticate(self,config_file):
        # Azure credential & client
        credentials = service_account.Credentials.from_service_account_file(config_file)
        return credentials

    def split_tag_values(columnname, columnvalue, tempdict):
        columnvalue = columnvalue.replace("\n", "")
        if ";" in columnvalue:
            # If there are more than one tag; split them by ";" and "="

            columnname = commonTools.check_column_headers(columnname)
            multivalues = columnvalue.split(";")
            multivalues = [part.split("=") for part in multivalues if part]
            """for value in multivalues:
                try:
                    value[1] = value[1].replace("\\","\\\\")
                except IndexError as e:
                    pass"""
            tempdict = {columnname: multivalues}
            print("if")
        else:
            # If there is only one tag; split them only by "="; each key-value pair is stored as a list
            columnname = commonTools.check_column_headers(columnname)
            multivalues = columnvalue.split("=")
            multivalues = [str(part).strip() for part in multivalues if part]
            """if multivalues != []:
                try:
                    multivalues[1] = multivalues[1].replace("\\","\\\\")
                except IndexError as e:
                    pass"""
            tempdict = {columnname: [multivalues]}
            print("else")
        print(tempdict)
        return tempdict
