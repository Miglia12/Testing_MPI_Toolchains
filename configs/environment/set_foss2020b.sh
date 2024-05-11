#!/bin/bash

# Determine the root of the repo
if ! ROOT_REPO=$(git rev-parse --show-toplevel); then
    printf "Failed to find the git repository root.\n" >&2
    exit 1
fi

TAR_FILE="$ROOT_REPO/src/osu-micro-benchmarks-7.4.tar.gz"
EXTRACTED_TAR="$ROOT_REPO/src/osu-micro-benchmarks-7.4"
SRC_DIR="$ROOT_REPO/src/"
BUILD="$ROOT_REPO/src/builds/build_foss2020b"
INSTALL="$ROOT_REPO/src/osu_foss2020b"

if [ ! -d "$EXTRACTED_TAR" ]; then
    printf "Directory '%s' does not exist. Extracting '%s'...\n" "$EXTRACTED_TAR" "$TAR_FILE"
    mkdir -p "$EXTRACTED_TAR" && tar -xzf "$TAR_FILE" -C "$SRC_DIR" || {
        printf "Failed to extract '%s'\n" "$TAR_FILE" >&2
        exit 1
    }
else
    printf "Directory '%s' already exists. Skipping extraction.\n" "$EXTRACTED_TAR"
fi

# Load the module
module purge
module load toolchain/foss/2020b

# Create the directory for building
mkdir -p "$BUILD"
mkdir -p "$INSTALL"

# Change directory to the build directory
cd "$BUILD" || { printf "Failed to change directory to %s\n" "$BUILD" >&2; exit 1; }

# Configure the benchmarks
if ! "$ROOT_REPO/src/osu-micro-benchmarks-7.4/configure" CC=mpicc CXX=mpicxx --prefix="$INSTALL"; then
    printf "Configuration failed.\n" >&2
    exit 1
fi

# Compile the benchmarks
if ! make; then
    printf "Make failed.\n" >&2
    exit 1
fi

# Install the benchmarks
if ! make install; then
    printf "Make install failed.\n" >&2
    exit 1
fi

# Move executables
mv "$INSTALL/libexec/osu-micro-benchmarks/mpi/"* "$INSTALL"
rm -r "$INSTALL/libexec"

# startup tests
INIT="$INSTALL/startup/osu_init"
HELLO="$INSTALL/startup/osu_hello"

# pt2pt tests
LATENCY="$INSTALL/pt2pt/osu_latency"
BW="$INSTALL/pt2pt/osu_bw"

# one-sided tests
PUT_LATENCY="$INSTALL/one-sided/osu_put_latency"
GET_LATENCY="$INSTALL/one-sided/osu_get_latency"

# Create a JSON configuration file
cat <<EOF > $ROOT_REPO/tests/paths.json
{
    "init": "$INIT",
    "hello": "$HELLO",
    "latency": "$LATENCY",
    "bw": "$BW",
    "put_latency": "$PUT_LATENCY",
    "get_latency": "$GET_LATENCY"
}
EOF

echo "Paths file created successfully."