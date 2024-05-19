site_configuration = {
    'systems': [
        {
            'name': 'aion',
            'descr': 'Aion cluster',
            'hostnames': [r'aion-[0-9]{4}'],
            'modules_system': 'lmod',
            'partitions': [
                {
                    'name': 'batch',
                    'descr': 'Aion compute nodes',
                    'scheduler': 'slurm',
                    'launcher': 'srun',
                    'access': ['--partition=batch', '--qos=normal'],
                    'max_jobs':  8,
                    'environs': ['foss2020b'],
                }
            ]
        }
    ],
    'environments': [
        {
            'name': 'foss2020b',
            'cc': 'mpicc',
            'cxx': 'mpicxx',
            'ftn': 'mpifort',
            'modules': ['toolchain/foss/2020b'],
            'target_systems': ['aion']
        },
    ]
}

