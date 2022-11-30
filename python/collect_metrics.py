from bcc import BPF
from os import system
import time
import sys

# define BPF program
prog = """
int syscall_event(void *ctx) {
    bpf_trace_printk("syscall");
    return 0;
}
"""

syscalls = []
thresholds = []
calls = []
progs = []
name = ""

# Read spec file to determine the syscalls of interest
try:
    f = open("../spec_files/simple_exp_spec.csv")
    lines = f.readlines()
    if(len(lines) > 0):
        for i, line in enumerate(lines):
            if(i == 0):
                name = line.split(',')[1]
                name = name.replace('\n', "")
            else:
                if(len(line) > 0):
                    syscalls.append(line.split(',')[0])
                    thresholds.append(int(line.split(',')[1]))
                    calls.append(0)

except Exception as e:
    print(e)
    
# Print the syscalls and thresholds read from the spec file
print("name = " + name)
print("syscalls = ")
print(syscalls)
print("thresholds = ")
print(thresholds)

# load BPF program to monitor each syscall in the spec file
for i, syscall in enumerate(syscalls):
    progs.append(BPF(text=prog.replace("syscall", syscall)))
    progs[i].attach_kprobe(event=progs[i].get_syscall_fnname(syscall), fn_name=(syscall + "_event"))
    # print(progs[i])

last_time = 0
# format output
try:
    while 1:
        for i, prog in enumerate(progs):
            try:
                #get trace fields from the bpf program
                (task, pid, cpu, flags, ts, msg) = prog.trace_fields()
                f = open("/proc/" + str(pid) + "/cmdline")
                process_location = f.readlines()
                if(len(process_location) > 0):
                    # check if this trace belongs to process of interest
                    if((name in process_location[0]) and syscalls[i] in msg):
                        calls[i]+=1
            except Exception as e:
                #print(e)
                continue
        
        if(time.time() - last_time > 1):
            textbuf = name + "\n"
            for i, syscall in enumerate(syscalls):
                if(calls[i] > thresholds[i]):
                    textbuf += syscall + "," + str(calls[i]) + ",1\n"
                else:
                    textbuf += syscall + "," + str(calls[i]) + ",0\n"
                calls[i] = 0
            print(textbuf)
            f = open("../metrics/"+ name + ".csv", "w")
            f.write(textbuf)
            f.close()
            last_time = time.time()
except KeyboardInterrupt:
    pass
    print("Exiting...") 
    sys.exit()   