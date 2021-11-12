#!/usr/bin/env python3
import os
import argparse
import json
from profiler import ProfileData

US_TO_MS = 1000

PICTURE_TEMPLATE = '''\
\\begin{{tikzpicture}}
\\begin{{loglogaxis}}[
    xlabel={{Input size (bytes)}},
    ylabel={{Runtime (ms)}},
    legend style={{legend cell align=left, anchor=south, at={{(0.5,1.03)}}}},
]
{plots}
\\legend{{{legends}}}
\\end{{loglogaxis}}
\\end{{tikzpicture}}'''

FRONTEND_STAGES = {
    'frontend.compile.tokenize': 'Lexing',
    'frontend.compile.parse': 'Parsing',
    'frontend.compile.build parse tree': 'Building parse tree',
    'frontend.compile.syntax': 'Restructuring',
    'frontend.compile.sema': 'Semantic Analysis',
}

BACKEND_STAGES = {
    'backend.translate ast': 'Translate AST',
    'backend.preprocessing': 'Preprocessing',
    'backend.instruction count': 'Instr. Count',
    'backend.instruction gen': 'Instr. Gen',
    'backend.optimize': 'Optimization',
    'backend.regalloc/instr remove': 'Regalloc',
    'backend.jump fix': 'Jump Fix',
    'backend.postprocess': 'Postprocessing',
}

p = argparse.ArgumentParser(description='Generate total throughput plot')
p.add_argument('results_dir', type=str, help='Path to the directory with results')
p.add_argument('test_data', type=str, help='Path to directory containing test data')
p.add_argument('frontend_output', type=str, help='Output of the frontend plot tex file')
p.add_argument('backend_output', type=str, help='Output of the backend plot tex file')
args = p.parse_args()

with open(os.path.join(args.results_dir, 'results.json')) as f:
    results = json.load(f)

frontend_data = {}
backend_data = {}

for stage in FRONTEND_STAGES.values():
    frontend_data[stage] = []

for stage in BACKEND_STAGES.values():
    backend_data[stage] = []

for data_set_name, profile_data_name in results['results'].items():
    data_set_path = os.path.join(args.test_data, data_set_name)
    profile_data_path = os.path.join(args.results_dir, profile_data_name)

    fz = os.path.getsize(data_set_path)
    pd = ProfileData.read(profile_data_path)

    for stage, name in FRONTEND_STAGES.items():
        time = pd.get_by_key(stage).avg() / US_TO_MS
        frontend_data[name].append(f'({fz:.2f}, {time:.2f})')

    for stage, name in BACKEND_STAGES.items():
        time = pd.get_by_key(stage).avg() / US_TO_MS
        backend_data[name].append(f'({fz:.2f}, {time:.2f})')


for (output, data) in [(args.frontend_output, frontend_data), (args.backend_output, backend_data)]:
    plots = []
    for coordinates in data.values():
        coordinates = ' '.join(coordinates)
        plots.append(f'\\addplot coordinates {{{coordinates}}};')

    legends=','.join(data.keys())

    with open(output, 'w') as f:
        f.write(PICTURE_TEMPLATE.format(plots='\n'.join(plots), legends=legends))
