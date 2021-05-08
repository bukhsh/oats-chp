#==================================================================
# DCOPF.mod
# PYOMO model file of "DC" balancing mechanism model
# This formulation uses the standard "DC" linearization of the AC power flow equations
# ---Author---
# W. Bukhsh,
# wbukhsh@gmail.com
# OATS
# Copyright (c) 2017 by W Bukhsh, Glasgow, Scotland
# OATS is distributed under the GNU GENERAL PUBLIC LICENSE v3. (see LICENSE file for details).
#==================================================================

#==========Import==========
from __future__ import division
from pyomo.environ import *
#==========================

model = AbstractModel()

# --- SETS ---
model.B      = Set()  # set of buses
model.G      = Set()  # set of generators
model.D      = Set()  # set of demands
model.L      = Set()  # set of lines
model.b0     = Set(within=model.B)  # set of reference buses
model.LE     = Set()  # line-to and from ends set (1,2)

# generators, buses, loads linked to each bus b
model.Gbs     = Set(within=model.B * model.G)    # set of generator-bus mapping
model.Dbs     = Set(within=model.B * model.D)    # set of demand-bus mapping

# --- parameters ---
# line matrix
model.A     = Param(model.L*model.LE)       # bus-line matrix
model.AT    = Param(model.TRANSF*model.LE)  # bus-transformer matrix

# demands
model.PD      = Param(model.D, within=Reals)  # real power demand
model.VOLL    = Param(model.D, within=Reals)  # value of lost load
# generators
model.PGmax    = Param(model.G, within=NonNegativeReals) # max real power of generator, p.u.
model.PGmin    = Param(model.G, within=Reals)            # min real power of generator, p.u.

# lines and transformer chracteristics and ratings
model.SLmax  = Param(model.L, within=NonNegativeReals)      # real power line limit


# cost data
model.bid      = Param(model.G, within=Reals)    # generator bid price
model.offer    = Param(model.G, within=Reals)    # generator offer price

#FPNs
model.PG      = Param(model.G, within=NonNegativeReals)    # FPN

model.baseMVA = Param(within=NonNegativeReals)# base MVA

#constants
model.eps = Param(within=NonNegativeReals)

# --- control variables ---
model.pG     = Var(model.G,  domain= Reals)  #real power generation
model.pGUp   = Var(model.G,  domain= NonNegativeReals)  #re-dispatch upwards
model.pGDown = Var(model.G,  domain= NonNegativeReals)  #re-dispatch downwards



model.pD    = Var(model.D, domain= Reals) #real power demand delivered
model.alpha = Var(model.D, domain= NonNegativeReals) #propotion of real power demand delivered
# --- state variables ---
model.deltaL  = Var(model.L, domain= Reals)      # angle difference across lines
model.delta   = Var(model.B, domain= Reals, initialize=0.0) # voltage phase angle at bus b, rad
model.pL      = Var(model.L, domain= Reals) # real power injected at b onto line l, p.u.

# --- cost function ---
def objective(model):
    obj = sum(model.offer[g]*(model.baseMVA*model.pGUp[g])+model.bidG[g]*(model.baseMVA*model.pGDown[g]) for g in model.G) +\
          sum(model.VOLL[d]*(1-model.alpha[d])*model.baseMVA*model.PD[d] for d in model.D)
    return obj
model.OBJ = Objective(rule=objective, sense=minimize)

# --- Kirchoff's current law at each bus b ---
def KCL_def(model, b):
    return sum(model.pG[g] for g in model.G if (b,g) in model.Gbs) == \
    sum(model.pD[d] for d in model.D if (b,d) in model.Dbs)+\
    sum(model.pL[l] for l in model.L if model.A[l,1]==b)- \
    sum(model.pL[l] for l in model.L if model.A[l,2]==b)+\
    sum(model.GB[s] for s in model.SHUNT if (b,s) in model.SHUNTbs)
model.KCL_const = Constraint(model.B, rule=KCL_def)

# --- FPN model ---
def Generator_redispatch(model,g):
    return model.pG[g] == model.PG[g]+model.pGUp[g]-model.pGDown[g]

model.RedispatcG = Constraint(model.G, rule=Generator_redispatch)

# --- Kirchoff's voltage law on each line and transformer---
def KVL_line_def(model,l):
    return model.pL[l] == (-model.BL[l])*model.deltaL[l]
model.KVL_line_const     = Constraint(model.L, rule=KVL_line_def)

# --- demand model ---
def demand_model(model,d):
    return model.pD[d] == model.alpha[d]*model.PD[d]
def demand_LS_bound_Max(model,d):
    return model.alpha[d] <= 1
model.demandmodelC = Constraint(model.D, rule=demand_model)
model.demandalphaC = Constraint(model.D, rule=demand_LS_bound_Max)

# --- generator power limits ---
def Real_Power_Max(model,g):
    return model.pG[g] <= model.PGmax[g]
def Real_Power_Min(model,g):
    return model.pG[g] >= model.PGmin[g]

model.PGmaxC = Constraint(model.G, rule=Real_Power_Max)
model.PGminC = Constraint(model.G, rule=Real_Power_Min)


# --- line power limits ---
def line_lim1_def(model,l):
    return model.pL[l] <= model.SLmax[l]
def line_lim2_def(model,l):
    return model.pL[l] >= -model.SLmax[l]
model.line_lim1 = Constraint(model.L, rule=line_lim1_def)
model.line_lim2 = Constraint(model.L, rule=line_lim2_def)

# --- phase angle constraints ---
def phase_angle_diff1(model,l):
    return model.deltaL[l] == model.delta[model.A[l,1]] - \
    model.delta[model.A[l,2]]
model.phase_diff1 = Constraint(model.L, rule=phase_angle_diff1)

# --- reference bus constraint ---
def ref_bus_def(model,b):
    return model.delta[b]==0
model.refbus = Constraint(model.b0, rule=ref_bus_def)
