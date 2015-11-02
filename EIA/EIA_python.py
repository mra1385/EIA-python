__author__ = 'Mike Azar'

import requests


# Global variables used as default parameters for certain EIA-python1 API queries
rows_global = 100
page_global = 1


class APIKeyError(Exception):
    pass


class NoResultsError(Exception):
    pass


class DateFormatError(Exception):
    pass


class InvalidSeries(Exception):
    pass


class EIA(object):
    def __init__(self, token):
        """
        Initialise the EIA-python1 class by requesting:
        :param token: string
        :return: EIA-python1 object
        """
        self.token = token

    @staticmethod
    def _filter_categories(d, filters_to_keep, filters_to_remove):
        filtered_dict = dict(d)
        if filters_to_keep is not None:
            if type(filters_to_keep) == str:
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
            if type(filters_to_remove) == str:
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
                           category_id=None,
                           filters_to_keep=None,
                           filters_to_remove=None,
                           return_list=False):
        search_url = 'http://api.eia.gov/category/?api_key={}&category_id={}'
        categories_dict = {}
        search = requests.get(search_url.format(self.token, category_id))
        if ('data' in str(search.json().items())) and \
                (search.json()['data']['error'].find(
                    'invalid or missing api_key') != -1):
            error_msg = search.json()['data']['error']
            raise APIKeyError(error_msg)

        elif ('childseries' in str(search.json().items())) and \
                (len(search.json()['category']['childseries']) > 0):
            for k in search.json()['category']['childseries']:
                categories_dict[k['name']] = {}
                categories_dict[k['name']]['Units'] = k['units']
                categories_dict[k['name']]['Frequency'] = k['f']
                categories_dict[k['name']]['Series ID'] = k['series_id']
            if filters_to_keep is not None or filters_to_remove is not None:
                categories_dict = self._filter_categories(categories_dict,
                                                          filters_to_keep,
                                                          filters_to_remove)

        elif ('childcategories' in str(search.json().items())) and \
                (len(search.json()['category']['childcategories']) > 0):
                raise NoResultsError("No Child Series Found. Narrow Your Search"
                                     " By Choosing a More Specific Category ID")
        if return_list is True:
            categories_lst = []
            for k in categories_dict:
                categories_lst.append(k)
            return categories_lst
        else:
            return categories_dict

    def search_by_keyword(self,
                          keyword=None,
                          filters_to_keep=None,
                          filters_to_remove=None,
                          rows=rows_global,
                          page=page_global,
                          return_list=False):
        if type(keyword) == list: keyword = '+'.join(keyword)
        search_url = 'http://api.eia.gov/search/?search_term=name&' \
                     'search_value="{}"&rows_per_page={}&page_num={}'
        categories_dict = {}
        search = requests.get(search_url.format(keyword, rows, page))
        if ('response' in str(search.json())) and \
                (len(search.json()['response']['docs']) > 0):
            for k in search.json()['response']['docs']:
                categories_dict[k['name']] = {}
                categories_dict[k['name']]['Units'] = k['units']
                categories_dict[k['name']]['Frequency'] = k['frequency']
                categories_dict[k['name']]['Series ID'] = k['series_id']
            if filters_to_keep is not None or filters_to_remove is not None:
                categories_dict = self._filter_categories(categories_dict,
                                                          filters_to_keep,
                                                          filters_to_remove)

        elif ('response' in str(search.json())) and \
                (len(search.json()['response']['docs']) == 0):
            raise NoResultsError('No Results Found')

        if return_list is True:
            categories_lst = []
            for k, v in categories_dict.items():
                categories_lst.append(k)
            return categories_lst
        else:
            return categories_dict

    def search_by_date(self,
                       date,
                       filters_to_keep=None,
                       filters_to_remove=None,
                       rows=rows_global,
                       page=page_global,
                       return_list=False):
        search_url = 'http://api.eia.gov/search/?search_term=last_updated&' \
                     'search_value=[{}]&rows_per_page={}&page_num={}'
        categories_dict = {}
        search = requests.get(search_url.format(date, rows, page))
        if ('response' in str(search.json()) and
                (len(search.json()['response']['docs']) > 0)):
            for k in search.json()['response']['docs']:
                categories_dict[k['name']] = {}
                categories_dict[k['name']]['Units'] = k['units']
                categories_dict[k['name']]['Frequency'] = k['frequency']
                categories_dict[k['name']]['Series ID'] = k['series_id']
            if filters_to_keep is not None or filters_to_remove is not None:
                categories_dict = self._filter_categories(categories_dict,
                                                          filters_to_keep,
                                                          filters_to_remove)
            if return_list is True:
                categories_lst = []
                for k in categories_dict:
                    categories_lst.append(k)
                return categories_lst
            else:
                return categories_dict

        elif 'solr connection failed' in str(search.json()):
            raise DateFormatError("Connection Failed. Check date format. "
                                  "Date should be in the following format:"
                                  "'2015-01-01T00:00:00Z TO "
                                  "2015-01-01T23:59:59Z'")
        elif len(search.json()['response']['docs']) == 0:
            raise NoResultsError('No Results Found')

    def data_by_category(self,
                         category,
                         filters_to_keep=None,
                         filters_to_remove=None):
        categories_dict = self.search_by_category(category,
                                                  filters_to_keep,
                                                  filters_to_remove)
        url_data = 'http://api.eia.gov/series/?series_id={}&api_key={}&out=json'
        values_dict = {}
        if categories_dict is not None:
            for series_id in categories_dict.values():
                search = requests.get(url_data.format(series_id['Series ID'],
                                                      self.token))
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
                        rows=rows_global,
                        page=page_global):
        categories_dict = self.search_by_keyword(keyword,
                                                 filters_to_keep,
                                                 filters_to_remove,
                                                 rows,
                                                 page)
        url_data = 'http://api.eia.gov/series/?series_id={}&api_key={}&out=json'
        values_dict = {}
        if categories_dict is not None:
            for series_id in categories_dict.values():
                search = requests.get(url_data.format(series_id['Series ID'],
                                                      self.token))
                if ('error' in str(search.json().items())) and \
                        (search.json()['data']['error'].find(
                            'invalid or missing api_key') != -1):
                    error_msg = search.json()['data']['error']
                    raise APIKeyError(error_msg)
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
                     rows=rows_global,
                     page=page_global):
        categories_dict = self.search_by_date(date,
                                              filters_to_keep,
                                              filters_to_remove,
                                              rows,
                                              page)
        url_data = 'http://api.eia.gov/series/?series_id={}&api_key={}&out=json'
        values_dict = {}
        if categories_dict is not None:
            for series_id in categories_dict.values():
                search = requests.get(url_data.format(series_id['Series ID'],
                                                      self.token))
                if ('error' in str(search.json().items())) and \
                        (search.json()['data']['error'].find(
                            'invalid or missing api_key') != -1):
                    error_msg = search.json()['data']['error']
                    raise APIKeyError(error_msg)
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
        elif categories_dict is None:
            raise NoResultsError("No Results Found")

    def data_by_series(self,
                       series):
        url_data = 'http://api.eia.gov/series/?series_id={}&api_key={}&out=json'
        values_dict = {}
        search = requests.get(url_data.format(series, self.token))
        if ('error' in str(search.json().items())) and \
                (search.json()['data']['error'].find(
                    'invalid or missing api_key') != -1):
            error_msg = search.json()['data']['error']
            raise APIKeyError(error_msg)
        elif ('error' in str(search.json().items())) and \
                (search.json()['data']['error'].find(
                    'invalid series_id') != -1):
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
