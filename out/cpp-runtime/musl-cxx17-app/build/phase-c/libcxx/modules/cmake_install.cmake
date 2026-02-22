# Install script for directory: /Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules

# Set the install prefix
if(NOT DEFINED CMAKE_INSTALL_PREFIX)
  set(CMAKE_INSTALL_PREFIX "/Users/zhoubot/linx-isa/out/cpp-runtime/musl-cxx17-app/install")
endif()
string(REGEX REPLACE "/$" "" CMAKE_INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}")

# Set the install configuration name.
if(NOT DEFINED CMAKE_INSTALL_CONFIG_NAME)
  if(BUILD_TYPE)
    string(REGEX REPLACE "^[^A-Za-z0-9_]+" ""
           CMAKE_INSTALL_CONFIG_NAME "${BUILD_TYPE}")
  else()
    set(CMAKE_INSTALL_CONFIG_NAME "Release")
  endif()
  message(STATUS "Install configuration: \"${CMAKE_INSTALL_CONFIG_NAME}\"")
endif()

# Set the component getting installed.
if(NOT CMAKE_INSTALL_COMPONENT)
  if(COMPONENT)
    message(STATUS "Install component: \"${COMPONENT}\"")
    set(CMAKE_INSTALL_COMPONENT "${COMPONENT}")
  else()
    set(CMAKE_INSTALL_COMPONENT)
  endif()
endif()

# Install shared libraries without execute permission?
if(NOT DEFINED CMAKE_INSTALL_SO_NO_EXE)
  set(CMAKE_INSTALL_SO_NO_EXE "0")
endif()

# Is this installation the result of a crosscompile?
if(NOT DEFINED CMAKE_CROSSCOMPILING)
  set(CMAKE_CROSSCOMPILING "TRUE")
endif()

# Set path to fallback-tool for dependency-resolution.
if(NOT DEFINED CMAKE_OBJDUMP)
  set(CMAKE_OBJDUMP "/Users/zhoubot/linx-isa/compiler/llvm/build-linxisa-clang/bin/llvm-objdump")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/algorithm.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/any.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/array.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/atomic.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/barrier.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/bit.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/bitset.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/cassert.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/cctype.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/cerrno.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/cfenv.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/cfloat.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/charconv.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/chrono.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/cinttypes.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/climits.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/clocale.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/cmath.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/codecvt.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/compare.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/complex.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/concepts.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/condition_variable.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/coroutine.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/csetjmp.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/csignal.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/cstdarg.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/cstddef.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/cstdint.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/cstdio.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/cstdlib.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/cstring.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/ctime.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/cuchar.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/cwchar.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/cwctype.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/deque.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/exception.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/execution.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/expected.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/filesystem.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/flat_map.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/flat_set.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/format.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/forward_list.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/fstream.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/functional.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/future.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/generator.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/hazard_pointer.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/initializer_list.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/iomanip.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/ios.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/iosfwd.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/iostream.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/istream.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/iterator.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/latch.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/limits.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/list.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/locale.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/map.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/mdspan.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/memory.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/memory_resource.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/mutex.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/new.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/numbers.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/numeric.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/optional.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/ostream.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/print.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/queue.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/random.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/ranges.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/ratio.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/rcu.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/regex.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/scoped_allocator.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/semaphore.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/set.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/shared_mutex.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/source_location.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/span.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/spanstream.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/sstream.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/stack.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/stacktrace.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/stdexcept.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/stdfloat.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/stop_token.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/streambuf.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/string.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/string_view.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/strstream.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/syncstream.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/system_error.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/text_encoding.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/thread.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/tuple.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/type_traits.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/typeindex.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/typeinfo.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/unordered_map.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/unordered_set.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/utility.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/valarray.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/variant.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/vector.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std/version.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std.compat" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std.compat/cassert.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std.compat" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std.compat/cctype.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std.compat" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std.compat/cerrno.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std.compat" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std.compat/cfenv.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std.compat" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std.compat/cfloat.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std.compat" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std.compat/cinttypes.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std.compat" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std.compat/climits.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std.compat" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std.compat/clocale.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std.compat" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std.compat/cmath.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std.compat" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std.compat/csetjmp.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std.compat" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std.compat/csignal.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std.compat" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std.compat/cstdarg.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std.compat" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std.compat/cstddef.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std.compat" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std.compat/cstdint.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std.compat" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std.compat/cstdio.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std.compat" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std.compat/cstdlib.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std.compat" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std.compat/cstring.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std.compat" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std.compat/ctime.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std.compat" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std.compat/cuchar.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std.compat" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std.compat/cwchar.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1/std.compat" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/compiler/llvm/libcxx/modules/std.compat/cwctype.inc")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/libc++/v1" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES
    "/Users/zhoubot/linx-isa/compiler/llvm/build-linxisa-clang/modules/c++/v1/std.cppm"
    "/Users/zhoubot/linx-isa/compiler/llvm/build-linxisa-clang/modules/c++/v1/std.compat.cppm"
    )
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "cxx-modules" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib" TYPE FILE PERMISSIONS OWNER_READ OWNER_WRITE GROUP_READ WORLD_READ FILES "/Users/zhoubot/linx-isa/out/cpp-runtime/musl-cxx17-app/build/phase-c/./lib/libc++.modules.json")
endif()

string(REPLACE ";" "\n" CMAKE_INSTALL_MANIFEST_CONTENT
       "${CMAKE_INSTALL_MANIFEST_FILES}")
if(CMAKE_INSTALL_LOCAL_ONLY)
  file(WRITE "/Users/zhoubot/linx-isa/out/cpp-runtime/musl-cxx17-app/build/phase-c/libcxx/modules/install_local_manifest.txt"
     "${CMAKE_INSTALL_MANIFEST_CONTENT}")
endif()
