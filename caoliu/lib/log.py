# -*- coding=utf-8 -*-
"""
log util
"""
################################################################################
#
# attrprovider
# @author dongliqiang@baidu.com
# Copyright (c) 2017 Baidu.com, Inc. All Rights Reserved
#
################################################################################

# import sys
# reload(sys)
# sys.setdefaultencoding('utf-8')

import six
import logging
import logging.handlers
import os
import urllib
import traceback
import json
import time


LOG_DIR = "./logs/"
MODULE = "app"
FOTMAT = "%(levelname)s: %(asctime)s %(f_module)s \
[filename=%(f_filename)s lineno=%(f_lineno)d \
process=%(process)d thread=%(thread)d \
thread_name=%(threadName)s created=%(created)f msecs=%(msecs)d %(message)s]"
ACCESS_FORMAT = "%(asctime)s %(module)s %(process)d [%(message)s]"
LEVEL_NOTICE = 21
LEVEL_FATAL = 41
logging.addLevelName(LEVEL_NOTICE, "NOTICE")
logging.addLevelName(LEVEL_FATAL, "FATAL")

"""
app_log is suitable for human reading.

app_omg_log is suitable for statistics and monitor,
each request ONLY has one line log.

"""
app_log = logging.getLogger(MODULE + ".log.app")
app_omp_log = logging.getLogger(MODULE + ".log.omp")
app_log_wf = logging.getLogger(MODULE + ".log.app_wf")
app_omp_log_wf = logging.getLogger(MODULE + ".log.omp_wf")


def _get_current_trackback():
    """
    get current traceback

    traceback is wrong in the log file.
    so we should find it by myself.
    """
    traces = traceback.extract_stack()
    for i, trace in enumerate(traces):
        if trace[0].endswith("log.py") or\
                trace[0].endswith("rmb/log.py") or\
                trace[0].endswith("rmb/log.pyo"):
            if trace[2] in [
                "debug", "notice", "warning", "fatal"]:
                return traces[i - 1]
    # can not find any current trace.
    # return the default
    return traces[0]


class MultiProcessSafeDailyRotatingFileHandler(logging.handlers.BaseRotatingHandler):
    """Similar with `logging.TimedRotatingFileHandler`, while this one is
    - Multi process safe
    - Rotate at midnight only
    - Utc not supported
    """
    def __init__(self, filename, encoding=None, delay=False, utc=False, **kwargs):
        self.utc = utc
        self.suffix = "%Y%m%d%H"
        self.baseFilename = filename
        self.currentFileName = self._compute_fn()
        logging.handlers.BaseRotatingHandler.__init__(self, filename, 'a', encoding, delay)

    def shouldRollover(self, record):
        """
        inner function
        """
        if self.currentFileName != self._compute_fn():
            return True
        return False

    def doRollover(self):
        """
        inner function
        """
        if self.stream:
            self.stream.close()
            self.stream = None
        self.currentFileName = self._compute_fn()

    def _compute_fn(self):
        """
        inner function
        """
        return self.baseFilename + "." + time.strftime(self.suffix, time.localtime())

"""
包装后的logger 会默认打印当前的trace
所有的日志 都会是log的行号 和 stack 信息
所以这里都统一替换一下

Args:
    parser (TYPE): Description
"""


class FilenameFilter(logging.Filter):
    """Summary
    FilenameFilter
    """

    def filter(self, record):
        """Summary
        filter
        """
        record.f_filename = os.path.abspath(_get_current_trackback()[0])
        return True


class ModuleFilter(logging.Filter):
    """Summary
    ModuleFilter
    """

    def filter(self, record):
        """Summary
        filter
        """
        record.f_module = _get_current_trackback()[2]
        return True


class LinenoFilter(logging.Filter):
    """Summary
    LinenoFilter
    """

    def filter(self, record):
        """Summary
        filter
        """
        record.f_lineno = _get_current_trackback()[1]
        return True


