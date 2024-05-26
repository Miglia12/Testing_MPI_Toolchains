# Testing_MPI_Toolchains

The goal of this project is to validate the MPI toolchains installed on the
Uni.lu HPC platform. The ReFrame framework will be used to orchestrate sets of
regression and sanity tests. We will leverage two sets of tests: the OSU
benchmarking suite [[link]](http://mvapich.cse.ohio-state.edu/benchmarks/), and
Supermagic [[link]](https://github.com/hpc/supermagic).

## Running instructions

These tests have been tailored for UniLu's Aion cluster. All necessary
configuration has already been specified in the repository files. In order to
run the tests, please login into Aion and request access to any interactive node
with the `si` command. Then, execute the following three commands from the
repository's root directory:

```bash
module use /work/projects/mhpc-softenv/easybuild/aion-epyc-prod-2023a/modules/all/
module load devel/ReFrame
reframe -C configs/aion_config.py -c tests --run
```

The first of them makes sure that the 2023 toolchain is available, as by default
only the 2020 one is available to Lmod. The second command loads the ReFrame
module. The third command instructs ReFrame to run all tests under the `tests`
folder respecting the configuration specified in `configs/aion_config.py`.
