#!/bin/bash

# Determine the root of the repo
if ! root_repo=$(git rev-parse --show-toplevel); then
    printf "Failed to find the git repository root.\n" >&2
    exit 1
fi

# Load the module
module purge
module use /work/projects/mhpc-softenv/easybuild/aion-epyc-prod-2023a/modules/all/
module load toolchain/foss/2023a

# Create the directory for building
BUILD="$root_repo/src/builds/build_foss2023a"
INSTALL="$root_repo/src/osu_foss2023a"
mkdir -p "$BUILD"
mkdir -p "$INSTALL"

# Change directory to the build directory
cd "$BUILD" || { printf "Failed to change directory to %s\n" "$BUILD" >&2; exit 1; }

# Configure the benchmarks
if ! "$root_repo/src/osu-micro-benchmarks-7.4/configure" CC=mpicc CXX=mpicxx --prefix="$INSTALL"; then
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

# Save the paths for Reframe
PUT_LATENCY="$INSTALL/one-sided/osu_put_latency"
GET_LATENCY="$INSTALL/one-sided/osu_get_latency"

# Create a JSON configuration file
cat <<EOF > $root_repo/tests/paths.json
{
    "put_latency": "$PUT_LATENCY",
    "get_latency": "$GET_LATENCY"
}
EOF

echo "Paths file created successfully."