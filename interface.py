import json
import subprocess
import time
import httplib2
import numpy as np
import pandas as pd
import requests
import torch
import os
from torch.utils.data import DataLoader
from flask import Flask, request, app, Response
from flask_cors import *

from utils import autoDeal
app = Flask(__name__)
CORS(app, resources=r'/*', supports_credentials=True)
# supports_credentials=True
port = [
    {"switch": 1, "port": 1},
    {"switch": 1, "port": 2},
    {"switch": 1, "port": 3},
    {"switch": 1, "port": 4},
    {"switch": 2, "port": 2},
    {"switch": 3, "port": 2},
    {"switch": 4, "port": 4},
    {"switch": 4, "port": 5},
    {"switch": 4, "port": 6},
]
host_switch_port = [
    {"switch": 1, "port": 1},
    {"switch": 4, "port": 4},
    {"switch": 4, "port": 5},
    {"switch": 4, "port": 6}
]


@app.route("/getTopo", methods=["GET"])
@cross_origin(supports_credentials=True)
def getTopo():
    t_json = {
        "hosts": [
            {"name": "h1", "ip": "10.0.0.1", "cover": 32, "id": "1"},
            {"name": "h2", "ip": "10.0.0.2", "cover": 32, "id": "2"},
            {"name": "h3", "ip": "10.0.0.3", "cover": 32, "id": "3"},
            {"name": "h4", "ip": "10.0.0.4", "cover": 32, "id": "4"}
        ],
        "switchs": [
            {"name": "s1", "id": "openflow1"},
            {"name": "s2", "id": "openflow2"},
            {"name": "s3", "id": "openflow3"},
            {"name": "s4", "id": "openflow4"}
        ],
        "links": [
            {"one": "s1", "other": "h1", "one_port": 1, "other_port": 1, "id": 1},
            {"one": "s1", "other": "s2", "one_port": 2, "other_port": 1, "id": 2},
            {"one": "s1", "other": "s3", "one_port": 3, "other_port": 1, "id": 3},
            {"one": "s1", "other": "s4", "one_port": 4, "other_port": 1, "id": 4},
            {"one": "s2", "other": "s4", "one_port": 2, "other_port": 2, "id": 5},
            {"one": "s3", "other": "s4", "one_port": 2, "other_port": 3, "id": 6},
            {"one": "s4", "other": "h2", "one_port": 4, "other_port": 1, "id": 7},
            {"one": "s4", "other": "h3", "one_port": 5, "other_port": 1, "id": 8},
            {"one": "s4", "other": "h4", "one_port": 6, "other_port": 1, "id": 9}
        ]
    }
    return Response(json.dumps(t_json, ensure_ascii=False), mimetype='application/json')


@app.route("/getSpeed", methods=["GET"])
@cross_origin(supports_credentials=True)
def getSpeed():
    data_1 = []
    data_2 = []
    speed = []
    for i in range(9):
        data_1.append(getData(i))
    time.sleep(2)
    for i in range(9):
        data_2.append(getData(i))
    print(data_1)
    print(data_2)
    for i in range(9):
        speed.append(float(data_2[i] - data_1[i]) / 2.16)
    return Response(json.dumps({"speed": speed}, ensure_ascii=False), mimetype='application/json')


def getData(link_id):
    http = httplib2.Http()
    http.add_credentials("admin", "admin")
    headers = {'Accept': 'application/json'}
    flow_name = 'flow_' + str(int(time.time() * 1000))

    headers = {'Content-type': 'application/json'}
    switch_id = port[link_id]['switch']
    port_id = port[link_id]['port']
    uri = f'http://127.0.0.1:8181/restconf/operational/opendaylight-inventory:nodes/node/openflow:{switch_id}/node-connector/openflow:{switch_id}:{port_id}'
    # print(uri)
    # response, content = requests.get(url=uri)
    response, content = http.request(uri=uri, method='GET')
    # print(response, content)
    content = json.loads(content.decode())
    statistics = content['node-connector'][0][
        'opendaylight-port-statistics:flow-capable-node-connector-statistics']
    byte = statistics['bytes']['transmitted']
    return byte


@app.route("/getHost", methods=["POST"])
@cross_origin(supports_credentials=True)
def getHost():
    if os.path.exists("attack.csv"):
        os.remove("attack.csv")
    if os.path.exists("view_history.pcap"):
        os.remove("view_history.pcap")
    host_id = int(request.form['host_id'])
    if not host_id:
        return Response(json.dumps({"message": "wrong"}, ensure_ascii=False), mimetype='application/json')
    string = 's' + str(host_switch_port[host_id-1]['switch']) + '-eth' + str(host_switch_port[host_id-1]['port'])
    # subprocess.run('sh dump.sh {}'.format(string), cwd='/home/jiang/sdn/', shell=True)
    # 第一次运行时需要输入密码
    os.system("sudo sh dump.sh {}".format(string))
    time.sleep(10)
    os.system("sudo sh load.sh {}")
    # subprocess.run('sh load.sh', cwd='/home/jiang/sdn/', shell=True)
    return Response(json.dumps({"message": "success"}, ensure_ascii=False), mimetype='application/json')

@app.route("/odl", methods=["GET"])
@cross_origin(supports_credentials=True)
def odl():
    # subprocess.Popen('python controller_odl3.py', cwd='/home/jiang/sdn/sdn/', shell=True)
    subprocess.call(["xterm", "-e", "python controller_odl3.py"])
    return Response(json.dumps({}, ensure_ascii=False), mimetype='application/json')
@app.route("/judge", methods=["POST"])
@cross_origin(supports_credentials=True)
def judge():
    host_id = request.form['host_id']
    model = torch.load('model.pt', map_location='cpu')
    deal = autoDeal(2)
    lst = deal.getAttackData("attack.csv")
    data = pd.DataFrame(lst)
    x = torch.FloatTensor(np.array(data.iloc[:, 0:8]))
    flag = False
    for item in x.data:
        pre_y = model(item)
        if pre_y <= 0.5:
            flag = True
            break       
    return Response(json.dumps({"isAttacking": flag}, ensure_ascii=False), mimetype='application/json')


if __name__ == "__main__":
    app.run(host='0.0.0.0', threaded=True, debug=True)
    CORS(app)


