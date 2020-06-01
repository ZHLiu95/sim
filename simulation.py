import random
import threading
class Simulation:
    def __init__(self,weibull,ssdfail,placement, network, onumgroup,
                 diskpernode,nodeperrack,numrack,
                 mission_time):
        self.weibull = weibull
        self.ssdfail = ssdfail
        self.placement = placement

        self.network = network

        self.onumgroup = onumgroup


        self.numdisk = diskpernode*nodeperrack*numrack
        self.diskpernode = diskpernode
        self.nodeperrack = nodeperrack
        self.numrack = numrack

        self.events_queue = []

        self.grouprack = self.numrack / onumgroup

        self.mission_time = mission_time

    def set_disk_fail(self, disk_id, curr_time):
        disk_per_rack=self.nodeperrack*self.diskpernode
        rackid = int(disk_id/disk_per_rack)
        rackingroup = rackid % self.grouprack
        k = 6
        n = 9
        if rackingroup >= (self.grouprack*k/n):
            fail_time = self.weibull.draw()
            if fail_time+curr_time <= self.mission_time:
                self.events_queue.append((fail_time+curr_time, disk_id, 0))
        else:
            fail_time=self.ssdfail.draw()
            if fail_time+curr_time <= self.mission_time:
                self.events_queue.append((fail_time+curr_time, disk_id, 0))

    def set_node_una(self, node_id, curr_time):
        fail_time = random.weibullvariate(2890.8, 1.0)
        if fail_time + curr_time <= self.mission_time:
            self.events_queue.append((fail_time+curr_time, node_id, 1))

    def set_node_cra(self, node_id, curr_time):
        fail_time = random.weibullvariate(91250., 1.0)
        if fail_time + curr_time <= self.mission_time:
            self.events_queue.append((fail_time+curr_time, node_id, 2))

    def disk_event_append(self):
        disk_per_rack = self.nodeperrack * self.diskpernode

        k = 6
        n = 9
        fail_time=0
        for disk in range(self.numdisk):
            fail_flag = random.random()
            if fail_flag > 0.0:
                rackid = int(disk / disk_per_rack)
                rackingroup = rackid % self.grouprack
                if rackingroup >= (self.grouprack*k/n):
                    fail_time = self.weibull.draw()
                else:
                    fail_time = self.ssdfail.draw()
                if fail_time <= self.mission_time:
                    self.events_queue.append((fail_time, disk, 0))
        #self.events_queue.sort()

    def node_event_append(self):
        num_node = self.nodeperrack*self.numrack
        #print "num_node", num_node
        for nodeid in range (num_node):
            fail_flag=random.random()
            if fail_flag>0.0:
                #for tmp in range (self.diskpernode):
                fail_time = random.weibullvariate(2890.8, 1.0)
                #disk_id = tmp+nodeid*self.diskpernode
                if fail_time <= self.mission_time:
                    self.events_queue.append((fail_time, nodeid, 1))

        for nodeid in range(num_node):
            #for tmp in range (self.diskpernode):
            fail_flag=random.random()
            if fail_flag>0.0:
                fail_time = random.weibullvariate(91250., 1.0)
                   #disk_id = tmp+nodeid*self.diskpernode
                if fail_time <= self.mission_time:
                    self.events_queue.append((fail_time, nodeid, 2))


    def add_event(self, start, end):
        for i in range(start, end):
            fail_flag = random.random()
            if fail_flag > 0.0:
                if self.events_queue[i][2] == 0:
                    self.set_disk_fail(self.events_queue[i][1], self.events_queue[i][0])
                if self.events_queue[i][2] == 1:
                    self.set_node_una(self.events_queue[i][1], self.events_queue[i][0])
                if self.events_queue[i][2] == 2:
                    self.set_node_cra(self.events_queue[i][1], self.events_queue[i][0])
        return end

    def reset(self):
        self.disk_event_append()
        self.node_event_append()
        start = 0
        end = len(self.events_queue)
        while(start < end):
            start = self.add_event(start, end)
            end = len(self.events_queue)
        self.events_queue.sort()

    def get_fail_list(self, max_time, fail_list_disk, fail_list_node, i):
        #print "max_time:", max_time
        qlen = len(self.events_queue)
        while (i < qlen) and (max_time > self.events_queue[i][0]):
            if self.events_queue[i][2] == 1:
                #for j in range(self.diskpernode):
                    #tmp = self.events_queue[i][1] * self.diskpernode + j
                fail_list_node.append(self.events_queue[i])
                i += 1

            elif self.events_queue[i][2] == 0:
                fail_list_disk.append(self.events_queue[i][1])
                i += 1

            elif self.events_queue[i][2] == 2:
                for j in range(self.diskpernode):
                    tmp = self.events_queue[i][1] * self.diskpernode + j
                    fail_list_disk.append(tmp)
                i += 1
        '''
        print "disk",
        print fail_list_disk
        print "node",
        print fail_list_node
        '''
        return i

    def get_delay_time(self, fail_list_node, fail_time, fail_wind):
        add_time = 0.0
        for node in fail_list_node:
            #print "get delay time", fail_list_node, fail_time, fail_wind
            add_time += self.network.delay_time(node[0], fail_time, fail_wind)
            #print "net work"
        #print "add_time:", add_time, fail_time
        return add_time

    def do_disk_fail(self,(fail_time, disk_id, type), index):
        fail_wind = self.network.repair_time()
        #print "fail_wind", fail_wind
        max_time = fail_time+fail_wind
        fail_list_disk = []
        fail_list_node = []
        i = index
        end_event = self.get_fail_list(max_time, fail_list_disk, fail_list_node, i)

        if len(fail_list_disk) < (self.placement.n-self.placement.k):
            data_lost_cra = False
        else:
            data_lost_cra = self.placement.check_data_lost(fail_list_disk)

        una_disk_list = []

        for una_disk in fail_list_node:
            for i in range(self.diskpernode):
                una_disk_list.append(una_disk[1]*self.diskpernode+i)
        for una_disk in fail_list_disk:
            una_disk_list.append(una_disk)

        if len(una_disk_list) < (self.placement.n-self.placement.k):
            data_lost_una = False
        else:
            data_lost_una = self.placement.check_data_lost(una_disk_list)


        if data_lost_cra:
            return (1, max_time)
        if (not data_lost_cra) and data_lost_una:
            curr_delay_time = self.get_delay_time(fail_list_node, fail_time, fail_wind)
            max_time += curr_delay_time
            fail_wind += curr_delay_time
            while 0.0 != curr_delay_time:
                tmp_fail_disk = []
                tmp_fail_node = []

                end_event = self.get_fail_list(max_time, tmp_fail_disk, tmp_fail_node, end_event)
                curr_delay_time = self.get_delay_time(tmp_fail_node, fail_time, fail_wind)

                max_time += curr_delay_time
                fail_wind += curr_delay_time
            fail_list_node = []
            fail_list_disk = []

            self.get_fail_list(max_time, fail_list_disk, fail_list_node, index)

            if self.placement.check_data_lost(fail_list_disk):
                # self.events_queue.pop(0)
                return (1, max_time)
            else:
                return (0, max_time)
        else:
            return (0, max_time)

    def do_node_una(self, (fail_time, node_id, type), index):
        fail_wind = self.network.node_repair_time()
        max_time = fail_time + fail_wind
        fail_disk_list = []
        fail_node_list = []
        i = index

        end_event = self.get_fail_list(max_time, fail_disk_list, fail_node_list, i)

        if len(fail_disk_list) < (self.placement.n-self.placement.k):
            data_lost_cra = False
        else:
            data_lost_cra = self.placement.check_data_lost(fail_disk_list)

        una_disk_list = []
        for una_disk in fail_node_list:
            for i in range(self.diskpernode):
                una_disk_list.append(una_disk[1] * self.diskpernode + i)
        for una_disk in fail_disk_list:
            una_disk_list.append(una_disk)

        if len(una_disk_list) < (self.placement.n-self.placement.k):
            data_lost_una = False
        else:
            data_lost_una = self.placement.check_data_lost(una_disk_list)

        if data_lost_cra:
            return (1, max_time)
        if not data_lost_cra and data_lost_una:
            curr_delay_time = self.get_delay_time(fail_node_list, fail_time, fail_wind)
            max_time += curr_delay_time
            fail_wind += curr_delay_time
            while 0.0 != curr_delay_time:
                tmp_fail_disk = []
                tmp_fail_node = []
                end_event = self.get_fail_list(max_time, tmp_fail_disk, tmp_fail_node, end_event)
                curr_delay_time = self.get_delay_time(tmp_fail_node, fail_time, fail_wind)

                max_time += curr_delay_time
                fail_wind += curr_delay_time

            fail_disk_list = []
            fail_node_list = []
            self.get_fail_list(max_time, fail_disk_list, fail_node_list, index)

            if self.placement.check_data_lost(fail_disk_list):
                # self.events_queue.pop(0)
                return (1, max_time)
            else:
                return (0, max_time)
        return (0, max_time)

    def do_node_cru(self, (fail_time, nodeid, type), index):
        fail_wind = self.network.node_cru_repair_time()
        #print fail_wind
        max_time = fail_time + fail_wind
        fail_list_disk = []
        fail_list_node = []
        i = index
        end_event = self.get_fail_list(max_time, fail_list_disk, fail_list_node, i)

        if len(fail_list_disk) < (self.placement.n-self.placement.k):
            data_lost_cra = False
        else:
            data_lost_cra = self.placement.check_data_lost(fail_list_disk)

        #print data_lost_cra

        una_data_list = []
        for una_node in fail_list_node:
            for i in range(self.diskpernode):
                una_data_list.append(una_node[1]*self.diskpernode+i)
        for una_disk in fail_list_disk:
            una_data_list.append(una_disk)


        if len(una_data_list) < (self.placement.n - self.placement.k):
            data_lost_una = False
        else:
            data_lost_una = self.placement.check_data_lost(una_data_list)

        if data_lost_cra:
            return (1, max_time)
        if (not data_lost_cra) and data_lost_una:
            #print "check point"
            curr_delay_time = self.get_delay_time(fail_list_node, fail_time, fail_wind)
            max_time += curr_delay_time
            fail_wind += curr_delay_time
            #print "maxtime", max_time
            while 0.0 != curr_delay_time:
                tmp_fail_disk = []
                tmp_fail_node = []

                end_event = self.get_fail_list(max_time, tmp_fail_disk, tmp_fail_node, end_event)
                curr_delay_time = self.get_delay_time(tmp_fail_node, fail_time, fail_wind)

                max_time += curr_delay_time
                fail_wind += curr_delay_time
            #print "maxtime2",max_time
            fail_list_node = []
            fail_list_disk = []
            self.get_fail_list(max_time, fail_list_disk, fail_list_node, index)
            #print "fail_list_disk", fail_list_disk
            if self.placement.check_data_lost(fail_list_disk):
                return (1, max_time)
            else:
                return (0, max_time)
        else:
            return (0, max_time)

    def do_event(self, start, end):
        (result, max_time) = (0, 0.0)
        while (start < end) and (result != 1):
            (fail_time, comp_id, type) = self.events_queue[start]
            if type == 0:
                (result, max_time) = self.do_disk_fail((fail_time, comp_id, type), start)
            if type == 1:
                (result, max_time) = self.do_node_una((fail_time, comp_id, type), start)
            if type == 2:
                (result, max_time) = self.do_node_cru((fail_time, comp_id, type), start)
            start += 1
            #print "next event", self.events_queue[start-1]
        #print result, fail_time, comp_id, type, max_time
        #print end
        return (result, fail_time, comp_id, type, max_time, start-1)

    def run(self):
        self.reset()
        (result, fail_time, comp_id, type, max_time, start) = self.do_event(0, len(self.events_queue))
        disk_cra_list = []
        node_una_list = []
        lost_stripes_num = 0
        if result == 1:
            self.get_fail_list(max_time, disk_cra_list, node_una_list, start)
            lost_stripes_num = self.placement.get_lost_strip(disk_cra_list)
        else:
            lost_stripes_num = 0
        return (result, lost_stripes_num)

    def test(self):
        count = 0
        for event in self.events_queue:
            if event[2]==1:
                count+=1
            print event
        print len(self.events_queue), count