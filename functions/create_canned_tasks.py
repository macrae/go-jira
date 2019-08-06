from jira_api import get_directory_names
from jira_api import get_file_names
from jira_api import get_payload
from jira_api import create_task
import os
import sys
import json
import yaml
import argparse


# load JIRA username and password
jira_creds = yaml.load(open('./user_dev.yml'))
username = jira_creds['user']['name']
password = jira_creds['user']['password']


def main():
    """
    Programmatically create a set of canned JIRA tasks.

    ArgumentParser:
        epic_name:              the name of the epic label
        epic_summary:           a high-level description of the epic
        epic_description:       a detailed description of the epic
        reporter:               the ML engagement lead
        domain:                 the JIRA domain or server address
        task_directory:         the directory containing canned tasks
    """
    parser = argparse.ArgumentParser(
        description="create new set of ML engagement tasks")

    parser.add_argument(
        "--epic_name",
        required=True,
        help="epic name")

    parser.add_argument(
        "--epic_summary",
        required=True,
        help="human readable summary of ML engagement")

    parser.add_argument(
        "--epic_description",
        required=True,
        help="detailed description of ML engagement (be verbose)")

    parser.add_argument(
        "--reporter",
        required=True,
        help="the JIRA username of the ML engagement lead")

    parser.add_argument(
        "--domain",
        required=True,
        help="the domain name of the JIRA server")

    parser.add_argument(
        "--task_directory",
        required=True,
        help="the directory where the canned ML engagement tasks are housed")

    args = parser.parse_args()

    # instantiate server url and directory to canned JIRA tasks variables
    url = args.domain
    task_path = args.task_directory

    # get the epic template from the tasks root
    epic_payload = get_payload(path= task_path + '/epic.json')

    # update epic template with passed arguments
    epic_payload['fields']['customfield_10004'] = args.epic_name
    epic_payload['fields']['summary'] = args.epic_summary
    epic_payload['fields']['description'] = args.epic_description
    epic_payload['fields']['reporter']['name'] = args.reporter

    # create the epic
    epic = create_task(url, username, password, epic_payload)

    # persist epic key - unless the response failed, then throw an exception
    if (epic['status_code'] != 200) & (epic['status_code'] != 201):
        print(sys.stderr, "Could not create Epic")
        sys.exit(1)
    else:
        # persist epic id and key
        epic_key = json.loads(epic['response'])['key']
        epic_self = json.loads(epic['response'])['self']

    # create tasks
    dir_names = get_directory_names(task_path)
    dir_paths = list(map(lambda x:  task_path + '/' + x, dir_names))

    # TODO - rename this, since it's not *just* file names...
    file_names = list(map(lambda x: [x, get_file_names(x)], dir_paths))

    # TODO - refactor this; it's definitely not easy to reason about
    task_paths = []
    for i in range(0, len(file_names)):
        task_paths.append(
            ([file_names[i][0] + '/' + x for x in file_names[i][1]]))

    # flatten task_paths into single list
    task_paths = [item for sublist in task_paths for item in sublist]

    tasks = {}

    # TODO - refactor the hell out of this ugly mess...
    for path in task_paths:
        # get the CRISP-DM phase
        phase_name = os.path.dirname(path).split('/')[2]

        # check if the phase already exists in the tasks dict
        if phase_name not in tasks.keys():
            tasks[phase_name] = {}
        else:
            None

        task_name = os.path.basename(path).split('.')[0]
        tasks[phase_name][task_name] = {}
        tasks[phase_name][task_name]['payload'] = dict(get_payload(path))

        # update task template
        tasks[phase_name][task_name]['payload']['fields']['customfield_10001'] = epic_key
        tasks[phase_name][task_name]['payload']['fields']['reporter']['name'] = args.reporter

        # create task (in JIRA)
        task = create_task(
            url,
            username,
            password,
            tasks[phase_name][task_name]['payload'])

        # persist task id and key
        tasks[phase_name][task_name]['response'] = {}
        tasks[phase_name][task_name]['response']['id'] = \
            json.loads(task['response'])['id']
        tasks[phase_name][task_name]['response']['key'] = \
            json.loads(task['response'])['key']
        tasks[phase_name][task_name]['response']['self'] = \
            json.loads(task['response'])['self']

        # check is there exist subtasks for this task
        task_index = \
            os.path.basename(path).split('.')[0].split('_')[0]
        phase_subtasks = get_file_names(os.path.dirname(path) + '/sub_tasks')
        subtasks = sorted(
            list(filter(lambda x: x.startswith(task_index), phase_subtasks)))
        tasks[phase_name][task_name]['subtasks'] = {}

        for subtask in subtasks:
            subtask_name = subtasks[0].split('.')[0]
            subtask_path = os.path.dirname(path) + '/sub_tasks/' + subtask
            tasks[phase_name][task_name]['subtasks'][subtask_name] = {}
            tasks[phase_name][task_name]['subtasks'][subtask_name]['payload'] = dict(
                get_payload(subtask_path))

            # update task template
            task_key = tasks[phase_name][task_name]['response']['key']
            tasks[phase_name][task_name]['subtasks'][subtask_name]['payload']['fields']['parent']['key'] = task_key
            tasks[phase_name][task_name]['subtasks'][subtask_name]['payload']['fields']['reporter']['name'] = "smacrae"

            # create subtask (in JIRA)
            new_subtask = create_task(
                url,
                username,
                password,
                tasks[phase_name][task_name]['subtasks'][subtask_name]['payload'])

            # persist subtask id and key
            tasks[phase_name][task_name]['subtasks'][subtask_name]['response'] = {}
            tasks[phase_name][task_name]['subtasks'][subtask_name]['response']['id'] = json.loads(
                new_subtask['response'])['id']
            tasks[phase_name][task_name]['subtasks'][subtask_name]['response']['key'] = json.loads(
                new_subtask['response'])['key']
            tasks[phase_name][task_name]['subtasks'][subtask_name]['response']['self'] = json.loads(
                new_subtask['response'])['self']

    results = {'epic': epic_key, 'epic_self': epic_self, 'tasks': tasks}

    # persist results to ./ml_engagements
    if not os.path.exists('./ml_engagements'):
        os.makedirs('./ml_engagements')

    with open(
            './ml_engagements/%s_tasks.txt' % str('epic_name'), 'w') as outfile:
        json.dump(results, outfile)

    # print epic key to console
    # print('Epic\n%s\t%s' % (args.epic_name, epic_key))
    print(epic_key)

if __name__ == "__main__":
    main()
