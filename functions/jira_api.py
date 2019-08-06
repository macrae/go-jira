import os
import sys
import json
import requests
from requests.auth import HTTPBasicAuth
requests.packages.urllib3.disable_warnings()


def get_directory_names(directory):
    """
    List all directory names in a directory.

    Args:
        directory (str): main directory

    Returns:
        list: directory names in the main directory.

    """
    return [d for d in os.listdir(directory)
            if os.path.isdir(os.path.join(directory, d))]


def get_file_names(directory):
    """
    List all file names in a directory.

    Args:
        directory (str): main directory

    Returns:
        list: file names in the main directory.

    """
    return [f for f in os.listdir(directory)
            if os.path.isfile(os.path.join(directory, f))]


def flatten_dict(d):
    """
    Flatten a nested dictionary into non-nested dictionary.

    Args:
        d (dict):            nested dictionary

    Returns:
        key_values (dict):   flattened dictionary

    """
    def items():
        for key, value in d.items():
            if isinstance(value, dict):
                for subkey, subvalue in flatten_dict(value).items():
                    yield key + "." + subkey, subvalue
            else:
                yield key, value
    return dict(items())


def get_task(url, username, password, key, id):
    """
    Return a JIRA task. When the task is finished, it will contain the result. The result may be an arbitrary JSON, its shape is different for each task type. Consult the documentation of the method that created the task to know what it is.

    To access a task, you need to be its creator or a JIRA admin. Otherwise a 403 response will be returned.

    Args:
        url (str):                domain name
        username (str):           username
        password (str):           pasword
        key (str):                project key
        id (str):                 task id

    Returns:
        dict:
            status_code (int):    HTTP status code
            response (str):       body of response

    """
    headers = {'Content-Type': 'application/json', 'Accept-Charset': 'UTF-8'}

    response = requests.get(
        url + '/rest/api/2/issue/' + str(key) + '-' + str(id),
        headers=headers,
        auth=HTTPBasicAuth(username, password),
        verify=False)

    return {"status_code": response.status_code, "response": response.text}


def get_all_tasks_in_epic(url, username, password, key, id):
    """
    Return all JIRA tasks in an epic. When the task is finished, it will contain the result. The result may be an arbitrary JSON, its shape is different for each task type. Consult the documentation of the method that created the task to know what it is.

    To access a task, you need to be its creator or a JIRA admin. Otherwise a 403 response will be returned.

    Args:
        url (str):                domain name
        username (str):           username
        password (str):           pasword
        key (str):                project key
        id (str):                 task id

    Returns:
        dict:
            status_code (int):    HTTP status code
            response (str):       body of response

    """
    headers = {'Content-Type': 'application/json', 'Accept-Charset': 'UTF-8'}

    response = requests.get(
        url + '/rest/api/2/search?jql=cf[10001]=' + str(key) + '-' + str(id)+\
        '&startAt=0&maxResults=100',
        headers=headers,
        auth=HTTPBasicAuth(username, password),
        verify=False)

    return {"status_code": response.status_code, "response": response.text}


def get_all_tasks(url, username, password, key, start_at=0, max_results=100):
    """
    Return all tasks using JQL search. When the task is finished, it will contain the result. The result may be an arbitrary JSON, its shape is different for each task type. Consult the documentation of the method that created the task to know what it is.

    To access a task, you need to be its creator or a JIRA admin. Otherwise a 403 response will be returned.

    Args:
        url (str):               domain name
        username (str):          username
        password (str):          pasword
        key (str):               project key
        start_at (int):          issue index to start query at
        max_results (int):       maximum number of issues to return

    Returns:
        dict:
            issues (list):       all issues in project
            total_issues (int):  total number of queriable issues

    """
    def create_url(url, start_at, max_results):
        new_url = url + '/rest/api/2/search?jql=project=' + str(key) + \
                '&startAt=%s&maxResults=%s' % (str(start_at), str(max_results))

        return new_url

    def get_issues(url):
        headers = {
                'Content-Type': 'application/json',
                'Accept-Charset': 'UTF-8'}

        response = requests.get(
                url,
                headers=headers,
                auth=HTTPBasicAuth(username, password),
                verify=False)

        return {'issues': json.loads(response.text)['issues'],
                'total': json.loads(response.text)['total']}

    def print_progress_bar(iteration,
                           total,
                           prefix='',
                           suffix='',
                           decimals=1,
                           length=100,
                           fill='#'):
        percent = ("{0:." + str(decimals) + "f}").\
          format(100 * (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        sys.stdout.flush()
        sys.stdout.write('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix))

        # print new line on complete
        if iteration == total:
            print()

    new_url = create_url(url, start_at, max_results)
    first_call = get_issues(new_url)
    issues = first_call['issues']
    total_issues = first_call['total']
    print_progress_bar(0, total_issues)

    # paginate through responses to get all results
    while (start_at + max_results) < total_issues:
        new_url = create_url(url, (start_at + max_results), max_results)
        issues.extend(get_issues(new_url)['issues'])
        start_at = (start_at + max_results)
        print_progress_bar(start_at, total_issues)

    return {'issues': issues, 'total_issues': total_issues}


def create_task(url, username, password, payload):
    """
    Creates an issue or a sub-task from a JSON representation. Creating a sub-task is similar to creating an issue with the following differences: the issueType field must be set to a sub-task issue type and you must provide a parent field with the ID or key of the parent issue.

    Args:
        url (str):       domain name
        username (str):  username
        password (str):  pasword
        payload (str):   JSON representation of task

    Returns:
        dict:
            status_code (int):    HTTP status code
            response (str):       body of response

    """
    headers = {'Content-Type': 'application/json', 'Accept-Charset': 'UTF-8'}

    response = requests.post(
        url + '/rest/api/2/issue/',
        data=json.dumps(payload),
        headers=headers,
        auth=HTTPBasicAuth(username, password),
        verify=False)

    return {"status_code": response.status_code, "response": response.text}


def get_payload(path):
    """
    Return the JSON representation of a task. This can be passed into the `create_task` method as the payload when creating new tasks.

    Args:
        path (str): relative or absolute path to payload

    Returns:
        JSON: representation of task

    """
    return json.load(open(path))
