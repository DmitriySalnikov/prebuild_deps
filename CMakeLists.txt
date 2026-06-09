cmake_minimum_required(VERSION 4.0)

include(cmake/fix_tools_permissions_and_PATH.cmake)

project("OBSNotifierDeps"
    VERSION "1.0"
    LANGUAGES "C" "CXX"
)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED YES)
set(CMAKE_CXX_EXTENSIONS OFF)

set(BASH_EXE bash)
if(WIN32)
  find_package(Git REQUIRED)
  get_filename_component(GIT_DIR "${GIT_EXECUTABLE}" DIRECTORY)
  find_program(BASH_EXE_windows NAMES bash.exe HINTS "${GIT_DIR}/../bin")

  if(BASH_EXE_windows)
    set(BASH_EXE ${BASH_EXE_windows})
  else()
    message(FATAL_ERROR "bash.exe not found!")
  endif()
endif()

#add_compile_options("$<$<C_COMPILER_ID:MSVC>:/utf-8>")
#add_compile_options("$<$<CXX_COMPILER_ID:MSVC>:/utf-8>")

include(cmake/get_prebuild_install_name.cmake)

set(INSTALL_DEPS_ROOT_DIR "${CMAKE_CURRENT_SOURCE_DIR}/out/install")
set(PREBUILD_DEPS_DIR "${CMAKE_CURRENT_SOURCE_DIR}/prebuild/${PREBUILD_INSTALL_DIR_NAME}")
set(INSTALL_DEPS_DIR "${INSTALL_DEPS_ROOT_DIR}/${PREBUILD_INSTALL_DIR_NAME}")
set(PREFIX_DEPS_DIR "${CMAKE_CURRENT_SOURCE_DIR}/out/external_build")
set(IS_DARWIN $<BOOL:$<STREQUAL:${CMAKE_SYSTEM_NAME},Darwin>>)

if(NOT PROJECT_IS_TOP_LEVEL)
  if(IS_DIRECTORY ${PREBUILD_DEPS_DIR})
    set(OBSNOTIF_DEPS_INSTALL_DIR ${PREBUILD_DEPS_DIR} PARENT_SCOPE)
    return()
  else()
    set(OBSNOTIF_DEPS_INSTALL_DIR ${INSTALL_DEPS_DIR} PARENT_SCOPE)
  endif()
endif()

set(GIT_RESET git reset --hard)
set(GIT_APPLY git apply --unsafe-paths --ignore-space-change --ignore-whitespace)

set(SHARED_CMAKE_ARGS
  -D CMAKE_POLICY_VERSION_MINIMUM=4.0
  -D BUILD_SHARED_LIBS=OFF       # Build the library as a shared library
  -D CMAKE_MSVC_RUNTIME_LIBRARY=MultiThreaded
  -D CMAKE_INSTALL_PREFIX=${INSTALL_DEPS_DIR}
)

include(ExternalProject)

##################################################################################
# FreeType

ExternalProject_Add(freetype
  SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/external/freetype
  PREFIX ${PREFIX_DEPS_DIR}
  INSTALL_DIR ${INSTALL_DEPS_DIR}
  CMAKE_ARGS
    ${SHARED_CMAKE_ARGS}
    -D FT_DISABLE_BROTLI=ON        # Disable support of compressed WOFF2 fonts.
    -D FT_DISABLE_BZIP2=ON         # Disable support of bzip2 compressed fonts.
    -D FT_DISABLE_HARFBUZZ=ON      # Disable HarfBuzz (used for improving auto-hinting of OpenType fonts).
    -D FT_DISABLE_HVF=ON           # Disable support of HVF vector fonts.
    -D FT_DISABLE_PNG=ON           # Disable support of PNG compressed OpenType embedded bitmaps.
    -D FT_DISABLE_ZLIB=ON          # Disable use of system zlib and use internal zlib library instead.
    -D FT_DYNAMIC_HARFBUZZ=OFF     # Load HarfBuzz library dynamically at runtime, if possible.
    -D FT_ENABLE_ERROR_STRINGS=ON  # Enable support for meaningful error descriptions.
)

##################################################################################
# HarfBuzz

ExternalProject_Add(harfbuzz
  SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/external/harfbuzz
  DEPENDS freetype
  PREFIX ${PREFIX_DEPS_DIR}
  INSTALL_DIR ${INSTALL_DEPS_DIR}
  CMAKE_ARGS
    ${SHARED_CMAKE_ARGS}
    -D CMAKE_INSTALL_INCLUDEDIR=${INSTALL_DEPS_DIR}/include
    -D HB_BUILD_GPU=OFF           # Build harfbuzz-gpu
    -D HB_BUILD_RASTER=OFF        # Build harfbuzz-raster
    -D HB_BUILD_SUBSET=OFF        # Build harfbuzz-subset
    -D HB_BUILD_VECTOR=OFF        # Build harfbuzz-vector
    -D HB_BUILD_UTILS=OFF         # Build harfbuzz utils, needs cairo, freetype, and glib properly be installed
    -D HB_HAVE_CAIRO=OFF          # Enable cairo interop helpers
    -D HB_HAVE_DIRECTWRITE=OFF    # Enable DirectWrite shaper backend on Windows
    -D HB_HAVE_FREETYPE=ON        # Enable freetype interop helpers
    -D HB_HAVE_GDI=OFF            # Enable GDI integration helpers on Windows
    -D HB_HAVE_GLIB=OFF           # Enable glib unicode functions
    -D HB_HAVE_GOBJECT=OFF        # Enable GObject Bindings
    -D HB_HAVE_GRAPHITE2=OFF      # Enable Graphite2 complementary shaper
    -D HB_HAVE_ICU=OFF            # Enable icu unicode functions
    -D HB_HAVE_INTROSPECTION=OFF  # Enable building introspection (.gir/.typelib) files
    -D HB_HAVE_UNISCRIBE=OFF      # Enable Uniscribe shaper backend on Windows
)

