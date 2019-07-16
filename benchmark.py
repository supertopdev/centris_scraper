import argparse
from benchmark import benchmark_run

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--target-name", help="target spider name")
    parser.add_argument("-p", "--parallel-jobs", help="parallel jobs")
    parser.add_argument("-o", "--output-path", help="output path")
    args = parser.parse_args()

    benchmark_run(args.target_name, args.parallel_jobs, args.output_path)
