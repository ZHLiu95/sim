from placement import Placement
import random
from network import Network
from smp_data_structures import test,Weibull,SSD_fail
from simulation import Simulation

import sys, getopt
import multiprocessing
#import fcntl
import time

def get_lost_disk(numdisk, lostdisk):
    if lostdisk>numdisk:
        print 'get_lost_disk err'
        return None
    else:
        return random.sample(range(numdisk), lostdisk)

def countres (startnum, num, times, numdisk, placement):
    res =[]
    for i in xrange(num):
        lostnum=i+startnum
        curres = 0
        for j in xrange(times):
            lostlist = get_lost_disk(numdisk, lostnum)
            if placement.check_data_lost(lostlist):
                curres += 1

        res.append(curres)
    return res
'''
class RunSim:
    def __init__(self, mission_time,
                 num_racks, node_per_rack, disks_per_node, numgroup,
                 capacity_per_disk,chunk_size, num_stripes,
                 bandwidth,
                 code_n, code_k, code_m,
                 weibull, ssd_fail):
        self.mission_time = mission_time

        self.num_racks =num_racks
        self.node_per_rack = node_per_rack
        self.disks_per_node = disks_per_node
        self.numgroup = numgroup

        self.capacity_per_disk = capacity_per_disk
        self.chunk_size = chunk_size
        self.num_stripes = num_stripes

        self.bandwidth = bandwidth

        self.code_n = code_n
        self.code_k = code_k
        self.code_m = code_m

        self.weibull = weibull
        self.ssd_fail = ssd_fail

    def run(self):
        print "run"
        placement = Placement(self.disks_per_node, self.node_per_rack, self.num_racks, self.numgroup, self.num_stripes,
                              self.code_n, self.code_k)
        placement.generate_palcement()

        network = Network(self.num_racks, self.num_racks*self.node_per_rack, self.numgroup, self.node_per_rack,
                          self.disks_per_node, self.bandwidth, self.capacity_per_disk, self.chunk_size,
                          self.code_n, self.code_k, self.code_m)
        sim = Simulation(self.weibull, self.ssd_fail, placement, network, self.disks_per_node, self.node_per_rack,
                         self.num_racks, self.mission_time)
        res = sim.run()
        print res
        return res
'''

def getresult(result):
    fail_num = 0.0
    lost_stripes = 0.0
    i = 0
    for res in result:
        i+=1
        fail_num += res.get()[0]
        lost_stripes += res.get()[1]
        print "iteration", i,  ":", res.get()[0], res.get()[1]
    print "final result:", fail_num, lost_stripes
    return (fail_num, lost_stripes)

def printconf(mission_time,total_iterations,num_processes,
                 num_racks, node_per_rack, disks_per_node, numgroup,
                 capacity_per_disk,chunk_size, num_stripes,
                 bandwidth,
                 code_n, code_k, code_m,
                use_ratio):
    print "mission_time:", mission_time
    print "total_iterations:", total_iterations
    print "num_processes:", num_processes
    print "num_racks:", num_racks
    print "node_per_rack:", node_per_rack
    print "disks_per_node:", disks_per_node
    print "numgroup:", numgroup
    print "capacity_per_disk:", capacity_per_disk
    print "chunk_size:", chunk_size
    print "num_stripes:", num_stripes
    print "bandwidth:", bandwidth
    print "code_n:", code_n
    print "code_k", code_k
    print "code_m", code_m
    print "use_ratio", use_ratio

def runjob(mission_time,
                 num_racks, node_per_rack, disks_per_node, onumgroup, numgroup,
                 capacity_per_disk,chunk_size, num_stripes,
                 bandwidth,
                 code_n, code_k, code_m, use_ratio,
                 weibull, ssd_fail):
    placement = Placement(disks_per_node, node_per_rack, num_racks, onumgroup, numgroup, num_stripes,
                          code_n, code_k)
    placement.generate_palcement()

    network = Network(num_racks, num_racks * node_per_rack, onumgroup, numgroup, node_per_rack,
                      disks_per_node, bandwidth, capacity_per_disk*use_ratio, chunk_size,
                      code_n, code_k, code_m)
    sim = Simulation(weibull, ssd_fail, placement, network, onumgroup, disks_per_node, node_per_rack,
                     num_racks, mission_time)
    res = sim.run()
    print res
    '''
    file =open("result", "a+")
    fcntl.flock(file.fileno(), fcntl.LOCK_EX)
    file.write(str(res)+"\n")
    file.close()
    '''
    return res

