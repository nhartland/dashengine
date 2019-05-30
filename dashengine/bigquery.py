import os
import yaml
import logging
import datetime
import google.auth
import pandas as pd
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage
from dataclasses import dataclass
from google.cloud import bigquery

# Create cache table in TinyDB: Note cache_size is set to zero
# here to disable caching of **TinyDB queries** not BigQuery ones.
CACHE_DB = TinyDB(storage=MemoryStorage)
CACHE_TABLE = CACHE_DB.table('dashengine-cache', cache_size=0)

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


#TODO Add BigQuery parameterised queries
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
    bytes_billed: float
    data_processed: float


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


def fetch_cached_queries() -> list:
    """ Lists all cached queries.

        Returns:
            (list): A list of all cached queries in the form of BigQueryResult objects.
    """
    cached_queries = []
    for query in CACHE_TABLE:
        cached_queries.append(query["result"])
    return cached_queries


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
    # Check cache for existing result
    cache_check = CACHE_TABLE.get(Query().query_id == query_id)
    if cache_check and cache_check["result"]:
        return cache_check["result"]

    # Setup BigQuery client
    client = bigquery.Client()
    # Read query
    query = load_query(query_id)
    # Run query
    query_result = client.query(query.body)
    query_data = query_result.to_dataframe()
    # Form up results class
    bqr = BigQueryResult(query,
                         query_data,
                         query_result.ended,
                         (query_result.ended - query_result.started).microseconds / 1.E6,
                         query_result.total_bytes_billed,
                         query_result.total_bytes_processed)

    # Insert result in cache
    CACHE_TABLE.insert({'query_id': query_id, 'result': bqr})
    return bqr
