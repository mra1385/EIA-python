import requests


# global variable for default row count parameter
glob_row = 100

# global variables with error messages from eia API
glob_invalid_series_id = 'invalid series_id. For key registration, ' \
                         'documentation, and examples see ' \
                         'http://www.eia.gov/developer/'

glob_invalid_api_key = 'invalid or missing api_key. For key registration, ' \
                       'documentation, and examples see ' \
                       'http://www.eia.gov/developer/'


class APIKeyError(Exception):
    pass


class NoResultsError(Exception):
    pass


class BroadCategory(Exception):
    pass


class DateFormatError(Exception):
    pass


class InvalidSeries(Exception):
    pass


class UndefinedError(Exception):
    pass


class API(object):
    def __init__(self, token):
        """
        Initialise the eia object:
        :param token: string
        :return: eia object
        """
        self.token = token

    @staticmethod
    def _filter_categories(d, filters_to_keep, filters_to_remove):
        """
        Filters a dictionary based on certain keywords.
        :param d: dictionary
        :param filters_to_keep: list or string
        :param filters_to_remove: list or string
        :return: filtered dictionary
        """
        filtered_dict = dict(d)
        if filters_to_keep is not None:
            if isinstance(filters_to_keep, str):
                filters_to_keep = filters_to_keep.split()
            for word in filters_to_keep:
                for key, values in d.items():
                    if str(key).lower().find(word.lower()) == -1 \
                            and str(values).lower().find(word.lower()) == -1:
                        try:
                            del filtered_dict[key]
                        except KeyError:
                            continue
                    else:
                        continue

        if filters_to_remove is not None:
            if isinstance(filters_to_remove, str):
                filters_to_remove = filters_to_remove.split()
            for word in filters_to_remove:
                for key, values in d.items():
                    if (str(key).lower().find(word.lower()) != -1) \
                            or (str(values).lower().find(word.lower()) != -1):
                        try:
                            del filtered_dict[key]
                        except KeyError:
                            continue
                    else:
                        continue
        return filtered_dict

    def search_by_category(self,
                           category=None,
                           filters_to_keep=None,
                           filters_to_remove=None,
                           return_list=False):
        """
        API Category Query
        :param filters_to_keep: sting or int or list of strings or ints
        :param filters_to_keep: list or string
        :param filters_to_remove: list or string
        :param return_list: boolean
        :return: If return_list is false, returns a dictionary of search results
        (name, units, frequency, and series ID) based on category_id.
        If return_list is true, returns a list of search results (name, only).
        """
        search_url = 'http://api.eia.gov/category/?api_key={}&category_id={}'
        categories_dict = {}
        search = requests.get(search_url.format(self.token, category))
        if search.json().get('data') \
                and search.json().get('data').get('error') == \
                glob_invalid_api_key:
            error_msg = search.json()['data']['error']
            raise APIKeyError(error_msg)

        elif (search.json().get('category')) and \
                (search.json().get('category').get('childseries')):
            for k in search.json()['category']['childseries']:
                categories_dict[k['name']] = {}
                categories_dict[k['name']]['Units'] = k['units']
                categories_dict[k['name']]['Frequency'] = k['f']
                categories_dict[k['name']]['Series ID'] = k['series_id']
            if filters_to_keep is not None or filters_to_remove is not None:
                categories_dict = self._filter_categories(categories_dict,
                                                          filters_to_keep,
                                                          filters_to_remove)

        elif search.json().get('data') and \
                search.json().get('data').get('error') == 'No result found.':
            raise NoResultsError("No Result Found. Try A Different Category ID")

        elif search.json().get('category') and \
                search.json().get('category').get('childcategories') and \
                not search.json().get('category').get('childseries'):
            raise BroadCategory("Category ID is Too Broad. Try Narrowing "
                                "Your Search with a Child Category.")

        if return_list:
            return list(categories_dict.keys())

        else:
            return categories_dict

    def search_by_keyword(self,
                          keyword=None,
                          filters_to_keep=None,
                          filters_to_remove=None,
                          rows=glob_row,
                          return_list=False):
        """
        API Search Data Query - Keyword
        :param keyword: list or string
        :param filters_to_keep: list or string
        :param filters_to_remove: list or string
        :param rows: string
        :param return_list: boolean
        :return: If return_list is false, returns a dictionary of search results
        (name, units, frequency, and series ID) based on keyword.
        If return_list is true, returns a list of search results (name, only).
        """
        if isinstance(keyword, list) == list: keyword = '+'.join(keyword)
        search_url = 'http://api.eia.gov/search/?search_term=name&' \
                     'search_value="{}"&rows_per_page={}'
        categories_dict = {}
        search = requests.get(search_url.format(keyword, rows))

        if (search.json().get('response')) and \
                (search.json().get('response').get('docs')):
            for k in search.json()['response']['docs']:
                categories_dict[k['name'][0]] = {}
                categories_dict[k['name'][0]]['Units'] = k['units']
                categories_dict[k['name'][0]]['Frequency'] = k['frequency']
                categories_dict[k['name'][0]]['Series ID'] = k['series_id']
            if filters_to_keep is not None or filters_to_remove is not None:
                categories_dict = self._filter_categories(categories_dict,
                                                          filters_to_keep,
                                                          filters_to_remove)

        elif (search.json().get('response')) and \
                (not search.json()['response']['docs']):
            raise NoResultsError('No Results Found')

        if return_list:
            return list(categories_dict.keys())

        else:
            return categories_dict

    def search_by_date(self,
                       date,
                       filters_to_keep=None,
                       filters_to_remove=None,
                       rows=glob_row,
                       return_list=False):
        """
        API Search Data Query - Date Search
        :param date: string
        :param filters_to_keep: string or list
        :param filters_to_remove: string or list
        :param rows: string
        :param return_list: boolean
        :return: If return_list is false, returns a dictionary of search results
        (name, units, frequency, and series ID) based on last update date.
        If return_list is true, returns a list of search results (name, only).
        """
        search_url = 'http://api.eia.gov/search/?search_term=last_updated&' \
                     'search_value=[{}]&rows_per_page={}'
        categories_dict = {}
        search = requests.get(search_url.format(date, rows))
        if (search.json().get('response')) and \
                (search.json().get('response').get('docs')):

            for k in search.json()['response']['docs']:
                categories_dict[k['name'][0]] = {}
                categories_dict[k['name'][0]]['Units'] = k['units']
                categories_dict[k['name'][0]]['Frequency'] = k['frequency']
                categories_dict[k['name'][0]]['Series ID'] = k['series_id']

            if filters_to_keep is not None or filters_to_remove is not None:
                categories_dict = self._filter_categories(categories_dict,
                                                          filters_to_keep,
                                                          filters_to_remove)
            if return_list:
                return list(categories_dict.keys())

            else:
                return categories_dict

        elif search.json().get('error') == 'solr connection failed.':
            raise DateFormatError("Connection Failed. Check date format. "
                                  "Date should be in the following format:"
                                  "'2014-01-01T00:00:00Z TO "
                                  "2015-01-01T23:59:59Z'")

        elif not search.json().get('response').get('docs'):
            raise NoResultsError('No Results Found')

    def data_by_category(self,
                         category,
                         filters_to_keep=None,
                         filters_to_remove=None):
        """
        API Category Query
        :param category: string or list
        :param filters_to_keep: sting or int or list of strings or ints
        :param filters_to_remove: string or list
        :return: Returns eia data series in dictionary form
        (name, units, frequency, and series ID) based on category ID.
        """
        categories_dict = self.search_by_category(category,
                                                  filters_to_keep,
                                                  filters_to_remove)
        url_data = 'http://api.eia.gov/series/?series_id={}&api_key={}&out=json'
        values_dict = {}
        if categories_dict is not None:
            for series_id in categories_dict.keys():
                search = requests.get(url_data.format(
                    categories_dict[series_id]['Series ID'],
                    self.token))

                if search.json().get('data') and \
                        search.json().get('data').get('error') == \
                        glob_invalid_series_id:
                    values_dict[series_id +
                                " (" +
                                categories_dict[series_id]['Units'] +
                                ") "] =\
                        "No Data Available"

                else:
                    lst_dates = [x[0][0:4] + " " + x[0][4:6] + " " + x[0][6:8]
                                 for x in search.json()['series'][0]['data']]
                    lst_values = [x[1] for x in
                                  search.json()['series'][0]['data']]
                    dates_values_dict = dict(zip(lst_dates, lst_values))
                    values_dict[search.json()['series'][0]['name'] +
                                " (" +
                                search.json()['series'][0]['units'] +
                                ")"] = \
                        dates_values_dict

            return values_dict

        else:
            raise NoResultsError('No Results Found')

    def data_by_keyword(self,
                        keyword,
                        filters_to_keep=None,
                        filters_to_remove=None,
                        rows=glob_row):
        """
        API Search Data Query - Keyword
        :param keyword: string
        :param filters_to_keep: string or list
        :param filters_to_remove: string or list
        :param rows: string
        :return: Returns eia data series in dictionary form
        (name, units, frequency, and series ID) based on keyword search.
        """
        categories_dict = self.search_by_keyword(keyword,
                                                 filters_to_keep,
                                                 filters_to_remove,
                                                 rows)

        url_data = 'http://api.eia.gov/series/?series_id={}&api_key={}&out=json'
        values_dict = {}

        if categories_dict is not None:
            for series_id in categories_dict.keys():
                search = requests.get(url_data.format(
                    categories_dict[series_id]['Series ID'],
                    self.token))
                if search.json().get('data') and \
                        search.json().get('data').get('error') == \
                        glob_invalid_api_key:
                    error_msg = search.json().get('data').get('error')
                    raise APIKeyError(error_msg)

                elif search.json().get('data') and \
                        search.json().get('data').get('error') == \
                        glob_invalid_series_id:
                    values_dict[series_id +
                                " (" +
                                categories_dict[series_id]['Units'] +
                                ") "] = \
                        "No Data Available"

                else:
                    lst_dates = [x[0][0:4] + " " + x[0][4:6] + " " + x[0][6:8]
                                 for x in search.json()['series'][0]['data']]
                    lst_values = [x[1] for x in
                                  search.json()['series'][0]['data']]
                    dates_values_dict = dict(zip(lst_dates, lst_values))
                    values_dict[search.json()['series'][0]['name'] +
                                " (" +
                                search.json()['series'][0]['units'] +
                                ")"] = \
                        dates_values_dict
            return values_dict

        elif categories_dict is None:
            raise NoResultsError("No Results Found")

    def data_by_date(self,
                     date,
                     filters_to_keep=None,
                     filters_to_remove=None,
                     rows=glob_row):
        """
        API Search Data Query - Date Search
        :param date: string
        :param filters_to_keep: string or list
        :param filters_to_remove: string or list
        :param rows: string
        :return: Returns eia data series in dictionary form
        (name, units, frequency, and series ID) based on last update date.
        """
        categories_dict = self.search_by_date(date,
                                              filters_to_keep,
                                              filters_to_remove,
                                              rows)
        url_data = 'http://api.eia.gov/series/?series_id={}&api_key={}&out=json'
        values_dict = {}
        if categories_dict is not None:
            for series_id in categories_dict.keys():
                search = requests.get(url_data.format(
                    categories_dict[series_id]['Series ID'],
                    self.token))

                if search.json().get('data') and \
                        search.json().get('data').get('error') == \
                        glob_invalid_api_key:
                    error_msg = search.json().get('data').get('error')
                    raise APIKeyError(error_msg)

                elif search.json().get('data') and \
                        search.json().get('data').get('error') == \
                        glob_invalid_series_id:
                    values_dict[series_id + " (" +
                                categories_dict[series_id]['Units'] +
                                ") "] = \
                        "No Data Available"

                else:
                    lst_dates = [x[0][0:4] + " " + x[0][4:6] + " " + x[0][6:8]
                                 for x in search.json()['series'][0]['data']]
                    lst_values = [x[1] for x in
                                  search.json()['series'][0]['data']]
                    dates_values_dict = dict(zip(lst_dates, lst_values))
                    values_dict[search.json()['series'][0]['name'] +
                                " (" +
                                search.json()['series'][0]['units'] +
                                ")"] = \
                        dates_values_dict

            return values_dict

        elif categories_dict is None:
            raise NoResultsError("No Results Found")

    def data_by_series(self,
                       series):
        """
        API Series Query
        :param series: string
        :return: Returns eia data series in dictionary form
        (name, units, frequency, and series ID) based on series ID.
        """
        url_data = 'http://api.eia.gov/series/?series_id={}&api_key={}&out=json'
        values_dict = {}
        search = requests.get(url_data.format(series, self.token))
        if search.json().get('data') and \
                search.json().get('data').get('error') == \
                glob_invalid_api_key:
            error_msg = search.json().get('data').get('error')
            raise APIKeyError(error_msg)

        elif search.json().get('data') \
                and search.json().get('data').get('error') == \
                glob_invalid_series_id:
                error_msg = search.json()['data']['error']
                raise InvalidSeries(error_msg)

        else:
            lst_dates = [x[0][0:4] + " " + x[0][4:] + " " + x[0][6:8]
                         for x in search.json()['series'][0]['data']]
            lst_values = [x[1] for x in
                          search.json()['series'][0]['data']]
            dates_values_dict = dict(zip(lst_dates, lst_values))
            values_dict[search.json()['series'][0]['name'] +
                        " (" +
                        search.json()['series'][0]['units'] +
                        ")"] = \
                dates_values_dict
            return values_dict

