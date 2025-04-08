# CMake Instrumentation Demo

This project is intended for testing the experimental CMake instrumentation feature available in CMake 4.0.

## Instructions

To make the most of this example, you should read the [Instrumentation documentation](https://cmake.org/cmake/help/git-stage/manual/cmake-instrumentation.7.html).

The `example/` subdirectory includes a sample CMake project that enables CMake instrumentation and includes some simple custom commands and compiles to generate sample output.

The provided `instrument.py` callback copies instrumentation data into `<CMAKE_BINARY_DIR>/instrumentation/` and generates a trace file to visualize the timing information.

In order to use the sample `instrument.py` callback provided in another CMake project, copy the `cmake_instrumentation` call
in `example/CMakeLists.txt` into the project's CMake code. You will also need to set `CMAKE_EXPERIMENTAL_INSTRUMENTATION`, update the path to `instrument.py`, and ensure
`Python_EXECUTABLE` is defined.

## Viewing Trace Files

This uses a modified version of the [ninja tracing script](https://github.com/nico/ninjatracing) to generate an output compatible with chrome's about:tracing format. 

Open about:tracing in chrome, or use https://ui.perfetto.dev/ and load the generated `trace.json` files.
