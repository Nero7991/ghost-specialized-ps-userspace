from bcc import BPF
from os import system
import time

# define BPF program
prog = """
int hello(void *ctx) {
    bpf_trace_printk("hello");
    return 0;
}
"""

# load BPF program
b = BPF(text=prog)
c = BPF(text=prog)
b.attach_kprobe(event=b.get_syscall_fnname("write"), fn_name="hello")
c.attach_kprobe(event=b.get_syscall_fnname("read"), fn_name="hello")

# header
print("%-18s %-16s %-6s %s" % ("TIME(s)", "COMM", "PID", "MESSAGE"))
read_calls = 0
write_calls = 0
current_time = 0
# format output
while 1:
    try:
        (task, pid, cpu, flags, ts, msg) = b.trace_fields()
    except ValueError:
        continue
    
    try:
        f = open("/proc/" + str(pid) + "/cmdline")
        process_location = f.readlines()
        if(len(process_location) > 0):
            if("mysql" in process_location[0]):
                read_calls+=1
                print(str(i) + " mysql %-18.9f %-16s %-6d %s" % (ts, task, pid, msg))

    except Exception as e:
        # print(e)
        # print("pid = " + str(pid))
        continue
    try:
        (task, pid, cpu, flags, ts, msg) = b.trace_fields()
    except ValueError:
        continue
    
    try:
        f = open("/proc/" + str(pid) + "/cmdline")
        process_location = f.readlines()
        if(len(process_location) > 0):
            if("mysql" in process_location[0]):
                write_calls+=1
                print(str(i) + " mysql %-18.9f %-16s %-6d %s" % (ts, task, pid, msg))
    except Exception as e:
        # print(e)
        # print("pid = " + str(pid))
        continue
    
    if(time.time() - current_time > 1):
        print("sys_read calls = " + str(read_calls) + " per sec, sys_write calls = " + str(write_calls) + " per sec") 
        read_calls = 0
        write_calls = 0
        current_time = time.time()      