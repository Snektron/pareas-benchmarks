# Pareas Benchmark repository

### Building and running

Building and running the benchmarks requires the following requirements:
* A C++20-capable compiler such as clang or gcc.
* The [Meson](https://mesonbuild.com/) build system.
* [Ninja](https://ninja-build.org) or [Samurai](https://github.com/michaelforney/samurai) to build.
* A [Futhark](https://github.com/diku-dk/futhark) compiler. The latest tested version is 20.6.
* Python, which is required for Meson as well as some build tools included in the project. At least version 3.8 is required.

Pareas itself and dependencies are automatically downloaded by Meson, and so this requires an active internet connection. Depending on the selected backend, some additional libraries are required.

To run the benchmarks run:
```
$ mkdir build
$ cd build
$ meson .. -Dpareas:futhark-backend=[opencl|cuda|c|multicore] -Dbenchmark-device=<device>
$ ninja bench-pareas
```
`<device>` is a Futhark device selector, either a device name or `#k` for the k-th GPU.

### Generating plots

Some tools are included to generate plots:
```
$ scripts/total_throughput_plot.py results/<machine>/<backend> testdata plot.tex
$ scripts/stages_throughput_plot.py results/<machine>/<backend> testdata frontend.tex backend.tex
```
