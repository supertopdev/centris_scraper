import argparse
import os
import json

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--read-directory", help="read products json directory")
    parser.add_argument("-c", "--compare-directory", help="compare products json directory")
    parser.add_argument("-o", "--output-directory", help="output directory")
    args = parser.parse_args()

    if os.path.isdir(args.read_directory) and os.path.isdir(args.compare_directory):
        if not os.path.isdir(args.output_directory):
            os.mkdir(args.output_directory)
        for p, d, f in os.walk(args.read_directory):
            for d1 in d:
                for child_p, sub_d, child_f in os.walk(os.path.join(p, d1)):
                    for file in child_f:
                        if '.json' not in file:
                            continue

                        compare_file = os.path.join(args.compare_directory, 'results_{}'.format(d1),
                                                    'result_{}'.format(file))

                        if not os.path.isfile(compare_file):
                            continue

                        read_file = os.path.join(child_p, file)

                        output_file = os.path.join(args.output_directory, file)

                        with open(compare_file, 'r') as fp:
                            try:
                                res = json.load(fp)
                            except:
                                os.rename(read_file, output_file)
                                fp.close()

                                continue
                            fp.close()
                        with open(compare_file, 'w', encoding='utf8') as fp:
                            fp.write(json.dumps(res, ensure_ascii=False, indent=4))
                            fp.close()

                        res = [
                            i.get('url')
                            for i in res
                        ]

                        with open(read_file, 'r') as fp:
                            prods = json.load(fp)
                            fp.close()
                            prods = [
                                i.get('url')
                                for i in prods
                            ]


                        exception_links = [
                            {'url': i}
                            for i in prods
                            if i not in res
                        ]

                        if not exception_links:
                            continue

                        with open(output_file, 'w') as fp:
                            json.dump(exception_links, fp)
                            fp.close()
    else:
        print('Can not read directory: {}'.format(args.read_directory))