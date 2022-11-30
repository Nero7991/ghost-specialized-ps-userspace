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
calls_by_pid={}
calls_by_task_pid={}
# calls_by_task={}
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
                        pid_dict={}
                        calls_by_task={}
                        task_dict={}


                        if pid in calls_by_pid:
                            pid_dict=calls_by_pid[pid]
                        else:
                            calls_by_pid[pid]=pid_dict
                        
                        if syscalls[i] in pid_dict:
                            pid_dict[syscalls[i]]+=1
                        else:
                            pid_dict[syscalls[i]]=0


                        if pid in calls_by_task_pid:
                            calls_by_task=calls_by_task_pid[pid]
                        else:
                             calls_by_task_pid[pid]=calls_by_task

                        if task in calls_by_task:
                            task_dict=calls_by_task[task]
                        else:
                            calls_by_task[task]=task_dict

                        if syscalls[i] in task_dict:
                            task_dict[syscalls[i]]+=1
                        else:
                            task_dict[syscalls[i]]=0
                        

            except Exception as e:
                # print(e)
                continue
        
        if(time.time() - last_time > 1):
            textbuf = name + "\n"
            for i, syscall in enumerate(syscalls):
                if(calls[i] > thresholds[i]):
                    textbuf += "ALL,"+syscall + "," + str(calls[i]) + ",1\n"
                else:
                    textbuf += "ALL,"+syscall + "," + str(calls[i]) + ",0\n"
                calls[i] = 0
            for pid, pid_map in calls_by_pid.items():
                for syscall,call_count in pid_map.items():
                    textbuf += "PID,"+str(pid) +","+syscall + "," + str(call_count) + "\n"
            calls_by_pid={}

            for pid,calls_by_task in calls_by_task_pid.items():
                for task, task_map in calls_by_task.items():
                    for syscall,call_count in task_map.items():
                        textbuf += "TASK,"+str(pid)+","+str(task) +","+syscall + "," + str(call_count) + "\n"
            calls_by_task_pid={}

            print(textbuf)
            f = open("../metrics/"+ name + ".csv", "w")
            f.write(textbuf)
            f.close()
            last_time = time.time()
except KeyboardInterrupt:
    pass
    print("Exiting...") 
    sys.exit()   