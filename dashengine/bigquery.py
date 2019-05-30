import os
import yaml
import time
import logging
import datetime
import google.auth
import pandas as pd
from dataclasses import dataclass
from google.cloud import bigquery

DIALECT = "standard"
QUERY_DATA_DIRECTORY = "queries"
CREDENTIALS, PROJECT_ID = google.auth.default()


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
    # bytes billed: float # Would be nice
    # data_processed: float # Would be nice


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


def list_available_queries() -> list:
    """ Lists the available query IDs """
    queries = []
    for filename in os.listdir(QUERY_DATA_DIRECTORY):
        if filename.endswith(".yml"):
            splitnames = os.path.splitext(filename)
            queries.append(splitnames[0])
    return queries


#TODO Somehow cache results without using FileSystem
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
    # Setup BigQuery client
    client = bigquery.Client()
    # Read query
    query = load_query(query_id)
    starttime = time.time()
    query_result = client.query(query.body).to_dataframe()
    query_time = time.time()
    query_duration = query_time - starttime

    # Form up results class
    bqr = BigQueryResult(query,
                         query_result,
                         query_time,
                         query_duration)
    return bqr
