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
    legend style={{legend pos=north west, legend cell align=left}},
]
\\addplot coordinates {{{coordinates}}};
\\legend{{Total throughput}}
\\end{{loglogaxis}}
\\end{{tikzpicture}}'''

p = argparse.ArgumentParser(description='Generate total throughput plot')
p.add_argument('results_dir', type=str, help='Path to the directory with results')
p.add_argument('test_data', type=str, help='Path to directory containing test data')
p.add_argument('output', type=str, help='Output of the plot tex file')
args = p.parse_args()

with open(os.path.join(args.results_dir, 'results.json')) as f:
    results = json.load(f)

coordinates = []
for data_set_name, profile_data_name in results['results'].items():
    data_set_path = os.path.join(args.test_data, data_set_name)
    profile_data_path = os.path.join(args.results_dir, profile_data_name)

    fz = os.path.getsize(data_set_path)
    pd = ProfileData.read(profile_data_path)

    time = (pd.get_by_key('frontend').avg() + pd.get_by_key('backend').avg()) / US_TO_MS
    coordinates.append(f'({fz:.2f}, {time:.2f})')

with open(args.output, 'w') as f:
    f.write(PICTURE_TEMPLATE.format(coordinates=' '.join(coordinates)))