##################################################################################
# SDL3

ExternalProject_Add(sdl
  SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/external/sdl
  PREFIX ${PREFIX_DEPS_DIR}
  INSTALL_DIR ${INSTALL_DEPS_DIR}
  CMAKE_ARGS
    ${SHARED_CMAKE_ARGS}
    -D SDL_SHARED=OFF
    -D SDL_STATIC=ON
    $<${IS_DARWIN}:-DSDL_FRAMEWORK_IOKIT=1>
    $<$<NOT:${IS_DARWIN}>:-DSDL_HIDAPI=OFF>

    -D SDL_AUDIO=ON
    -D SDL_CAMERA=OFF
    -D SDL_JOYSTICK=OFF
    -D SDL_XINPUT=OFF
    -D SDL_WASAPI=ON
    -D SDL_HAPTIC=OFF
    -D SDL_POWER=OFF
    -D SDL_SENSOR=OFF
    -D SDL_DIALOG=OFF
    -D SDL_OFFSCREEN=OFF
    -D SDL_DUMMYCAMERA=OFF
    -D SDL_LIBTHAI=OFF
    -D SDL_TESTS=OFF
    -D SDL_TEST_LIBRARY=OFF
    -D SDL_EXAMPLES=OFF
    -D SDL_AVX512F=OFF
    -D SDL_AVX2=OFF
    -D SDL_MMX=OFF

    -D SDL_RENDER_D3D=OFF
    -D SDL_GPU_OPENXR=OFF
    -D SDL_VIVANTE=OFF
)

##################################################################################
# SDL_image

ExternalProject_Add(sdl_image
  SOURCE_DIR   ${CMAKE_CURRENT_SOURCE_DIR}/external/sdl_image
  DEPENDS      sdl
  PREFIX       ${PREFIX_DEPS_DIR}
  INSTALL_DIR  ${INSTALL_DEPS_DIR}
  CMAKE_ARGS
    ${SHARED_CMAKE_ARGS}
    # enabled:  bmp gif jpg png apng webp
    -D SDLIMAGE_INSTALL=ON         # Enable SDL3_image install target
    -D SDLIMAGE_DEPS_SHARED=OFF    # Load dependencies dynamically
    -D SDLIMAGE_VENDORED=ON        # Use vendored third-party libraries
    -D SDLIMAGE_ANI=OFF            # Support loading ANI animations
    -D SDLIMAGE_ANI_SAVE=OFF       # Add ANI save support
    -D SDLIMAGE_AVIF=OFF           # Support loading AVIF images
    -D SDLIMAGE_AVIF_SAVE=OFF      # Add AVIF save support
    -D SDLIMAGE_BACKEND_STB=OFF    # Use stb_image for loading JPEG files
    -D SDLIMAGE_BACKEND_WIC=OFF    # Add WIC backend (Windows Imaging Component)
    -D SDLIMAGE_BMP=ON             # Support loading BMP images
    -D SDLIMAGE_BMP_SAVE=OFF       # Add BMP save support
    -D SDLIMAGE_GIF=ON             # Support loading GIF images
    -D SDLIMAGE_GIF_SAVE=OFF       # Add GIF save support
    -D SDLIMAGE_JPG=ON             # Support loading JPEG images
    -D SDLIMAGE_JPG_SAVE=OFF       # Add JPEG save support
    -D SDLIMAGE_JXL=OFF            # Support loading JXL images
    -D SDLIMAGE_LBM=OFF            # Support loading LBM images
    -D SDLIMAGE_PCX=OFF            # Support loading PCX images
    -D SDLIMAGE_PNG=ON             # Support loading PNG images
    -D SDLIMAGE_PNG_LIBPNG=ON      # Support loading PNGs using libpng (useful for APNGs)
    -D SDLIMAGE_PNG_SAVE=OFF       # Add PNG save support
    -D SDLIMAGE_PNM=OFF            # Support loading PNM images
    -D SDLIMAGE_QOI=OFF            # Support loading QOI images
    -D SDLIMAGE_SAMPLES=OFF        # Build the SDL3_image sample program(s)
    -D SDLIMAGE_STRICT=ON          # Fail when a dependency could not be found
    -D SDLIMAGE_SVG=OFF            # Support loading SVG images
    -D SDLIMAGE_TESTS=OFF          # Build unit tests?
    -D SDLIMAGE_TESTS_INSTALL=OFF  # Install unit tests?
    -D SDLIMAGE_TGA=ON             # Support loading TGA images
    -D SDLIMAGE_TGA_SAVE=OFF       # Add TGA save support
    -D SDLIMAGE_TIF=OFF            # Support loading TIFF images
    -D SDLIMAGE_WEBP=ON            # Support loading WEBP images
    -D SDLIMAGE_WEBP_SAVE=OFF      # Add WEBP save support
    -D SDLIMAGE_WERROR=OFF         # Treat warnings as errors
    -D SDLIMAGE_XCF=OFF            # Support loading XCF images
    -D SDLIMAGE_XPM=OFF            # Support loading XPM images
    -D SDLIMAGE_XV=OFF             # Support loading XV images
)

