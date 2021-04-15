#!/usr/bin/env python3

import re
import requests
import os
import time
import fileinput


class AnalyticsEventsService:
    # create_event_schema('sample_schema', 'https://analytics.api.appdynamics.com:443',
    def __init__(self, es_url='http://ajsap-20110nosshcontro-useyaxbj.appd-cx.com:9080',
                 events_api_key='f48ab200-71e3-4a2e-95df-5c285068d4a3',
                 events_api_account_name='customer1_3cd654eb-ecbd-4ff1-b879-b1ad53a2f2ab'):
        self.update(es_url, events_api_key, events_api_account_name)

    def update(self, es_url, events_api_key, events_api_account_name):
        self.es_url = es_url
        self.events_api_key = events_api_key
        self.events_api_account_name = events_api_account_name

    def reset(self):
        self.update('', '', '', '')


#.ds_store filename messes up this method sometimes. will get bad unicode-32 error
input_dir_ext = "/Users/jacobsaa/Desktop/url_list/"
sleep_time_var = 1


def get_dir_files(input_dir, sleep_time=''):
    input_files = os.listdir(input_dir)
    for i in input_files:
        urls_file = input_dir + i
        # print("file path: ", urls_file)

        with open(urls_file, 'rb') as data:
            for line in fileinput.input(urls_file):
                new_l = str(line)
                url_monitor(new_l)
                time.sleep(sleep_time)


def url_monitor(url):
    timeout = 30
    response = requests.get(url, timeout=timeout)
    status_code = str(response.status_code)
    response_reason = str(response.reason)
    response_time = int(response.elapsed.microseconds / 1000)

    url_str = str(url)

    url_str = url_str.replace("\n", "")
    hostname = str(re.findall('\:\/\/([^}]+):', url_str))
    hostname = hostname.replace("[", "")
    hostname = hostname.replace("]", "")
    hostname = hostname.replace("'", "")

    print("name=Custom Metrics|{}, value={}".format(hostname, response_time))

    publish_url_performance_data_to_es("custom_synthetics", es.es_url, es.events_api_key, es.events_api_account_name,
                                       url_str, response_time, status_code, response_reason)



    return url, response_time, status_code, response_reason


def publish_url_performance_data_to_es(schema_name, es_url, events_api_key, events_api_account_name, url_in, resp_time_in,
                                       status_code_in, response_reason_in):
    headers = {'X-Events-API-Key': events_api_key, 'X-Events-API-AccountName': events_api_account_name,
               'Content-type': 'application/vnd.appd.events+json;v=2'}

    full_url = es_url + "/events/publish/{}".format(schema_name)

    data = [{"url": url_in, "response_time_in_min": resp_time_in, "status_code": status_code_in, "response_reason": response_reason_in}]

    r = requests.post(full_url, headers=headers, json=data)
    # print(url_in)
    # print(status_code_in, " ", response_reason_in)
    # print("response time: ", resp_time_in)


es = AnalyticsEventsService()
get_dir_files(input_dir_ext, 1)
