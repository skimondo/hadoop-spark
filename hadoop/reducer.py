import sys

current_year = None
exchange_rates = []

for line in sys.stdin:
    line = line.strip()
    year, rate = line.split("\t")
    rate = float(rate)
    
    if current_year == year:
        exchange_rates.append(rate)
    else:
        if current_year:
            mean = sum(exchange_rates) / len(exchange_rates)
            print("{}\t{:.4f}".format(current_year, mean))
        
        current_year = year
        exchange_rates = [rate]

if current_year:
    mean = sum(exchange_rates) / len(exchange_rates)
    print("{}\t{:.4f}".format(current_year, mean))
