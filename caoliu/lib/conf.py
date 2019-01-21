# -*- coding=utf-8 -*-
"""
conf py
"""
################################################################################
#
# attrprovider
# @author dongliqiang@baidu.com
# Copyright (c) 2017 Baidu.com, Inc. All Rights Reserved
#
################################################################################

import os
import io
#import validate
from configobj import ConfigObj

# parameter Validator


# def _validator_is_dict(value):
#     """
#     extents for ConfigObj Vaildator
#     """
#     if not isinstance(value, dict):
#         raise validate.VdtTypeError(value)
#     return value
#
# #global validator
# VALIDATOR = validate.Validator()
# VALIDATOR.functions["dict"] = _validator_is_dict


class Conf(object):
    """
    Huskar Conf Class
    adapter for baidu idc
    """

    _IDC_PREFIX = ".IDC_"
    _VALID_SUFFIX = ".valid"
    _ENCODEING = "UTF-8"
    _INDENT_TYPE = None

    def __init__(self, **kwargs):
        """
        super __init__
        """
        infile = kwargs["infile"] or None
        self._conf = None
        self._idc = kwargs["_idc"] if "_idc" in kwargs else None
        if self._idc is not None:
            del kwargs["_idc"]

        kwargs["encoding"] = self._ENCODEING
        kwargs["default_encoding"] = self._ENCODEING
        kwargs["indent_type"] = self._INDENT_TYPE
        kwargs["write_empty_values"] = True

        print("conf file [%s] type[%s]" % (infile, type(infile)))
        if infile is not None:
            # you can ONLY read conf
            if isinstance(infile, str) and os.path.isfile(infile):
                # validation
                infile_valid = infile + self._VALID_SUFFIX
                if os.path.isfile(infile_valid):
                    kwargs["infile"] = infile
                    kwargs["configspec"] = infile_valid
                    self._conf = ConfigObj(**kwargs)
                    # test = self._conf.validate(VALIDATOR)
                    # if test is not True:
                    #     #raise huskar.error.BaseError(
                    #     #    errno=huskar.error.ERRNO_FRAMEWORK,
                    #     #    errmsg="conf vaild failed.[%s]" % str(test))
                    #     raise Exception(
                    #         "can not find valid file for [%s]"
                    #         " needed valid file [%s]" % (infile, infile_valid))
                else:
                    # in this framework
                    # we MUST use the validation
                    raise Exception(
                        "can not find valid file for [%s]"
                        " needed valid file [%s]" % (infile, infile_valid))

            if isinstance(infile, io.StringIO) and\
                    getattr(infile, "read") is not None:
                self._conf = ConfigObj(**kwargs)

        if self._conf is None:
            raise Exception("conf is not found. [%s]" % infile)

        self._conf.walk(self._parse_idc, call_on_sections=True)

    def _parse_idc(self, section, key):
        """
        get the configuration by the current idc
        """
        value = section[key]
        if isinstance(value, dict) and len(value) > 0:
            keys = list(value.keys())
            cur_idc = self._IDC_PREFIX + self._idc
            idc_mode_keys = [x for x in keys if x.startswith(self._IDC_PREFIX)]
            if len(idc_mode_keys) > 0:
                # in idc mode
                matches_idc = [x for x in idc_mode_keys if x == cur_idc]
                if len(matches_idc) == 1:
                    # find current idc
                    section[key] = self._merge_dicts(section[key], value[cur_idc])
                    del section[key][cur_idc]
                else:
                    # can not find current idc in conf
                    raise Exception(
                        "useing idc mode, can not find matched idc[%s] in file[%s]"
                        % ((cur_idc), self._conf.filename))

            # delete all idc in every section
            for k in keys:
                if k.startswith(self._IDC_PREFIX) and k != cur_idc:
                    del section[key][k]

    def _merge_dicts(self, *dict_args):
        """
        Given any number of dicts, shallow copy and merge into a new dict,
        precedence goes to key value pairs in latter dicts.
        """
        result = {}
        for dictionary in dict_args:
            result.update(dictionary)
        return result

    def __getitem__(self, key):
        """
        hack for __getitem__
        adapter for baidu idc
        """
        return self._conf.__getitem__(key)

    def __setitem__(self, key, value):
        """
        hack for __setitem__
        you CAN NOT set value to the configuration
        """
        pass

    def __repr__(self):
        """
        __repr__
        """
        return repr(self._conf)

    def __str__(self):
        """
        __str__
        """
        return str(self._conf)


if __name__ == '__main__':

    input_config = u"""
    [s1]
    author = dongliqiang
    description = Test config

    [s2]
    [[.IDC_nj]]
    key1 = aaa
    [[.IDC_cq01]]
    key1 = bbb

    [s3]
    key3 = abc
    [[s4]]
    [[[.IDC_nj]]]
    key2 = ccc
    [[[.IDC_cq01]]]
    key2 = ddd
    """
    conf = Conf(infile=io.StringIO(input_config), _idc="cq01")
    #print conf, conf["s2"]
