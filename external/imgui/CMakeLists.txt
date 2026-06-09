cmake_minimum_required(VERSION 4.0)

project("imgui_dep"
    VERSION "1.92.9"
    LANGUAGES "C" "CXX"
)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED YES)
set(CMAKE_CXX_EXTENSIONS OFF)

set(IS_DARWIN $<BOOL:$<STREQUAL:${CMAKE_SYSTEM_NAME},Darwin>>)

set(imgui_headers
  imgui/imconfig.h
  imgui/imgui.h
  imgui/imgui_internal.h
  imgui/imstb_rectpack.h
  imgui/imstb_textedit.h
  imgui/imstb_truetype.h
  imgui/misc/cpp/imgui_stdlib.h
  imgui/misc/freetype/imgui_freetype.h
  imgui/misc/single_file/imgui_single_file.h
)

set(imgui_sources
  imgui/imgui.cpp
  imgui/imgui_demo.cpp
  imgui/imgui_draw.cpp
  imgui/imgui_tables.cpp
  imgui/imgui_widgets.cpp
  imgui/misc/cpp/imgui_stdlib.cpp
  imgui/misc/freetype/imgui_freetype.cpp
)

add_library(imgui ${imgui_sources} ${imgui_headers})

find_package(freetype REQUIRED)
find_package(lunasvg REQUIRED)
message(STATUS "Freetype_FOUND: ${Freetype_FOUND}")
message(STATUS "lunasvg found: ${lunasvg_FOUND}")

target_sources(imgui PUBLIC FILE_SET HEADERS FILES ${imgui_headers})
target_link_libraries(imgui INTERFACE Freetype::Freetype lunasvg::lunasvg)
target_compile_options(imgui PRIVATE "$<$<CXX_COMPILER_ID:MSVC>:/utf-8>")
target_include_directories(imgui PRIVATE "imgui" "${CMAKE_INSTALL_PREFIX}/include/freetype2")
target_compile_definitions(imgui INTERFACE
  IMGUI_DISABLE_OBSOLETE_FUNCTIONS  # Don't define obsolete functions/enums/behaviors. Consider enabling from time to time after updating to clean your code of obsolete function/names.
  IMGUI_DEFINE_MATH_OPERATORS       # Use Dear ImGui's own very basic math operators.
  IMGUI_ENABLE_FREETYPE             # Use FreeType to build and rasterize the font atlas (instead of stb_truetype which is embedded by default in Dear ImGui)
  IMGUI_ENABLE_FREETYPE_LUNASVG     # Use FreeType + lunasvg to render OpenType SVG fonts (SVGinOT)

  #IMGUI_DISABLE                    # Disable everything: all headers and source files will be empty.
  #IMGUI_DISABLE_DEMO_WINDOWS       # Disable demo windows: ShowDemoWindow()/ShowStyleEditor() will be empty.
  #IMGUI_DISABLE_DEBUG_TOOLS        # Disable metrics/debugger and other debug tools: ShowMetricsWindow(), ShowDebugLogWindow() and ShowIDStackToolWindow() will be empty.
  #IMGUI_USE_WCHAR32 #Use 32-bit for ImWchar (default is 16-bit) to support Unicode planes 1-16. (e.g. point beyond 0xFFFF like emoticons, dingbats, symbols, shapes, ancient languages, etc...)
)

include(GNUInstallDirs)
include(CMakePackageConfigHelpers)

install(TARGETS imgui
  EXPORT imguiTargets
  RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
  ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
  LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
  FILE_SET HEADERS DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
  FRAMEWORK DESTINATION Library/Frameworks
)

install(
    EXPORT imguiTargets
    FILE imguiTargets.cmake
    NAMESPACE imgui::
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/imgui
)

configure_package_config_file(
    imguiConfig.cmake.in
    ${CMAKE_CURRENT_BINARY_DIR}/imguiConfig.cmake
    INSTALL_DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/imgui
)

write_basic_package_version_file(
    ${CMAKE_CURRENT_BINARY_DIR}/imguiConfigVersion.cmake
    VERSION ${PROJECT_VERSION}
    COMPATIBILITY SameMajorVersion
)

install(
    FILES
        ${CMAKE_CURRENT_BINARY_DIR}/imguiConfig.cmake
        ${CMAKE_CURRENT_BINARY_DIR}/imguiConfigVersion.cmake
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/imgui
)
