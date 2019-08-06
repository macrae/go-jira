import os
import sys
import yaml
import json

sys.path.insert(0, os.path.abspath('./functions'))
from jira_api import get_directory_names
from jira_api import get_file_names
from jira_api import flatten_dict
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


def test_get_directory_names():
    """Test get_directory_names method."""
    task_directories = get_directory_names('./tasks')

    assert task_directories == ['crisp_dm','onboarding','tests']


def test_get_file_names():
    """Test get_file_names method."""
    function_file_names = get_file_names('./functions')
    task_file_names = get_file_names('./tasks/crisp_dm')

    assert function_file_names == ['.coverage',
                                   'create_canned_tasks.py',
                                   'get_all_task_status.py',
                                   'jira_api.py']

    assert task_file_names == ['epic.json']


def test_flatten_dict():
    """Test flatten_dict method."""
    d = {'first_key': {'second_key': 'value'}}
    flat_d = flatten_dict(d)

    assert flat_d == {'first_key.second_key': 'value'}


def test_get_task():
    """Test that get a task is successful."""
    response = get_task(url, username, password, "AI", "2")

    assert response['status_code'] == 200
    assert len(json.loads(response['response']).keys()) == 5


def test_get_all_tasks():
    """Check that the number of issues returned is equal to the number of queriable issues."""
    issues = get_all_tasks(
        url,
        username,
        password,
        key="AI",
        start_at=0,
        max_results=100)

    assert len(issues['issues']) == issues['total_issues']


def test_get_payload():
    """Test loading a payload."""
    payload = get_payload(
        './tasks/crisp_dm/1_business_understanding/1_preplanning.json')

    assert type(payload) == dict
    assert len(payload.keys()) == 1
    assert len(payload['fields']) == 7


def test_create_tasks():
    """Test creating a task in JIRA."""
    epic_payload = get_payload('./tasks/crisp_dm/epic.json')
    epic_payload['fields']['reporter']['name'] = username

    # create epic
    epic = create_task(url, username, password, epic_payload)
    epic_key = json.loads(epic['response'])['key']

    # create task
    task_payload = get_payload(
        './tasks/crisp_dm/1_business_understanding/1_preplanning.json')
    task_payload['fields']['reporter']['name'] = username
    task_payload['fields']['customfield_10001'] = epic_key
    task = create_task(url, username, password, task_payload)

    assert task['status_code'] == 201
    assert str(json.loads(task['response'])['key']).startswith("AI")


# def test_task_order():
#     """Test order of epic, task and subtask creation."""
#     issues = get_all_tasks(url, username, password, "AI", 0, 100)['issues']

#     # TODO: find the most recently created epic

#     # TODO: test that the epic key is less than all it's task keys

#     # TODO: test that each task key is less than all it's subtask keys
