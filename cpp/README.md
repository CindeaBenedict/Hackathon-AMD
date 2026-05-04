# ProbePilot C++ bridge

Fast paths for **SCPI**, **USB/serial**, **waveform CSV parsing**, and **measurement safety checks**.

Expose to Python via **pybind11** (see `CMakeLists.txt` option `PROBEPILOT_BUILD_PYBIND`), **gRPC**, **ZeroMQ**, or a small **REST** sidecar.

```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build
```

ROCm / MI300X training jobs stay on the GPU host; this layer typically runs on the bench PC or edge gateway closest to instruments.
