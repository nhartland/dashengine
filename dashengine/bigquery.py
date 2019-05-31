import os
import yaml
import uuid
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
        query_id (str): The ID of the query.
        name (str): The name of the query.
        description (str): A short description of the query
        body (str): The query body itself.
        parameter_spec (dict): A dictionary of query parameter specifications keyed by name.
    """
    query_id:       str
    name:           str
    description:    str
    body:           str
    parameter_spec: dict


@dataclass(frozen=True)
class BigQueryResult:
    """ Results of a BigQuery request.

    This class stores the results returned from querying
    a BigQuery dataset, along with some metadata.

    Attributes:
        uuid (str): A unique identifying string for this result
        source (BigQuery): The query that generated this result.
        parameters (dict): The dictionary of parameters for this result.
        result (pandas.DataFrame): The pandas DataFrame containing the result.
        time   (datetime.time): The execution time of the query.
        duration (datetime.time): The time taken to execute the query.
        bytes_billed (float): The amount of billable bytes processed in BQ.
        bytes_processed (float): The total number of bytes processed in BQ.
    """
    uuid:       str
    source:     BigQuery
    parameters: dict
    result:     pd.DataFrame
    time:       datetime.time
    duration:   datetime.time
    bytes_billed: float
    bytes_processed: float

    def memory_usage(self) -> float:
        """ Returns the memory usage of the stored dataframe in MB. """
        return self.result.memory_usage(index=True, deep=True).sum() / 1.E6


def _load_query(query_id: str) -> BigQuery:
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
            # Build query object
            query_object = BigQuery(query_id,
                                    qdata["name"],
                                    qdata["description"],
                                    qdata["body"],
                                    qdata.get("parameters", []))
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


def _build_query_parameters(query: BigQuery, parameters: dict) -> list:
    """ Builds the parameter list for a BigQuery job from a supplied
        list of parameter values.

        Args:
            query (BigQuery): A query with parameter specification.
            parameters (dict): Corresponding dict of parameters and supplied values.

        Returns:
            (list) A list of BigQuery parameters.
    """
    # Build query parameters
    query_params = []
    for spec in query.parameter_spec:
        pname = spec["name"]
        ptype = spec["type"]
        if pname not in parameters:
            raise RuntimeError(f"Parameter '{pname}' unspecified in `run_query`")

        if spec["array_type"] is False:
            bqparam = bigquery.ScalarQueryParameter(pname, ptype, parameters[pname])
        else:
            if type(parameters[pname]) != list:
                raise RuntimeError(f"Query '{query.name}' expects parameter '{pname}' to be a list")
            bqparam = bigquery.ArrayQueryParameter(pname, ptype, parameters[pname])
        query_params.append(bqparam)
    return query_params


def run_query(query_id: str, parameters: dict = {}) -> BigQueryResult:
    """ Performs a query over BigQuery and returns the result.

    This function reads a query from file, according to the provided id, and
    executes it in Google BigQuery. The result is returned as a
    `BigQueryResult`. The query id specifies the filename of the query under
    the `bqueries` subfolder. If the query has parameters, these may be passed
    as elements of a dictionary via the `parameters` argument.

    Args:
        query_id (str): A string identifier for the query.
        parameters (dict) (optional): An optional dictionary of query parameters.

    Returns:
        (BigQueryResult): The results of the query.
    """
    logger = logging.getLogger(__name__)
    # Check cache for existing result with these parameters
    BQuery = Query()
    cache_check = CACHE_TABLE.get((BQuery.query_id == query_id) &
                                  (BQuery.parameters == parameters))
    # Returned cached value if present
    if cache_check and cache_check["result"]:
        result = cache_check["result"]
        params = cache_check["parameters"]
        logger.debug(f"Local cache hit: {query_id} {params}")
        return result

    # Setup BigQuery client
    client = bigquery.Client()
    # Read query
    query = _load_query(query_id)

    # Build job configuration
    job_config = bigquery.QueryJobConfig()
    job_config.query_parameters = _build_query_parameters(query, parameters)

    # Run query
    query_result = client.query(query.body, job_config=job_config)
    query_data = query_result.to_dataframe()

    # Form up results class
    bqr = BigQueryResult(str(uuid.uuid4()),
                         query,
                         parameters,
                         query_data,
                         query_result.ended,
                         (query_result.ended - query_result.started).microseconds / 1.E6,
                         query_result.total_bytes_billed,
                         query_result.total_bytes_processed)

    # Insert result in cache
    # Note upsert is used here to ensure no duplicates are added due to multiple thread execution
    CACHE_TABLE.upsert({'query_id': bqr.source.query_id,
                        'parameters': bqr.parameters,
                        'result': bqr},
                       (BQuery.query_id == query_id) & (BQuery.parameters == parameters))
    logger.debug(f"New cache entry: {bqr.uuid} {query_id} {parameters}")
    return bqr
