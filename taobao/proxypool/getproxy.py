import math
import os
import re
import urllib.request
from multiprocessing import Pool, Manager

import requests

# process pool num
pool_num = 60
# proxy list url
url = 'https://raw.githubusercontent.com/fate0/proxylist/master/proxy.list'


def backup():
    try:
        os.rename('proxy.py', 'proxy.bak')
    except Exception:
        os.replace('proxy.py', 'proxy.bak')


def check_proxy(f1, proxy_list):
    f2 = ''
    for ip in f1:
        try:
            res = requests.get('https://www.taobao.com', proxies={ip.split(':')[0]: ip}, timeout=2)
            if res.status_code == 200:
                f2 += '\'%s\',\n' % ip
        except Exception:
            pass
    proxy_list.append(f2)


if __name__ == '__main__':
    print('BACKING UP')
    backup()

    print('DOWNLOADING proxy.list FROM GITHUB')
    urllib.request.urlretrieve(url, 'proxy.list')

    print('CLEANING proxy.list')
    with open('proxy.list', 'r') as f:
        content = []
        for line in f.readlines():
            host = re.search('host.+?(\d+\.\d+\.\d+\.\d+)', line).group(1)
            http = re.search('type.+?(\w+)', line).group(1)
            port = re.search('port.+?(\d+)', line).group(1)
            ip = '%s://%s:%s' % (http, host, port)
            content.append(ip)
        part = math.ceil(len(content) / pool_num)

    print('GENERATING PROCESS POOL')
    manager = Manager()
    m_list = manager.list()
    p = Pool(pool_num - 1)
    for i in range(pool_num):
        cur = i * part
        if i is not pool_num - 1:
            p.apply_async(check_proxy, args=(content[cur:cur + part], m_list))
        else:
            p.apply_async(check_proxy, args=(content[cur:], m_list))
    p.close()
    p.join()

    with open('proxy.py', 'w') as new:
        new.write('pool = [\n')
        for l in m_list:
            new.write(l)
        new.write(']\n')
