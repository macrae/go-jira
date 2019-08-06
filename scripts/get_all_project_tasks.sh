curl --insecure\
  -u userame:password \
  -X GET \
  -H "Content-Type: application/json" \
  https://jira.emdeon.net/rest/api/2/search?jql=project="AI"&startAt="100"&maxResults="100"