##################################################################################
# rlottie

set(RLOTTIE_PATCH_rlottie_msvcrt_fix_cmd ${GIT_APPLY} --directory=${CMAKE_CURRENT_SOURCE_DIR}/external/rlottie "${CMAKE_CURRENT_SOURCE_DIR}/patches/rlottie_msvcrt_fix.patch")
set(RLOTTIE_PATCH_rlottie_install_dir_fix_cmd ${GIT_APPLY} --directory=${CMAKE_CURRENT_SOURCE_DIR}/external/rlottie "${CMAKE_CURRENT_SOURCE_DIR}/patches/rlottie_install_dir_fix.patch")
set(RLOTTIE_PATCH_cmd ${GIT_RESET} && ${RLOTTIE_PATCH_rlottie_msvcrt_fix_cmd} && ${RLOTTIE_PATCH_rlottie_install_dir_fix_cmd})

ExternalProject_Add(rlottie
  SOURCE_DIR     ${CMAKE_CURRENT_SOURCE_DIR}/external/rlottie
  PREFIX         ${PREFIX_DEPS_DIR}
  INSTALL_DIR    ${INSTALL_DEPS_DIR}
  PATCH_COMMAND  ${RLOTTIE_PATCH_cmd}
  CMAKE_ARGS
    ${SHARED_CMAKE_ARGS}
    -D LIB_INSTALL_DIR=${INSTALL_DEPS_DIR}/lib
    -D LOTTIE_MODULE=OFF          # Enable LOTTIE MODULE SUPPORT
    -D LOTTIE_THREAD=ON           # Enable LOTTIE THREAD SUPPORT
    -D LOTTIE_CACHE=ON            # Enable LOTTIE CACHE SUPPORT
    -D LOTTIE_TEST=OFF            # Build LOTTIE AUTOTESTS
    -D LOTTIE_CCACHE=OFF          # Enable LOTTIE ccache SUPPORT
    -D LOTTIE_ASAN=OFF            # Compile with asan
)

##################################################################################
# lunasvg

ExternalProject_Add(lunasvg
  SOURCE_DIR   ${CMAKE_CURRENT_SOURCE_DIR}/external/lunasvg
  PREFIX       ${PREFIX_DEPS_DIR}
  INSTALL_DIR  ${INSTALL_DEPS_DIR}
  CMAKE_ARGS
    ${SHARED_CMAKE_ARGS}
    -D LUNASVG_DISABLE_LOAD_SYSTEM_FONTS=ON
    -D LUNASVG_BUILD_EXAMPLES=OFF
)

##################################################################################
# LUA

set(LUAJIT_ROOT_DIR ${CMAKE_CURRENT_SOURCE_DIR}/external/luajit)

set(LUAJIT_INSTALL_cmd ${BASH_EXE} ${CMAKE_CURRENT_SOURCE_DIR}/scripts/luajit_install.sh ${CMAKE_SYSTEM_NAME} ${INSTALL_DEPS_DIR})

set(LUAJIT_PATCH_luajit_msvcrt_fix_cmd ${GIT_APPLY} --directory=${LUAJIT_ROOT_DIR} "${CMAKE_CURRENT_SOURCE_DIR}/patches/luajit_msvcrt_fix.patch")
set(LUAJIT_PATCH_cmd ${GIT_RESET} && ${LUAJIT_PATCH_luajit_msvcrt_fix_cmd})

set(LUAJIT_BUILD_cmd "")
if(WIN32 AND MSVC)
  set(LUAJIT_BUILD_cmd ${LUAJIT_ROOT_DIR}/src/msvcbuild.bat amalg static)
endif()

ExternalProject_Add(luajit
  SOURCE_DIR   ${LUAJIT_ROOT_DIR}
  PREFIX       ${PREFIX_DEPS_DIR}
  CONFIGURE_COMMAND ""
  BUILD_COMMAND     cd ${LUAJIT_ROOT_DIR}/src && ${LUAJIT_BUILD_cmd}
  INSTALL_COMMAND   "${LUAJIT_INSTALL_cmd}"
  PATCH_COMMAND     ${LUAJIT_PATCH_cmd}
)

##################################################################################
# RmlUI

set(RMLUI_PATCH_rmlui_fix_luajit_search_cmd ${GIT_APPLY} --directory=${CMAKE_CURRENT_SOURCE_DIR}/external/RmlUi "${CMAKE_CURRENT_SOURCE_DIR}/patches/rmlui_fix_luajit_search.patch")
set(RMLUI_PATCH_cmd ${GIT_RESET} && ${RMLUI_PATCH_rmlui_fix_luajit_search_cmd})