if __name__ == "__main__":
    start = time.time()
    '''
    placement = Placement(8, 32, 32, 1, 2500000, 15, 8)
    placement.generate_palcement()
    count = 0
    for i in range (100):
        count += placement.get_influ_disk(i)
    print count/100

    for disklist in placement.stripes_per_disk:
        print disklist
        print '\n'

    res = countres(3, 30, 1000, 1024, placement)

    print res
 
    placement = Placement(1, 32, 32, 1, 250000, 9, 8)
    placement.generate_palcement()
    ssdfail=0
    diskpernode = 1
    nodeperrack = 32
    network = Network(32, 32*32, 1, 32, 32, 10, 1024*1024, 256, 9, 8, 2)
    racknum = 32
    missiontime = 876000
    weibull=Weibull(shape=1.2, scale=87600, location=0.01)
    sim= Simulation(weibull, ssdfail, placement, network,
                    diskpernode, nodeperrack, racknum,
                    missiontime)
    print sim.run()
    net = Network(32, 32, 1, 125.0, 1024.0*1024.0, 256.0, 9, 6, 3)
    net.test()
    '''

    total_iterations = 1000
    num_processes = 4
    mission_time = 87600

    num_racks = 32
    nodes_per_rack = 32
    disk_per_node = 2
    onum_group = 1
    num_group = 1
    capacity_per_disk = 1 * 2 ** 20

    chunk_size = 256
    num_stripes = 500000

    code_n = 9
    code_k = 6
    code_m = code_n - code_k

    bandwidth = 50

    (opts, args) = getopt.getopt(sys.argv[1:], "hi:p:m:R:N:D:O:G:C:n:k:s:",
                                 ["help", "total_iterations=", "numprocess=",
                                  "num_racks=", "nodes_per_rack=", "disk_per_node=", "onum_group=", "num_group="
                                  "mission_time=", "capacity_per_disk=", "num_stripes="])
    if len(opts) == 0:
        print "Please specify at least one parameter\n"
        sys.exit(2)
    for o, a in opts:
        if o in ("-h", "--help"):
            print "help"
            sys.exit(0)
        elif o in ("-i", "--total_iterations"):
            total_iterations = int(a)
        elif o in ("-p", "--numprocess"):
            num_processes = int(a)
        elif o in ("-m", "--mission_time"):
            mission_time = int(a)
        elif o in ("-R", "--num_racks"):
            num_racks = int(a)
        elif o in ("-N", "--nodes_per_rack"):
            nodes_per_rack = int(a)
        elif o in ("-D", "disk_per_node"):
            disk_per_node = int(a)
        elif o in ("-O", "--onum_group"):
            onum_group = int(a)
        elif o in ("-G","num_group"):
            num_group = int(a)
        elif o in ("-C", "capacity_per_disk"):
            capacity_per_disk = int(a)
        elif o in ("-n"):
            code_n = int(a)
            code_m = code_n - code_k
        elif o in ("-k"):
            code_k = int(a)
            code_m = code_n - code_k
        elif o in ("-s", "--num_stripes"):
            num_stripes = int(a)

    '''
    ssdfail = 0
    weibull = Weibull(shape=1.2, scale=87600, location=0.01)
    run_sim = RunSim(87600,32,32,1,1,1024*1024,256,250000,125,9,6,3,weibull,ssdfail)
    print run_sim.run()
    '''
    ssd_fail = SSD_fail()
    #ssd_fail.drawlist()
    weibull = Weibull(shape=1.2, scale=87600, location=0.01)

    use_ratio = (num_stripes*code_n*chunk_size)/float(capacity_per_disk*num_racks*nodes_per_rack*disk_per_node)
    printconf(mission_time, total_iterations, num_processes,
                 num_racks, nodes_per_rack, disk_per_node, num_group,
                 capacity_per_disk, chunk_size, num_stripes,
                 bandwidth,
                 code_n, code_k, code_m, use_ratio)
    pool = multiprocessing.Pool(num_processes)

    result=[]
    for i in xrange(total_iterations):
        result.append(pool.apply_async(runjob, (mission_time, num_racks, nodes_per_rack, disk_per_node, onum_group, num_group,
                 capacity_per_disk, chunk_size, num_stripes,
                 bandwidth, code_n, code_k, code_m, use_ratio,
                 weibull, ssd_fail,)))
    pool.close()
    pool.join()
    getresult(result)
    end =time.time()
    print "run time", end - start