def init(log_dir=LOG_DIR, module=MODULE, debug=True):
    """Summary
    feed log init.

    Attribute:
        log_dir: log dir
        module: log name
        debug:
    """
    try:
        if not os.path.isdir(log_dir):
            os.makedirs(log_dir)
    except:
        pass

    if debug is True:
        app_log.setLevel(logging.DEBUG)
        app_omp_log.setLevel(logging.DEBUG)
        app_log_wf.setLevel(logging.DEBUG)
        app_omp_log_wf.setLevel(logging.DEBUG)
    else:
        app_log.setLevel(logging.INFO)
        app_omp_log.setLevel(logging.INFO)
        app_log_wf.setLevel(logging.WARNING)
        app_omp_log_wf.setLevel(logging.WARNING)

    formatter = logging.Formatter(FOTMAT)
    filename_filter = FilenameFilter()
    module_filter = ModuleFilter()
    lineno_filter = LinenoFilter()

    # app log
    app_log_hd = MultiProcessSafeDailyRotatingFileHandler(
        log_dir + "/" + module + ".log")
    app_log_hd.setFormatter(formatter)
    app_log.addHandler(app_log_hd)
    app_log.addFilter(filename_filter)
    app_log.addFilter(module_filter)
    app_log.addFilter(lineno_filter)
    app_log.propagate = False

    # app warning fatal log
    app_log_wf_hd = MultiProcessSafeDailyRotatingFileHandler(
        log_dir + "/" + module + ".log.wf")
    app_log_wf_hd.setFormatter(formatter)
    app_log_wf.addHandler(app_log_wf_hd)
    app_log_wf.addFilter(filename_filter)
    app_log_wf.addFilter(module_filter)
    app_log_wf.addFilter(lineno_filter)
    app_log_wf.propagate = False

    # app omp log
    app_omp_log_hd = MultiProcessSafeDailyRotatingFileHandler(
        log_dir + "/" + module + ".new.log")
    app_omp_log_hd.setFormatter(formatter)
    app_omp_log.addHandler(app_omp_log_hd)
    app_omp_log.addFilter(filename_filter)
    app_omp_log.addFilter(module_filter)
    app_omp_log.addFilter(lineno_filter)
    app_omp_log.propagate = False

    # app omp warning fatal log
    app_omp_log_wf_hd = MultiProcessSafeDailyRotatingFileHandler(
        log_dir + "/" + module + ".new.log.wf")
    app_omp_log_wf_hd.suffix = "%Y%m%d%H"
    app_omp_log_wf_hd.setFormatter(formatter)
    app_omp_log_wf.addHandler(app_omp_log_wf_hd)
    app_omp_log_wf.addFilter(filename_filter)
    app_omp_log_wf.addFilter(module_filter)
    app_omp_log_wf.addFilter(lineno_filter)
    app_omp_log_wf.propagate = False


def _urlencode(value):
    """Summary
    _urlencode
    """
    # if isinstance(value, unicode):
    #     return urllib.quote_plus(value.encode('utf8'))
    return urllib.parse.quote_plus(value)


def debug(*args):
    """Summary
    add a DEBUG log
    """
    if isinstance(args[0], six.string_types):
        value = "None" if len(args) <= 1 else args[1]
        app_log.debug("%s=%s" % (args[0], value))

    elif isinstance(args[0], dict):
        app_log.debug(' '.join(['%s=%s' % (key, value)
                                for (key, value) in args[0].items()]))

    else:
        raise Exception(
            "can not call log.debug, parameters error. need str or dict."
        )


def notice(*args, **kwargs):
    """Summary
    add a NOTICE log
    """
    if isinstance(args[0], six.string_types):
        value = "None" if len(args) <= 1 else args[1]
        app_log.log(LEVEL_NOTICE, "%s=%s" % (args[0], value))
        app_omp_log.log(LEVEL_NOTICE, "%s=%s" % (args[0], _urlencode(str(value))))

    elif isinstance(args[0], dict):
        app_log.log(LEVEL_NOTICE, ' '.join(['%s=%s' % (key, value)
                                for (key, value) in args[0].items()]))
        app_omp_log.log(LEVEL_NOTICE, ' '.join(['%s=%s' % (key, value)
                                for (key, value) in args[0].items()]))
    else:
        raise Exception(
            "can not call log.notice, parameters error. need str or dict."
        )

def warning(*args):
    """Summary
    add a WARNING log
    """
    if isinstance(args[0], six.string_types):
        value = "None" if len(args) <= 1 else args[1]
        app_log_wf.warning("%s=%s" % (args[0], value))
        app_omp_log_wf.warning("%s=%s" % (args[0], _urlencode(str(value))))

    elif isinstance(args[0], dict):
        app_log_wf.warning(' '.join(['%s=%s' % (key, value)
                                     for (key, value) in args[0].items()]))
        app_omp_log_wf.warning(' '.join(['%s=%s' % (key, _urlencode(str(value)))
                                         for (key, value) in args[0].items()]))

    else:
        raise Exception(
            "can not call log.warning, parameters error. need str or dict."
        )


def fatal(*args):
    """Summary
    add a FATAL log
    """
    if isinstance(args[0], six.string_types):
        value = "None" if len(args) <= 1 else args[1]
        app_log_wf.log(LEVEL_FATAL, "%s=%s" % (args[0], value))
        app_omp_log_wf.log(LEVEL_FATAL, "%s=%s" % (args[0], _urlencode(str(value))))

    elif isinstance(args[0], dict):
        app_log_wf.log(LEVEL_FATAL, ' '.join(['%s=%s' % (key, value)
                                              for (key, value) in args[0].items()]))
        app_omp_log_wf.log(LEVEL_FATAL,
                           ' '.join(['%s=%s' % (key, _urlencode(str(value)))
                                     for (key, value) in args[0].items()]))

    else:
        raise Exception(
            "can not call log.fatal, parameters error. need str or dict."
        )


if __name__ == '__main__':

    init()

    notice("port", "start 8999")
    notice("aaa", "bbfdl;akr3i2u53214%#&^%&^%#$@Wgfdlk\
        sjf红额外哦IQ缴费机啊街坊大姐唉算了；就发")

    warning("get_error_func", "fdaljfda辅导课辣椒水放假的撒娇 ")
    fatal("get_user_info", "failed to get user infomation")

    # test unicode
    notice("fdafda", u"地方大快速链接++++")

    # test dict
    notice({"a": "b", "c": "d"})

