import math


class autoDeal:
    def __init__(self, input_seconds):
        self.seconds = input_seconds
        self.last_flows = []
        self.last_flows_set = set()

    def getPPS(self, flow):
        return float(len(flow) / self.seconds)

    def getFER(self, flow):
        last_flows_count = len(self.last_flows_set)
        [self.last_flows_set.update({item[3], item[4]}) for item in flow]
        new_flows_count = len(self.last_flows_set)
        return float(
            (new_flows_count - last_flows_count) / self.seconds), new_flows_count, new_flows_count - last_flows_count

    def getAPPF(self, flow):
        flows_tmp = set()
        [flows_tmp.update({item[3], item[4]}) for item in flow]
        return float(len(flow) / len(flows_tmp))

    def getSFP(self, flow):
        flows_tmp = set()
        [flows_tmp.add((item[3], item[4])) for item in flow]
        address1 = set()
        address2 = set()
        [address1.update(item[0]) for item in flows_tmp]
        [address2.update(item[1]) for item in flows_tmp]
        address2 = address1 - address2
        return float(len(address2) / len(flows_tmp))

    def getPS(self, flow):
        protocols_count = {"tcp": 0.0, "udp": 0.0}
        protocols_type = ["eth:ethertype:ip:tcp", "eth:ethertype:ip:udp"]
        for item in flow:
            if item[2].__contains__("tcp"):
                protocols_count['tcp'] += 1
            elif item[2].__contains__("udp"):
                protocols_count['udp'] += 1
        flows_count = len(flow)
        PS = 0.0
        func = lambda x: (-protocols_count[x] / flows_count) * math.log(protocols_count[x] / flows_count)
        for ki, kv in protocols_count.items():
            if kv != 0:
                PS += func(ki)
        return PS

    def getOthers(self, flows):
        H = 0.0
        sIP = 0.0
        dIP = 0.0
        srcIP = set()
        dstIP = set()
        dstPort = set()
        tmp_flows = set()
        #tmp_flows = set(flows)
        #[tmp_flows.add(item) for item in flows]
        [srcIP.add(item[3]) for item in flows]
        [dstIP.add(item[4]) for item in flows]
        [dstPort.add(item[6]) for item in flows]
        srcList = list(srcIP)
        dstList = list(dstIP)
        portList = list(dstPort)
        dstMap = [0 for i in range(len(dstList))]
        src_dstMap = [dstMap for i in range(len(srcList))]
        for flow in flows:
            if flow[3] in srcList and flow[4] in dstList:
                i = srcList.index(flow[3])
                k = dstList.index(flow[4])
                src_dstMap[i][k] += 1
                dstMap[k] += 1
        for i in range(len(dstList)):
            cover_x = (float(dstMap[i]) / float(len(flows)))
            cover_y = 0.0
            for k in range(len(srcList)):
                if src_dstMap[k][i] != 0 and dstMap[i] != 0:
                    cover_y += float((src_dstMap[k][i] / dstMap[i]) * (math.log(src_dstMap[k][i] / dstMap[i])))
            H += cover_x * cover_y
        H = -H
        dstMap = [0 for i in range(len(dstList))]
        port_dstMap = [dstMap for i in range(len(portList))]
        for flow in flows:
            if flow[6] in portList and flow[4] in dstList:
                i = portList.index(flow[6])
                k = dstList.index(flow[4])
                port_dstMap[i][k] += 1

        for i in range(len(dstList)):
            cover_x = (float(dstMap[i]) / float(len(flows)))
            cover_y = 0.0
            for k in range(len(portList)):
                if src_dstMap[k][i] != 0 and dstMap[i] != 0:
                    cover_y += float((src_dstMap[k][i] / dstMap[i]) * (math.log(src_dstMap[k][i] / dstMap[i])))
            dIP += cover_x * cover_y
        dIP = -dIP

        portMap = [0 for i in range(len(portList))]
        port_srcMap = [portMap for i in range(len(srcList))]

        for flow in flows:
            if flow[3] in srcList and flow[6] in portList:
                i = srcList.index(flow[3])
                k = portList.index(flow[6])
                port_srcMap[i][k] += 1
                portMap[k] += 1

        for i in range(len(portList)):
            cover_x = (float(portMap[i]) / float(len(flows)))
            cover_y = 0.0
            for k in range(len(srcList)):
                if src_dstMap[k][i] != 0 and dstMap[i] != 0:
                    cover_y += float((src_dstMap[k][i] / dstMap[i]) * (math.log(src_dstMap[k][i] / dstMap[i])))
            sIP += cover_x * cover_y
        sIP = -sIP
        return H, sIP, dIP

    def getAttackData(self, path):
        init = 0
        res = []
        result = []
        flag = False
        flows_num = 0
        data_csv = open(path, "r")
        for row in data_csv:
            if not flag:
                flag = True
                continue
            lst = row.split(",")
            timestamp = float(lst[1])
            if init == 0:
                init = timestamp
            res.append(lst)

            if int(timestamp - init) == 1:
                PPS = self.getPPS(res)
                FER, last_flows_num, new_flows_num = self.getFER(res)
                APPF = self.getAPPF(res)
                SFP = self.getSFP(res)
                PS = self.getPS(res)
                H, sIP, dIP = self.getOthers(res)
                result.append((PPS, FER, APPF, SFP, PS, H, sIP, dIP))

                print(result)
                result = []
                res = []
                init = 0



if __name__ == '__main__':
    deal = autoDeal(2)
    deal.getAttackData("attack.csv")
