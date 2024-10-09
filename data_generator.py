
import json
import random
import sys
from datetime import datetime, timedelta

from faker import Faker
from faker.providers import BaseProvider, date_time
from pytz import timezone

fake = Faker("en_UK")
fake.add_provider(date_time)


# Pass in fake dates and return with UK timezone offsets
def uk_time_iso8601(fake_date):
    uk_timezone = timezone("Europe/London")
    fake_date_with_tz = uk_timezone.localize(fake_date)

    return fake_date_with_tz


class FileBasedOrgProvider(BaseProvider):
    """This organisation provider selects from a static JSON file"""

    FILE_PATH = "./scripts/orgs.json"

    with open(FILE_PATH) as orgs_json:
        json_array_as_string = orgs_json.read()
        orgs = json.loads(json_array_as_string)
        num_orgs = len(orgs)

    def org_name(self, org_id):
        """Return the name of the org at that index"""
        self.__validate_org_id(org_id)
        return self.orgs[org_id - 1]["name"]

    def org_description(self, org_id):
        """Return the name of the org at that index"""
        self.__validate_org_id(org_id)
        return self.orgs[org_id - 1]["description"]

    def __validate_org_id(self, org_id):
        if org_id > self.num_orgs:
            raise IndexError(
                f"There are only {self.num_orgs} organisations "
                f"so "
                f"pass an org_id between 1 and {self.num_orgs}"
            )
        elif org_id < 0:
            raise IndexError("Org ids must be positive integers")
        return True


# Add the FileBasedOrgProvider to our faker object
fake.add_provider(FileBasedOrgProvider)


class DjangoModel:
    def __init__(self, model_id):
        self.model_id = model_id

    def to_json(self):
        d = self.to_dict()
        return json.dumps(d)


class Organisation(DjangoModel):
    def __init__(self, model_id, name, description, created_at, created_by=""):
        super().__init__(model_id)

        self.name = name
        self.description = description
        self.created_at = str(created_at)
        self.created_by = created_by
        self.updated_at = self.created_at
        self.updated_by = created_by
        self.has_consented_to_share = fake.boolean()
        self.has_consented_to_store = fake.boolean()

    def to_json(self):
        d = self.to_dict()
        del d["id"]
        return json.dumps(d)

    def to_dict(self):
        d = {
            "id": self.model_id,
            "name": f"{self.name}",
            "description": self.description,
            "created_at": self.created_at,
            "created_by": self.created_by,
            "updated_at": self.updated_at,
            "updated_by": self.updated_by,
            "has_consented_to_share": self.has_consented_to_share,
            "has_consented_to_store": self.has_consented_to_share,
        }
        return d


class User(DjangoModel):
    def __init__(
        self,
        model_id,
        name,
        email,
        created_at,
        created_by="",
        organisation_id=None,
    ):
        super().__init__(model_id)

        self.name = name
        self.email = email
        self.username = (email,)
        self.display_name = name
        self.created_at = str(created_at)
        self.updated_at = self.created_at
        self.created_by = created_by
        self.organisation_id = organisation_id
        self.updated_by = created_by

    def __str__(self):
        return f"{self.name}({self.model_id})"

    def to_json(self):
        d = self.to_dict()
        del d["id"]
        return json.dumps(d)

    def to_dict(self):
        d = {
            "id": self.model_id,
            "name": f"{self.name}",
            "email": self.email,
            "username": self.email,
            "display_name": f"{self.display_name}",
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "created_by": self.created_by,
            "organisation_id": self.organisation_id,
            "updated_by": self.updated_by,
        }
        return d


# Container produces the json output in the format needed by loaddata
class DjangoModelContainer:
    def __init__(self, classname: str, django_model):
        self.classname = classname
        self.django_model = django_model

    # function to put the new attributes into a dictionary and then
    # into json format
    def to_json(self):
        # get model attributes dictionary as a json object
        fields_json = self.django_model.to_json()

        container_dict = {
            "model": self.classname,
            "pk": self.django_model.model_id,
            "fields": fields_json,
        }
        return json.dumps(container_dict)


def make_datetime(fake):
    today = datetime.today().date()
    # ignore leap years!
    last_year_yesterday = today + timedelta(days=-365)
    return fake.date_time_between(last_year_yesterday, today)


# Creating a super_user for the created_by
super_user_created_at = make_datetime(fake)
super_user_created_at_with_tz = uk_time_iso8601(super_user_created_at)
super_user = User(
    model_id=1,
    name="Admin User",
    email="AdminUser@geneticsinc.com",
    created_at=super_user_created_at_with_tz,
    created_by=1,
)
# create empty list for all json string model objects to be added to
django_model_items_array = []
# add outer fixture formatting to super user attribute fields
super_user_container = DjangoModelContainer("core.User", super_user)
# add container instance to list - super user
django_model_items_array.append(super_user_container.to_json())


# Create 20 organisations with random number of users between 1 and 10
user_id = 1
num_orgs = 20

for i in range(num_orgs):
    # create organisation
    org_id = i
    # grab next organisation from orgs.json
    org_name = fake.org_name(org_id)
    org_description = fake.org_description(org_id)
    org_created_at = make_datetime(fake)
    org_created_at_with_tz = uk_time_iso8601(org_created_at)
    new_org = Organisation(
        model_id=org_id,
        name=org_name,
        description=org_description,
        created_at=org_created_at_with_tz,
        created_by=super_user.model_id,
    )
    org_container = DjangoModelContainer("core.Organisation", new_org)

    # add container instance to list - organisation
    django_model_items_array.append(org_container.to_json())

    # create random no of users for this organisation
    for _x in range(random.randrange(1, 10)):
        user_id += 1
        user_name = fake.name()
        if "'" in user_name:
            user_name = user_name.replace("'", "")
        user_email = (
            user_name.lower().replace(" ", "")
            + "@"
            + org_name.lower().replace(" ", "")
            + ".com"
        )
        user_created_at = make_datetime(fake)
        user_created_at_with_tz = uk_time_iso8601(user_created_at)
        new_user = User(
            model_id=user_id,
            name=user_name,
            email=user_email,
            created_at=user_created_at_with_tz,
            created_by=super_user.model_id,
            organisation_id=new_org.model_id,
        )

        user_container = DjangoModelContainer("core.User", new_user)

        # add container instance to list - user
        django_model_items_array.append(user_container.to_json())


# get output into correct json format for loaddata
output = json.dumps(django_model_items_array)
output2 = output.replace("\\", "")
output3 = output2.replace('"{', "{")
output4 = output3.replace('}"', "}")


# write code to .json file
# if running from a test set flag to true and write to test file
this_is_a_test = "test" in sys.argv

if this_is_a_test is True:
    with open("scripts/tests/generated_test_data.json", "w") as demo_data:
        demo_data.write(output4)
else:
    with open("core/tests/generated_data.json", "w") as demo_data:
        demo_data.write(output4)
