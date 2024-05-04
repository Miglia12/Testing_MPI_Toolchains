#define BENCHMARK "OSU MPI Multi Latency Test"
/*
 * Copyright (c) 2002-2024 the Network-Based Computing Laboratory
 * (NBCL), The Ohio State University.
 *
 * Contact: Dr. D. K. Panda (panda@cse.ohio-state.edu)
 *
 * For detailed copyright and licensing information, please refer to the
 * copyright file COPYRIGHT in the top level OMB directory.
 */

#include <osu_util_mpi.h>

char *s_buf, *r_buf;

static int multi_latency(int rank, int pairs);

double calculate_total(double, double, double);

int errors_reduced = 0;
MPI_Comm omb_comm = MPI_COMM_NULL;
omb_mpi_init_data omb_init_h;

int main(int argc, char *argv[])
{
    int rank, nprocs;
    int message_size;
    int pairs;
    int po_ret = 0;
    options.bench = PT2PT;
    options.subtype = LAT;

    set_header(HEADER);
    set_benchmark_name("osu_multi_lat");

    po_ret = process_options(argc, argv);

    if (PO_OKAY == po_ret && NONE != options.accel) {
        if (init_accel()) {
            fprintf(stderr, "Error initializing device\n");
            exit(EXIT_FAILURE);
        }
    }
    omb_init_h = omb_mpi_init(&argc, &argv);
    omb_comm = omb_init_h.omb_comm;
    if (MPI_COMM_NULL == omb_comm) {
        OMB_ERROR_EXIT("Cant create communicator");
    }
    MPI_CHECK(MPI_Comm_rank(omb_comm, &rank));
    MPI_CHECK(MPI_Comm_size(omb_comm, &nprocs));

    pairs = nprocs / 2;

    if (0 == rank) {
        switch (po_ret) {
            case PO_CUDA_NOT_AVAIL:
                fprintf(stderr, "CUDA support not enabled.  Please recompile "
                                "benchmark with CUDA support.\n");
                break;
            case PO_OPENACC_NOT_AVAIL:
                fprintf(stderr, "OPENACC support not enabled.  Please "
                                "recompile benchmark with OPENACC support.\n");
                break;
            case PO_BAD_USAGE:
                print_bad_usage_message(rank);
                break;
            case PO_HELP_MESSAGE:
                print_help_message(rank);
                break;
            case PO_VERSION_MESSAGE:
                print_version_message(rank);
                omb_mpi_finalize(omb_init_h);
                exit(EXIT_SUCCESS);
                break;
            case PO_OKAY:
                break;
        }
    }

    switch (po_ret) {
        case PO_CUDA_NOT_AVAIL:
        case PO_OPENACC_NOT_AVAIL:
        case PO_BAD_USAGE:
            omb_mpi_finalize(omb_init_h);
            exit(EXIT_FAILURE);
        case PO_HELP_MESSAGE:
        case PO_VERSION_MESSAGE:
            omb_mpi_finalize(omb_init_h);
            exit(EXIT_SUCCESS);
        case PO_OKAY:
            break;
    }

    print_preamble(rank);

    MPI_CHECK(MPI_Barrier(omb_comm));

    message_size = multi_latency(rank, pairs);

    MPI_CHECK(MPI_Barrier(omb_comm));

    omb_mpi_finalize(omb_init_h);

    if (NONE != options.accel) {
        if (cleanup_accel()) {
            fprintf(stderr, "Error cleaning up device\n");
            exit(EXIT_FAILURE);
        }
    }

    if (0 != errors_reduced && options.validate && 0 == rank) {
        fprintf(stdout,
                "DATA VALIDATION ERROR: %s exited with status %d on"
                " message size %d.\n",
                argv[0], EXIT_FAILURE, message_size);
        exit(EXIT_FAILURE);
    }
    return EXIT_SUCCESS;
}

