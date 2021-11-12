#!/usr/bin/env python3
import argparse
import os
import sys
import socket
import subprocess
import multiprocessing
import json
from profiler import ProfileData

p = argparse.ArgumentParser(description='Pareas benchmark runner')
p.add_argument('data', nargs='+', type=str, help='Datasets to test')
p.add_argument('--result-dir', type=str, required=True, help='Directory to write output files to')
p.add_argument('--futhark-backend', type=str, required=True, help='Futhark backend the executable is compiled with')
p.add_argument('--repeat', type=int, required=True, help='Number of times to repeat the experiments')
p.add_argument('--exe', type=str, required=True, help='Pareas executable to test')
p.add_argument('--threads', type=int, help='Number of threads (multicore only)')

args = p.parse_args()

if args.repeat < 1:
    print('Error: Minimum repeat is 1', file=sys.stderr)
    sys.exit(1)
elif args.threads is not None and args.threads < 1:
    print('Error: Minimum number of threads is 1', file=sys.stderr)
    sys.exit(1)
elif args.futhark_backend not in ['c', 'opencl', 'multicore', 'cuda']:
    print('Error: Invalid futhark backend', file=sys.stderr)
    sys.exit(1)

machine = os.uname()[1]
cores = multiprocessing.cpu_count()
threads = cores if args.threads is None else args.threads

if args.futhark_backend != 'multicore':
    threads = 1

print(f"Benchmarking machine: '{machine}'")
print(f'Cores: {cores}')
print(f'Thread(s): {threads}')
print(f'Futhark backend: {args.futhark_backend}')

result_dir = os.path.join(args.result_dir, machine, args.futhark_backend)

os.makedirs(result_dir, exist_ok=True)

common_args = [args.exe, '-p', '4']

if 'PAREAS_BENCH_DEVICE' in os.environ:
    common_args += ['-d', os.environ['PAREAS_BENCH_DEVICE']]
    print(f'Benchmark device: {common_args[-1]}')

if args.futhark_backend == 'multicore':
    common_args.append(['--threads', str(threads)])

total_steps = len(args.data) * args.repeat

def run(data_set):
    try:
        result = subprocess.run(common_args + [data_set], capture_output=True)
        if len(result.stderr) != 0:
            print(f'Experiment returned stderr: {result.stderr.decode()}')

        return ProfileData(result.stdout.decode())
    except subprocess.CalledProcessError as e:
        print(f'Experiment failed: {e}')
        return None

step = 0
result_data = {}
profile_data = {}
for data_set in args.data:
    data_set_name = os.path.basename(data_set)
    pds = []
    for i in range(args.repeat):
        step += 1
        print(f"[{step}/{total_steps}] Benchmarking data set '{data_set_name}', repetition {i + 1}")
        result = run(data_set)
        if result is not None:
            pds.append(result)

    combined = ProfileData.merge_all(pds)
    fname = f'{data_set_name}.txt'
    with open(os.path.join(result_dir, fname), 'w') as f:
        print(combined, file=f)

    result_data[data_set_name] = fname
    profile_data[data_set] = combined

results = {
    'machine': machine,
    'cores': cores,
    'threads': threads,
    'results': result_data,
    'futhark backend': args.futhark_backend,
}

if 'PAREAS_BENCH_DEVICE' in os.environ:
    results['bench device'] = os.environ['PAREAS_BENCH_DEVICE']

with open(os.path.join(result_dir, 'results.json'), 'w') as f:
    json.dump(results, f, indent=4)
