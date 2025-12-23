##########################################################################
# A simple CMake project designed to have non-trivial instrumentation data
##########################################################################

cmake_minimum_required(VERSION 4.0)
project(InstrumentationDemo LANGUAGES CXX)
enable_testing()
set(CMAKE_BUILD_TYPE Debug)
set(CMAKE_CXX_STANDARD 17)

# Allow parallel install
set_property(GLOBAL PROPERTY INSTALL_PARALLEL ON)

# Enable experimental feature!!
set(CMAKE_EXPERIMENTAL_INSTRUMENTATION
  ec7aa2dc-b87f-45a3-8022-fe01c5f59984)

# Instrumentation query
# find_package(Python COMPONENTS Interpreter)
cmake_instrumentation(
  API_VERSION 1
  DATA_VERSION 1
  HOOKS postGenerate preBuild postBuild preCMakeBuild postCMakeBuild postCMakeInstall postCTest
  OPTIONS trace
#  CALLBACK ${Python_EXECUTABLE} ${CMAKE_SOURCE_DIR}/../instrument.py
  CALLBACK ${CMAKE_SOURCE_DIR}/../instrument.sh
)

macro(add_subdirectory_build n)
  set(dir subdir${n})
  set(wait_time ${n})
  execute_process(
    COMMAND ${CMAKE_COMMAND} -E copy_directory_if_different
    ${CMAKE_SOURCE_DIR}/subdir ${CMAKE_BINARY_DIR}/${dir}
  )
  add_subdirectory(${CMAKE_BINARY_DIR}/${dir})
endmacro()
set_property(
  DIRECTORY APPEND PROPERTY
  CMAKE_CONFIGURE_DEPENDS subdir/CMakeLists.txt
)

# Create several subdirectories for more interesting output
add_subdirectory_build(1)
add_subdirectory_build(2)
add_subdirectory_build(3)
add_subdirectory_build(4)

# Add some executables with >100ms compile times
add_executable(thousand thousand.cxx)
add_executable(million million.cxx)
foreach(target thousand million)
  target_compile_options(${target} PRIVATE
    $<$<CXX_COMPILER_ID:GNU>:-fconstexpr-loop-limit=1000000>
  )
  add_dependencies(${target}
    subdir1_wait
    subdir2_wait
    subdir3_wait
    subdir4_wait
  )
endforeach()
