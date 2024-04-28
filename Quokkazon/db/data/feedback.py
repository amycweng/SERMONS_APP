import csv,random,os
from collections import defaultdict 
from datetime import datetime, timedelta
from faker import Faker
Faker.seed(0)
fake = Faker()

# read in the purchases data 
purchases = {}
with open("Purchases.csv",newline='') as file: 
    reader = csv.reader(file, delimiter=',')
    for row in reader: 
        uid,sid,pid = row[:3]
        date_fulfilled = row[7]
        if uid not in purchases: purchases[uid] = {}
        if sid not in purchases[uid]: purchases[uid][sid] = {}
        purchases[uid][sid][pid] = date_fulfilled 

# read in sample product reviews to incorporate into the generated product feedback 
sample_product_reviews = defaultdict(dict)
with open("Sample Reviews.csv",newline='') as file: 
    reader = csv.reader(file, delimiter=',')
    for row in reader: 
        pid,rating,review = row[0],row[1],row[3]
        sample_product_reviews[pid][int(rating)] = review

# read in sample image data 
image_folder = '/home/ubuntu/quokkazon/app/static/product_images'
image_files = [f for f in os.listdir(image_folder) if os.path.isfile(os.path.join(image_folder, f))]

# generate the seller and product feedback CSVs 
def get_csv_writer(f):
    return csv.writer(f, dialect='unix')
# uid, pid/sid, rating, review, date_time 
product_file = open("ProductFeedback.csv","w")
seller_file = open("SellerFeedback.csv","w")
product_writer = get_csv_writer(product_file)
seller_writer = get_csv_writer(seller_file)

users, seller_reviews, product_reviews = [],[],[]
for uid,info in purchases.items():
    users.append(uid)
    product_ratings = {}
    seller_ratings = {}
    earliest_purchase_from_seller = None 
    seller_product_ratings = defaultdict(list)
    for sid, pid_list in info.items(): 
        for pid,date_fulfilled in pid_list.items():
            if date_fulfilled == '': continue 
            # users can only leave feedback for products that they have received 
            date_fulfilled = datetime.strptime(date_fulfilled, '%Y-%m-%d %H:%M:%S')
            default_time = fake.date_time_between(start_date=date_fulfilled, end_date='now')
            if not earliest_purchase_from_seller:
                earliest_purchase_from_seller = date_fulfilled 

            # make sure that the user has not left a review for this product already 
            if pid in product_ratings: 
                seller_product_ratings[sid].append(product_ratings[pid])
                continue 
            # generate product rating and review (if applicable)
            p_rating = random.randint(1,5)
            # if random.choice([True,False]) and p_rating < 5: p_rating += 0.5
            seller_product_ratings[sid].append(p_rating)
            product_ratings[pid] = p_rating 
            # leave_p_review = random.choice([True,False])
            leave_p_review = True
            if leave_p_review: 
                # get a random image 
                if random.choice([True,False]) == True: 
                    image = "product_images/" + random.choice(image_files)
                else: 
                    image = None
                length = random.randint(6,10)
                product_reviews.append((uid,pid))
                review = fake.sentence(nb_words=length)[:-1] + ". " + sample_product_reviews[pid][int(p_rating)] + " " + fake.sentence(nb_words=length)[:-1] + "." 
                product_writer.writerow([uid,pid,p_rating,review,default_time,image])
            else: 
                product_writer.writerow([uid,pid,p_rating,None,default_time,None])
        if len(seller_product_ratings[sid]) == 0: continue  
        # make sure that the user has not left a review for this seller already 
        if sid in seller_ratings: continue 
        # rating for seller is the average of the ratings left for the products bought from that seller 
        s_rating = int(sum(seller_product_ratings[sid])/len(seller_product_ratings[sid]))
        seller_ratings[sid] = s_rating
        # if random.choice([True,False]) and s_rating < 5: s_rating += 0.5
        #default_time = random.choice(default_times)
        default_time = fake.date_time_between(start_date=earliest_purchase_from_seller, end_date='now')
        # leave_s_review = random.choice([True,False])
        leave_s_review = True
        if leave_s_review: 
            length = random.randint(10,20)
            seller_reviews.append((uid,sid))
            seller_writer.writerow([uid,sid,s_rating,fake.sentence(nb_words=length)[:-1],default_time])
        else: 
            seller_writer.writerow([uid,sid,s_rating,"",default_time])
seller_file.close()
product_file.close()


# randomly generate upvotes data for seller and product reviews
# as well as messages between users 
seller_file = open("SellerReviewUpvotes.csv","w")
product_file = open("ProductReviewUpvotes.csv","w")
messages_file = open("Messages.csv","w")
messaged = [] 
seller_upvotes = get_csv_writer(seller_file)
product_upvotes = get_csv_writer(product_file)
messages = get_csv_writer(messages_file)
s_cap, p_cap, m_cap = 300, 500, 10

for user in users: 
    s_count, p_count = 0,0
    for uid, sid in seller_reviews: 
        if uid != sid: 
            if (uid,sid) in messaged: continue
            if random.choice([True,False]) == True: 
                messaged.append((uid,sid))
                messaged.append((sid,uid))
                # start a message thread 
                msg_date = fake.date_time_between(start_date='-3y', end_date='now')
                for _ in range(random.randint(0,m_cap)): 
                    msg_date = msg_date + timedelta(hours = random.randint(1,100))
                    last_mst_date = msg_date
                    length = random.randint(6,20)
                    msg = fake.sentence(nb_words=length)[:-1]  
                    sender = random.choice([uid,sid])
                    if sender == uid: 
                        recipient = sid 
                    else: 
                        recipient = uid 
                    messages.writerow([sender,recipient,msg_date,msg])
        # make sure that upvotes are slightly uncommon 
        if random.choice([True,False]) == True: 
            seller_upvotes.writerow([user,uid,sid])
            s_count += 1 
        if s_count == s_cap: break
    for uid, pid in product_reviews: 
        if random.choice([True,False,False,False]) == True: 
            product_upvotes.writerow([user,uid,pid])
            p_count += 1 
        if p_count == p_cap: break
seller_file.close()
product_file.close()
messages_file.close()