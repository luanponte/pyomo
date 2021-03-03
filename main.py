# --- Requisitos ---
# pip3 install pyomo
# pip3 install pandas
# pip3 install openpyxl
# apt-get install -y -qq coinor-cbc 

import pandas as pd
import pyomo.environ as pyo
from pyomo.opt import SolverFactory

produtos = pd.read_excel('./xlsx/produtos.xlsx')
recursos = pd.read_excel('./xlsx/recursos.xlsx')
consumos = pd.read_excel('./xlsx/consumos.xlsx')

consumos.set_index(['produto', 'recurso']).consumo.to_dict()

model = pyo.ConcreteModel() 

model.Produtos = pyo.Set(initialize=produtos.nome)
model.Recursos = pyo.Set(initialize=recursos.nome)

model.lucro = pyo.Param(model.Produtos, initialize=produtos.set_index('nome').lucro.to_dict())
model.capacidade = pyo.Param(model.Recursos, initialize=recursos.set_index('nome').capacidade.to_dict())
model.consumo = pyo.Param(model.Produtos, model.Recursos, initialize=consumos.set_index(['produto', 'recurso']).consumo.to_dict())

model.x = pyo.Var(model.Produtos, within=pyo.NonNegativeReals)

model.objetivo = pyo.Objective(expr=sum(model.lucro[i] * model.x[i] for i in model.Produtos), sense=pyo.maximize)

model.restricao = pyo.ConstraintList()
for j in model.Recursos:
  model.restricao.add(sum(model.consumo[i, j] * model.x[i] for i in model.Produtos) <= model.capacidade[j])

solver = SolverFactory('cbc')

solver.solve(model)
model.display()

resultado = pd.DataFrame({'Produto': [i for i in model.Produtos],
              'Quantidade produzida': [model.x[i].value for i in model.Produtos]})
resultado.loc[resultado['Quantidade produzida'] > 0]
