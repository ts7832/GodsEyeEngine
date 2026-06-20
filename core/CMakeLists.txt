cmake_minimum_required(VERSION 3.10)
project(GodsEyeEngine)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find SQLite3
find_package(SQLite3 REQUIRED)

# Include directories
include_directories(${SQLite3_INCLUDE_DIRS})

# Add source files
set(SOURCES
    main.cpp
    graph.cpp
    thesis.cpp
    db_handler.cpp
)

# Add executable
add_executable(godseye ${SOURCES})

# Link libraries
target_link_libraries(godseye ${SQLite3_LIBRARIES})
