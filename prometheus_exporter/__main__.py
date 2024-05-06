import sys
import time
import getopt
import random
import signal
import threading
from prometheus_client import *
from prometheus_client.core import *
from prometheus_client.registry import *


class SampleCollector(Collector):

    def collect(self):
        metric01 = CounterMetricFamily('sample_metric_01',
                                       'Help text',
                                       labels=['label-01'])
        metric01.add_metric(['value-01'], 1.0)
        yield metric01

        metric02 = GaugeMetricFamily('sample_metric_02',
                                     'Help text',
                                     labels=['label-01'])
        metric02.add_metric(['value-01'], 1.0)
        yield metric02

        metric03 = HistogramMetricFamily('sample_metric_03',
                                         'Help text',
                                         labels=['label-01'])
        metric03.add_metric(['value-01'], [('0', 1.0)], 1.0)
        yield metric03

        metric04 = InfoMetricFamily('sample_metric_04',
                                    'Help text',
                                    labels=['label-01'])
        metric04.add_metric(['value-01'], {'key-01': 'value-01'})
        yield metric04

        metric05 = SummaryMetricFamily('sample_metric_05',
                                       'Help text',
                                       labels=['label-01'])
        metric05.add_metric(['value-01'], 1, 1.0)
        yield metric05


def whenGettingValueFromOutside():
    REGISTRY.register(SampleCollector())


def whenSettingValueInternally():
    metric01 = Counter('metric01', 'Description of counter', ['label_01'])
    metric02 = Gauge('metric02', 'Description of gauge', ['label_01'])
    metric03 = Histogram('metric03', 'Description of histogram', ['label_01'])
    metric04 = Info('metric04', 'Description of info', ['label_01'])
    metric05 = Summary('metric05', 'Description of summary', ['label_01'])

    lock = threading.Lock()
    lock.acquire()

    def __job():
        while lock.locked():
            metric01.labels('value-01').inc()
            metric01.labels('value-01').inc(2.0)

            metric02.labels('value-01').inc()
            metric02.labels('value-01').inc(2.0)
            metric02.labels('value-01').dec()
            metric02.labels('value-01').dec(2.0)
            metric02.labels('value-01').set(1.0)

            metric03.labels('value-01').observe(1.0)

            metric04.labels('value-01').info({
                'key-01': 'value-01',
                'key-02': 'value-02'
            })

            metric05.labels('value-01').observe(1.0)

            time.sleep(1)

    t = threading.Thread(target=__job)
    t.start()

    return t, lock


def main():
    opts, args = getopt.getopt(sys.argv[1:], 'hp:', ['help', 'port='])
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print('python', sys.argv[0], '--port <port>')
            sys.exit()
        elif opt in ('-p', '--port'):
            port = int(arg)

    server, t1 = start_http_server(port)

    whenGettingValueFromOutside()
    t2, lock = whenSettingValueInternally()

    signal.signal(signal.SIGINT, lambda signum, frame: 0)
    signal.signal(signal.SIGTERM, lambda signum, frame: 0)
    signal.pause()

    lock.release()
    t2.join()

    server.shutdown()
    t1.join()


if __name__ == '__main__':
    main()
