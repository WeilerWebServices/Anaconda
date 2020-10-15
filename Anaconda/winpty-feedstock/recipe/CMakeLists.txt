# Winpty CMake generator
project(winpty)
cmake_minimum_required (VERSION 2.8)

execute_process(COMMAND cmd /c "cd shared && GetCommitHash.bat" OUTPUT_VARIABLE WINPTY_COMMIT_HASH)
execute_process(COMMAND cmd /c "cd shared && UpdateGenVersion.bat ${WINPTY_COMMIT_HASH}"
                OUTPUT_VARIABLE ADDITIONAL_LIB OUTPUT_STRIP_TRAILING_WHITESPACE)

SET (EXECUTABLE_OUTPUT_PATH ${CMAKE_BINARY_DIR}/bin)
SET (LIBRARY_OUTPUT_PATH ${CMAKE_BINARY_DIR}/lib)

#set(WINPTY_MSBUILD_TOOLSET%)

SET(TARGET "winpty-agent")
SET(TOOLSET "target")

SET(winpty-agent_lib_sources
  "agent/Agent.cc"
  "agent/AgentCreateDesktop.cc"
  "agent/ConsoleFont.cc"
  "agent/ConsoleInput.cc"
  "agent/ConsoleInputReencoding.cc"
  "agent/ConsoleLine.cc"
  "agent/DebugShowInput.cc"
  "agent/DefaultInputMap.cc"
  "agent/EventLoop.cc"
  "agent/InputMap.cc"
  "agent/LargeConsoleRead.cc"
  "agent/NamedPipe.cc"
  "agent/Scraper.cc"
  "agent/Terminal.cc"
  "agent/Win32Console.cc"
  "agent/Win32ConsoleBuffer.cc"
  "agent/main.cc"
  "shared/BackgroundDesktop.cc"
  "shared/Buffer.cc"
  "shared/DebugClient.cc"
  "shared/GenRandom.cc"
  "shared/OwnedHandle.cc"
  "shared/StringUtil.cc"
  "shared/WindowsSecurity.cc"
  "shared/WindowsVersion.cc"
  "shared/WinptyAssert.cc"
  "shared/WinptyException.cc"
  "shared/WinptyVersion.cc")

SET(winpty-agent_lib_headers
  "agent/Agent.h"
  "agent/AgentCreateDesktop.h"
  "agent/ConsoleFont.h"
  "agent/ConsoleInput.h"
  "agent/ConsoleInputReencoding.h"
  "agent/ConsoleLine.h"
  "agent/Coord.h"
  "agent/DebugShowInput.h"
  "agent/DefaultInputMap.h"
  "agent/DsrSender.h"
  "agent/EventLoop.h"
  "agent/InputMap.h"
  "agent/LargeConsoleRead.h"
  "agent/NamedPipe.h"
  "agent/Scraper.h"
  "agent/SimplePool.h"
  "agent/SmallRect.h"
  "agent/Terminal.h"
  "agent/UnicodeEncoding.h"
  "agent/Win32Console.h"
  "agent/Win32ConsoleBuffer.h"
  "shared/AgentMsg.h"
  "shared/BackgroundDesktop.h"
  "shared/Buffer.h"
  "shared/DebugClient.h"
  "shared/GenRandom.h"
  "shared/OsModule.h"
  "shared/OwnedHandle.h"
  "shared/StringBuilder.h"
  "shared/StringUtil.h"
  "shared/UnixCtrlChars.h"
  "shared/WindowsSecurity.h"
  "shared/WindowsVersion.h"
  "shared/WinptyAssert.h"
  "shared/WinptyException.h"
  "shared/WinptyVersion.h"
  "shared/winpty_snprintf.h"
)

add_executable(winpty-agent ${winpty-agent_lib_sources} ${winpty-agent_lib_headers})
set_property(TARGET winpty-agent APPEND PROPERTY INCLUDE_DIRECTORIES ${CMAKE_BINARY_DIR}/${ADDITIONAL_LIB})
set_property(TARGET winpty-agent APPEND PROPERTY INCLUDE_DIRECTORIES ${CMAKE_BINARY_DIR}/include)
set_target_properties(winpty-agent PROPERTIES COMPILE_DEFINITIONS "UNICODE;_UNICODE;_WIN32_WINNT=0x0501;NOMINMAX;WINPTY_AGENT_ASSERT;")
target_link_libraries(winpty-agent
  "-ladvapi32"
  "-lshell32"
  "-luser32"
)

