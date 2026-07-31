from common.python.commonTools import *
from typing import Dict, Optional
import os
from google.oauth2 import service_account
from google.api_core.exceptions import GoogleAPIError
from google.cloud import resourcemanager_v3


class gcpCommonTools():
    tagColumns = {'labels', 'Labels'}

    def authenticate(self,config_file):
        # GCP credential & client
        try:
            if config_file=='':
                print("\nCannot run export workflow as authentication parameters are missing!!\n")
                exit()
            credentials = service_account.Credentials.from_service_account_file(config_file)
        except Exception as e:
            print("\n")
            print(str(e))
            print(f"\nError reading credentials file. Exiting!!!\n")
            exit(1)

        projects_client = resourcemanager_v3.ProjectsClient(credentials=credentials)
        from google.cloud import oracledatabase_v1

        shared_client = oracledatabase_v1.OracleDatabaseClient(credentials=credentials)
        active_project_ids = []

        try:
            # Search across all accessible projects
            search_request = resourcemanager_v3.SearchProjectsRequest()
            project_pages = projects_client.search_projects(request=search_request)
            regions=[]
            for project in project_pages:
                # Only target live, active projects (exclude deleted/pending delete)
                if project.state == resourcemanager_v3.Project.State.ACTIVE:
                    active_project_ids.append(project.project_id)

                    from google.cloud import compute_v1
                    client = compute_v1.RegionsClient(credentials=credentials)
                    for region in client.list(project=project.project_id):
                        regions.append(region.name)

        except GoogleAPIError as e:
            print(f"Error reading project hierarchy: {e}")
            print("Falling back. Please verify organization viewer permissions.")
        return credentials,active_project_ids,regions

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
        return tempdict
