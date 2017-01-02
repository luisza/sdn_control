import requests

CONTROLLER_PORT = 3798
OVS_PORT = 3698
HTTP_PROTOCOL = "http:"


def start_controller(net, controller):
    url = "%s//%s:%d/controller/create/%d" % (HTTP_PROTOCOL,
                                              controller.control_ip,
                                              CONTROLLER_PORT,
                                              controller.pk)
    print(url)

    requests.get(url)


def stop_controller(net, controller):
    requests.get("%s//%s:%d/controller/delete/%d" %
                 (HTTP_PROTOCOL,
                  controller.control_ip,
                  CONTROLLER_PORT,
                  controller.pk))


def create_bridges(net, ovs, pk):
    url = "%s//%s:%s/bridge/create/%d/%d" % (
        HTTP_PROTOCOL,
        ovs.control_ip,
        OVS_PORT,
        net,
        pk
    )
    requests.get(url)
