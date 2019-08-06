from jira_api import get_all_tasks
from jira_api import flatten_dict
import pandas as pd
import numpy as np
import datetime
import json
import yaml
import urllib3
import os
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# load JIRA username and password
jira_creds = yaml.load(open('./user_dev.yml'))
username = jira_creds['user']['name']
password = jira_creds['user']['password']

# point to JIRA development environment
# url = 'https://10.221.100.4'

# point to JIRA production environment
url = 'https://jira.emdeon.net'


def main():
  """
  Get the status of all Epics in the Artificial Intelligence Project.

  Persist all project status to s3 for reporting downstream.
  """
  all_tasks = get_all_tasks(url,
                            username,
                            password,
                            "AI",
                            start_at=0,
                            max_results=100)

  # pipe issues to txt
  now = datetime.datetime.now()
  today = now.strftime("%Y-%m-%d")

  # persist results to ./ml_engagements
  if not os.path.exists('./status_report'):
    os.makedirs('./status_report')

  with open(
          './status_report/raw/%s.txt' % str(today), 'w') as outfile:
    json.dump(all_tasks, outfile)

  df = pd.DataFrame.from_dict(all_tasks['issues'])

  # flatten all issues
  explode_issues = pd.DataFrame.from_dict(
      list(map(lambda x: flatten_dict(x), df['fields'])))

  field_mapping = json.load(open('./scripts/chc_jira_prod_fields.json'))

  # find and replace customfields with field names
  for i in np.arange(0, len(field_mapping)):
    explode_issues.columns = explode_issues.columns.str.replace(
        dict(field_mapping[i])['id'],
        dict(field_mapping[i])['name'])

  # format column names to lower case w/o spaces
  explode_issues.columns = explode_issues.columns.str.lower().str.replace(' ', '_')

  # persist flattened issues to .csv
  explode_issues.reset_index().to_csv(
      '../status_report/flattened/tasks/%s.txt' % str(today),
      index=False)

  # kludgey update to extract and flatten sub-tasks

  def flatten(l):
    return flatten(l[0]) + (flatten(l[1:]) if len(l) > 1 else []) if type(l) is list else [l]

  def coalesce_dicts(list_of_dicts):
    if len(list_of_dicts) == 1:
      return flatten(list_of_dicts[0])
    if len(list_of_dicts) > 1:
      dict1 = list_of_dicts[0]
      for i in np.arange(1, len(list_of_dicts)):
        dict1 = dict(
            (k, flatten([dict1[k], list_of_dicts[i].get(k)])) for k in dict1)
    return dict1

  def explode_json(d):
    if d == []:
      return np.nan
    else:
      return list(map(lambda x: flatten_dict(x), d))

  def combine_json(l):
    if l is np.nan:
      return np.nan
    else:
      return pd.DataFrame.from_dict(coalesce_dicts(l))

  temp = list(map(lambda x: explode_json(x), explode_issues['sub-tasks']))

  temp_2 = pd.DataFrame(list(map(lambda x: combine_json(x), temp))).dropna()

  indices = []
  dfs = []

  for i in temp_2.index:
    indices.append(i)
    dfs.append(temp_2.loc[i, 0])

  temp_3 = pd.concat(dfs, axis=0, keys=indices)
  column_names = 'subtask_' + temp_3.columns

  temp_3.columns = column_names

  temp_3 = temp_3.reset_index().drop('level_1', axis=1)

  temp_3.columns = temp_3.columns.str.replace('level_0', 'index')

  # persist flattened issues to .csv
  temp_3.to_csv(
      '../status_report/flattened/sub_tasks/%s.txt' % str(today),
      index=False)


if __name__ == "__main__":
  main()
