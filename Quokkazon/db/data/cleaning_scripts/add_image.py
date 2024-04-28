import os, random, csv

#Code to add random quokka images to each of the product entries in the products.csv
image_folder = '/home/ubuntu/quokkazon/app/static/product_images'
image_files = [f for f in os.listdir(image_folder) if os.path.isfile(os.path.join(image_folder, f))]

input_file = '/home/ubuntu/quokkazon/db/data/Products1.csv'
output_file = '/home/ubuntu/quokkazon/db/data/Products.csv'

new_rows = []

with open(input_file, 'r') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        random_image = "product_images/" + random.choice(image_files)
        row[3] = random_image
        new_rows.append(row)
        
with open(output_file, 'w', newline='') as output_csv:
    writer = csv.writer(output_csv)
    writer.writerows(new_rows)
