import sys
import csv
from datetime import datetime

for line in sys.stdin:

    line = line.strip()
    columns = list(csv.reader([line]))[0]
    
    if len(columns) < 2:
        continue
    
    date = columns[0]
    currency = columns[1]
    exchange_rate = columns[4]

    if currency == "Canadian-Dollar Effective Exchange Rate Index (CERI)":
        try:
            year = datetime.strptime(date, "%Y-%m-%d").strftime("%Y")
            exchange_rate = float(exchange_rate)
            print("{}\t{}".format(year, exchange_rate))
        except ValueError:
            continue
