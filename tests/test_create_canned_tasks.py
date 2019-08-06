import os
import sys
import yaml
import json
import subprocess

sys.path.insert(0, os.path.abspath('./functions'))
from create_canned_tasks import main
from jira_api import get_all_tasks_in_epic

# load JIRA username and password
jira_creds = yaml.load(open('./user_dev.yml'))
username = jira_creds['user']['name']
password = jira_creds['user']['password']

# point to JIRA development environment
url = 'https://10.221.100.4'


def test_main():
    """Integration test of main method."""

    output = subprocess.check_output("./run_create_canned_tasks.sh",shell=True)

    # TO-DO: Refactor this mess!!!
    # parse create_canned_tasks_output
    output_index = str(output).find('AI-')
    epic_key = str(output)[output_index:][:-3]
    key = epic_key.split('-')[0]
    id = epic_key.split('-')[1]

    # get all tasks associated with epic_key
    response = get_all_tasks_in_epic(url, username, password, key, id)

    assert response['status_code'] == 200

    # # confirm that tasks match with ./tasks/tests/
    # number_of_tasks = json.loads(response['response'])['total']

    # assert number_of_tasks == 'number_of_tasks_in_tests'

    # issues = json.loads(response['response'])['issues']

    # issue_summaries = list(map(lambda x: x['fields']['summary'], issues))

    # assert issue_summaries == 'summaries in JSON in tests'
