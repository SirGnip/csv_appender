import csv
from pathlib import Path
import datetime
from typing import Tuple, List, Set, Sequence
import click


CsvTableType = List[List]
KeySetType = Set[Tuple]
ColumnIdxsType = Tuple[int, ...]

APPEND_TIMESTAMP_HEADER = "append_timestamp"

@click.command()
@click.argument("src_filename")
@click.argument("trg_filename")
@click.argument("key_column_idxs", type=int, nargs=-1)
def appender(src_filename: str, trg_filename: str, key_column_idxs: ColumnIdxsType):
    print(src_filename, trg_filename, key_column_idxs)

    # read source csv, loop over it, and write any rows that don't have a matching key to target
    src_table = _read_csv(src_filename)
    src_header = src_table[0]
    src_data = src_table[1:]
    print("Source file row count:", len(src_data))
    if max(key_column_idxs) > len(src_header):
        raise Exception(f"At least one key_column_idx ({key_column_idxs} is greater than the number of columns ({len(src_header)}) in the source file.")

    # read target csv and generate Set of keys to determine uniqueness
    trg_keys = set()
    try:
        trg_table = _read_csv(trg_filename)
        trg_header = trg_table[0]
        trg_data = trg_table[1:]
        print("Target file initial row count:", len(trg_data))
        trg_keys = _make_trg_keys(trg_data, key_column_idxs)
    except FileNotFoundError:
        trg_header = [APPEND_TIMESTAMP_HEADER] + src_header
        print(f"Target filename '{trg_filename}' not found. Creating empty file with headers: {trg_header}")
        with Path(trg_filename).open("a", newline="") as out:
            csv_writer = csv.writer(out, dialect="excel")
            csv_writer.writerow(trg_header)

    _check_headers(src_header, trg_header)

    # append rows from source csv that don't already have matching rows in the target csv
    appended = 0
    skipped = 0
    now = datetime.datetime.now()
    now_str = now.strftime('%d/%m/%Y %H:%M:%S')
    print("Timestamp for appended rows:", now_str)
    with Path(trg_filename).open("a", newline="") as out:
        csv_writer = csv.writer(out, dialect="excel")
        for row in src_data:
            src_key = _make_src_key(row, key_column_idxs)
            if src_key not in trg_keys:
                row.insert(0, now_str)
                print("Appending:", row)
                csv_writer.writerow(row)
                appended += 1
            else:
                print("Skip:", row)
                skipped += 1

    # ending summary
    print(f"Done. Rows appended:{appended} skipped:{skipped}")


def _check_headers(src_headers, trg_headers) -> bool:
    core_trg_headers = trg_headers[1:]  # strip off the "append_timestamp" header
    if tuple(src_headers) != tuple(core_trg_headers):
        raise Exception(f"Headers of source file ({src_headers} do not match headers of target file ({core_trg_headers})")


def _make_src_key(row: Sequence, key_column_idxs: ColumnIdxsType) -> Tuple:
    return tuple([row[idx-1] for idx in key_column_idxs])


def _make_trg_key(row: Sequence, key_column_idxs: ColumnIdxsType) -> Tuple:
    return tuple([row[idx] for idx in key_column_idxs])


def _make_trg_keys(table: CsvTableType, key_column_idxs: ColumnIdxsType) -> KeySetType:
    keys: KeySetType = set()
    for row in table:
        keys.add(_make_trg_key(row, key_column_idxs))
    return keys


def _read_csv(filename) -> CsvTableType:
    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile, dialect="excel")
        return list(reader)


if __name__ == '__main__':
    appender()  # pylint: disable=no-value-for-parameter
