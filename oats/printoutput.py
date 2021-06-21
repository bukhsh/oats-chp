#==================================================================
# printout.py
# A Python script to write output to xls and on screen
# ---Author---
# W. Bukhsh,
# wbukhsh@gmail.com
# OATS
# Copyright (c) 2015 by W Bukhsh, Glasgow, Scotland
# OATS is distributed under the GNU GENERAL PUBLIC LICENSE v3 (see LICENSE file for details).
#==================================================================
from pyomo.opt import SolverStatus, TerminationCondition
from tabulate import tabulate
import pandas as pd
import math
import sys
class printoutput(object):
    def __init__(self, results, instance,mod):
        self.results   = results
        self.instance  = instance
        self.mod       = mod
    def greet(self):
        print ("========================")
        print ("\n Output from the OATS")
        print ("========================")
    def solutionstatus(self):
        self.instance.solutions.load_from(self.results)
        print ("------Solver Message------")
        print (self.results.solver)
        print ("--------------------------")
        if (self.results.solver.status == SolverStatus.ok) \
        and (self.results.solver.termination_condition == TerminationCondition.optimal):
            print ("Optimization Converged!")
        elif self.results.solver.termination_condition == TerminationCondition.infeasible:
            sys.exit("Problem is infeasible!\nOats terminated. No output is written on the results file.")
        else:
            print (sys.exit("Problem is infeasible!\nOats terminated. No output is written on the results file."))
    def printsummary(self):
        if 'LF' not in self.mod:
            print ("Cost of the objective function:", str(float(self.instance.OBJ())))
        print ("***********")
        print ("\n Summary")
        print ("***********")
        tab_summary = []
        tab_summary.append(['Total generation (MW)', 'Demand (MW)'])
        tab_summary.append([sum(self.instance.pG[g].value for g in self.instance.G)*self.instance.baseMVA,\
        sum(self.instance.PD[d] for d in self.instance.D)*self.instance.baseMVA])
        print (tabulate(tab_summary, headers="firstrow", tablefmt="grid"))
        print ("==============================================")
    def printoutputxls(self):
        #===initialise pandas dataframes
        cols_summary    = ['Generation (MW)', 'Demand (MW)','Objective function value']
        cols_generation = ['name', 'zone', 'pG(MW)']
        cols_flows = ['from', 'to', 'flow(MW)']
        summary         = pd.DataFrame(columns=cols_summary)
        generation      = pd.DataFrame(columns=cols_generation)
        flow            = pd.DataFrame(columns=cols_flows)

        #-----write Data Frames

        summary.loc[0] = pd.Series({'Generation (MW)': sum(self.instance.pG[g].value for g in self.instance.G)*self.instance.baseMVA,\
        'Demand (MW)':sum(self.instance.pD[d].value for d in self.instance.D)*self.instance.baseMVA,\
        'Objective function value': self.instance.OBJ()})

        ind = 0
        for g in self.instance.Gbs:
            generation.loc[ind] = pd.Series({'name': g[1], 'zone': g[0], \
                                             'pG(MW)': round(self.instance.pG[g[1]].value * self.instance.baseMVA, 3)})
            ind += 1

        ind = 0
        for l in self.instance.L:
            flow.loc[ind] = pd.Series({'from': self.instance.A[l,1], 'to': self.instance.A[l,2], \
                                             'flow(MW)': round(self.instance.pL[l].value * self.instance.baseMVA, 3)})
            ind += 1

        #----------------------------------------------------------
        #===write output on xlsx file===
        #

        writer = pd.ExcelWriter('results.xlsx', engine ='xlsxwriter')
        summary.to_excel(writer, sheet_name = 'summary',index=False)
        generation.to_excel(writer, sheet_name = 'generator',index=False)
        flow.to_excel(writer, sheet_name='flows', index=False)
        writer.save()
