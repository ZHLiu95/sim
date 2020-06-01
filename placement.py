import random

class Placement:
    def __init__(self, diskpernode, numnode, numrack, onumgroup, numgroup, numstripes, n, k):
        self.numdisk = diskpernode*numnode*numrack
        self.diskpernode = diskpernode
        self.numnode = numnode
        self.numrack = numrack

        self.numgroup = numgroup
        self.onumgroup = onumgroup

        self.nodepergroup = numnode/numgroup
        self.numstripes = numstripes
        self.n = n
        self.k = k
        self.m = n-k
        self.stripes_per_disk = [[] for i in range(self.numdisk)]

        #test
    def get_diff_ogroup(self):
        return random.randint(0, self.onumgroup-1)

    def get_diff_group(self):
        return random.randint(0, self.numgroup-1)

    def get_diff_rack(self, diffracks, onumgroup):
        if self.numrack < diffracks:
            print 'get rack err'
            return None
        grouprack = self.numrack / self.onumgroup
        knumrack = int(grouprack * self.k / self.n)
        mnumrack = grouprack - knumrack
        flag = 1
        #print grouprack, knumrack, mnumrack
        racklist = []
        if flag == 1:
            kracklist = random.sample(range(knumrack), self.k)
            mracklist = random.sample(range(mnumrack), self.m)
            for i in xrange(len(mracklist)):
                mracklist[i] += knumrack
            racklist = kracklist + mracklist
        else:
            racklist = random.sample(range(grouprack), diffracks)
        for i in xrange(len(racklist)):
            racklist[i] = racklist[i] + onumgroup * grouprack
        #print racklist
        return racklist

    def get_diff_node(self, rackid, groupid, diffnodes):
        if self.numnode < diffnodes:
            print 'get node err'
            return None
        nodes_list = random.sample(range(self.nodepergroup), diffnodes)         ###
        for i in xrange(len(nodes_list)):
            nodes_list[i] += rackid * self.numnode
            nodes_list[i] += groupid * self.nodepergroup   ### group
        return nodes_list

    def get_diff_disk(self, rackid, groupid, diffdisk):
        nodes_list = self.get_diff_node(rackid, groupid, diffdisk)
        if self.diskpernode == 1:
            return nodes_list
        else:
            disk_list = []
            for each in nodes_list:
                disk_list.append(each*self.diskpernode+random.randint(0, self.diskpernode-1))
            return disk_list

    def generate_palcement(self):
        for stripeid in xrange(self.numstripes):
            '''
            if stripeid % 1000000 == 0:
                print "stripeid:", stripeid
            '''
            ogroupid = self.get_diff_ogroup()
            groupid = self.get_diff_group()
            racklist = self.get_diff_rack(self.n, ogroupid)
            for rackid in racklist:
                    disklist = self.get_diff_disk(rackid, groupid, 1)
                    for diskid in disklist:
                        self.stripes_per_disk[diskid].append(stripeid)

    def check_data_lost(self, disklist):
        stripedic = {}
        for diskid in disklist:
            for stripeid in self.stripes_per_disk[diskid]:
                if stripeid in stripedic:
                    stripedic[stripeid] += 1
                else:
                    stripedic[stripeid] = 1
        for key in stripedic:
            if stripedic[key] > (self.n-self.k):
                return True
        #print stripedic
        return False

    def get_lost_strip(self, disk_list):
        stripedic = {}
        for disk_id in disk_list:
            for stripe_id in self.stripes_per_disk[disk_id]:
                if stripe_id in stripedic:
                    stripedic[stripe_id] += 1
                else:
                    stripedic[stripe_id] = 1
        count = 0
        for key in stripedic:
            if stripedic[key] >(self.n-self.k):
                count += 1
        return count

    def node_whether_influ_disk(self,diskid, node_list):
        stripe_node = set()
        stripe_disk = set(self.stripes_per_disk[diskid])
        for disk_innode in node_list:
            for stripeid in self.stripes_per_disk[disk_innode]:
                stripe_node.add(stripeid)
        influ_stripe = stripe_disk & stripe_node
        return len(influ_stripe) == 0

    def get_rapair_time(self):
        r_time = 12*1024*1024/128
        r_time = float(r_time/3600)
        return r_time
