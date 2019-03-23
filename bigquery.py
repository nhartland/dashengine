import os
import yaml
import time
import logging
import datetime
import pandas as pd
import pandas_gbq as gbq
from dataclasses import dataclass
import credentials

DIALECT = "standard"
QUERY_DATA_DIRECTORY = "queries"
CREDENTIALS, PROJECT_ID = credentials.fetch()

gbq.context.dialect = DIALECT
gbq.context.project = PROJECT_ID
gbq.context.credentials = CREDENTIALS


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
        result (pandas.DataFrame): The pandas DataFrame containing the result.
        time_duration  (datetime.time): The execution time of the query.
    """
    source:         BigQuery
    result:         pd.DataFrame
    time_duration:  datetime.time
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


def get(query_id: str) -> BigQueryResult:
    """ Retrieves data from BigQuery according to a query id.

    This function reads a query from file, according to the provided id, and
    executes it in Google BigQuery. The result is returned as a
    `BigQueryResult`. The query id specifies the filename of the query under
    the `bqueries` subfolder.

    Args:
        query_id (str): A string identifier for the query.

    Returns:
        (BigQueryResult): The results of the query.
    """
    query = load_query(query_id)
    starttime = time.time()
    query_result = gbq.read_gbq(query.body)
    query_time = time.time() - starttime
    bqr = BigQueryResult(query, query_result, query_time)
    return bqr
