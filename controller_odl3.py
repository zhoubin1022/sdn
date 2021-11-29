import httplib2
import time
import json


def makeFlowTable(fid, ip_src, ip_dst, output, priority, cookie):
	flow_table = ('{"flow": [{"' + str(fid) + '": "0","match": {"ethernet-match":{"ethernet-type": {"type": "2048"}},'
	+ '"ipv4-source":"' + ip_src + '/32","ipv4-destination": "' + ip_dst + '"},"instructions": {"instruction": [{"order": "0",'
	+ '"apply-actions": {"action": [{"output-action": {"output-node-connector": "' + str(output) + '"},"order": "0"}]}}]},'
	+ '"priority": "' + str(priority) + '","cookie": "' + str(cookie) + '","table_id": "0"}]}')
	return flow_table
#s2和s3下发流表（不变）
s2Ands3_left = '{"flow": [{"id": "0","match": {"ethernet-match":' \
		       '{"ethernet-type": {"type": "2048"}},' \
		       '"ipv4-source":"{ip_src}}/32","ipv4-destination": "{ip_dst}/32"},' \
		       '"instructions": {"instruction": [{"order": "0",' \
		       '"apply-actions": {"action": [{"output-action": {' \
		       '"output-node-connector": "1"},"order": "0"}]}}]},' \
		       '"priority": "101","cookie": "1","table_id": "0"}]}'
s2Ands3_right = '{"flow": [{"id": "1","match": {"ethernet-match":' \
		       '{"ethernet-type": {"type": "2048"}},' \
		       '"ipv4-source":"{ip_src}}/32","ipv4-destination": "{ip_dst}/32"},' \
		       '"instructions": {"instruction": [{"order": "0",' \
		       '"apply-actions": {"action": [{"output-action": {' \
		       '"output-node-connector": "2"},"order": "0"}]}}]},' \
		       '"priority": "101","cookie": "2","table_id": "0"}]}'
#s1的接收流表（不变） id ip_src ip_dst
s1_rcv = '{"flow": [{"id": "{id}","match": {"ethernet-match":' \
		 '{"ethernet-type": {"type": "2048"}},' \
		 '"ipv4-source":"{ip_src}/32","ipv4-destination": "{ip_dst}/32"},' \
		 '"instructions": {"instruction": [{"order": "0",' \
		 '"apply-actions": {"action": [{"output-action": {' \
		 '"output-node-connector": "1"},"order": "0"}]}}]},' \
		 '"priority": "101","cookie": "1","table_id": "0"}]}'
#s4的接收流表（不变）id ip_src ip_dst output
s4_rcv = '{"flow": [{"id": "{id}","match": {"ethernet-match":' \
		 '{"ethernet-type": {"type": "2048"}},' \
		 '"ipv4-source":"{ip_src}/32","ipv4-destination": "{ip_dst}/32"},' \
		 '"instructions": {"instruction": [{"order": "0",' \
		 '"apply-actions": {"action": [{"output-action": {' \
		 '"output-node-connector": "{output}"},"order": "0"}]}}]},' \
		 '"priority": "101","cookie": "1","table_id": "0"}]}'
#s4的发送流表（变化） id:默认与端口 ip_src ip_dst output
s4_send = '{"flow": [{"id": "{id}","match": {"ethernet-match":' \
		  '{"ethernet-type": {"type": "2048"}},' \
		  '"ipv4-source":"{ip_src}/32","ipv4-destination": "{ip_dst}/32"},' \
		  '"instructions": {"instruction": [{"order": "0",' \
		  '"apply-actions": {"action": [{"output-action": {' \
		  '"output-node-connector": "{output}"},"order": "0"}]}}]},' \
		  '"priority": "101","cookie": "1","table_id": "0"}]}'
#id:默认与端口 ip_src ip_dst output
ms4_send = '{"flow": [{"id": "{id}","match": {"ethernet-match":' \
		   '{"ethernet-type": {"type": "2048"}},' \
		   '"ipv4-source":"{ip_src}/32","ipv4-destination": "{ip_dst}/32"},' \
		   '"instructions": {"instruction": [{"order": "0",' \
		   '"apply-actions": {"action": [{"output-action": {' \
		   '"output-node-connector": "{output}"},"order": "0"}]}}]},' \
		   '"priority": "100","cookie": "3","table_id": "0"}]}'

