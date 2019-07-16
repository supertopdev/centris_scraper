import csv
import json
class loader(object):
    def parse(self):
        csv_file = open('input.csv', newline='')
        readers = csv.DictReader(csv_file)
        values = []
        for idx, reader in enumerate(list(readers)):
            reader['series_id'] = idx + 1
            values.append(reader)
        with open('result.json', 'w', encoding='utf8') as f:
            json.dump(values, f, indent=4)

def main(event, context):
    lo = loader()
    lo.parse()
if __name__ == "__main__":
    main(0, 0)