import oats
#
# oats.uc()
# import os
# pp_dir = os.path.dirname(os.path.realpath(__file__))
#
from oats.run import bmtransport

bmtransport(neos=False,solver='cplex',tc='tests/GB_ReducedNetwork_test.xlsx')
