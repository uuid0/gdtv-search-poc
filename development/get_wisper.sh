#!/bin/bash -ex

BASE_DIR=$(dirname "$0")
cd "$BASE_DIR"
BASE_DIR="$(pwd)"

WHISPER_CPP_VERSION=v1.8.1

git clone -b $WHISPER_CPP_VERSION --depth 1 https://github.com/ggerganov/whisper.cpp.git
cd whisper.cpp
cmake -B build \
      -DCMAKE_BUILD_TYPE=Release \
      -DGGML_NATIVE=ON
cmake --build build -j2 --config Release

cd "$BASE_DIR"
ln -s whisper.cpp/build/bin/whisper-cli ./whisper