#s1的发送流表（变化）id:默认与端口 ip_src ip_dst output
s1_send = '{"flow": [{"id": "{id}","match": {"ethernet-match":' \
		  '{"ethernet-type": {"type": "2048"}},' \
		  '"ipv4-source":"{ip_src}/32","ipv4-destination": "{ip_dst}/32"},' \
		  '"instructions": {"instruction": [{"order": "0",' \
		  '"apply-actions": {"action": [{"output-action": {' \
		  '"output-node-connector": "{output}"},"order": "0"}]}}]},' \
		  '"priority": "101","cookie": "2","table_id": "0"}]}'
#id:默认与端口 ip_src ip_dst output
ms1_send = '{"flow": [{"id": "{id}","match": {"ethernet-match":' \
		   '{"ethernet-type": {"type": "2048"}},' \
		   '"ipv4-source":"{ip_src}/32","ipv4-destination": "{ip_dst}/32"},' \
		   '"instructions": {"instruction": [{"order": "0",' \
		   '"apply-actions": {"action": [{"output-action": {' \
		   '"output-node-connector": "{output}"},"order": "0"}]}}]},' \
		   '"priority": "100","cookie": "3","table_id": "0"}]}'

class OdlUtil:
	url = ''

	def __init__(self, host, port):
		self.url = 'http://' + host + ':' + str(port)

	def install_flow(self, container_name='default', username="admin", password="admin"):
		http = httplib2.Http()
		http.add_credentials(username, password)
		headers = {'Accept': 'application/json'}
		flow_name = 'flow_' + str(int(time.time() * 1000))

		headers = {'Content-type': 'application/json'}
		num = 0
		# 下发流表，地址由ODL上获得
		# 下发s1的接收流表

		for i in range(3): #0-2->接收流表
			response, content = http.request(
				uri='http://127.0.0.1:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:1/flow-node-inventory:table/0/flow/' + str(i),
				body=makeFlowTable(fid=i, ip_src='10.0.0.' + str(i + 2), ip_dst='10.0.0.1', output=1, priority=101, cookie=1), method='PUT', headers=headers)
		#下发s4的接收流表
		for i in range(3): #0-2-》接收流表
			response, content = http.request(
				uri='http://127.0.0.1:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:4/flow-node-inventory:table/0/flow/' + str(i),
				body=makeFlowTable(fid=i, ip_src='10.0.0.1', ip_dst='10.0.0.' + str(i + 2), output=i + 4, priority=101, cookie=1), method='PUT', headers=headers)
		#下发s2流表
		for i in range(3):
			response, content = http.request(
				uri='http://127.0.0.1:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:2/flow-node-inventory:table/0/flow/' + str(i),
				body=makeFlowTable(fid=i, ip_src='10.0.0.1', ip_dst='10.0.0.' + str(i + 2), output=2, priority=101, cookie=2), method='PUT', headers=headers)
		for i in range(3, 6):
			response, content = http.request(
				uri='http://127.0.0.1:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:2/flow-node-inventory:table/0/flow/' + str(i),
				body=makeFlowTable(fid=i, ip_src='10.0.0.' + str(i - 1), ip_dst='10.0.0.1', output=1, priority=101, cookie=1), method='PUT', headers=headers)
		#下发s3流表
		for i in range(3):
			response, content = http.request(
				uri='http://127.0.0.1:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:3/flow-node-inventory:table/0/flow/' + str(
					i),
				body=makeFlowTable(fid=i, ip_src='10.0.0.1', ip_dst='10.0.0.' + str(i + 2), output=2, priority=101,
				                   cookie=2), method='PUT', headers=headers)
		for i in range(3, 6):
			response, content = http.request(
				uri='http://127.0.0.1:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:3/flow-node-inventory:table/0/flow/' + str(
					i),
				body=makeFlowTable(fid=i, ip_src='10.0.0.' + str(i - 1), ip_dst='10.0.0.1', output=1, priority=101,
				                   cookie=1), method='PUT', headers=headers)

		while num < 4:
			s1_uri_1 = 'http://127.0.0.1:8181/restconf/operational/opendaylight-inventory:nodes/node/openflow:1/node-connector/openflow:1:4'
			s1_uri_2 = 'http://127.0.0.1:8181/restconf/operational/opendaylight-inventory:nodes/node/openflow:1/node-connector/openflow:1:2'
			s4_uri_1 = 'http://127.0.0.1:8181/restconf/operational/opendaylight-inventory:nodes/node/openflow:4/node-connector/openflow:4:1'
			s4_uri_2 = 'http://127.0.0.1:8181/restconf/operational/opendaylight-inventory:nodes/node/openflow:4/node-connector/openflow:4:2'
			# 获取s1端口2的流量
			response1, content1 = http.request(uri=s1_uri_1, method='GET')
			response2, content2 = http.request(uri=s1_uri_2, method='GET')
			content1 = json.loads(content1.decode())
			content2 = json.loads(content2.decode())
			statistics1 = content1['node-connector'][0][
				'opendaylight-port-statistics:flow-capable-node-connector-statistics']
			statistics2 = content2['node-connector'][0][
				'opendaylight-port-statistics:flow-capable-node-connector-statistics']
			s1_bytes1_1 = statistics1['bytes']['transmitted']
			s1_bytes1_2 = statistics2['bytes']['transmitted']
			# 0.5秒后再次获取
			time.sleep(0.5)
			response1, content1 = http.request(uri=s1_uri_1, method='GET')
			response2, content2 = http.request(uri=s1_uri_2, method='GET')
			content1 = json.loads(content1.decode())
			content2 = json.loads(content2.decode())
			statistics1 = content1['node-connector'][0][
				'opendaylight-port-statistics:flow-capable-node-connector-statistics']
			statistics2 = content2['node-connector'][0][
				'opendaylight-port-statistics:flow-capable-node-connector-statistics']
			s1_bytes2_1 = statistics1['bytes']['transmitted']
			s1_bytes2_2 = statistics2['bytes']['transmitted']

			s1_speed1 = float(s1_bytes2_1 - s1_bytes1_1) / 0.5
			s1_speed2 = float(s1_bytes2_2 - s1_bytes1_2) / 0.5

			if s1_speed1 != 0:  # 获取有效的速度
				print('s1端口4速度：')
				print(s1_speed1)
				print('s1端口2速度：')
				print(s1_speed2)
				# 在检测到s1端口2流量空闲时发的流表
				if s1_speed1 < 500:
					print(' s1端口4空闲，数据包改为往s1端口4通过')
					response, content = http.request(
						uri='http://127.0.0.1:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:1/flow-node-inventory:table/0/flow/3',
						body=makeFlowTable(fid=3, ip_src='i0.0.0.1', ip_dst='10.0.0.2', output=4, priority=101,
						                   cookie=2), method='PUT', headers=headers)
					response, content = http.request(
						uri='http://127.0.0.1:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:1/flow-node-inventory:table/0/flow/4',
						body=makeFlowTable(fid=4, ip_src='i0.0.0.1', ip_dst='10.0.0.3', output=4, priority=101,
						                   cookie=2), method='PUT', headers=headers)
					response, content = http.request(
						uri='http://127.0.0.1:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:1/flow-node-inventory:table/0/flow/5',
						body=makeFlowTable(fid=5, ip_src='i0.0.0.1', ip_dst='10.0.0.4', output=4, priority=101,
						                   cookie=2), method='PUT', headers=headers)
					response, content = http.request(
						uri='http://127.0.0.1:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:1/flow-node-inventory:table/0/flow/6',
						body=makeFlowTable(fid=6, ip_src='i0.0.0.1', ip_dst='10.0.0.2', output=4, priority=100,
						                   cookie=3), method='PUT', headers=headers)
					response, content = http.request(
						uri='http://127.0.0.1:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:1/flow-node-inventory:table/0/flow/7',
						body=makeFlowTable(fid=7, ip_src='i0.0.0.1', ip_dst='10.0.0.3', output=4, priority=100,
						                   cookie=3), method='PUT', headers=headers)
					response, content = http.request(
						uri='http://127.0.0.1:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:1/flow-node-inventory:table/0/flow/8',
						body=makeFlowTable(fid=8, ip_src='i0.0.0.1', ip_dst='10.0.0.4', output=4, priority=100,
						                   cookie=3), method='PUT', headers=headers)
				# 在检测到s1端口2流量满载时发的流表
				elif s1_speed1 >= 500 and s1_speed2 < 500:
					print(' s1端口4满载，数据包改为往s1端口2通过')
					response, content = http.request(
						uri='http://127.0.0.1:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:1/flow-node-inventory:table/0/flow/3',
						body=makeFlowTable(fid=3, ip_src='i0.0.0.1', ip_dst='10.0.0.2', output=2, priority=101,
						                   cookie=2), method='PUT', headers=headers)
					response, content = http.request(
						uri='http://127.0.0.1:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:1/flow-node-inventory:table/0/flow/4',
						body=makeFlowTable(fid=4, ip_src='i0.0.0.1', ip_dst='10.0.0.3', output=2, priority=101,
						                   cookie=2), method='PUT', headers=headers)
					response, content = http.request(
						uri='http://127.0.0.1:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:1/flow-node-inventory:table/0/flow/5',
						body=makeFlowTable(fid=5, ip_src='i0.0.0.1', ip_dst='10.0.0.4', output=4, priority=101,
						                   cookie=2), method='PUT', headers=headers)
					response, content = http.request(
						uri='http://127.0.0.1:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:1/flow-node-inventory:table/0/flow/6',
						body=makeFlowTable(fid=6, ip_src='i0.0.0.1', ip_dst='10.0.0.2', output=2, priority=100,
						                   cookie=3), method='PUT', headers=headers)
					response, content = http.request(
						uri='http://127.0.0.1:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:1/flow-node-inventory:table/0/flow/7',
						body=makeFlowTable(fid=7, ip_src='i0.0.0.1', ip_dst='10.0.0.3', output=2, priority=100,
						                   cookie=3), method='PUT', headers=headers)
					response, content = http.request(
						uri='http://127.0.0.1:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:1/flow-node-inventory:table/0/flow/8',
						body=makeFlowTable(fid=8, ip_src='i0.0.0.1', ip_dst='10.0.0.4', output=4, priority=100,
						                   cookie=3), method='PUT', headers=headers)
				else:
					print(' s1端口2满载，数据包改为往s1端口3通过')
					response, content = http.request(
						uri='http://127.0.0.1:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:1/flow-node-inventory:table/0/flow/3',
						body=makeFlowTable(fid=3, ip_src='i0.0.0.1', ip_dst='10.0.0.2', output=2, priority=101,
						                   cookie=2), method='PUT', headers=headers)
					response, content = http.request(
						uri='http://127.0.0.1:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:1/flow-node-inventory:table/0/flow/4',
						body=makeFlowTable(fid=4, ip_src='i0.0.0.1', ip_dst='10.0.0.3', output=3, priority=101,
						                   cookie=2), method='PUT', headers=headers)
					response, content = http.request(
						uri='http://127.0.0.1:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:1/flow-node-inventory:table/0/flow/5',
						body=makeFlowTable(fid=5, ip_src='i0.0.0.1', ip_dst='10.0.0.4', output=4, priority=101,
						                   cookie=2), method='PUT', headers=headers)
					response, content = http.request(
						uri='http://127.0.0.1:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:1/flow-node-inventory:table/0/flow/6',
						body=makeFlowTable(fid=6, ip_src='i0.0.0.1', ip_dst='10.0.0.2', output=2, priority=100,
						                   cookie=3), method='PUT', headers=headers)
					response, content = http.request(
						uri='http://127.0.0.1:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:1/flow-node-inventory:table/0/flow/7',
						body=makeFlowTable(fid=7, ip_src='i0.0.0.1', ip_dst='10.0.0.3', output=3, priority=100,
						                   cookie=3), method='PUT', headers=headers)
					response, content = http.request(
						uri='http://127.0.0.1:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:1/flow-node-inventory:table/0/flow/8',
						body=makeFlowTable(fid=8, ip_src='i0.0.0.1', ip_dst='10.0.0.4', output=4, priority=100,
						                   cookie=3), method='PUT', headers=headers)


			# 获取s2端口1的流量
			response1, content1 = http.request(uri=s4_uri_1, method='GET')
			response2, content2 = http.request(uri=s4_uri_2, method='GET')
			content1 = json.loads(content1.decode())
			content2 = json.loads(content2.decode())
			statistics1 = content1['node-connector'][0][
				'opendaylight-port-statistics:flow-capable-node-connector-statistics']
			statistics2 = content2['node-connector'][0][
				'opendaylight-port-statistics:flow-capable-node-connector-statistics']
			s4_bytes1_1 = statistics1['bytes']['transmitted']
			s4_bytes1_2 = statistics2['bytes']['transmitted']
			# 0.5秒后再次获取
			time.sleep(0.5)
			response1, content1 = http.request(uri=s4_uri_1, method='GET')
			response2, content2 = http.request(uri=s4_uri_2, method='GET')
			content1 = json.loads(content1.decode())
			content2 = json.loads(content2.decode())
			statistics1 = content1['node-connector'][0][
				'opendaylight-port-statistics:flow-capable-node-connector-statistics']
			statistics2 = content2['node-connector'][0][
				'opendaylight-port-statistics:flow-capable-node-connector-statistics']
			s4_bytes2_1 = statistics1['bytes']['transmitted']
			s4_bytes2_2 = statistics2['bytes']['transmitted']

			s4_speed1 = float(s4_bytes2_1 - s4_bytes1_1) / 0.5
			s4_speed2 = float(s4_bytes2_2 - s4_bytes1_2) / 0.5

			if s4_speed1 != 0 and s4_speed2 != 0:  # 获取有效的速度
				print('s4端口1速度：')
				print(s4_speed1)
				print('s4端口2速度：')
				print(s4_speed2)
				if s4_speed1 < 500:
					print(' s4端口1空闲，数据包改为往s4端口1通过')
					response, content = http.request(
						uri='http://127.0.0.1:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:4/flow-node-inventory:table/0/flow/3',
						body=makeFlowTable(fid=3, ip_src='i0.0.0.2', ip_dst='10.0.0.1', output=1, priority=101,
						                   cookie=1), method='PUT', headers=headers)
					response, content = http.request(
						uri='http://127.0.0.1:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:4/flow-node-inventory:table/0/flow/4',
						body=makeFlowTable(fid=4, ip_src='i0.0.0.3', ip_dst='10.0.0.1', output=1, priority=101,
						                   cookie=1), method='PUT', headers=headers)
					response, content = http.request(
						uri='http://127.0.0.1:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:4/flow-node-inventory:table/0/flow/5',
						body=makeFlowTable(fid=5, ip_src='i0.0.0.4', ip_dst='10.0.0.1', output=1, priority=101,
						                   cookie=1), method='PUT', headers=headers)
					response, content = http.request(
						uri='http://127.0.0.1:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:4/flow-node-inventory:table/0/flow/6',
						body=makeFlowTable(fid=6, ip_src='i0.0.0.2', ip_dst='10.0.0.1', output=1, priority=100,
						                   cookie=3), method='PUT', headers=headers)
					response, content = http.request(
						uri='http://127.0.0.1:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:4/flow-node-inventory:table/0/flow/7',
						body=makeFlowTable(fid=7, ip_src='i0.0.0.3', ip_dst='10.0.0.1', output=1, priority=100,
						                   cookie=3), method='PUT', headers=headers)
					response, content = http.request(
						uri='http://127.0.0.1:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:4/flow-node-inventory:table/0/flow/8',
						body=makeFlowTable(fid=8, ip_src='i0.0.0.4', ip_dst='10.0.0.1', output=1, priority=100,
						                   cookie=3), method='PUT', headers=headers)
				# 在检测到s2端口1流量满载时发的流表
				elif s4_speed1 >= 500 and s4_speed2 < 500:
					print(' s4端口1满载，数据包改为往s4端口2通过')
					response, content = http.request(
						uri='http://127.0.0.1:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:4/flow-node-inventory:table/0/flow/3',
						body=makeFlowTable(fid=3, ip_src='i0.0.0.2', ip_dst='10.0.0.1', output=1, priority=101,
						                   cookie=1), method='PUT', headers=headers)
					response, content = http.request(
						uri='http://127.0.0.1:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:4/flow-node-inventory:table/0/flow/4',
						body=makeFlowTable(fid=4, ip_src='i0.0.0.3', ip_dst='10.0.0.1', output=2, priority=101,
						                   cookie=1), method='PUT', headers=headers)
					response, content = http.request(
						uri='http://127.0.0.1:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:4/flow-node-inventory:table/0/flow/5',
						body=makeFlowTable(fid=5, ip_src='i0.0.0.4', ip_dst='10.0.0.1', output=2, priority=101,
						                   cookie=1), method='PUT', headers=headers)
					response, content = http.request(
						uri='http://127.0.0.1:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:4/flow-node-inventory:table/0/flow/6',
						body=makeFlowTable(fid=6, ip_src='i0.0.0.2', ip_dst='10.0.0.1', output=1, priority=100,
						                   cookie=3), method='PUT', headers=headers)
					response, content = http.request(
						uri='http://127.0.0.1:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:4/flow-node-inventory:table/0/flow/7',
						body=makeFlowTable(fid=7, ip_src='i0.0.0.3', ip_dst='10.0.0.1', output=2, priority=100,
						                   cookie=3), method='PUT', headers=headers)
					response, content = http.request(
						uri='http://127.0.0.1:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:4/flow-node-inventory:table/0/flow/8',
						body=makeFlowTable(fid=8, ip_src='i0.0.0.4', ip_dst='10.0.0.1', output=2, priority=100,
						                   cookie=3), method='PUT', headers=headers)
				else:
					print(' s4端口2满载，数据包改为往s4端口3通过')
					response, content = http.request(
						uri='http://127.0.0.1:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:4/flow-node-inventory:table/0/flow/3',
						body=makeFlowTable(fid=3, ip_src='i0.0.0.2', ip_dst='10.0.0.1', output=1, priority=101,
						                   cookie=1), method='PUT', headers=headers)
					response, content = http.request(
						uri='http://127.0.0.1:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:4/flow-node-inventory:table/0/flow/4',
						body=makeFlowTable(fid=4, ip_src='i0.0.0.3', ip_dst='10.0.0.1', output=2, priority=101,
						                   cookie=1), method='PUT', headers=headers)
					response, content = http.request(
						uri='http://127.0.0.1:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:4/flow-node-inventory:table/0/flow/5',
						body=makeFlowTable(fid=5, ip_src='i0.0.0.4', ip_dst='10.0.0.1', output=3, priority=101,
						                   cookie=1), method='PUT', headers=headers)
					response, content = http.request(
						uri='http://127.0.0.1:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:4/flow-node-inventory:table/0/flow/6',
						body=makeFlowTable(fid=6, ip_src='i0.0.0.2', ip_dst='10.0.0.1', output=1, priority=100,
						                   cookie=3), method='PUT', headers=headers)
					response, content = http.request(
						uri='http://127.0.0.1:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:4/flow-node-inventory:table/0/flow/7',
						body=makeFlowTable(fid=7, ip_src='i0.0.0.3', ip_dst='10.0.0.1', output=2, priority=100,
						                   cookie=3), method='PUT', headers=headers)
					response, content = http.request(
						uri='http://127.0.0.1:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:4/flow-node-inventory:table/0/flow/8',
						body=makeFlowTable(fid=8, ip_src='i0.0.0.4', ip_dst='10.0.0.1', output=3, priority=100,
						                   cookie=3), method='PUT', headers=headers)


odl = OdlUtil('127.0.0.1', '8181')
odl.install_flow()