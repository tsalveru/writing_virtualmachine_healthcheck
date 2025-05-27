#!/usr/bin/env python3

import argparse
import os
import subprocess

def get_cpu_usage():
    # Get the CPU idle percentage from top, then calculate used percent
    top_cmd = "top -bn2 | grep 'Cpu(s)' | tail -n1"
    output = subprocess.check_output(top_cmd, shell=True).decode()
    # Output format: %Cpu(s):  4.5 us,  1.0 sy,  0.0 ni, 94.0 id, ...
    for part in output.split(','):
        if 'id' in part:
            idle = float(part.strip().split()[0])
            return 100.0 - idle
    return 0.0

def get_mem_usage():
    # Use free -m to get memory usage
    output = subprocess.check_output("free", shell=True).decode()
    lines = output.splitlines()
    for line in lines:
        if line.startswith("Mem:"):
            parts = line.split()
            total = float(parts[1])
            used = float(parts[2])
            return used * 100.0 / total if total > 0 else 0.0
    return 0.0

def get_disk_usage():
    # Use df / to get root partition usage
    output = subprocess.check_output("df /", shell=True).decode()
    lines = output.splitlines()
    if len(lines) > 1:
        # The last column is Use%
        usage_str = lines[1].split()[-2]
        return float(usage_str.strip('%'))
    return 0.0

def main():
    parser = argparse.ArgumentParser(description="Check VM health based on CPU, memory, and disk usage.")
    parser.add_argument('explain', nargs='?', default=None, help="Show explanation of health status")
    args = parser.parse_args()

    cpu_usage = get_cpu_usage()
    mem_usage = get_mem_usage()
    disk_usage = get_disk_usage()

    status = "healthy"
    reasons = []

    if cpu_usage > 60.0:
        status = "not healthy"
        reasons.append(f"CPU usage is above 60% ({cpu_usage:.2f}%).")
    if mem_usage > 60.0:
        status = "not healthy"
        reasons.append(f"Memory usage is above 60% ({mem_usage:.2f}%).")
    if disk_usage > 60.0:
        status = "not healthy"
        reasons.append(f"Disk usage is above 60% ({disk_usage:.2f}%).")

    print(f"VM Health Status: {status}")

    if args.explain == "explain":
        if status == "healthy":
            print("All system resources are under 60% utilization:")
        else:
            print("Reason(s): " + " ".join(reasons))
        print(f"- CPU usage: {cpu_usage:.2f}%")
        print(f"- Memory usage: {mem_usage:.2f}%")
        print(f"- Disk usage: {disk_usage:.2f}%")

if __name__ == "__main__":
    main()
