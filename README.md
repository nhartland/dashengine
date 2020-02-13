# Dash quickstart framework for Google Cloud Platform

![Build](https://github.com/nhartland/dashengine/workflows/Cloud%20Run%20Deployment/badge.svg)

Dashengine provides boilerplate code for quickly setting up [Plotly
Dash](https://plot.ly/dash/) applications on the [Google Cloud
Platform](https://cloud.google.com/).

Such boilerplate includes:
 - A mechanism for automatically loading and indexing new pages from a `pages` directory.
 - A simple API for running standard and parametrised queries against [BigQuery](https://cloud.google.com/bigquery).
 - A caching mechanism for the BigQuery results.
 - A standard profiling page where cached queries can be analysed.
 - GitHub actions workflow for deployment to Google Cloud Run.

## Quickstart

[![Run on Google Cloud](https://deploy.cloud.run/button.svg)](https://deploy.cloud.run)

See the `demo` subdirectory for an example of a complete Dashengine
application including multiple pages, (parametrised) queries and profiling.

## Deployment

Originally Dashengine was developed with Google App Engine (GAE) in mind
(hence the name) although deploying on Google Cloud Run may provide a better
fit. The core of the project is provided by a Docker container (built by the
root Dockerfile) and should be extended with application pages. The resulting
container can be naturally be deployed to any infrastructure that supports
containers, but Dashengine assumes that default GCP authentication is
available.

This repository is automatically deployed to Cloud Run via GitHub Actions.

#### Local build and deploy

To build the container image:

```shell
docker build . -t dashengine
```

Which can take some time (in building the various python dependencies). To run
the container for local testing:

```
docker run -p 8050:8050 -v "/Users/<username>/.config:/root/.config" dashengine
```

where the path `/Users/<username>/.config` points to the config directory used
by Google's default authentication credentials.

## Architecture

### Dashboard page system

Dashboard pages are loaded automatically from the `pages` directory, which is
provided by the container extending Dashengine. For examples see the `demo`
directory. If no `pages` directory is provided, the demo application is used.


### Querying system

A core part of the Dashengine infrastructure is the querying system. It has a
number of features.

1. Queries are stored and versioned independently of the overall code.
2. Queries are parametrisable, through the use of BQ [Parameterized
   Queries](https://cloud.google.com/bigquery/docs/parameterized-queries).
   Parametrisation at the level of projects will not be supported, however
   query scopes can be restricted to project level simply by not including
   a project ID in the query. This can be useful in the case of multiple project
   environments (DEV, PROD).
3. Queries can be performed asynchronously for performance.
4. Query results can be cached per dashboard page-view for performance.
5. Queries have their performance metrics (time, data use) recorded for analysis.


### Query caching

Query results are cached via
[flask-caching](https://flask-caching.readthedocs.io/). Note that the default
in-memory caching means the developer must be careful about memory usage to fit
into application memory limits. The general principle being that any
heavy lifting should be done in the SQL queries rather than on the application
instance.  Furthermore this caching, being in-instance-memory, is not preserved
across instances. This can be easily modified by using an external cache e.g
Redis, for which support is built-in.

### Profiler

The query profiler provides summary information on the performance of cached
queries.  The profiler can work (although maybe not perfectly) even in a
multi-threaded environment and even with a simple (in-memory) cache. Queries are
referenced in the profiler by a query ID string and parameters only. Therefore
if in any given thread the query has not been cached, the thread is able to
re-run the query to display profiling information.


### Credentials

Are obtained through `google.auth.default`.

For how to set these credentials when working locally with a project, [see the
documentation
here](https://google-auth.readthedocs.io/en/latest/reference/google.auth.html).

