import csv

DELIMITER = ','


def csv_to_dict(csv_path, delimiter=DELIMITER, skip_line=0):
    with open(csv_path, 'r') as csv_fd:
        for _ in range(skip_line):
            csv_fd.readline()
        yield from csv.DictReader(csv_fd, delimiter=delimiter)
