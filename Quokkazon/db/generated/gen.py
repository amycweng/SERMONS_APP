from werkzeug.security import generate_password_hash
import csv,random,re
from faker import Faker
from collections import defaultdict
from datetime import datetime

num_users = 100
num_products = 200
num_purchases = 1000

Faker.seed(0)
fake = Faker()


def get_csv_writer(f):
    return csv.writer(f, dialect='unix', quoting=csv.QUOTE_NONE, escapechar='\\')

def gen_users(num_users):
    with open('Users.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Users...', end=' ', flush=True)
        for uid in range(num_users):
            if uid % 10 == 0:
                print(f'{uid}', end=' ', flush=True)
            profile = fake.profile()
            email = profile['mail']
            plain_password = f'pass{uid}'
            #password = generate_password_hash(plain_password)
            password = generate_password_hash("1234")
            name_components = profile['name'].split(' ')
            firstname = name_components[0]
            lastname = name_components[-1]
            address = profile['address'].replace("\n"," ")
            phone_number=random.randint(1000000000, 9999999999)
            # print([uid,email,firstname,lastname,address,password,phone_number,0])
            writer.writerow([int(uid),email,firstname,lastname,address,password,phone_number,0])
        print(f'{num_users} generated')
    return

def fix_products_csv(file): 
    with open(file,"r") as f: 
        writer = get_csv_writer(open("Products.csv","w"))
        for line in f.readlines(): 
            info = line.split(",")
            # 1,Quokka Fur Brush,grooming,,A comb or something,12:58.0,12:58.0
            default_time = fake.date_time_between(start_date='-5y', end_date='now')
            writer.writerow([info[0],info[1],info[2],info[3],info[4],default_time,default_time])

def get_available_products():
    available = defaultdict(dict)
    with open("Inventory.csv","r") as f: 
        info = f.readlines()
        for line in info: 
            # (sid, pid,quantity,num_for_sale,price)
            line = line.split(',')
            sid,pid,num_for_sale = line[0].replace("\"",''),line[1].replace("\"",''),line[3].replace("\"",'')
            available[pid][sid] = int(num_for_sale)
    return available 

# Generate purchase entries with a user id, seller id, product id, order id, time purchased, quantity, and date fulfilled 
def gen_purchases(num_purchases, available):
    # Set initiial purchase values for first entry
    order_id = 0
    count = 0 
    uid  = 0
    time_purchased = fake.date_time_between(start_date='-5y', end_date='now')
    order_pids = []     # keep track of products already contained by the current order
    with open('Purchases.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Purchases...', end=' ', flush=True)
        for id in range(num_purchases):
            if len(available) == 0: 
                # if no more inventory left, stop generating
                break
            if id % 100 == 0:   # track progress in console
                print(f'{id}', end=' ', flush=True)            
            # Start with random product and seller id for each new entry
            pid = fake.random_element(elements=list(available.keys()))
            sid = random.choice(list(available[pid].keys()))
            quantity_available = available[pid][sid]
            # If there is more of the random product available, decide randomly whether to start a new order for a new user and time of purchase or not
            if fake.random.random() < 0.6 and quantity_available > 0:
                order_id += 1
                uid = fake.random_int(min=0, max=num_users-1)
                time_purchased = fake.date_time_between(start_date='-5y', end_date='now')
                order_pids = []
            else:
                counter = 0
                while (pid in order_pids or quantity_available <= 0) and counter < 5:   # Make sure the newly selected product is not already present within the order
                    pid = fake.random_element(elements=list(available.keys()))
                    sid = random.choice(list(available[pid].keys()))
                    quantity_available = available[pid][sid]
                    counter += 1
                if counter >= 5:    # if we have failed multiple times to find a valid next product, we just stop generation here
                    break
            quantity = fake.random_int(min=1,max=min(20,quantity_available + 1))
            # ensure that items cannot be re-purchased 
            available[pid][sid] -= quantity
            if available[pid][sid] == 0: 
                del available[pid][sid] 
            if len(available[pid]) == 0: 
                del available[pid]
            price = random.randint(0,30) + 0.99
            
            date_fulfilled = fake.date_time_between(start_date=time_purchased, end_date='now')
            if time_purchased.year == datetime.today().year and fake.random.random() < 0.5:     # Randomly select some orders made this year as unfulfilled orders
                date_fulfilled = None
            writer.writerow([uid, sid, pid, order_id, time_purchased,quantity,price,date_fulfilled])
            count += 1 
            order_pids.append(pid)
        print(f'{count} generated')
    return

