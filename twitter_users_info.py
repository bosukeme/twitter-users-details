import pandas as pd
import twint
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv
import os
from os.path import join, dirname


dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


MONGO_URL = os.environ.get("MONGO_URL")

client= MongoClient(MONGO_URL, connect=False)
db = client.twitter_user_info



def get_handles(txt_file):
    with open(txt_file) as f:
        usernames = f.readlines()
    usernames = [x.strip() for x in usernames]
    print("len: ", len(usernames[:1510]) )
    return usernames[:1510]


def search_db(usernames):
    twitter_user_collection = db.twitter_user_collection
    
    twitter_users=list(twitter_user_collection.find({},{ "_id": 0, "Twitter_Handle": 1})) 
    twitter_users=list((val for dic in twitter_users for val in dic.values()))
    
    new_usernames = []
    for username in usernames:
        if username not in twitter_users:
            new_usernames.append(username)
    
    print("Len: ", len(new_usernames))
    return new_usernames
    
    
    
def process_usernames(new_usernames):
    
    #usernames = ['FHEEFS', 'firstround', 'Doc_D3mz', 'Gaohmee']
    for username in new_usernames:
        try:
            user_name_df = pd.DataFrame()
            user_id_list = []
            user_handle_list = []
            user_name_list = []
            user_bio_list = []
            user_profile_image_list = []

            c = twint.Config()
            c.Username = username
            c.Store_object = True
            c.User_full = False
            c.Pandas =True
            twint.run.Lookup(c)
            user_df = twint.storage.panda.User_df.drop_duplicates(subset=['id'])
            user_id = list(user_df['id'])[0]
            user_name = list(user_df['name'])[0]
            user_bio = list(user_df['bio'])[0]
            user_profile_image = list(user_df['avatar'])[0]
            user_id_list.append(user_id)
            user_handle_list.append(username)
            user_name_list.append(user_name)
            user_bio_list.append(user_bio)
            user_profile_image_list.append(user_profile_image)

            
            user_name_df['Twitter_Handle'] = user_handle_list   
            user_name_df['Twitter_ID'] = user_id_list  
            user_name_df['Twitter_Name'] = user_name_list  
            user_name_df['Twitter_Bio'] = user_bio_list  
            user_name_df['Twitter_Profile_Image'] = user_profile_image_list
            #print(user_name_df)
            save_to_mongodb(user_name_df)
           

        except:
            user_name_df = pd.DataFrame()
            user_id_list = []
            user_handle_list = []
            user_name_list = []
            user_bio_list = []
            user_profile_image_list = []

            print(username)
            user_id_list.append('NA')
            user_handle_list.append(username)
            user_name_list.append('NA')
            user_bio_list.append('NA')
            user_profile_image_list.append('NA')

            user_name_df['Twitter_Handle'] = user_handle_list   
            user_name_df['Twitter_ID'] = user_id_list  
            user_name_df['Twitter_Name'] = user_name_list  
            user_name_df['Twitter_Bio'] = user_bio_list  
            user_name_df['Twitter_Profile_Image'] = user_profile_image_list
            #print(user_name_df)
            save_to_mongodb(user_name_df)
    

def save_to_mongodb(user_name_df):
    
    # Load in the twitter_user_collection from MongoDB
    twitter_user_collection = db.twitter_user_collection 
    
    cur = twitter_user_collection.find() ##check the number before adding
    print('We had %s twitter_user entries at the start' % cur.count())
    

    #loop throup the handles, and add only new enteries
    for handle, _id, name, bio, image in user_name_df[['Twitter_Handle', 'Twitter_ID', 'Twitter_Name', 'Twitter_Bio', 'Twitter_Profile_Image']].itertuples(index=False):
        twitter_user_collection.insert_one({"Twitter_Handle":handle, "Twitter_ID":_id, "Twitter_Name":name, "Twitter_Bio":bio, 'Twitter_Profile_Image': image}) 
    
    cur = twitter_user_collection.find() ##check the number after adding
    print('We have %s twitter_user entries at the end' % cur.count())
    


def run_all():
    start = datetime.now()
    usernames = get_handles('verified_handles.txt')
    new_usernames = search_db(usernames)
    user_name_df = process_usernames(new_usernames)
    
    end = datetime.now()
    print("It took :", end - start)

