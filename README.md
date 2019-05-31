# Skeleton Dash App on Google App Engine

## Aims
I want to have a basic skeleton of an App Engine dashboard, querying data from
BigQuery in a maintainable fashion. I should be able to fork this repository to
create new dashboards in the future. This repository should have several
principle features:

### Deployment
1. Should be deployable to a GAE python3 standard environment.
2. Deployment of new versions should be automated via cloud-build triggers.

### Querying system
1. Queries are stored and versioned independently of the overall code.
2. Queries should be parametrisable, through the use of BQ [Parameterized
   Queries](https://cloud.google.com/bigquery/docs/parameterized-queries).
   Parametrisation at the level of projects will not be supported, however
   query scopes can be restricted to project level simply by not including
   a project ID in the query. This can be useful in the case of multiple project
   environments (DEV, PROD).
3. Queries should be performed asynchronously for performance.
4. Query results should be cached per dashboard page-view for performance.
5. Queries should have their performance metrics (time, data use) recorded.


### Dashboard system
1. Each dashboard page should be built around a dataset of queries setup
   when the page is first viewed.
2. There should be a `profiling` dashboard available, giving the cost in time,
   local memory usage, and bytes processed in BigQuery. 

### Query caching
Query results are cached in memory via
[TinyDB](https://tinydb.readthedocs.io/en/latest/). Note that this means the
developer must be careful about memory usage to fit into GAE standard memory
limits. The general principle being that any heavy-lifting should be done in the
SQL queries rather than on the GAE instance. Furthermore this caching, being
in-memory through TinyDB, is not preserved across instances.

To keep memory usage down, caching is performed only at the level of BigQuery
results. To allow for the straightforward filtering of results in the cache in
the case of parametrised queries, TinyDB is used rather than Flask caching.

### Credentials

Are obtained through `google.auth.default`.

For how to set these credentials when working locally with a project, [see the
documentation
here](https://google-auth.readthedocs.io/en/latest/reference/google.auth.html).

### TODO

1. Fix the met-demo callback not running at start (may be that the callback is
   attached before a layout?, see the exception suppression in dashapp)
2. 'Refresh' data button
3. Final documentation, quickstart, skeleton page, etc
4. Investigate errors in profiling page
