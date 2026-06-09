#!/usr/bin/env bash

git submodule update --init --depth 1 --filter=blob:none \
external/cpr \
external/curl \
external/freetype \
external/glaze \
external/harfbuzz \
external/imgui/imgui \
external/luajit \
external/lunasvg \
external/rlottie \
external/rmlui \
external/sdl \
external/sdl_image \
external/spdlog

pushd external/harfbuzz
git sparse-checkout set --no-cone '/*' '!test' '!perf'
popd

pushd external/sdl_image
git submodule update --init --depth 1 --filter=blob:none \
external/jpeg \
external/libpng \
external/libtiff \
external/libwebp \
external/zlib
popd
