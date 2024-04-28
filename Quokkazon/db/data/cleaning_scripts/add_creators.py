import csv
import random

#Code to add creators with ids from the seller table to the products.csv
input_file = '/home/ubuntu/quokkazon/db/data/Products2.csv'
output_file = '/home/ubuntu/quokkazon/db/data/Products.csv'

sellers = ["2", "5", "6", "8", "9", "10", "12", "13", "14", "22", "31", "36", "39", "42", "50", "51", "52", "65", "81", "82", "96", "98"]
with open(input_file, 'r') as csv_file:
    reader = csv.reader(csv_file)
    rows = [row + [random.choice(sellers)] for row in reader]


with open(output_file, 'w', newline='') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerows(rows)