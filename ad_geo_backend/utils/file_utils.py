import csv

DELIMITER = ','


def csv_to_dict(csv_path, delimiter=DELIMITER, skip_line=0):
    with open(csv_path, 'r') as csv_fd:
        for _ in range(skip_line):
            csv_fd.readline()
        yield from csv.DictReader(csv_fd, delimiter=delimiter)


def txt_to_dict(txt_path, delimiter='\t'):
    with open(txt_path, 'r') as txt_fd:
        for line in txt_fd:
            splitted_line = line.strip().split(delimiter)
            yield splitted_line
