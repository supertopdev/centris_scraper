def benchmark_run(target, parallel_jobs, output_path):

    crawler = getattr(__import__('benchmark.{}'.format(target)), target)
    if not crawler or not parallel_jobs:
        print("Cannot find crawler for {}".format(target))

    try:
        parallel_jobs = int(parallel_jobs)
    except (ValueError, TypeError):
        parallel_jobs = 1

    crawler.benchmark(parallel_jobs, output_path)
