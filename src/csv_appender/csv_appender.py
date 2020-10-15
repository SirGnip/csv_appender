"""
handle empty or missing trg file:
- no keys in set
- write header row to new trg

- column indexes are one-based indexes identifying the columns in the src file
Look out for csv files with newline at the end...

- confirm that headers match? error if they don't
- what if src contains data w/ identical keys? should the script only append one row?
    Or, should it be naive and just append them all?
"""

import csv
from pathlib import Path
import datetime
from typing import Tuple, List, Set, Sequence
import click


CsvTableType = List[List]
KeySetType = Set[Tuple]
ColumnIdxsType = Tuple[int, ...]

@click.command()
@click.argument("src_filename")
@click.argument("trg_filename")
@click.argument("key_column_idxs", type=int, nargs=-1)
def appender(src_filename: str, trg_filename: str, key_column_idxs: ColumnIdxsType):
    print(src_filename, trg_filename, key_column_idxs)

    # read target csv and generate Set of keys to determine uniqueness
    trg_table = _read_csv(trg_filename)
    trg_data = trg_table[1:]
    print("Target file initial row count:", len(trg_data))
    trg_keys = _make_trg_keys(trg_data, key_column_idxs)

    # read source csv, loop over it, and write any rows that don't have a matching key to target
    src_table = _read_csv(src_filename)
    src_data = src_table[1:]
    print("Source file row count:", len(trg_data))

    # append rows from source csv that don't already have matching rows in the target csv
    appended = 0
    skipped = 0
    now = datetime.datetime.now()
    now_str = now.strftime('%d/%m/%Y %H:%M')
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