ExternalProject_Add(rmlui
  SOURCE_DIR     ${CMAKE_CURRENT_SOURCE_DIR}/external/rmlui
  DEPENDS        sdl sdl_image harfbuzz freetype rlottie lunasvg luajit
  PREFIX         ${PREFIX_DEPS_DIR}
  INSTALL_DIR    ${INSTALL_DEPS_DIR}
  PATCH_COMMAND  ${RMLUI_PATCH_cmd}
  CMAKE_ARGS
    ${SHARED_CMAKE_ARGS}
    -D USE_STATIC_LIBS=ON                 # lua flag
    #-D RMLUI_SAMPLES=ON
    -D RMLUI_BACKEND=SDL_GPU
    -D RMLUI_HARFBUZZ_SAMPLE=ON
    -D RMLUI_IME_SAMPLE_USE_NOTO_FONTS=ON
    -D RMLUI_LUA_BINDINGS=ON              # Build Lua bindings.
    -D RMLUI_LUA_BINDINGS_LIBRARY=luajit  # Build Lua bindings.
    -D RMLUI_LOTTIE_PLUGIN=ON             # Enable plugin for Lottie animations. Requires the rlottie library.
    -D RMLUI_SVG_PLUGIN=ON                # Enable plugin for SVG images. Requires the lunasvg library.
)

##################################################################################
# ImGui

ExternalProject_Add(imgui
  SOURCE_DIR     ${CMAKE_CURRENT_SOURCE_DIR}/external/imgui
  DEPENDS        freetype lunasvg
  PREFIX         ${PREFIX_DEPS_DIR}
  INSTALL_DIR    ${INSTALL_DEPS_DIR}
  CMAKE_ARGS
    ${SHARED_CMAKE_ARGS}
)

##################################################################################
# spdlog

ExternalProject_Add(spdlog
  SOURCE_DIR     ${CMAKE_CURRENT_SOURCE_DIR}/external/spdlog
  PREFIX         ${PREFIX_DEPS_DIR}
  INSTALL_DIR    ${INSTALL_DEPS_DIR}
  CMAKE_ARGS
    ${SHARED_CMAKE_ARGS}
    -D SPDLOG_BUILD_ALL=OFF               # Build all artifacts
    -D SPDLOG_BUILD_BENCH=OFF             # Build benchmarks (Requires https:/ /github.com/google/benchmark.git to be installed)
    -D SPDLOG_BUILD_EXAMPLE=OFF           # Build example
    -D SPDLOG_BUILD_EXAMPLE_HO=OFF        # Build header only example
    -D SPDLOG_BUILD_PIC=ON                # Build position independent code (-fPIC)
    -D SPDLOG_BUILD_SHARED=OFF            # Build shared library
    -D SPDLOG_BUILD_TESTS=OFF             # Build tests
    -D SPDLOG_BUILD_TESTS_HO=OFF          # Build tests using the header only version
    -D SPDLOG_BUILD_WARNINGS=OFF          # Enable compiler warnings
    -D SPDLOG_CLOCK_COARSE=OFF            # non supported option
    -D SPDLOG_DEBUG_POSTFIX=d             # Filename postfix for libraries in debug builds
    -D SPDLOG_DISABLE_DEFAULT_LOGGER=OFF  # Disable default logger creation
    -D SPDLOG_ENABLE_PCH=OFF              # Build static or shared library using precompiled header to speed up compilation time
    -D SPDLOG_FMT_EXTERNAL=OFF            # Use external fmt library instead of bundled
    -D SPDLOG_FMT_EXTERNAL_HO=OFF         # Use external fmt header-only library instead of bundled
    -D SPDLOG_FWRITE_UNLOCKED=ON          # Use the unlocked variant of fwrite. Leave this on unless your libc doesn't have it
    -D SPDLOG_INSTALL=ON                  # Generate the install target
    -D SPDLOG_MSVC_UTF8=ON                # Enable/disable msvc /utf-8 flag required by fmt lib
    -D SPDLOG_NO_ATOMIC_LEVELS=OFF        # prevent spdlog from using of std::atomic log levels (use only if your code never modifies log levels concurrently
    -D SPDLOG_NO_EXCEPTIONS=OFF           # Compile with -fno-exceptions. Call abort() on any spdlog exceptions
    -D SPDLOG_NO_THREAD_ID=OFF            # prevent spdlog from querying the thread id on each log call if thread id is not needed
    -D SPDLOG_NO_TLS=OFF                  # prevent spdlog from using thread local storage
    -D SPDLOG_NO_TZ_OFFSET=OFF            # Omit %z timezone offset (use on platforms without tm_gmtoff)
    -D SPDLOG_PREVENT_CHILD_FD=ON         # Prevent from child processes to inherit log file descriptors
    -D SPDLOG_SANITIZE_ADDRESS=OFF        # Enable address sanitizer in tests
    -D SPDLOG_SANITIZE_THREAD=OFF         # Enable thread sanitizer in tests
    -D SPDLOG_SYSTEM_INCLUDES=OFF         # Include as system headers (skip for clang-tidy).
    -D SPDLOG_TIDY=OFF                    # run clang-tidy
    -D SPDLOG_USE_STD_FORMAT=OFF          # Use std::format instead of fmt library.
    -D SPDLOG_WCHAR_CONSOLE=OFF           # Support wchar output to console
    -D SPDLOG_WCHAR_FILENAMES=OFF         # Support wchar filenames
    -D SPDLOG_WCHAR_SUPPORT=OFF           # Support wchar api
)

