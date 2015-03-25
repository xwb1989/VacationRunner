#!/usr/bin/python

import os
import sys
import subprocess
import datetime
import logging
import threading

SKIPLIST_BOOST = "/home/wenbinx/transactional_memory/vacation-experiment/vacation-skiplist"
SKIPLIST_TL2 = "/home/wenbinx/transactional_memory/vacation-experiment/vacation-skiplist-tl2"

CMD = "/vacation"

max_c = 32
min_c = 1

max_n = 32
min_n = 1

r = 65536

max_q = 100
min_q = 10
q_step = 10

max_u = 100
min_u = 10
u_step = 10

num_tx = 65536 * 2

reps = 5

TIMEOUT = 30 * 60
MAX_RETRY = 10
class Command:
    def __init__(self, cmd):
        self.cmd = cmd
        self.fail = 0

    def run(self, timeout):
        def target():
            try:
                self.fail = 0
                subprocess.check_call(self.cmd, shell=True)
            except subprocess.CalledProcessError:
                self.fail = 1
        retry = 0
        while True:
            thread = threading.Thread(target=target) 
            thread.start()
            thread.join(timeout)
            if thread.isAlive():
                logging.info("Timeout, kill cmd: " + self.cmd) 
                subprocess.call("killall -9 vacation", shell=True) #kill the process
                logging.info("Try to rerun: " + self.cmd) 
                thread.join()
                retry += 1
                if retry >= MAX_RETRY:
                    logging.info("Exceed MAX_RETRY, experiment quit.")
                    sys.exit(1)
            elif self.fail:
                retry += 1
                logging.info("Error during running. Gonna rerun current setting.")
                self.fail = 0
                if retry >= MAX_RETRY * 2:
                    logging.info("Failure exceeds MAX_RETRY*2, experiment quit.")
                    sys.exit(1)
            else:
                break
        

def run_cmd(app_dir, output):
    print("Creating file: " + output_file) 
    subprocess.call("touch " + output_file, shell=True)
    curr_c = min_c
    while curr_c <= max_c:
        curr_n = min_n
        while curr_n <= max_n:
            curr_u = min_u
            while curr_u <= max_u:
                curr_q = min_q
                while curr_q <= max_q:
                    args = " -c%i -n%i -r%i -q%i -u%i -t%i" %(curr_c, curr_n, r, curr_q, curr_u, num_tx)
                    cmd = app_dir + CMD + args + " >> " + output
                    logging.info("Runing with cmd: " + cmd) 
                    for i in range(reps):
                        cmd_proc = Command(cmd)
                        cmd_proc.run(TIMEOUT)
                    curr_q += q_step
                curr_u += u_step
            curr_n *= 2
        curr_c *= 2



if __name__ == "__main__":

    print "running wl_runner"
    if not os.path.isdir("output"):
        os.makedirs("output")

    #setup datetime
    today = datetime.datetime.today().strftime("%Y%m%d%H%M%S")
    #setup logging
    logging.basicConfig(filename="logs/" + today, level=logging.INFO, format="%(asctime)s %(message)s", datefmt='%m/%d/%Y %I:%M:%S %p')
   
    if not os.path.isdir("output/"+ today):
        print "making output directory"
        os.makedirs("output/" + today)
    #option
    opt = sys.argv[1]
    if len(sys.argv) > 3:
        TIMEOUT = float(sys.argv[2])
        MAX_RETRY = float(sys.argv[3])

    print "start running"
    if opt == "all" or opt == "skiplist-boost":
        print("BOOST")
        output_file = "output/" + today + "/skiplist-boost"
        run_cmd(SKIPLIST_BOOST, output_file)
    if opt == "all" or opt == "skiplist-tl2":
        print("TL2")
        output_file = "output/" + today + "/skiplist-tl2"
        run_cmd(SKIPLIST_TL2, output_file)
    print "done"
