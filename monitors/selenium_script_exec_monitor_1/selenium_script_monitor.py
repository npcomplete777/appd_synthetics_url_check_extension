#!/usr/bin/env python3

import subprocess
import requests
import os
import re


class AnalyticsEventsService:
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


# .ds_store filename messes up this method sometimes. will get bad unicode-32 error
# input dir string must always end with '/' char
input_dir_ext = "/Users/jacobsaa/Desktop/selenium_scripts/queue_1/"


def get_dir_files(input_dir, schema_name_to_publish_data="custom_synthetics"):
    job_status = ""
    city = "Colorado Springs"
    country = "United States"
    continent= "North America"
    input_files = os.listdir(input_dir)
    print("files in directory: ", input_files)
    for i in input_files:
        if i == ".DS_Store":
            print()
        else:
            scripts_file = input_dir + i
            print("file path: ", scripts_file)
            stdout = str(subprocess.run('python3 {}'.format(scripts_file), capture_output=True, shell=True))
            print("stdout: ", stdout)

            # keys/pg names = [], values/metrics = {} in monitored selenium scripts
            pg_name_list = re.findall('\[([^]]+)', stdout)
            metric_list = re.findall('\{([^}]+)}', stdout)
            print("page name list: ", pg_name_list)
            print()
            print("metric list: ", metric_list)

            metrics_dict = dict(zip(pg_name_list, metric_list))

            for key, value in metrics_dict.items():
                # print("URL: ", key)
                # print("response time: ", value)
                # val_str = str(value)

                print("name=Custom Metrics|Selenium Monitor|{}, value={}".format(key, int(value)))

                if str(key).endswith("job"):
                    job_status = "COMPLETE"
                    publish_url_performance_data_to_es(schema_name_to_publish_data, es.es_url, es.events_api_key,
                                                       es.events_api_account_name,
                                                       str(key), int(value), "", "", str(i), job_status, city, country, continent)
                elif int(value) == 00000:
                    job_status = "FAILED"
                    print("**********FAILED**********")
                    print("response time: ", value)
                    publish_url_performance_data_to_es(schema_name_to_publish_data, es.es_url, es.events_api_key,
                                                       es.events_api_account_name,


                                                       str(key), int(value), "", "", str(i), job_status, city, country, continent)
                else:
                    job_status = "IN-PROGRESS"
                    publish_url_performance_data_to_es(schema_name_to_publish_data, es.es_url, es.events_api_key,
                                                       es.events_api_account_name,
                                                       str(key), int(value), "", "", str(i), job_status, city, country, continent)



def publish_url_performance_data_to_es(schema_name, es_url, events_api_key, events_api_account_name, url_in, resp_time_in,
                                       status_code_in, response_reason_in, job_name_in, job_status_in, city_in,
                                       country_in, continent_in):
    headers = {'X-Events-API-Key': events_api_key, 'X-Events-API-AccountName': events_api_account_name,
               'Content-type': 'application/vnd.appd.events+json;v=2'}

    full_url = es_url + "/events/publish/{}".format(schema_name)

    # print("response time: ", resp_time_in)
    # NOTE: Below JSON field names must match those in the analytics schema the are POSTing to
    data = [{"url": url_in, "response_time_in_ms": resp_time_in, "status_code": status_code_in, "response_reason": response_reason_in,
             "job_name": job_name_in, "job_status": job_status_in, "city": city_in, "country": country_in, "continent": continent_in}]

    r = requests.post(full_url, headers=headers, json=data)
    print('POST analytics data status code:', r.status_code)
    print(r.content)
    print()


es = AnalyticsEventsService()
get_dir_files(input_dir_ext)

#publish_url_performance_data_to_es("custom_synthetics", es.es_url, es.events_api_key,
 #                                  es.events_api_account_name,
 #                                  "mysite", 777, "", "", "selenium_script_2", "COMPLETE", "Dallas", "United States", "North America")