##################################################################################
# glaze

ExternalProject_Add(glaze
  SOURCE_DIR     ${CMAKE_CURRENT_SOURCE_DIR}/external/glaze
  PREFIX         ${PREFIX_DEPS_DIR}
  INSTALL_DIR    ${INSTALL_DEPS_DIR}
  CMAKE_ARGS
    ${SHARED_CMAKE_ARGS}
    -D glaze_INSTALL=ON                       # Generate installation rules for glaze
    -D glaze_DISABLE_SIMD_WHEN_SUPPORTED=OFF  # disable SIMD optimizations even when targets support it (e.g. AVX2)
    -D glaze_DISABLE_ALWAYS_INLINE=OFF        # disable forced inlining to reduce binary size and compilation time
    -D glaze_BUILD_EXAMPLES=OFF               # Build GLAZE examples
    -D glaze_EETF_FORMAT=OFF                  # Enable Erlang external term format parsing
    -D glaze_ENABLE_SSL=OFF                   # Enable SSL/TLS support for HTTPS servers
    -D glaze_ENABLE_REFLECTION26=OFF          # Enable C++26 P2996 reflection (requires Bloomberg clang-p2996 or compatible compiler)
    -D glaze_DEVELOPER_MODE=OFF               # Enable developer mode
    -D glaze_ENABLE_FUZZING=OFF               # Enable building fuzzers
    -D glaze_INCLUDES_WITH_SYSTEM=OFF         # Use SYSTEM modifier for glaze's includes, disabling warnings
)

##################################################################################
# MbedTLS

ExternalProject_Add(mbedtls
  SOURCE_DIR     ${CMAKE_CURRENT_SOURCE_DIR}/external/mbedtls
  PREFIX         ${PREFIX_DEPS_DIR}
  INSTALL_DIR    ${INSTALL_DEPS_DIR}
  CMAKE_ARGS
    ${SHARED_CMAKE_ARGS}
    -D ENABLE_PROGRAMS=OFF                   # Build TF-PSA-Crypto programs.
    -D ENABLE_TESTING=OFF                    # Build TF-PSA-Crypto tests.
    -D GEN_FILES=OFF                         # Generate the auto-generated files as needed
    -D INSTALL_MBEDTLS_HEADERS=ON            # Install Mbed TLS headers.
    -D INSTALL_TF_PSA_CRYPTO_HEADERS=ON      # Install TF PSA Crypto headers.
    -D LINK_WITH_PTHREAD=OFF                 # Explicitly link Mbed TLS library to pthread.
    -D LINK_WITH_TRUSTED_STORAGE=OFF         # Explicitly link Mbed TLS library to trusted_storage.
    -D MBEDTLS_FATAL_WARNINGS=ON             # Compiler warnings treated as errors
    -D MSVC_STATIC_RUNTIME=ON                # Build the libraries with /MT compiler flag
    -D TF_PSA_CRYPTO_FATAL_WARNINGS=ON       # Compiler warnings treated as errors
    -D TF_PSA_CRYPTO_TEST_DRIVER=OFF         # Build TF-PSA-Crypto test driver for driver dispatch testing
    -D USE_SHARED_MBEDTLS_LIBRARY=OFF        # Build Mbed TLS shared library.
    -D USE_SHARED_TF_PSA_CRYPTO_LIBRARY=OFF  # Build TF-PSA-Crypto shared library.
    -D USE_STATIC_MBEDTLS_LIBRARY=ON         # Build Mbed TLS static library.
    -D USE_STATIC_TF_PSA_CRYPTO_LIBRARY=ON   # Build TF-PSA-Crypto static library.
)

##################################################################################
# curl

