import os
import sys
import yaml
import json

sys.path.insert(0, os.path.abspath('./functions'))
from jira_api import get_directory_names
from jira_api import get_file_names
from jira_api import get_task
from jira_api import get_all_tasks
from jira_api import get_payload
from jira_api import create_task


# load JIRA username and password
jira_creds = yaml.load(open('./user_dev.yml'))
username = jira_creds['user']['name']
password = jira_creds['user']['password']

# point to JIRA development environment
url = 'https://10.221.100.4'
