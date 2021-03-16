# from qcodes.tests.instrument_mocks import DummyInstrument

# from functools import partial
import numpy as np

# from simulations.pixel_array_sim_2 import pixelarrayQPC
# from optimization.newpoint import new_point
from optimization.cma import optimize_cma
from lossfunctions.staircasiness import staircasiness
from datahandling.datahandling import datahandler

import matplotlib.pyplot as plt
import time

# from qcodes.dataset.experiment_container import new_experiment
# from qcodes.dataset.database import initialise_database
# from qcodes.dataset.measurements import Measurement

from triton7.pixel_sweep import sweep_gates
from optimization.newpoint import new_point,simple_new_point

# bounds=[(-0.1,0)]*9
bounds=(-0.1,0.1)
pfactor=0.001

start=-0.22
stop=-0.12
points=100
wait=0.05
# start1=-0.56
# stop1=-0.5
# start2=-0.32
# stop2=-0.26
# points=100
# wait=0.1

vals=np.linspace(start,stop,points)
# vals1=np.linspace(start1,stop1,points)
# vals2=np.linspace(start2,stop2,points)

# set bias on 1 ohmic with qdac
# qdac2.BNC24(0.001)


stairs=staircasiness(delta=0.05,last_step=20)
# QPC=pixelarrayQPC()
dat=datahandler('QCODESCHECK')



# def Conductance_get():
#     voltage=lockin2.X()/100
#     current=lockin3.X()*1e-7
#     if current==0:
#         current=np.nan
#     return 1/((voltage/current)/25.8125e3)

# Conductance = qc.Parameter(name='g',label='Conductance',unit=r'$e^2/h$', get_cmd=Conductance_get)


pixel_gates=[qdac2.BNC10,
             qdac2.BNC12,
             qdac2.BNC14,
             qdac2.BNC4,
             qdac2.BNC16,
             qdac2.BNC49,
             qdac2.BNC2,
             qdac2.BNC50,
             qdac2.BNC46]


# param_sets=[bottom_gates_pixel,top_gates_pixel]
outer_gates_pixel(-0.19)


def func_to_minimize(x,foldername):
    """
    Parameters
    ----------
    x : Optimization parameters, 
    foldername : data saving folder, for saving dataids of individual runs

    Returns
    -------
    loss : loss of this particular set of parameters.

    """
    
    # x_projected,penalty=simple_new_point(x,bounds=bounds)
    x_projected,penalty=new_point(x,bounds=bounds)
    # for i,val in enumerate(x_projected):
    #     if val>0:
    #         x_projected[i]=0
    # if x_projected<=-0.2:
    #     raise 
    # for i,gate in enumerate(pixel_gates):
    #     gate(x_projected[i])
    
    # vals_x=np.vstack((vals1,vals2)).T
    vals_x=(x_projected[:,np.newaxis]+vals).T

    
    result,dataid=sweep_gates(param_sets=pixel_gates,param_set_vals=vals_x,delay=wait,param_meas=Ithaco_lockin) #outer gate1, outer gate2, opt params for registering custom parameters, start,stop,number,delay and measurement param
    
    loss=pfactor*penalty+stairs.deriv_metric(result)
    with open(foldername+'dataids.txt','a+') as file:
        file.write('dataid={}, loss={}\n'.format(dataid,loss) + str(x_projected)+'\n')
        # file.write()
    
    return loss



xbest=optimize_cma(func_to_minimize,dat,maxfevals=150,sigma=0.5,start_point=np.zeros(9),time_stop=100)
    
# all_gates_pixel(0)

def custom_plot_by_id(dataid):
    data=load_by_id(dataid)
    Conductance=data.get_parameter_data('g')['g']['g']
    # gates=all_data['Ithaco']['qdac2_BNC1']
    # V43=all_data['Ithaco']['qdac2_BNC2']
    # tilt=all_data['Ithaco']['tilt'][0]
    # middle_gate=all_data['Ithaco']['middle_gate'][0]
    
    # Ithaco=all_data['Ithaco']['Ithaco']
    
    # avg=(V38+V43)/2
    
    fig,ax=plt.subplots()
    ax.plot(Conductance)
    # ax.plot(avg,Ithaco)
    # ax.set_title("#:{} tilt:{:.4f}, middle gate: {:.4f}".format(dataid,tilt,middle_gate),fontsize=15)
    # ax.set_xlabel('outer gate voltage 38&43[V]',fontsize=15)
    ax.set_ylabel('Conductance',fontsize=15)
    ax.grid('on')
    # plt.savefig("F:/qcodes_data/BBQPC_2021/figures/optimization_test2.pdf",format='pdf')
    fig.show()



# for dataid in np.arange(628,639):
#     custom_plot_by_id(dataid)
    
