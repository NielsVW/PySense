import requests
import urllib.parse

from PySense import PySenseException


class RestConnector:
    
    def __init__(self, host, username, password, debug):
        self._host = format_host(host)
        self.debug = debug
        data = {'username': username, 'password': password}
        resp = requests.post('{}/api/v1/authentication/login'.format(self._host), data=data)
        parse_response(resp)
        self._token = {'authorization':  "Bearer " + resp.json()['access_token']}
        
    def rest_call(self, action_type, url, *, data=None, json_payload=None, query_params=None, raw=False):
        """
        Run an arbitrary rest command against your Sisense instance and returns the JSON response    
    
        :param action_type: REST request type  
        :param url: url to hit, example api/v1/app_database/encrypt_database_password or api/branding  
        
        Optional:  
        :param data: The data portion of the payload  
        :param json_payload: The json portion of the payload  
        :param query_params: a dictionary of query values to be added to the end of the url  
        :param raw: True if raw content response wanted, 
        :return: The rest response object  
        """
        
        action_type = action_type.lower()
        if query_params is not None:
            query_string = build_query_string(query_params)
        else:
            query_string = ''
        full_url = '{}/{}{}'.format(self._host, url, query_string)

        if self.debug:
            print('{}: {}'.format(action_type, full_url))
            if data is not None:
                print('Data: {}'.format(data))
            if json_payload is not None:
                print('JSON: {}'.format(json_payload))
        response = requests.request(action_type, full_url, headers=self._token, data=data, json=json_payload)
        parse_response(response)
        if len(response.content) == 0:
            return None
        elif raw:
            return response.content
        else:
            try:
                return response.json()
            except ValueError as e:
                return response.content
            

def parse_response(response):
    if response.status_code not in [200, 201, 204]:
        raise PySenseException.PySenseException('ERROR: {}: {}\nURL: {}'
                                                .format(response.status_code, response.content, response.url))


def format_host(host):
    if not host.startswith('http'):
        host = 'http://' + host
    if host.endswith('/'):
        host = host[:-1]
    return host


def build_query_string(dictionary):
    ret_arr = []
    separator = '&'
    for key, value in dictionary.items():
        if value is not None:
            if isinstance(value, bool):
                if value is True:
                    validated = 'true'
                elif value is False:
                    validated = 'false'
            elif isinstance(value, list):
                validated = ','.join(value)
            else:
                validated = urllib.parse.quote(str(value))
            ret_arr.append("{}={}".format(key, validated))
    query_string = separator.join(ret_arr)
    if len(query_string) > 1:
        return '?' + query_string
    else:
        return ''






