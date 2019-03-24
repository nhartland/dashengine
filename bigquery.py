import os
import yaml
import time
import logging
import datetime
import pandas as pd
import pandas_gbq as gbq
from dataclasses import dataclass
import concurrent.futures
import credentials

DIALECT = "standard"
QUERY_DATA_DIRECTORY = "queries"
CREDENTIALS, PROJECT_ID = credentials.fetch()

gbq.context.dialect = DIALECT
gbq.context.project = PROJECT_ID
gbq.context.credentials = CREDENTIALS

# Basic caching of queries by ID in a dictionary
# Requests for datasets are pushed to QUERY_REQUESTS,
# then a call to update_cache moves them into QUERY_CACHE
QUERY_REQUESTS = []
QUERY_CACHE = {}


@dataclass(frozen=True)
class BigQuery:
    """ A BigQuery query message.

    This class contains the name, description and body of a query intended for
    BigQuery.

    Attributes:
        name (str): The name of the query.
        description (str): A short description of the query
        body (str): The query body itself.
    """
    name:         str
    description:  str
    body:         str


#TODO add query parameters, should be able to do {%param_name%} in the query body
# and have this replaced at query time.
@dataclass(frozen=True)
class BigQueryResult:
    """ Results of a BigQuery request.

    This class stores the results returned from querying
    a BigQuery dataset, along with some metadata.

    Attributes:
        source (BigQuery): The query that generated this result.
        result (pandas.DataFrame): The pandas DataFrame containing the result.
        time   (datetime.time): The execution time of the query.
        duration (datetime.time): The time taken to execute the query.
    """
    source:   BigQuery
    result:   pd.DataFrame
    time:     datetime.time
    duration: datetime.time
    # bytes billed: float # Would be nice, probably needs modification of pandas_gbq
    # data_processed: float # Would be nice, probably needs modification of pandas_gbq


def load_query(query_id: str) -> BigQuery:
    """ Loads a query from file by query id.
    This function reads a query from file, according to the provided id, and
    returns it as a BigQuery object.

    Args:
        query_id (str): A string identifier for the query.

    Returns:
        (BigQuery): The query and query metadata.
    """
    logger = logging.getLogger(__name__)
    target_queryfile = os.path.join(QUERY_DATA_DIRECTORY, query_id + '.yml')

    with open(target_queryfile, 'r') as infile:
        try:
            qdata = yaml.safe_load(infile)
            query_object = BigQuery(qdata["name"], qdata["description"], qdata["body"])
            return query_object

        #TODO figure out better error handling scheme
        except yaml.YAMLError as exc:
            logger.error(exc)
            raise exc


def project_id() -> str:
    """ Returns the ID of the GCP project used for accessing BigQuery."""
    return PROJECT_ID


def run_query(query_id: str) -> BigQueryResult:
    """ Performs a query over BigQuery and returns the result.

    This function reads a query from file, according to the provided id, and
    executes it in Google BigQuery. The result is returned as a
    `BigQueryResult`. The query id specifies the filename of the query under
    the `bqueries` subfolder.

    Args:
        query_id (str): A string identifier for the query.

    Returns:
        (BigQueryResult): The results of the query.
    """
    #TODO get the query time from the BQ metadata itself rather than timing
    query = load_query(query_id)
    starttime = time.time()
    query_result = gbq.read_gbq(query.body)
    query_time = time.time()
    query_duration = query_time - starttime

    # Form up results class
    bqr = BigQueryResult(query,
                         query_result,
                         query_time,
                         query_duration)
    return bqr


def update_query_cache():
    """ Update the query cache.

        This method runs over existing query reuqests in the queue and adds
        them to the local cache.
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        jobs = {}
        # Form a dictionary of required jobs
        for qid in QUERY_REQUESTS:
            if qid not in QUERY_CACHE:
                jobs[executor.submit(run_query, qid)] = qid
        # Loop over job results
        for ds_job in concurrent.futures.as_completed(jobs):
            queryid = jobs[ds_job]
            try:
                query_data = ds_job.result()
                QUERY_CACHE[queryid] = query_data
            except Exception as exc:
                print('%r generated an exception: %s' % (queryid, exc))
    # Clear cache
    QUERY_REQUESTS.clear()


def prefetch(query_ids: list):
    """ Pre-register a list of queryIDs for use in the report.

        This function appends a provided list of query IDs to the
        queue for fetching. On the next call to fetch() all of these
        queries will be performed asynchronously.
    """
    QUERY_REQUESTS.extend(query_ids)


def fetch(query_id: str) -> BigQueryResult:
    """ Retrieves data from the local BigQuery results cache.

    This checks the provided query ID against a local query results cache, if
    the result is already present it returns the existing result. If the result
    is not present the cache is updated. In either case a query result is
    returned.

    Args:
        query_id (str): A string identifier for the query.

    Returns:
        (BigQueryResult): The results of the query.
    """
    # Check for query in cache: should also add a cache expiry here
    #TODO add cache expiry, force-refresh options
    if query_id not in QUERY_CACHE:
        QUERY_REQUESTS.append(query_id)
        # Run async update over all the requests in the queue
        update_query_cache()
    return QUERY_CACHE[query_id]


# TODO should return an immutable view rather than the results themselves
def list() -> dict:
    """ Returns the dictionary of cached queries."""
    return QUERY_CACHE

