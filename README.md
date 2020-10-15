# csv_appender

A command line tool that appends data from one .csv file to another .csv while skipping items
that already exist. This makes the script idempotent.

General syntax:

    csv_appender <src.csv> <trg.csv> [col_idx1, col_idx2, ...]

Example:

    csv_appender daily.csv master.csv 1 2 5
    
This example means that the rows from daily.csv will be appended to msater.csv. If the daily
row already exists in master.csv, it will not be appended. Only the columns listed (ex: 1 2 5)
are used to check if a row already exists. The column indexes are 1-based column indexes into
the source csv file.