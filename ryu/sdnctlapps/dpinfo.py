from ryu.base import app_manager
from ryu.controller import ofp_event, dpset
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib import dpid as dpid_lib
import requests

class DPinfo(app_manager.RyuApp):

    @set_ev_cls(dpset.EventDP, CONFIG_DISPATCHER)
    def multidatapathswitch_register(self, dp, enter_leave=True):
        dpid = dp.dp.id
        sw_id = dpid_lib.dpid_to_str(dpid)
        sw_id = dpid_lib.dpid_to_str(dpid)
        if enter_leave:
            requests.post("http://0.0.0.0:3798/register/dp", data={
                    'code': sw_id,
                    'ports': ";".join([port.name for port in dp.ports])
                    })  
        else:
            requests.post("http://0.0.0.0:3798/unregister/dp", data={
                    'code': sw_id,
                    'ports': ";".join([port.name for port in dp.ports])
                    })  
