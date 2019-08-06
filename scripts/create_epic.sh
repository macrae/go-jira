curl -D- --insecure\
 -u username:password \
 -X POST \
 --data @../tasks/epic.json \
 -H "Content-Type: application/json" \
 https://jira-dev.emdeon.net/rest/api/2/issue/
