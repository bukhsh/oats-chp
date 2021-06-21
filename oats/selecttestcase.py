#==================================================================
# select_testcase.py
# This Python script loads the test case file from the library
# ---Author---
# W. Bukhsh,
# wbukhsh@gmail.com
# OATS
# Copyright (c) 2015 by W Bukhsh, Glasgow, Scotland
# OATS is distributed under the GNU GENERAL PUBLIC LICENSE v3 (see LICENSE file for details).
#==================================================================

import pandas as pd

def selecttestcase(test):
    data_flags = {'storage':1,'ts':1,'shunt':1}
    xl = pd.ExcelFile(test)

    df_bus         = xl.parse("zone")
    df_demand      = xl.parse("demand")
    df_branch      = xl.parse("zonalNTC")
    df_generators  = xl.parse("generator")
    df_baseMVA     = xl.parse("baseMVA")

    data = {
    "bus": df_bus.dropna(how='all'),
    "demand": df_demand.dropna(how='all'),
    "branch": df_branch.dropna(how='all'),
    "generator": df_generators.dropna(how='all'),
    "baseMVA": df_baseMVA.dropna(how='all'),
    "flags":data_flags
    }

    return data
