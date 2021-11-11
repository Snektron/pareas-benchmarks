project(
    'pareas-benchmarks',
    ['c', 'cpp'],
    version: '0.0.0',
    default_options: [
        'cpp_std=c++2a',
        'buildtype=debugoptimized',
    ]
)

pareas_proj = subproject('pareas')

repeats = '30'

pareas_test_sources = [
    files('testdata/1.par'),
    files('testdata/2.par'),
    files('testdata/3.par'),
    files('testdata/4.par'),
    files('testdata/5.par'),
    files('testdata/6.par'),
    # files('testdata/7.par'),
]

pareas_runner = find_program('scripts/benchmark_pareas.py')

env = environment()
if get_option('benchmark-device') != ''
    env.set('PAREAS_BENCH_DEVICE', get_option('benchmark-device'))
endif

run_target(
    'bench-pareas',
    command: [
        pareas_runner,
        '--exe', pareas_proj.get_variable('pareas_exe'),
        '--futhark-backend', pareas_proj.get_variable('futhark_backend'),
        '--repeat', repeats,
        '--result-dir', '@SOURCE_ROOT@/results/',
    ] + pareas_test_sources,
    env: env,
)