ExternalProject_Add(curl
  SOURCE_DIR     ${CMAKE_CURRENT_SOURCE_DIR}/external/curl
  DEPENDS        mbedtls
  PREFIX         ${PREFIX_DEPS_DIR}
  INSTALL_DIR    ${INSTALL_DEPS_DIR}
  CMAKE_ARGS
    ${SHARED_CMAKE_ARGS}
    -D BUILD_CURL_EXE=OFF                         # Build curl executable
    -D BUILD_EXAMPLES=OFF                         # Build libcurl examples
    -D BUILD_LIBCURL_DOCS=OFF                     # Build libcurl man pages
    -D BUILD_MISC_DOCS=OFF                        # Build misc man pages (e.g. curl-config and mk-ca-bundle)
    -D BUILD_STATIC_CURL=ON                       # Build curl executable with static libcurl
    -D BUILD_STATIC_LIBS=ON                       # Build static libraries
    -D BUILD_TESTING=OFF                          # Build tests
    -D CURL_BROTLI=OFF                            # Build curl with brotli support (AUTO, ON or OFF)
    -D CURL_BUILD_EVERYTHING=OFF                  # Build optional build targets (examples, tests) by default
    -D CURL_CA_NATIVE=OFF                         # Use native CA store
    -D CURL_CA_SEARCH_SAFE=OFF                    # Enable safe CA bundle search (within the curl tool directory) on Windows
    -D CURL_CLANG_TIDY=OFF                        # Run the build through clang-tidy
    -D CURL_CODE_COVERAGE=OFF                     # Enable code coverage build options
    -D CURL_DEBUG_GLOBAL_MEM=OFF                  # Debug curl_global_init_mem
    -D CURL_DISABLE_ALTSVC=ON                     # Disable alt-svc support
    -D CURL_DISABLE_AWS=ON                        # Disable aws-sigv4
    -D CURL_DISABLE_BASIC_AUTH=OFF                # Disable Basic authentication
    -D CURL_DISABLE_BEARER_AUTH=OFF               # Disable Bearer authentication
    -D CURL_DISABLE_BINDLOCAL=OFF                 # Disable local binding support
    -D CURL_DISABLE_CA_SEARCH=OFF                 # Disable unsafe CA bundle search in PATH on Windows
    -D CURL_DISABLE_COOKIES=ON                    # Disable cookies support
    -D CURL_DISABLE_DICT=ON                       # Disable DICT
    -D CURL_DISABLE_DIGEST_AUTH=OFF               # Disable Digest authentication
    -D CURL_DISABLE_DOH=ON                        # Disable DNS-over-HTTPS
    -D CURL_DISABLE_FILE=ON                       # Disable FILE
    -D CURL_DISABLE_FORM_API=ON                   # Disable form-api
    -D CURL_DISABLE_FTP=ON                        # Disable FTP
    -D CURL_DISABLE_GETOPTIONS=OFF                # Disable curl_easy_options API for existing options to curl_easy_setopt
    -D CURL_DISABLE_GOPHER=ON                     # Disable Gopher
    -D CURL_DISABLE_HEADERS_API=OFF               # Disable headers-api support
    -D CURL_DISABLE_HSTS=ON                       # Disable HSTS support
    -D CURL_DISABLE_HTTP=OFF                      # Disable HTTP
    -D CURL_DISABLE_HTTP_AUTH=OFF                 # Disable all HTTP authentication methods
    -D CURL_DISABLE_IMAP=ON                       # Disable IMAP
    -D CURL_DISABLE_INSTALL=OFF                   # Disable installation targets
    -D CURL_DISABLE_IPFS=ON                       # Disable IPFS
    -D CURL_DISABLE_KERBEROS_AUTH=ON              # Disable Kerberos authentication
    -D CURL_DISABLE_LDAP=ON                       # Disable LDAP
    -D CURL_DISABLE_LDAPS=ON                      # Disable LDAPS
    -D CURL_DISABLE_LIBCURL_OPTION=OFF            # Disable --libcurl option from the curl tool
    -D CURL_DISABLE_MIME=OFF                      # Disable MIME support
    -D CURL_DISABLE_MQTT=ON                       # Disable MQTT
    -D CURL_DISABLE_NEGOTIATE_AUTH=ON             # Disable negotiate authentication
    -D CURL_DISABLE_NETRC=ON                      # Disable netrc parser
    -D CURL_DISABLE_OPENSSL_AUTO_LOAD_CONFIG=OFF  # Disable automatic loading of OpenSSL configuration
    -D CURL_DISABLE_PARSEDATE=OFF                 # Disable date parsing
    -D CURL_DISABLE_POP3=ON                       # Disable POP3
    -D CURL_DISABLE_PROGRESS_METER=ON             # Disable built-in progress meter
    -D CURL_DISABLE_PROXY=ON                      # Disable proxy support
    -D CURL_DISABLE_RTSP=ON                       # Disable RTSP
    -D CURL_DISABLE_SHA512_256=ON                 # Disable SHA-512/256 hash algorithm
    -D CURL_DISABLE_SHUFFLE_DNS=ON                # Disable shuffle DNS feature
    -D CURL_DISABLE_SMTP=ON                       # Disable SMTP
    -D CURL_DISABLE_SOCKETPAIR=ON                 # Disable use of socketpair for curl_multi_poll()
    -D CURL_DISABLE_SRP=ON                        # Disable TLS-SRP support
    -D CURL_DISABLE_TELNET=ON                     # Disable Telnet
    -D CURL_DISABLE_TFTP=ON                       # Disable TFTP
    -D CURL_DISABLE_TYPECHECK=OFF                 # Disable curl_easy_setopt()/curl_easy_getinfo() type checking
    -D CURL_DISABLE_VERBOSE_STRINGS=OFF           # Disable verbose strings
    -D CURL_DISABLE_WEBSOCKETS=OFF                # Disable WebSocket
    -D CURL_DROP_UNUSED=OFF                       # Drop unused code and data from built binaries
    -D CURL_ENABLE_EXPORT_TARGET=ON               # Enable CMake export target
    -D CURL_ENABLE_NTLM=OFF                       # Enable NTLM support
    -D CURL_ENABLE_SMB=OFF                        # Enable SMB
    -D CURL_GCC_ANALYZER=OFF                      # Enable GCC --analyzer option
    -D CURL_HIDDEN_SYMBOLS=ON                     # Hide libcurl internal symbols (=hide all symbols that are not officially external)
    -D CURL_LINT=OFF                              # Run lint checks while building
    -D CURL_LTO=OFF                               # Enable compiler Link Time Optimizations
    -D CURL_STATIC_CRT=ON                         # Build libcurl with static CRT with MSVC (/MT)
    -D CURL_USE_CMAKECONFIG=ON                    # Enable detecting dependencies via CMake Config
    -D CURL_USE_GSASL=OFF                         # Use libgsasl
    -D CURL_USE_GSSAPI=OFF                        # Use GSSAPI implementation
    -D CURL_USE_LIBBACKTRACE=OFF                  # Use libbacktrace. Requires debug-enabled build and DWARF debug information.
    -D CURL_USE_LIBPSL=OFF                        # Use libpsl
    -D CURL_USE_LIBSSH=OFF                        # Use libssh
    -D CURL_USE_LIBSSH2=OFF                       # Use libssh2
    -D CURL_USE_LIBUV=OFF                         # Use libuv for event-based tests
    -D CURL_ENABLE_SSL=ON                         # Enable SSL support
    -D CURL_USE_OPENSSL=OFF                       # Enable OpenSSL for SSL/TLS
    -D CURL_USE_MBEDTLS=ON                        # Enable mbedTLS for SSL/TLS
    -D CURL_USE_GNUTLS=OFF                        # Enable GnuTLS for SSL/TLS
    -D CURL_USE_SCHANNEL=OFF                      # Enable Windows native SSL/TLS (Schannel)
    -D USE_APPLE_SECTRUST=OFF                     # Use Apple OS-native certificate verification
    -D CURL_USE_WOLFSSL=OFF                       # Enable wolfSSL for SSL/TLS
    -D CURL_USE_PKGCONFIG=OFF                     # Enable pkg-config to detect dependencies
    -D CURL_USE_RUSTLS=OFF                        # Enable Rustls for SSL/TLS (experimental)
    -D CURL_WERROR=OFF                            # Turn compiler warnings into errors
    -D CURL_WINDOWS_SSPI=OFF                      # Enable SSPI on Windows
    -D CURL_ZLIB=OFF                              # Build curl with ZLIB support (AUTO, ON or OFF)
    -D CURL_ZSTD=OFF                              # Build curl with zstd support (AUTO, ON or OFF)
    -D ENABLE_ARES=OFF                            # Enable c-ares support
    -D ENABLE_CURL_MANUAL=OFF                     # Build the man page for curl and enable its -M/--manual option
    -D ENABLE_DEBUG=OFF                           # Enable curl debug features (for developing curl itself)
    -D ENABLE_IPV6=ON                             # Enable IPv6 support
    -D ENABLE_THREADED_RESOLVER=ON                # Enable threaded DNS lookup
    -D ENABLE_UNICODE=ON                          # Use the Unicode version of the Windows API functions
    -D ENABLE_UNIX_SOCKETS=ON                     # Enable Unix domain sockets support
    -D LIBCURL_OUTPUT_NAME=libcurl                # Basename of the curl library
    -D PICKY_COMPILER=ON                          # Enable picky compiler options
    -D USE_ECH=OFF                                # Enable ECH support (experimental)
    -D USE_HTTPSRR=OFF                            # Enable HTTPS RR support (experimental)
    -D USE_LIBIDN2=OFF                            # Use libidn2 for IDN support
    -D USE_NGHTTP2=OFF                            # Use nghttp2 library
    -D USE_NGTCP2=OFF                             # Use ngtcp2 and nghttp3 libraries for HTTP/3 support
    -D USE_PROXY_HTTP3=OFF                        # Enable HTTP/3 proxy support (experimental)
    -D USE_QUICHE=OFF                             # Use quiche library for HTTP/3 support (experimental)
    -D USE_SSLS_EXPORT=OFF                        # Enable SSL session import/export (experimental)
    -D USE_WIN32_IDN=OFF                          # Use WinIDN for IDN support
    -D USE_WIN32_LDAP=OFF                         # Use Windows LDAP impleme
)

