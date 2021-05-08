#==================================================================
# runfile.py
# This is a top level OATS script. Simulations can be ran using this script
# ---Author---
# W. Bukhsh,
# wbukhsh@gmail.com
# OATS
# Copyright (c) 2017 by W. Bukhsh, Glasgow, Scotland
# OATS is distributed under the GNU GENERAL PUBLIC LICENSE v3. (see LICENSE file for details).
#==================================================================
import logging
import os
from oats.runcase import runcase

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='oatslog.log',
                    filemode='w')
logging.info("OATS log file")
logging.info("Program started")
oats_dir = os.path.dirname(os.path.realpath(__file__))
default_testcase = oats_dir+'/testcases/case24_ieee_rts.xlsx'

#----------------------------------------------------------------------
# BM Transport model
def bmtransport(tc='default',solver='ipopt',neos=True,out=0):
    """
    Solves BM Transport model (built for the CHP project)

    ARGUMENTS:
        **tc** (*.xlsx file)  - OATS test case. See OATS data format for details

        **solver** (str)  - name of a solver. Defualt is 'ipopt'

        **neos** (bool) - If True, the problem is solved using NEOS otherwise using a localy install solver.

        **out** (bool) - If True, the output is displayed on screen.
    """

    if tc == 'default':
        tc = default_testcase
    #options
    opt=({'neos':neos,\
    'solver':solver,'out':out})
    testcase = tc
    model ='BM_Transport'
    # ==log==
    logging.info("Solver selected: "+opt['solver'])
    logging.info("Testcase selected: "+testcase)
    logging.info("Model selected: "+model)
    runcase(testcase,model,opt)
    logging.info("Done!")