UNSET(TARGET)
UNSET(TOOLSET)

SET(TARGET "winpty")
SET(TOOLSET "target")

SET(winpty_lib_sources
  "libwinpty/AgentLocation.cc"
  "libwinpty/winpty.cc"
  "shared/BackgroundDesktop.cc"
  "shared/Buffer.cc"
  "shared/DebugClient.cc"
  "shared/GenRandom.cc"
  "shared/OwnedHandle.cc"
  "shared/StringUtil.cc"
  "shared/WindowsSecurity.cc"
  "shared/WindowsVersion.cc"
  "shared/WinptyAssert.cc"
  "shared/WinptyException.cc"
  "shared/WinptyVersion.cc"
)

SET(winpty_lib_headers
  "include/winpty.h"
  "libwinpty/AgentLocation.h"
  "shared/AgentMsg.h"
  "shared/BackgroundDesktop.h"
  "shared/Buffer.h"
  "shared/DebugClient.h"
  "shared/GenRandom.h"
  "shared/OsModule.h"
  "shared/OwnedHandle.h"
  "shared/StringBuilder.h"
  "shared/StringUtil.h"
  "shared/WindowsSecurity.h"
  "shared/WindowsVersion.h"
  "shared/WinptyAssert.h"
  "shared/WinptyException.h"
  "shared/WinptyVersion.h"
  "shared/winpty_snprintf.h"
)

add_library(winpty SHARED ${winpty_lib_sources} ${winpty_lib_headers})
set_property(TARGET winpty APPEND PROPERTY INCLUDE_DIRECTORIES ${CMAKE_BINARY_DIR}/${ADDITIONAL_LIB})
set_property(TARGET winpty APPEND PROPERTY INCLUDE_DIRECTORIES ${CMAKE_BINARY_DIR}/include)
set_target_properties(winpty PROPERTIES COMPILE_DEFINITIONS "UNICODE;_UNICODE;_WIN32_WINNT=0x0501;NOMINMAX;COMPILING_WINPTY_DLL;")
target_link_libraries(winpty
  "-ladvapi32"
  "-luser32"
)

UNSET(TARGET)
UNSET(TOOLSET)

SET(TARGET "winpty-debugserver")
SET(TOOLSET "target")

SET(winpty-debugserver_lib_sources
  "debugserver/DebugServer.cc"
  "shared/DebugClient.cc"
  "shared/OwnedHandle.cc"
  "shared/StringUtil.cc"
  "shared/WindowsSecurity.cc"
  "shared/WindowsVersion.cc"
  "shared/WinptyAssert.cc"
  "shared/WinptyException.cc"
)

SET(winpty-debugserver_lib_headers
  "shared/DebugClient.h"
  "shared/OwnedHandle.h"
  "shared/OsModule.h"
  "shared/StringBuilder.h"
  "shared/StringUtil.h"
  "shared/WindowsSecurity.h"
  "shared/WindowsVersion.h"
  "shared/WinptyAssert.h"
  "shared/WinptyException.h"
  "shared/winpty_snprintf.h"
)

add_executable(winpty-debugserver ${winpty-debugserver_lib_sources} ${winpty-debugserver_lib_headers})
set_property(TARGET winpty-debugserver APPEND PROPERTY INCLUDE_DIRECTORIES ${CMAKE_BINARY_DIR}/include)
set_property(TARGET winpty-debugserver APPEND PROPERTY INCLUDE_DIRECTORIES ${CMAKE_BINARY_DIR}/${ADDITIONAL_LIB})
set_target_properties(winpty-debugserver PROPERTIES COMPILE_DEFINITIONS "UNICODE;_UNICODE;_WIN32_WINNT=0x0501;NOMINMAX;")
target_link_libraries(winpty-debugserver
  "-ladvapi32"
)
