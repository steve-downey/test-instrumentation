# CMake Instrumentation Experimental Tests

This project is intended for testing the experimental CMake instrumentation feature on: [my branch](https://gitlab.kitware.com/martin.duffy/cmake/-/commits/instrumentation).

## Instructions

Create a `.json` file in either `~/.config/cmake/timing/v1/query/` or `<CMAKE_BINARY_DIR>/.cmake/timing/v1/query` with the following contents:

```json
{
    "version": 1,
    "callbacks": ["<PATH_TO_PYTHON_EXE> <PATH_TO_THIS_REPO>/instrument.py"]
}
```

You can also add the following key to collect system information as part of the instrumentation:

```
    "queries": ["staticSystemInfo", "dynamicSystemInfo"]
```

Configure/Build your project using a version of CMake with the instrumentation changes built, then run `<YOUR_CMAKE_BUILD>/cmake -E collect_timing <YOUR_PROJECT_BINARY_DIR>` and see the output generated in the `output` directory.

Optionally add the following key to run data indexing automatically at certain intervals instead of running `cmake -E collect_timing` manually:

```
    "hooks": ["preConfigure", "postGenerate", "preCMakeBuild", "postCMakeBuild", "postInstall", "postTest"]
```

This uses a modified version of the [ninja tracing script](https://github.com/nico/ninjatracing) to generate an output compatible with chrome's about:tracing format. 

Open about:tracing in chrome, or use https://www.speedscope.app/ or https://ui.perfetto.dev/ and load the generated `output/trace.json` file.
