# Script to generate fake test data and transfer into a .json file

from faker import Faker
from models import Organisation, User

import random
import json

# Set locale for faker method to UK
fake = Faker('en_UK')

num_users = 20

num_orgs = 20

# generate dictionary of random company names from which to attach users and create organisations
def generate_dict_fake_organisations(num_orgs):
    fake_orgs = {}
    organisation_id = 0
    for i in range(num_orgs):
        organisation = fake.company()
        organisation_id += 1
        #add to disctionary of {id: organisation}
        fake_orgs[organisation_id] = organisation
        print(fake_orgs)
    
    return(fake_orgs)



#create users 
#create superuser first? that is the created_by for 
#all of the other users and themselves?
super_user = User.objects.create(
    id = 1,
    name = "Super User",
    password = "dummy",
    email = "SuperUser@Evident.Studio",
    username = "SuperUser",
    display_name = "SuperUser",
    created_at = fake.date_time,
    updated_at = fake.date_time,
    organisation = fake.company,
    created_by = 1
)


def create_test_users(num_users):
    for i in range(num_users):
        #new_user = []

        user = User.objects.create(
            name = fake.name(),
            password = fake.password(),
            email = fake.email(),
            username = name,
            display_name = name,
            created_at = fake.date_time,
            updated_at = fake.date_time,
            organisation = fake.company,
            created_by = User.objects.get(id = 1)
        )
        user.save()
        

#create organisations - 20 to start - have number as parameter

def create_test_organisations(num_orgs):

    fake_orgs_dict = generate_dict_fake_organisations(num_orgs)
    print(fake_orgs_dict)

    for i in range(len(fake_orgs_dict)):
        user_id = random.randint(1, num_users)
        user = User.objects.get(id = user_id)
        org_id = i
        org_name = fake_orgs_dict[i]
        organisation = Organisation.objects.create(
            # grab from fake_orgs dictionary
            id = org_id,
            #grab from fake_orgs dictionary
            name = org_name,
            description = fake.text(),
            created_at = fake.date_time(),
            created_by = User.objects.get(id = user_id),
            updated_at = fake.date_time(),
            updated_by = User.objects.get(id = user_id),
            has_consented = fake.boolean()
        )
        organisation.save()


def transfer_data_to_json_file(num_users, num_orgs):

    all_users = create_test_users(num_users)

    all_orgs = create_test_organisations(num_orgs)

    #transfer list into .json file
    #create data object
    json_data1 = all_users

    #write to json file
    with open('initial_data.json', 'w') as out_file:
     json.dump(json_data1, out_file, sort_keys = True, indent = 4,
               ensure_ascii = False)
     
    json_data2 = all_orgs

    with open('initial_data.json', 'w') as out_file:
        json.dump(json_data2, out_file, sort_keys = True, indent = 4,
               ensure_ascii = False)

    
