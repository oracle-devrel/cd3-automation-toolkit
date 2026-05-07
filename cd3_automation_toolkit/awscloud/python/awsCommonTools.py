# Copyright (c) 2016, 2024, Oracle and/or its affiliates. All rights reserved.
#
# Common tools for ODB @AWS CD3 scripts.
# awscommontools.py
#

from typing import Dict, Optional
from common.python.commonTools import *


class awsCommonTools():


    tagColumns = {'common tags', 'common_tags', 'peering tags', 'peering_tags'}

    def split_tag_values(columnname, columnvalue, tempdict):

        columnvalue = columnvalue.replace("\n", "")
        if ";" in columnvalue:

            columnname = commonTools.check_column_headers(columnname)
            multivalues = columnvalue.split(";")
            multivalues = [part.split("=") for part in multivalues if part]
            tempdict = {columnname: multivalues}
        else:
            # If there is only one tag; split them only by "="; each key-value pair is stored as a list
            columnname = commonTools.check_column_headers(columnname)
            multivalues = columnvalue.split("=")
            multivalues = [str(part).strip() for part in multivalues if part]
            tempdict = {columnname: [multivalues]}
        return tempdict

    def _flatten_tags(tags: Optional[Dict[str, str]]) -> str:

        if not tags:
            return ""
        try:
            return ";".join([f"{k}={v}" for k, v in tags.items() if v is not None])
        except Exception:
            return ""