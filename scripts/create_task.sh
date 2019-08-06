curl -D- --insecure\
 -u userame:password \
 -X POST \
 --data @./some_task.json \
 -H "Content-Type: application/json" \
 https://jira-dev.emdeon.net/rest/api/2/issue/