static int multi_latency(int rank, int pairs)
{
    int size, partner;
    int i, j;
    double t_start = 0.0, t_end = 0.0, t_total = 0.0;

    /*needed for the kernel loss calculations*/
    double t_lo = 0.0;
    size_t num_elements = 0;
    MPI_Datatype omb_curr_datatype = MPI_CHAR;
    size_t omb_ddt_transmit_size = 0;
    int mpi_type_itr = 0, mpi_type_size = 0, mpi_type_name_length = 0;
    char mpi_type_name_str[OMB_DATATYPE_STR_MAX_LEN];
    MPI_Datatype mpi_type_list[OMB_NUM_DATATYPES];
    omb_graph_options_t omb_graph_options;
    omb_graph_data_t *omb_graph_data = NULL;
    int papi_eventset = OMB_PAPI_NULL;
    MPI_Status reqstat;
    struct omb_buffer_sizes_t omb_buffer_sizes;
    MPI_Comm barrier_comm;
    double t_total_reduce = 0.0;

    omb_populate_mpi_type_list(mpi_type_list);
    omb_graph_options_init(&omb_graph_options);
    omb_papi_init(&papi_eventset);
    for (mpi_type_itr = 0; mpi_type_itr < options.omb_dtype_itr;
         mpi_type_itr++) {
        MPI_CHECK(MPI_Type_size(mpi_type_list[mpi_type_itr], &mpi_type_size));
        MPI_CHECK(MPI_Type_get_name(mpi_type_list[mpi_type_itr],
                                    mpi_type_name_str, &mpi_type_name_length));
        omb_curr_datatype = mpi_type_list[mpi_type_itr];
        if (0 == rank) {
            fprintf(stdout, "# Datatype: %s.\n", mpi_type_name_str);
        }
        fflush(stdout);
        print_only_header(rank);
        for (size = options.min_message_size; size <= options.max_message_size;
             size = (size ? size * 2 : 1)) {
            num_elements = size / mpi_type_size;
            if (0 == num_elements) {
                continue;
            }
            if (allocate_memory_pt2pt_mul_size(&s_buf, &r_buf, rank, pairs,
                                               size)) {
                /* Error allocating memory */
                omb_mpi_finalize(omb_init_h);
                exit(EXIT_FAILURE);
            }

            omb_ddt_transmit_size =
                omb_ddt_assign(&omb_curr_datatype, mpi_type_list[mpi_type_itr],
                               num_elements) *
                mpi_type_size;
            num_elements = omb_ddt_get_size(num_elements);
            set_buffer_pt2pt(s_buf, rank, options.accel, 'a', size);
            set_buffer_pt2pt(r_buf, rank, options.accel, 'b', size);

            if (size > LARGE_MESSAGE_SIZE) {
                options.iterations = options.iterations_large;
                options.skip = options.skip_large;
            } else {
                options.iterations = options.iterations;
                options.skip = options.skip;
            }

#ifdef _ENABLE_CUDA_KERNEL_
            if ((options.src == 'M' && options.MMsrc == 'D') ||
                (options.dst == 'M' && options.MMdst == 'D')) {
                t_lo = measure_kernel_lo_no_window(s_buf, size);
            }
#endif /* #ifdef _ENABLE_CUDA_KERNEL_ */

            omb_graph_allocate_and_get_data_buffer(
                &omb_graph_data, &omb_graph_options, size, options.iterations);
            MPI_CHECK(MPI_Barrier(omb_comm));
            MPI_CHECK(MPI_Comm_split(omb_comm, rank < pairs, 0, &barrier_comm));
            t_total = 0.0;

            for (i = 0; i < options.iterations + options.skip; i++) {
                if (i == options.skip) {
                    omb_papi_start(&papi_eventset);
                }
                if (options.validate) {
                    set_buffer_validation(s_buf, r_buf, size, options.accel, i,
                                          omb_curr_datatype, omb_buffer_sizes);
                }
                for (j = 0; j <= options.warmup_validation; j++) {
                    MPI_CHECK(MPI_Barrier(omb_comm));
                    if (rank < pairs) {
                        partner = rank + pairs;
                        if (i >= options.skip &&
                            j == options.warmup_validation) {
                            t_start = MPI_Wtime();
                        }

#ifdef _ENABLE_CUDA_KERNEL_
                        if (options.src == 'M') {
                            touch_managed_src_no_window(s_buf, size, ADD);
                        }
#endif /* #ifdef _ENABLE_CUDA_KERNEL_ */

                        MPI_CHECK(MPI_Send(s_buf, num_elements,
                                           omb_curr_datatype, partner, 1,
                                           omb_comm));
                        MPI_CHECK(MPI_Recv(r_buf, num_elements,
                                           omb_curr_datatype, partner, 1,
                                           omb_comm, &reqstat));
#ifdef _ENABLE_CUDA_KERNEL_
                        if (options.src == 'M') {
                            touch_managed_src_no_window(r_buf, size, SUB);
                        }
#endif /* #ifdef _ENABLE_CUDA_KERNEL_ */

                        if (i >= options.skip &&
                            j == options.warmup_validation) {
                            t_end = MPI_Wtime();
                            t_total += calculate_total(t_start, t_end, t_lo);
                            if (options.graph) {
                                omb_graph_data->data[i - options.skip] =
                                    calculate_total(t_start, t_end, t_lo) *
                                    1e6 / 2.0;
                            }
                        }
#ifdef _ENABLE_CUDA_KERNEL_
                        if (options.validate &&
                            !(options.src == 'M' && options.MMsrc == 'D' &&
                              options.dst == 'M' && options.MMdst == 'D')) {
                            if (options.src == 'M' && options.MMsrc == 'D') {
                                touch_managed(r_buf, size, ADD);
                                synchronize_stream();
                            } else if (options.dst == 'M' &&
                                       options.MMdst == 'D') {
                                touch_managed(r_buf, size, SUB);
                                synchronize_stream();
                            }
                        }
                        if (options.src == 'M' && options.MMsrc == 'D' &&
                            options.validate) {
                            touch_managed_src_no_window(s_buf, size, SUB);
                        }
#endif /* #ifdef _ENABLE_CUDA_KERNEL_ */
                    } else {
                        partner = rank - pairs;

#ifdef _ENABLE_CUDA_KERNEL_
                        if (options.dst == 'M') {
                            touch_managed_dst_no_window(s_buf, size, ADD);
                        }
#endif /* #ifdef _ENABLE_CUDA_KERNEL_ */

                        MPI_CHECK(MPI_Recv(r_buf, num_elements,
                                           omb_curr_datatype, partner, 1,
                                           omb_comm, &reqstat));
#ifdef _ENABLE_CUDA_KERNEL_
                        if (options.dst == 'M') {
                            touch_managed_dst_no_window(r_buf, size, SUB);
                        }
#endif /* #ifdef _ENABLE_CUDA_KERNEL_ */

                        MPI_CHECK(MPI_Send(s_buf, num_elements,
                                           omb_curr_datatype, partner, 1,
                                           omb_comm));
#ifdef _ENABLE_CUDA_KERNEL_
                        if (options.validate &&
                            !(options.src == 'M' && options.MMsrc == 'D' &&
                              options.dst == 'M' && options.MMdst == 'D')) {
                            if (options.src == 'M' && options.MMsrc == 'D') {
                                touch_managed(r_buf, size, SUB);
                                synchronize_stream();
                            } else if (options.dst == 'M' &&
                                       options.MMdst == 'D') {
                                touch_managed(r_buf, size, ADD);
                                synchronize_stream();
                            }
                        }
                        if (options.dst == 'M' && options.MMdst == 'D' &&
                            options.validate) {
                            touch_managed_dst_no_window(s_buf, size, SUB);
                        }
#endif /* #ifdef _ENABLE_CUDA_KERNEL_ */
                    }
                }
                if (options.validate) {
                    int error = 0, error_temp = 0;
                    error = validate_data(r_buf, size, 1, options.accel, i,
                                          omb_curr_datatype);
                    MPI_CHECK(MPI_Reduce(&error, &error_temp, 1, MPI_INT,
                                         MPI_SUM, 0, omb_comm));
                    errors_reduced += error_temp;
                }
            }
            omb_papi_stop_and_print(&papi_eventset, size);

            MPI_CHECK(MPI_Reduce(&t_total, &t_total_reduce, 1, MPI_DOUBLE,
                                 MPI_SUM, 0, barrier_comm));
            t_total = t_total_reduce / pairs;
            if (0 == rank) {
                double latency = (t_total * 1e6) / (2.0 * options.iterations);
                fprintf(stdout, "%-*d", 10, size);
                if (options.validate) {
                    fprintf(stdout, "%*.*f%*s", FIELD_WIDTH, FLOAT_PRECISION,
                            latency, FIELD_WIDTH,
                            VALIDATION_STATUS(errors_reduced));
                } else {
                    fprintf(stdout, "%*.*f", FIELD_WIDTH, FLOAT_PRECISION,
                            latency);
                }
                if (options.omb_enable_ddt) {
                    fprintf(stdout, "%*zu", FIELD_WIDTH, omb_ddt_transmit_size);
                }
                fprintf(stdout, "\n");
                fflush(stdout);
                if (options.graph && 0 == rank) {
                    omb_graph_data->avg = latency;
                }
            }

            omb_ddt_free(&omb_curr_datatype);
            free_memory_pt2pt_mul(s_buf, r_buf, rank, pairs);

            if (options.validate) {
                MPI_CHECK(MPI_Bcast(&errors_reduced, 1, MPI_INT, 0, omb_comm));
                if (0 != errors_reduced) {
                    break;
                }
            }
        }
    }
    if (options.graph) {
        omb_graph_plot(&omb_graph_options, benchmark_name);
    }
    omb_graph_combined_plot(&omb_graph_options, benchmark_name);
    omb_graph_free_data_buffers(&omb_graph_options);
    omb_papi_free(&papi_eventset);
    return size;
}

double calculate_total(double t_start, double t_end, double t_lo)
{
    double t_total;
    if ((options.src == 'M' && options.MMsrc == 'D') &&
        (options.dst == 'M' && options.MMdst == 'D')) {
        t_total = (t_end - t_start) - (2 * t_lo);
    } else if (((options.src == 'M' && options.MMsrc == 'H') &&
                (options.dst == 'M' && options.MMdst == 'D')) ||
               ((options.src == 'M' && options.MMsrc == 'D') &&
                (options.dst == 'M' && options.MMdst == 'H'))) {
        t_total = (t_end - t_start) - t_lo;
    } else if ((options.src == 'M' && options.MMsrc == 'D') ||
               (options.dst == 'M' && options.MMdst == 'D')) {
        t_total = (t_end - t_start) - t_lo;
    } else {
        t_total = (t_end - t_start);
    }

    return t_total;
}
/* vi: set sw=4 sts=4 tw=80: */
