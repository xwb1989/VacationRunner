#!/usr/bin/python

#File_name: result_query.py
#Author: Wenbin Xiao

import sys
import os
import re

class VacationSet:
    def __init__(self, entries):
        self.entries = entries
    def search(self, key, val):
        return VacationSet([e for e in self.entries if e.properties[key] == val ])
    def average(self, key):
        if key == "version":
            print "Error: please input a numeric key"
        else:
            res = [ e.properties[key] for e in self.entries ]
            if len(res )!= 0:
                return sum(res) / float(len(res))
            else:
                return 0
            
    def __str__(self):
        s = ""
        for e in self.entries:
            s += e.__str__()
        return s
class VacationEntry:
    #Constructor
    def __init__(self, version, properties):
        self.properties = { "version" : version}
        self.properties.update(properties)
        self.properties["abort_ratio"] = properties["Aborts"] / float(properties["Starts"])

    @staticmethod
    def FileToEntries(file_path):
        """
            This method is based on the format of entry:
                --------Following is the entry-------
            Initializing manager... done.
            Initializing clients... done.
                Transactions        = 4194304
                Clients             = 16
                Transactions/client = 262144
                Queries/transaction = 8
                Relations           = 65536
                Query percent       = 10
                Query range         = 6554
                Percent user        = 80
            TL2 system ready: GV=GV4
            Running clients... done.
            Time = 83.392587
            Checking tables... done.
            Deallocating memory... done.
            TL2 system shutdown:
              GCLOCK=0x7E7020 Starts=16038459 Aborts=11844155
              Overflows: R=0 W=10608 L=0
              -------------Entry finishes------------
        """
        cnt = 0
        n = 18 
        skipped = set([1,2,11,12,14,15,16])
        res = []
        version = "boost"
        if "boost" in file_path:
            print file_path
            version = "boost"
        else:
            version = "default"


        try:
            f = open(file_path)
            properties = {}
            for line in f:
                #skip useless lines
                if cnt+1 in skipped:
                    pass
                elif cnt+1 == 17:
                    valid = line[line.find("Start"):]
                    properties.update(multiple_equations_to_key_value(valid))
                elif cnt+1 == 18:
                    properties.update(multiple_equations_to_key_value(line.split(":")[1]))
                else:
                    ret = single_equation_to_key_value(line)
                    properties.update(ret)
                cnt += 1
                cnt %= n
                if cnt == 0:
                    res.append(VacationEntry(version, properties))
                    properties = {}
        except IOError:
            sys.stderr.write("Failed to open file: %s" % (file_path))
        return res
    def __str__(self):
        s = "VacationEntry:\n"
        for key, val in self.properties.iteritems():
            s += ("\t%s = %s\n" %(key, val))
        return s

def multiple_equations_to_key_value(line):
    pattern = re.compile("\w+\s*=\w+\s*")
    l = re.findall(pattern, line)
    res = {}
    for e in l:
        res.update(single_equation_to_key_value(e))
    return res


    
def single_equation_to_key_value(line):
    splited = [word.strip() for word in line.split('=')]
    return { splited[0] : int(float(splited[1])) }
def printf(line):
    sys.stdout.write(line.__str__())
def get_file_list(target_dir):
    return [ os.path.join(target_dir, file) for file in os.listdir(target_dir) if os.path.isfile(os.path.join(target_dir, file)) if "output" in file] 
    
    
if __name__ == "__main__":
    #argument check
    if len(sys.argv) != 2:
        sys.stderr.write("Invalid argument. Usage: raw2cvs.py target_dir")
        sys.exit()
    
    target_dir = sys.argv[1]
    print "Target Directory: %s" %(target_dir)

    #file list
    entries = []
    for file in get_file_list(target_dir):
        entries += (VacationEntry.FileToEntries(file))
    vacation_set = VacationSet(entries)
    entries1 = entries

    default = vacation_set.search("Transactions", 4194304).search("version", "default")
    boost = vacation_set.search("Transactions", 4194304).search("version", "boost")
    i = 1
    while i <= 32:
        print "%d clients: " %(i)
        print "\tdefault average time: %.2f" %(default.search("Clients", i)).average("Time")
        print "\tdefault average abort ratio: %.2f" %(default.search("Clients", i)).average("abort_ratio")
        print "\tboost average time: %.2f" %(boost.search("Clients", i)).average("Time")
        print "\tboost average abort ratio: %.2f" %(boost.search("Clients", i)).average("abort_ratio")
        i *= 2




