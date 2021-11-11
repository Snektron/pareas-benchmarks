import os
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

def make(output_path, profile_data):
    coordinates = []
    for path, pd in profile_data.items():
        fz = os.path.getsize(path)
        time = (pd.get_by_key('frontend').avg() + pd.get_by_key('backend').avg()) / US_TO_MS
        coordinates.append(f'({fz:.2f}, {time:.2f})')

    with open(output_path, 'w') as f:
        f.write(PICTURE_TEMPLATE.format(coordinates=' '.join(coordinates)))
