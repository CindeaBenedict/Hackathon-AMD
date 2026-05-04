cmake_minimum_required(VERSION 3.20)
project(probepilot_bridge LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)

add_library(instrument_bridge STATIC
  src/instrument_bridge.cpp
)

target_include_directories(instrument_bridge PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)

option(PROBEPILOT_BUILD_PYBIND "Build pybind11 module" OFF)
if(PROBEPILOT_BUILD_PYBIND)
  find_package(pybind11 CONFIG REQUIRED)
  pybind11_add_module(probepilot_cpp src/bindings.cpp)
  target_link_libraries(probepilot_cpp PRIVATE instrument_bridge)
endif()
