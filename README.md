# Skeleton Dash App on Google App Engine

## Aims
I want to have a basic skeleton of an App Engine dashboard, querying data from
BigQuery in a maintainable fashion. I should be able to fork this repository to
create new dashboards in the future. This repository should have several
principle features:

### Deployment
1. Should be deployable to a GAE python3 standard environment.
2. Deployment of new versions should be automated via cloud-build triggers.
3. (Maybe) ```TerraForm``` could be used to quickly setup a new project.

### Querying system
1. Queries are stored and versioned independently of the overall code.
2. Queries should be parametrisable, there should be a system for replacing tags
   such as ```{%param_name%}``` with a user-supplied parameter at
   query-execution time. Either that or through the use of BQ [Parameterized
   Queries](https://cloud.google.com/bigquery/docs/parameterized-queries),
   although those do not support table or column names as parameters.
   Potentially we should only allow {PROJECT_NAME} as a parameter outside of BQ
   standard queries for security reasons.
3. Queries should be performed asynchronously for performance.
4. Query results should be cached per dashboard page-view for performance.
5. Queries should have their performance metrics (time, data use) recorded.

### Dashboard system
1. Each dashboard page should be built around a dataset of queries setup
   when the page is first viewed.
2. There should be a `meta` dashboard for each page, giving the time cost of
   each query.

### Credentials

Are obtained through `google.auth.default`.

For how to set these credentials when working locally with a project, [see the
documentation
here](https://google-auth.readthedocs.io/en/latest/reference/google.auth.html).

## Planning

I'll start by setting up a basic Dash dashboard system with a BigQuery link
and build from there.

### TODO

1. Setup parametrisable queries
2. Fix the met-demo callback not running at start (may be that the callback is
   attatched before a layout?, see the exception supression in dashapp)
3. 'Refresh' data button
4. Setup a nice navigation bar e.g from dash-bootstrap-components, but one
   that plays well with AppEngine.
5. Use tinyDB for memory caching
   (https://www.reddit.com/r/googlecloud/comments/bl4rrr/gae_python_3_tinydb_for_memcache/)
