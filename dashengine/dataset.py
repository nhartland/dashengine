""" This module handles the caching of query results for use across all app pages """
import concurrent.futures
import dashengine.bigquery as bq


class DataSet:
    def __init__(self):
        """ Initialises a dataset. """
        # A dictionary [query_id]: [query_result] that caches results.
        self.query_cache = {}
        # A list of requested query IDs. Queries are not actually
        # performed until a fetch() request, in this way we can fetch
        # all requested queries asynchronously.
        self.query_requests = []

    def update_query_cache(self):
        """ Update the query cache.

            This method runs over existing query reuqests in the queue and adds
            them to the local cache.
        """
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            jobs = {}
            # Form a dictionary of required jobs
            for qid in self.query_requests:
                if qid not in self.query_cache:
                    jobs[executor.submit(bq.run_query, qid)] = qid
            # Loop over job results
            for ds_job in concurrent.futures.as_completed(jobs):
                queryid = jobs[ds_job]
                try:
                    query_data = ds_job.result()
                    self.query_cache[queryid] = query_data
                except Exception as exc:
                    print('%r generated an exception: %s' % (queryid, exc))
        # Clear cache
        self.query_requests.clear()

    def prefetch(self, query_ids: list):
        """ Pre-register a list of queryIDs for use in the report.

            This function appends a provided list of query IDs to the
            queue for fetching. On the next call to fetch() all of these
            queries will be performed asynchronously.
        """
        self.query_requests.extend(query_ids)

    def fetch(self, query_id: str) -> bq.BigQueryResult:
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
        if query_id not in self.query_cache:
            self.query_requests.append(query_id)
            # Run async update over all the requests in the queue
            self.update_query_cache()
        return self.query_cache[query_id]

    # TODO should return an immutable view rather than the results themselves
    def list(self) -> dict:
        """ Returns the dictionary of cached queries."""
        self.update_query_cache()
        return self.query_cache