##################################################################################
# cpr

ExternalProject_Add(cpr
  SOURCE_DIR     ${CMAKE_CURRENT_SOURCE_DIR}/external/cpr
  DEPENDS        curl mbedtls
  PREFIX         ${PREFIX_DEPS_DIR}
  INSTALL_DIR    ${INSTALL_DEPS_DIR}
  CMAKE_ARGS
    ${SHARED_CMAKE_ARGS}
    -D CPR_ENABLE_INSTALL=ON                # Set to ON to enable all cpr install targets
    -D CPR_GENERATE_COVERAGE=OFF            # Set to ON to generate coverage reports
    -D CPR_CURL_NOSIGNAL=OFF                # Set to ON to disable use of signals in libcurl
    -D CURL_VERBOSE_LOGGING=ON              # Curl verbose logging during building curl
    -D CPR_USE_SYSTEM_GTEST=OFF             # If ON, this project will look in the system paths for an installed gtest library. If none is found it will use the built-in one
    -D CPR_USE_SYSTEM_CURL=ON               # If enabled we will use the curl lib already installed on this system
    -D CPR_USE_EXISTING_CURL_TARGET=OFF     # Use an existing libcurl cmake target instead of having the cpr project source the dependency itself
    -D CPR_CURL_USE_LIBPSL=OFF              # Since curl 8.13 curl depends on libpsl (https:/ /everything.curl.dev/build/deps.html#libpsl). By default cpr keeps this as a secure default enabled wich in turn requires meson as build dependency. If set to OFF, psl support inside curl will be disabled
    -D CPR_USE_SYSTEM_LIB_PSL=OFF           # If enabled we will use the psl lib already installed on this system. Else meson is required as build dependency. Only relevant in case 'CPR_CURL_USE_LIBPSL' is set to ON." $
    -D CPR_ENABLE_CURL_HTTP_ONLY=OFF        # If enabled we will only use the HTTP/HTTPS protocols from CURL. If disabled, all the CURL protocols are enabled. This is useful if your project uses libcurl and you need support for other CURL features e.g. sending emails
    -D CPR_ENABLE_SSL=ON                    # Enables or disables the SSL backend. Required to perform HTTPS requests
    -D CPR_FORCE_OPENSSL_BACKEND=OFF        # Force to use the OpenSSL backend. If CPR_FORCE_OPENSSL_BACKEND, CPR_FORCE_DARWINSSL_BACKEND, CPR_FORCE_MBEDTLS_BACKEND, and CPR_FORCE_WINSSL_BACKEND are set to to OFF, cpr will try to automatically detect the best available SSL backend (WinSSL - Windows, OpenSSL - Linux, DarwinSSL - Mac 
    -D CPR_FORCE_MBEDTLS_BACKEND=ON         # Force to use the Mbed TLS backend. If CPR_FORCE_OPENSSL_BACKEND, CPR_FORCE_DARWINSSL_BACKEND, CPR_FORCE_MBEDTLS_BACKEND, and CPR_FORCE_WINSSL_BACKEND are set to to OFF, cpr will try to automatically detect the best available SSL backend (WinSSL - Windows, OpenSSL - Linux, DarwinSSL - Mac 
    -D CPR_FORCE_WINSSL_BACKEND=OFF         # Force to use the WinSSL backend. If CPR_FORCE_OPENSSL_BACKEND, CPR_FORCE_DARWINSSL_BACKEND, CPR_FORCE_MBEDTLS_BACKEND, and CPR_FORCE_WINSSL_BACKEND are set to to OFF, cpr will try to automatically detect the best available SSL backend (WinSSL - Windows, OpenSSL - Linux, DarwinSSL - Mac 
    -D CPR_FORCE_DARWINSSL_BACKEND=OFF      # Force to use the DarwinSSL backend. If CPR_FORCE_OPENSSL_BACKEND, CPR_FORCE_DARWINSSL_BACKEND, CPR_FORCE_MBEDTLS_BACKEND, and CPR_FORCE_WINSSL_BACKEND are set to to OFF, cpr will try to automatically detect the best available SSL backend (WinSSL - Windows, OpenSSL - Linux, DarwinSSL - Mac 
    -D CPR_ENABLE_LINTING=OFF               # Set to ON to enable clang linting
    -D CPR_ENABLE_CPPCHECK=OFF              # Set to ON to enable Cppcheck static analysis. Requires CPR_BUILD_TESTS and CPR_BUILD_TESTS_SSL to be OFF to prevent checking google tests source code
    -D CPR_BUILD_TESTS=OFF                  # Set to ON to build cpr tests
    -D CPR_BUILD_TESTS_SSL=OFF              # Set to ON to build cpr ssl tests
    -D CPR_BUILD_TESTS_PROXY=OFF            # Set to ON to build proxy tests. They fail in case there is no valid proxy server available in proxy_tests.cpp
    -D CPR_BUILD_VERSION_OUTPUT_ONLY=OFF    # Set to ON to only export the version into 'build/version.txt' and exit
    -D CPR_SKIP_CA_BUNDLE_SEARCH=OFF        # Skip searching for Certificate Authority certs. Turn ON for systems like iOS where file access is restricted and prevents https from working
    -D CPR_USE_BOOST_FILESYSTEM=OFF         # Set to ON to use the Boost.Filesystem library. This is useful, on, e.g., Apple platforms, where std::filesystem may not always be available when targeting older OS versions
    -D CPR_DEBUG_SANITIZER_FLAG_THREAD=OFF  # Enables the ThreadSanitizer for debug builds
    -D CPR_DEBUG_SANITIZER_FLAG_ADDR=OFF    # Enables the AddressSanitizer for debug builds
    -D CPR_DEBUG_SANITIZER_FLAG_LEAK=OFF    # Enables the LeakSanitizer for debug builds
    -D CPR_DEBUG_SANITIZER_FLAG_UB=OFF      # Enables the UndefinedBehaviorSanitizer for debug builds
    -D CPR_DEBUG_SANITIZER_FLAG_ALL=OFF     # Enables all sanitizers for debug builds except the ThreadSanitizer since it is incompatible with the other sanitizers
)

##################################################################################
# Fix and pack

set(PACK_ALL_LIBS
  cpr
  curl
  freetype
  glaze
  harfbuzz
  imgui
  luajit
  lunasvg
  mbedtls
  rlottie
  rmlui
  sdl
  sdl_image
  spdlog
)

ExternalProject_Add(pack
  SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/scripts
  DEPENDS ${PACK_ALL_LIBS}
  CONFIGURE_COMMAND ""
  INSTALL_COMMAND ""
  BUILD_COMMAND python "${CMAKE_CURRENT_SOURCE_DIR}/scripts/pack_install_dir.py" "${INSTALL_DEPS_DIR}"
)
