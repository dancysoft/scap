 # -*- coding: utf-8 -*-
"""
    scap.monitor
    ~~~~~~~~~~~~
    This module provides classes and utilities used by scap to monitor
    services, logs or metrics for anomalous events.

"""
import urllib, json

class Monitor(object):
    def __init__(self):
        pass

class HttpMonitor(Monitor):
    def get(self, url, params = ""):
        if isinstance(params, dict):
            params = urllib.urlencode(params)
        f = urllib.urlopen("%s?%s" % (url, params))
        data = f.read()
        f.close()
        return data


class ErrorRateMetric(HttpMonitor):
    def __init__(self,metric):
        self.metric = metric

    def check(self):
        params = {
            "from": "-30minutes",
            "target": self.metric,
            "format": "json"
        }
        data = self.get("http://graphite.wikimedia.org/render/", params)
        data = json.loads(data)
        maxVal = 0
        sumVal = 0
        data = data[0].get("datapoints")
        for i in data:
            maxVal = max(maxVal, i[0])
            sumVal += i[0]
            lastVal = i[0]
        avgVal = sumVal / len(data)
        print ("max: %s / average: %s last: %s" % (maxVal, avgVal, lastVal))
        return data
def main():
    mon = ErrorRateMetric("transformNull(restbase.v1_page_html_-title-_-revision--_tid-.GET.5xx.sample_rate,0)")
    data = mon.check()
    print data

if __name__ == '__main__':
    main()