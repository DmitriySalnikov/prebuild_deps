# Check for MINGW_PREFIX
if(DEFINED ENV{COMPILING_WITH_MINGW})
  if(DEFINED ENV{MINGW_PREFIX})
    message(STATUS "MINGW_PREFIX is set to: $ENV{MINGW_PREFIX}")
  else()
    message(FATAL_ERROR "MINGW_PREFIX is not set!")
  endif()
endif()
