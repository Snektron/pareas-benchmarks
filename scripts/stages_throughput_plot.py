import os
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

STAGES = [
    'frontend.compile.tokenize',
    'frontend.compile.parse',
    'frontend.compile.build parse tree',
    'frontend.compile.syntax',
    'frontend.compile.sema',
    'backend.translate ast',
    'backend.preprocessing',
    'backend.instruction count',
    'backend.instruction gen',
    'backend.optimize',
    'backend.regalloc/instr remove',
    'backend.Jump Fix',
    'backend.postprocess',
]

def make(output_path, profile_data):
    data = {}

    for stage in STAGES:
        data[stage] = []

    for path, pd in profile_data.items():
        fz = os.path.getsize(path)

        for stage in STAGES:
            time = pd.get_by_key(stage).avg() / US_TO_MS
            data[stage].append(f'({fz:.2f}, {time:.2f})')

    plots = []
    for stage, coordinates in data.items():
        coordinates = ' '.join(coordinates)
        plots.append(f'\\addplot coordinates {{{coordinates}}};')

    legends=','.join(STAGES)

    with open(output_path, 'w') as f:
        f.write(PICTURE_TEMPLATE.format(plots='\n'.join(plots), legends=legends))
