import csv

#Adding a category ID to each product, because each product belongs to one category
input_file = '/home/ubuntu/quokkazon/db/data/working_cat.csv'
output_file = '/home/ubuntu/quokkazon/db/data/finished_cat.csv'

with open(input_file, 'r') as file:
    reader = csv.reader(file)
    data = list(reader)

category_to_number = {
    'Grooming': 1,
    'Kitchenware': 2,
    'Art': 3,
    'Entertainment': 4,
    'Food': 5,
    'Tool': 6,
    'Clothing': 7,
    'Books': 8,
    'Technology': 9,
    'Home Appliances': 10,
    'Kitchen Appliances': 11,
    'Home and Bedding': 12,
    'Home Decor': 13,
    'Sports & Outdoor Recreation': 14,
    'Home and Garden': 15,
    'Office Supplies': 16,
    'Music': 17,
    'Science': 18,
    'Stationery': 19,
    'Accessories': 20,
    'Education': 21,
    'Footwear': 22
}
for row in data:
    category = row[1]
    if category in category_to_number:
        row[0] = category_to_number[category]
    else:
        print("wrong", category)

with open(output_file, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(data)