def gen_sellers(num_users):
    with open('Sellers.csv','w') as f:
        writer = get_csv_writer(f)
        print('Sellers...', end=' ', flush=True)
        random.seed('quokka')
        num_sellers = 0
        for id in range(num_users):
            if random.random() < 0.2:
                writer.writerow([id])
                num_sellers += 1
        print(f'{num_sellers} users designated as sellers')
    return

def get_sellers(file):
    with open(file,'r') as f:
        return [int(sid.replace('"','').strip()) for sid in f.readlines()]

def get_pids(file):
    with open(file,'r') as f:
        return [int(line.split(',')[0]) for line in f.readlines()]

# Generate inventory table values using the established Sellers and Products
def gen_inventory():
    with open('Inventory.csv','w') as f:
        writer = get_csv_writer(f)
        print('Inventory...', end=' ', flush=True)
        random.seed('quokka')
        rows_added = 0
        for sid in get_sellers('/home/ubuntu/quokkazon/db/data/Sellers.csv'):
            num_items = random.randint(1,10)
            products = random.sample(get_pids('/home/ubuntu/quokkazon/db/data/Products.csv'),num_items)
            for pid in products:
                quantity = random.randint(0,1000)
                num_for_sale = random.randint(0,quantity)
                price = random.randint(0,30) + 0.99
                writer.writerow([sid, pid, quantity, num_for_sale, price])
                rows_added += 1
        print(f'{rows_added} entries added to Inventory')
    return

def get_available_sellers(file):
    available = []
    with open(file,"r") as f: 
        info = f.readlines()
        for line in info: 
            sid = line.replace("\"","").strip()
            available.append(sid)
    return available

def gen_cart(num_users):
    with open('Cart.csv','w') as f:
        writer = get_csv_writer(f)
        print('Cart...', end=' ', flush=True)
        random.seed('quokka')
        available_sellers = get_available_sellers("/home/ubuntu/quokkazon/db/generated/Sellers.csv")
        for id in range(int(num_users)):
            uid = fake.random_int(min=0, max=num_users-1)
            sid = fake.random_element(elements=available_sellers)
            while(sid == uid):
                sid = fake.random_element(elements=available_sellers)
            pid = fake.random_int(min=1, max=253)
            quantity = fake.random_int(min = 1, max = 10)
            saved_for_later = 0
            writer.writerow([uid, sid, pid, quantity, saved_for_later])
            print(f'{num_users/2} generated')
        return


def gen_cart(num_users):
    with open('Cart.csv','w') as f:
        writer = get_csv_writer(f)
        print('Cart...', end=' ', flush=True)
        random.seed('quokka')
        available_sellers = get_available_sellers("/home/ubuntu/quokkazon/db/generated/Sellers.csv")
        for id in range(int(num_users)):
            uid = fake.random_int(min=0, max=num_users-1)
            sid = fake.random_element(elements=available_sellers)
            while(sid == uid):
                sid = fake.random_element(elements=available_sellers)
            pid = fake.random_int(min=1, max=253)
            quantity = fake.random_int(min = 1, max = 10)
            saved_for_later = 0
            writer.writerow([uid, sid, pid, quantity, saved_for_later])
            print(f'{num_users/2} generated')
        return

if __name__ == "__main__": 
    #gen_inventory()
    #gen_users(num_users)
    available = get_available_products()
    gen_purchases(num_purchases, available)
    fix_products_csv("/home/ubuntu/quokkazon/db/data/Products.csv")
