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
   query-execution time.
3. Queries should be performed asynchronously for performance.
4. Query results should be cached per dashboard page-view for performance.
5. Queries should have their performance metrics (time, data use) recorded.

### Dashboard system
1. Each dashboard page should be built around a dataset of queries setup
   when the page is first viewed.

## Planning

I'll start by setting up a basic Dash dashboard system with a BigQuery link
and build from there.
