import time
import requests

EPMC_REST_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest"
EPMC_SEARCH_URL = "/".join([EPMC_REST_URL, "search"])


def request_retryer(request_function, num_retries, **kwargs):
    for i in range(0, num_retries):
        try:
            return request_function(**kwargs)
        except Exception:
            print("  retrying")
            time.sleep(0.5)


def epmc_idlist_search(query=None, cursormark="*"):
    params = {
        "query": "PMCID",
        "format": "json",
        "resultType": "idlist",
        "cursorMark": cursormark
    }
    response = requests.get(EPMC_SEARCH_URL, params=params)

    try:
        response_json = response.json()
        results = response_json["resultList"]
        next_cursormark = response_json["nextCursorMark"]
    except (KeyError, IndexError):
        print("Query: {} returned no results".format(query))
        return {}
    return next_cursormark, results


if __name__ == '__main__':

    query = '(TITLE:"ebola")'
    #query = '(GRANT_AGENCY:"Wellcome Trust")'
    print(request_retryer(epmc_idlist_search, 10, query=query, cursormark="*"))
