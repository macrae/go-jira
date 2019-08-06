# JIRA Task Loader for ML Engagements

This project creates JIRA tasks programmatically via RESTful API. The tasks created are specific to Machine Learning (ML) engagements and follow the [CRISP-DM](https://ops.emdeon.net/display/AI/CRISP-DM+Guide) data mining workflow.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing. See "Using the Project" below for notes on how to use the project in a live environment.

### Prerequisites

Python3 is required to run this application. The list of third-party dependencies can be found in the `requirements.txt` file.

### Installing

Create a Python3 virtual environment.

```
python3 -m venv .venv
```

If you get an error saying "returned non-zero exit status 1",
make sure you have Python3 and pip3 upgraded to the current version and
if that doesn't work, re-run the above command as:

```
python3 -m venv --without-pip .venv
```

Activate the virtual environemnt

```
source .venv/bin/activate
```

Install the third-party dependencies.

```
pip3 install -r requirements.txt
```

Create a `user.yml` with your JIRA username and password. Since we don't want to share login credentials we ignore `*.yml` files.

```
user:
    name: JIRA username
    password: JIRA password
```

To verify RESTful authentication you can run this in a terminal window replacing `username:password` with the contents of `user.yml` and replacing `taskId-taskKey` with a task id and key, for example `AI-446`.

```
curl \
  -u username:password \
  -X GET \
  -H "Content-Type: application/json" \
  https://jira.emdeon.net/rest/api/2/issue/taskId-taskKey
```

If authentication is successful you will receive a JSON response, such as:

```
{"expand":"renderedFields,names,schema,transitions,operations,editmeta,changelog","id":"253378","self":"https://jira.emdeon.net/rest/api/2/issue/253378","key":"AI-446","fields":{"issuetype":... etc...
```

## Running the tests

We are using [pytest](https://docs.pytest.org/en/2.9.1/getting-started.html) for test writing. Run this snippet in a terminal window to run the tests - you need to be in the root `./jira-api`.

```
pytest -vv
```

You can also run the test suite with a coverage report. Although it may not be possible to achieve 100% coverage - nor does 100% coverage ensure a well written test suite - it is still a useful heuristic in assessing overall application health.

```
pytest --cov-report html --cov functions --verbose
```

After running the coverage report, open the summary in your browser with the following.

```
open htmlcov/index.html
```

### Break down into end to end tests

...

```
test_get_task() # authenticates and gets task status
```

### And coding style tests

Check for PEP8 style guide adherence.

```
test_pep8(self)
```

## Using the Project

When you run `run_application.sh` all of the Tasks captured in the `./tasks` directory (each task is a `json` file) will be created in JIRA. Each Task is linked to the same Epic which is defined in the `./tasks` directory root (and called `epic.json`).

An Epic Name correspondes with an ML engagement (for example "Altegra Highcost") and Task Labels are used for tracking lead time and cycle time of an engagement. Engagement reporting may soon be available in [eazyBI](https://jira.emdeon.net/plugins/servlet/eazybi/home) until a fully fledged metric monitoring system is in place.

You may need to add read/write/execute modes to `run_application.sh`. Use this this snippet, then simply run `./run_application.sh` in your terminal.

```
sudo chmod +rwx ./run_application.sh
```

Arguments are parsed from the `run_application.sh` file and contain definitions for the Epic Name, Epic Summary, Epic Descrption and Reporter. Make sure these are updated for your project prior to running the application.

## Built With

* [JIRA REST API](https://developer.atlassian.com/jiradev/jira-apis) - Web service
* [Python3 venv](https://docs.python.org/3/library/venv.html) - Dependency Management

## Contributing

Please read [CONTRIBUTING.md](https://gitlab.healthcareit.net/smacrae/jira-api/blob/master/CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

Describe how we version here.

## Authors

* **Sean MacRae** - *Initial work* - [smacrae](https://gitlab.healthcareit.net/smacrae)

* **Nick Gaylord** - *On-boarding and more* - [ngaylord](https://gitlab.healthcareit.net/ngaylord)

See also the list of [contributors](https://gitlab.healthcareit.net/smacrae/jira-api/graphs/master) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

Tip of the hat to [Nick Gaylord](https://gitlab.healthcareit.net/ngaylord) for his creativity and help naming this project.
