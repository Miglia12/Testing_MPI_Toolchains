# Testing_MPI_Toolchains

The goal of this project is to validate the MPI toolchains installed on the Uni.lu HPC platform. The ReFrame framework will be used to orchestrate sets of regression and sanity tests. We will leverage two sets of tests: the  [OSU benchmarking suite](http://mvapich.cse.ohio-state.edu/benchmarks/), and [Supermagic](https://github.com/hpc/supermagic).

## Folder structure
```
Testing_MPI_Toolchains/
├── configs/                    
│   ├── aion_config.py      # ReFrame configuration file
│   ├── tests/              # Test-specific configuration files
├── tests/
│   ├── osu_benchmarks/     # OSU Benchmark tests
│   │   ├── base/           
│   │   ├── collective.py
│   │   ├── one_sided.py
│   │   ├── pt2pt.py
│   │   └── startup.py
│   └── supermagic/         # Supermagic tests
│       └── supermagic.py
└── README.md
```


## Running instructions

NOTE. Please, note that the performance reports can fail because of a high
variance inherent to their execution time. Sanity tests should not fail under
any circumstance. If you want an explanation to this high variance, please,
consult the plots at the end of this document.

These tests have been tailored for UniLu's Aion cluster. All necessary
configuration has already been specified in the repository files. 
To run the tests, execute the following commands from the repository's root directory:

1. Login to Aion and request access to an interactive node for one hour:
   ```bash
   si -t 01:00:00
   ```

2. Set up the environment:

```bash
module use /work/projects/mhpc-softenv/easybuild/aion-epyc-prod-2023a/modules/all/
module load devel/ReFrame
```

The first of them makes sure that the 2023 toolchain is available, as by default
only the 2020 one is available to Lmod. 

The second command loads the ReFrame module.

3. Run the specific benchmark tests using ReFrame with the `aion_config.py` configuration file:

* run the OSU Benchmark tests:
```bash
reframe -C configs/aion_config.py -c tests/osu_benchmarks --run
```

* run the Supermagic tests:
```bash
reframe -C configs/aion_config.py -c tests/supermagic --run
```

4. Now, please generate a report summarising the performance of the OSU tests:

```bash
reframe -C configs/aion_config.py -c tests/osu_benchmarks --run --performance-report
```

## Configuring tests

By default, the OSU tests run with both an intra-node and inter-node configuration. However, the number of tasks can be configured from the configuration files under `configs/tests`. If you change the number of tasks, you should also add a corresponding performance reference value with the format `{i}_tasks`.

For example:
```
{
   ...
   "num_tasks": 6,
   "reference": {
      ...
      "3_tasks": [23000, -0.05, None, 'MB/s'],
      "6_tasks": [<ref_val>, <lower threshold>, <upper threshold>, <unit>]
   }
}
```

## Results

Put latency measures the time it takes to transfer a message from the origin process to the target process's memory. This operation is akin to a "write" operation:

![pic](https://github.com/Miglia12/Testing_MPI_Toolchains/blob/main/plots/put_latency.png?raw=true) ![pic2](https://github.com/Miglia12/Testing_MPI_Toolchains/blob/main/plots/put_bandwidth.png?raw=true)

"All-to-All" benchmarks measure the performance of collective communication operations where every process sends data to and receives data from every other process:

![pic](https://github.com/Miglia12/Testing_MPI_Toolchains/blob/main/plots/alltoall_blocking_non_blocking.png?raw=true) ![pic2](https://github.com/Miglia12/Testing_MPI_Toolchains/blob/main/plots/alltoall_toolchains.png?raw=true)
