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
module purge
module use /work/projects/mhpc-softenv/easybuild/aion-epyc-prod-2023a/modules/all/
module load devel/ReFrame
```

The first of them makes sure that the 2023 toolchain is available, as by default
only the 2020 one is available to Lmod. 

The second command loads the ReFrame module.

3. Run the specific benchmark tests using ReFrame with the `aion_config.py` configuration file:

* run the OSU Benchmark tests (only sanity checks):
```bash
reframe -C configs/aion_config.py -c tests/osu_benchmarks --run --skip-performance-check
```

* run the OSU Benchmark tests (only performance checks):
```bash
reframe -C configs/aion_config.py -c tests/osu_benchmarks --run --skip-sanity-check
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

We now turn on to discuss the results we obtained for the performance tests. The data for all tables below has been obtained by performing ten independent runs of a subset of the performance tests. In all of these graphs we can spot a growing trend of variance. In fact, we can see that variance escales exponentially. This is somewhat expected, as the scale of the plots also scale exponentially.

First, we will consider thae latency and bandwidth for transfering messages of a varying size from a single source to a single receiver. These results can be consulted in the first two tables below. In both cases, the X axis indicates the message size, and Y axeses represent latency and bandwidth. Each image shows one plot for each combination of compilation toolchain (2020 vs 2023) and number of nodes (1 vs 2).

Both graphs reflect the same situation. The latency graph indicates that latency keeps constantly low up to message sizes around 10K characters. After that point, it increases exponentially. As for the bandwidth, it increases exponentially for message sizes between 0 and 10K characters, and stalls after that point. Thus, at 10K our network becomes saturated with information, and messages have to wait for being able to enter inter- or intra-node communication chanels, creating longer and longer stalls.

We also note some differences between the 1 node and 2 node versions. The 2 node versions feature a constantly higher latency and constantly lower bandwidth. This is due to the fact that inter-node communication is more costly than the intra-node one. The 2020 toolchain seems to better employ the single-node environment, whereas the 2023 toolchain performs better in the multi-node one.
<p float="left">
   <img src="https://github.com/Miglia12/Testing_MPI_Toolchains/blob/main/plots/put_latency.png?raw=true"   width=300>
   <img src="https://github.com/Miglia12/Testing_MPI_Toolchains/blob/main/plots/put_bandwidth.png?raw=true" width=300>
</p>

We now turn on to consider performance in all-to-all tests which involve sending messages to all other nodes in the network. The graph on the left displays blocking and non-blocking message passing for the 2020 toolchain, whereas the graph on the right does so across toolchains for blocking implementations. We may see that the situation is similar as before, all times remaining constant up to some point, and then increasing almost exponentially. However, the blocking implementations do seem to start to get worse earlier than the non-blocking ones, perhaps because of the added number of messages needed to perform the blocking operations.
<p float="left">
   <img src="https://github.com/Miglia12/Testing_MPI_Toolchains/blob/main/plots/alltoall_blocking_non_blocking.jpg?raw=true" width=300>
   <img src="https://github.com/Miglia12/Testing_MPI_Toolchains/blob/main/plots/alltoall_toolchains.png?raw=true"            width=300>
</p>
