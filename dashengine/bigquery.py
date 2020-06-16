import os
import uuid
import json
import logging
import datetime
import google.auth
import pandas as pd
from ruamel.yaml import YAML
from dataclasses import dataclass
from google.cloud import bigquery
from dashengine.dashapp import cache

# BigQuery
DIALECT = "standard"
QUERY_DATA_DIRECTORY = "queries"
CREDENTIALS, PROJECT_ID = google.auth.default()

# YAML parser
yaml = YAML(typ="safe")


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

    query_id: str
    name: str
    description: str
    body: str
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

    uuid: str
    source: BigQuery
    parameters: dict
    result: pd.DataFrame
    time: datetime.time
    duration: datetime.time
    bytes_billed: float
    bytes_processed: float

    def memory_usage(self) -> float:
        """ Returns the memory usage of the stored dataframe in MB. """
        return self.result.memory_usage(index=True, deep=True).sum() / 1.0e6


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
    target_queryfile = os.path.join(QUERY_DATA_DIRECTORY, query_id + ".yml")

    with open(target_queryfile, "r") as infile:
        try:
            qdata = yaml.load(infile)
            # Build query object
            query_object = BigQuery(
                query_id,
                qdata["name"],
                qdata["description"],
                qdata["body"],
                qdata.get("parameters", []),
            )
            return query_object

        # TODO figure out better error handling scheme
        except yaml.YAMLError as exc:
            logger.error(exc)
            raise exc


def fetch_num_cached_queries() -> int:
    """ Lists all cached queries.

        Returns:
            (list): A list of all cached queries in the form of BigQueryResult objects.
    """
    # Fetch registry of queries
    registry = cache.get("query-registry")
    if registry is None:
        return 0
    return len(registry)


def fetch_cached_queries() -> list:
    """ Lists all cached queries.

        Returns:
            (list): A list of all cached queries in the form of BigQueryResult objects.
    """
    # Fetch registry of queries
    registry = cache.get("query-registry")
    if registry is None:
        return []
    cached_queries = []
    for query in registry.values():
        result = run_query(query["query_id"], query["parameters"])
        cached_queries.append(result)
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
                raise RuntimeError(
                    f"Query '{query.name}' expects parameter '{pname}' to be a list"
                )
            bqparam = bigquery.ArrayQueryParameter(pname, ptype, parameters[pname])
        query_params.append(bqparam)
    return query_params


def _register_query(query_id: str, parameters: dict):
    """ Add a query and it's parameters to the query registry.

        Note that this is not thread-safe: The registry is meant
        for debug purposes and therefore should normally only be
        run in a single-threaded debug server.
    """
    registry_key = query_id + ":" + json.dumps(parameters, sort_keys=True, default=str)
    registry = cache.get("query-registry")
    if registry is None:
        registry = {}
    registry[registry_key] = {"query_id": query_id, "parameters": parameters}
    cache.set("query-registry", registry)


@cache.memoize(timeout=300)
def run_query(query_id: str, parameters: dict = {}) -> BigQueryResult:
    """ Performs a query over BigQuery and returns the result.

    This function reads a query from file, according to the provided id, and
    executes it in Google BigQuery. The result is returned as a
    `BigQueryResult`. The query id specifies the filename of the query under
    the `queries` subfolder. If the query has parameters, these may be passed
    as elements of a dictionary via the `parameters` argument.

    Args:
        query_id (str): A string identifier for the query.
        parameters (dict) (optional): An optional dictionary of query parameters.

    Returns:
        (BigQueryResult): The results of the query.
    """
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

    # Register the query in the cache (for the profiler)
    _register_query(query_id, parameters)

    # Form up results class
    return BigQueryResult(
        str(uuid.uuid4()),
        query,
        parameters,
        query_data,
        query_result.ended,
        (query_result.ended - query_result.started).microseconds / 1.0e6,
        query_result.total_bytes_billed,
        query_result.total_bytes_processed,
    )
