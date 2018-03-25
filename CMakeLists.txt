cmake_minimum_required(VERSION 3.2)

project(sample CXX)

set(SUB_DIR ${CMAKE_CURRENT_SOURCE_DIR}/src)

set(BIN_DIR ${CMAKE_CURRENT_SOURCE_DIR}/bin)

unset(EXTERNAL_PROJECTS_INCLUDE_PATHS)

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${BIN_DIR}/topology)
add_subdirectory(${SUB_DIR}/topology)
