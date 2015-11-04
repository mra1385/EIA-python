EIA-python
======
A Python 2/3 wrapper for the Energy Information Agency (EIA) API. Designed to
return data formatted for easy loading into pandas DataFrame objects.

Installation
-----
```
pip install EIA_python.
```
Requires
-----
  * requests


EIA API
------------------------------
Please review EIA's [API documentation](http://www.eia.gov/beta/api/).


Authentication
-----

The EIA API uses an API key for authentication. Obtain an EIA API key by registering on
the [EIA website](http://www.eia.gov/beta/api/register.cfm).


Examples:
-----

The next two sections, titled "Series Search" and "Data Retrieval" contain 
examples of how to use the EIA-python module. The module is generally split into
"Series Search" methods, to help the user find the desired EIA data sets, and
"Data Retrieval" methods, to help the user actually acquire the data.

"Series Search" methods are wrappers around the EIA API for searching for series 
using category IDs (API Category Query), keywords (API Search Data Query - 
Keyword Search / Manipulate Rows Per Page) or dates last 
updated (API Search Data Query - Date Search). These methods help the user
find specific series or groups of series from within the EIA data set. The 
intention is that once the desired series are found using the "Series Search" 
methods (which may require a few runs and tweaks of search parameters), 
the actual data can then be queried using the "Data Retrieval" methods described 
below.

"Data Retrieval" methods are wrappers around the EIA API Series Query using 
category IDs, keywords, dates or series ID. The parameters are all the exact 
same as for the analogue "Series Search" methods, except for the "return_list"
parameter, which is NOT a parameter for the "Data Retrieval" methods.


Series Search:
-----

    import eia
    
    api_key = "YOUR_API-KEY"
    api = eia.API(api_key)
    
    ### Search By Keyword ###
    # set return_list to True if you only want a list of data series names.
    # filters_to_keep and filters_to_remove filter the search results, and 
    # keep or delete, respectively, search results which contain filtered words.
    keyword_search = api.search_by_keyword(keyword=['crude oil', 'price'],
                                           filters_to_keep=['AEO2015'],
                                           filters_to_remove=['high price'],
                                           rows=1000, 
                                           return_list=False)
    
    for key, value in keyword_search.items():
        print(key, value)


    ### Search By Category ID ###
    # set return_list to True if you only want a list of data series names
    category_search = api.search_by_category(category=2,
                                             filters_to_keep=['Alabama'],
                                             filters_to_remove=['quarterly'],
                                             return_list=False)
    
    for key, value in category_search.items():
        print(key, value)


    ### Search By Date Last Updated ###
    # set return_list to True if you only want a list of data series names
    date_search = api.search_by_date(date='2014-01-01T00:00:00Z TO 
                                           2015-01-01T23:59:59Z',
                                     filters_to_keep=['Arkansas'],
                                     filters_to_remove=['annual'],
                                     rows=1000, 
                                     return_list=True)
    
    for result in date_search:
        print(result)


Data Retrieval:
-----
     
    import eia
    import pandas as pd
    
    api_key = "YOUR_API-KEY"
    api = eia.API(api_key)
    
    ### Retrieve Data By Keyword ###
    keyword_search = api.data_by_keyword(keyword=['crude oil', 'price'],
                                         filters_to_keep=['brent'],
                                         filters_to_remove=['AEO2015'],
                                         rows=1000)
    
    for key,value in keyword_search.items():
        print(key,value)

    df = pd.DataFrame(keyword_search)

    ### Retrieve Data by Category ID ###
    category_search = api.data_by_keyword(category=2,
                                          filters_to_keep=['brent'],
                                          filters_to_remove=['AEO2015'])
    
    for key,value in category_search.items():
        print(key,value)

    df = pd.DataFrame(category_search)


    ### Retrieve Data By Date Last Updated ###
    date_search = api.data_by_date(date='2015-01-01T00:00:00Z 
                                              TO 2015-01-01T23:59:59Z',
                                   filters_to_keep=['brent'],
                                   filters_to_remove=['AEO2015'],
                                   rows=1000)

    for key,value in date_search.items():
        print(key,value)

    df = pd.DataFrame(date_search)


    ### Retrieve Data By Series ID ###
    series_search = api.data_by_series(series='ELEC.GEN.ALL-AL-99.A')
    
    for key,value in series_search.items():
        print(key,value)

    df = pd.DataFrame(series_search)


Submitting an Issue
-------------------
Please feel free to contact me if you discover a bug or have an idea for 
improved functionality.



Copyright
---------
Copyright (c) 2015, chart-it.blogspot.com. All rights reserved.
By contributing to EIA-python, you agree that your contributions will be licensed under its BSD license.
