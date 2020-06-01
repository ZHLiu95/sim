import random

class Network:
    def __init__(self,num_racks, num_node, onumgroup, group_num, node_per_rack, disk_per_node, band_width, disk_cap, chunk_size, rs_n,rs_k,rs_m):
        self.num_racks = num_racks
        self.num_node = num_node
        self.group_num = group_num*onumgroup
        self.node_per_rack = node_per_rack
        self.disk_per_node = disk_per_node

        self.band_width = band_width
        self.disk_cap = disk_cap

        self.chunk_size = chunk_size
        self.rs_n = rs_n
        self.rs_k = rs_k
        self.rs_m = rs_m

    def repair_time_phase1(self):
        datasize_all = self.disk_cap*self.rs_k
        datasize_pre = datasize_all/((self.num_node-self.node_per_rack)/self.group_num)
        repair_time1 = datasize_pre/self.band_width
        #print repair_time1
        return repair_time1

    def repair_time_phase2(self):
        data_size = self.disk_cap
        repair_time2 = data_size/self.band_width
        return repair_time2

    def repair_time(self):
        repair_time = self.repair_time_phase1()+self.repair_time_phase2()  ###RS()
        #repair_time = self.repair_time_phase2()
        #print repair_time/3600.0
        #print "repair time", repair_time
        return repair_time/3600.0

    def delay_time(self, transient_fail_time, permanently_fail_time, repair_windows):
        #return 3.0
        tran_repair_time = random.weibullvariate(0.25, 1.0)
        #print tran_repair_time
        per_repair_time = repair_windows
        #print per_repair_time
        if(permanently_fail_time + per_repair_time) > (transient_fail_time+tran_repair_time+(self.chunk_size*(self.rs_k+1)/self.band_width/3600)):
           # print 'no eff'
            return 0
        if random.random() < (permanently_fail_time+per_repair_time-transient_fail_time)/per_repair_time:
            #print (permanently_fail_time+per_repair_time-transient_fail_time)/per_repair_time
            return transient_fail_time+tran_repair_time-(permanently_fail_time+per_repair_time)+(self.chunk_size*(self.rs_k+1)/self.band_width/3600)
        else:
            return 0
    def node_repair_time(self):
        return random.weibullvariate(0.25, 1.0)

    def node_cru_phase1(self):
        data_size_all = self.disk_cap*self.disk_per_node*self.rs_k
        data_size_per = data_size_all/self.num_racks
        repair_time1 = data_size_per/self.band_width
        return repair_time1

    def node_cru_phase2(self):
        data_size = self.disk_cap*self.disk_per_node
        repair_time2 = data_size/self.band_width
        return repair_time2

    def node_cru_repair_time(self):
        repair_time =self.node_cru_phase2()
        return repair_time/3600.0

    def test(self):
        print self.repair_time()
        for i in range(20):
            print self.delay_time(1024.0, 1021.5)