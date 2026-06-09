# Fix unix permissions
if(UNIX)
  if(CMAKE_HOST_SYSTEM_NAME STREQUAL "Linux" OR CMAKE_HOST_SYSTEM_NAME STREQUAL "Darwin")
    set(NINJA_PATH "${CMAKE_SOURCE_DIR}/tools/ninja/${CMAKE_HOST_SYSTEM_NAME}/ninja")
    set(NASM_PATH "${CMAKE_SOURCE_DIR}/tools/nasm/${CMAKE_HOST_SYSTEM_NAME}/nasm")
    set(NDISASM_PATH "${CMAKE_SOURCE_DIR}/tools/nasm/${CMAKE_HOST_SYSTEM_NAME}/ndisasm")

    set(ENV{PATH} "${CMAKE_SOURCE_DIR}/tools/ninja/${CMAKE_HOST_SYSTEM_NAME};${CMAKE_SOURCE_DIR}/tools/nasm/${CMAKE_HOST_SYSTEM_NAME};$ENV{PATH}")
  else()
    message(FATAL_ERROR "Unsupported UNIX-like system: ${CMAKE_HOST_SYSTEM_NAME}")
  endif()

  foreach(TOOL_PATH IN LISTS NINJA_PATH NASM_PATH NDISASM_PATH)
    execute_process(
      COMMAND chmod +x ${TOOL_PATH}
      WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
      RESULT_VARIABLE chmod_result
      ERROR_VARIABLE chmod_error
    )

    if(NOT chmod_result EQUAL 0)
      if(NOT TOOL_PATH MATCHES "^/mnt/hgfs/.*")
          message(FATAL_ERROR "Failed to set execute permissions for '${TOOL_PATH}': ${chmod_error}")
      endif()
    else()
      message(STATUS "Successfully added execution permissions to the '${TOOL_PATH}'.")
    endif()
  endforeach()
elseif(WIN32)
  set(ENV{PATH} "${CMAKE_SOURCE_DIR}/tools/ninja/Windows;${CMAKE_SOURCE_DIR}/tools/nasm/Windows;$ENV{PATH}")
endif()
