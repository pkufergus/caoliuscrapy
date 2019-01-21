#!/usr/bin/env python
#-*-coding:utf-8-*-
import argparse
import time
import os
#import logging

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
#from scrapy.utils.log import configure_logging

from caoliu.spiders.caoliu_spider import CaoLiuSpider


from lib import log
from lib import conf
import sys

process_name=os.path.basename(sys.argv[0]).split(".")[0]
print("file=%s" % os.path.abspath(__file__))
DIR_APP = os.path.dirname(os.path.abspath(__file__))
print("dir app=%s" % DIR_APP)
DIR_BASE = DIR_APP
print("base=%s" % DIR_BASE)
#sys.path.insert(0, DIR_BASE)
print("base=%s" % DIR_BASE)
DIR_LOG = DIR_BASE + "/log/"
DIR_CONF = DIR_BASE + "/conf/"
log.notice("conf=%s" % DIR_CONF)
print("conf=%s" % DIR_CONF)
DIR_DATA = DIR_BASE + "/data/"
if not os.path.exists(DIR_DATA):
    os.makedirs(DIR_DATA)
DIR_DATA_TMP = DIR_DATA + "/tmp/"
if not os.path.exists(DIR_DATA_TMP):
    os.makedirs(DIR_DATA_TMP)

CONF_IDC = conf.Conf(infile=DIR_CONF + "idc.conf")
CURRENT_IDC = CONF_IDC["idc"]
print("current idc=%s" % CURRENT_IDC)
CONF_APP = conf.Conf(infile=DIR_CONF + "app.conf", _idc=CURRENT_IDC)
CONF_APP["common"]["app_name"]=process_name
log.init(DIR_LOG, CONF_APP["common"]["app_name"], CONF_APP["common"]["debug"])
log.notice(CONF_APP["common"]["app_name"] + ".init", "load all conf successfully.")

#logging.basicConfig(
    #filename='/tmp/caoliu.log',
    #format='%(name)s %(levelname)s %(asctime)s: %(message)s',
    #datefmt="%Y-%m-%d %H:%M:%S",
    #level=logging.DEBUG
#)
#configure_logging({'LOG_STDOUT': True})

def run(max_page=5):
    settings = get_project_settings()
    settings.set('MAX_PAGE', max_page, 'project')
    crawler_process = CrawlerProcess(settings)
    crawler_process.crawl(CaoLiuSpider)
    crawler_process.start()

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--maxpage', default=20, type=int)
    parser.add_argument('--sleep', default=300, type=int)
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_args()
    max_page = args.maxpage
    sleep_time = args.sleep
    run(max_page)
