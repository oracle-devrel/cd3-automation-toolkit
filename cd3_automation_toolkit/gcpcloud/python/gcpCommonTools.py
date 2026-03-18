from common.python.commonTools import *
from typing import Dict, Optional
import os
from google.oauth2 import service_account


class gcpCommonTools():
    def authenticate(self,config_file):
        # Azure credential & client
        credentials = service_account.Credentials.from_service_account_file(config_file)
        return credentials
