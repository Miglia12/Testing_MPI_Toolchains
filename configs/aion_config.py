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
                    'environs': ['gnu', 'builtin'],
                }
            ]
        }
    ],
    'environments': [
        {
            'name': 'gnu',
            'modules': ['toolchain/foss/2020b'],
            'cc': 'gcc',
            'cxx': 'g++',
            'ftn': 'gfortran',
            'target_systems': ['aion']
        },
        {
            'name': 'builtin',
            'cc': 'gcc',
            'cxx': 'g++',
            'ftn': 'gfortran',
            'target_systems': ['aion']
        },
    ]
}
