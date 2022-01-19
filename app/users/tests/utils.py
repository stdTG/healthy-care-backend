from random import choice
from typing import Any, Dict, List, Optional

import faker

from app.user_roles import Roles
from app.users.common.models.web import SexEnum

fake = faker.Faker()


def generate_user(
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        birth_date: Optional[str] = None,
        sex: Optional[str] = None,
        city: Optional[str] = None,
        country: Optional[str] = None,
        zipcode: Optional[int] = None,
        address: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        role: Optional[str] = None,
        # password: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Creates and returns a user automatically generating data for fields not specified.
    """
    if email is None:
        email = fake.email()

    if phone is None:
        phone = fake.phone_number()

    if role is None:
        role = choice(Roles.ALL_EXCEPT_PATIENT)

    if sex is None:
        sex = choice((SexEnum.MALE, SexEnum.FEMALE, SexEnum.OTHER))

    if first_name is None:
        if sex == SexEnum.MALE:
            first_name = fake.first_name_male()
        elif sex == SexEnum.FEMALE:
            first_name = fake.first_name_female()
        else:
            first_name = fake.first_name_nonbinary()

    if last_name is None:
        if sex == SexEnum.MALE:
            last_name = fake.last_name_male()
        elif sex == SexEnum.FEMALE:
            last_name = fake.last_name_female()
        else:
            last_name = fake.last_name_nonbinary()

    if birth_date is None:
        birth_date = fake.date_of_birth(
            minimum_age=15, maximum_age=90
        )

    if country is None:
        country = fake.country()

    if city is None:
        city = fake.city()

    if address is None:
        address = fake.address()

    if zipcode is None:
        zipcode = fake.zipcode()

    # if password is None:
    #     password = fake.password()

    return {
        "email": email,
        "phone": phone,
        # "password": password,
        "firstName": first_name,
        "lastName": last_name,
        "birthDate": birth_date,
        "address": {
            "city": city,
            "address": address,
            "zipcode": zipcode,
            "country": country,
        },
        "sex": sex,
        "role": role,
    }


def generate_users(
        users_num: int,
        unique_towns: int = 10,
        **user_kwargs
) -> List[Dict[str, Any]]:
    """
    Generates a list of users.
    :param users_num: Number of users
    :param unique_towns: Number of unique cities
    :param user_kwargs: Arguments to generate_user function
    """
    # Limited set of cities
    towns = [fake.city() for _ in range(unique_towns)]

    # Create users
    users = []
    for _ in range(users_num):
        user_kwargs['city'] = user_kwargs.get('city', choice(towns))
        users.append(generate_user(**user_kwargs))

    return users


def generate_patient(**patient_kwargs):
    patient_kwargs["role"] = Roles.PATIENT

    return generate_user(**patient_kwargs)


def generate_patients(
        users_num: int,
        unique_towns: int = 10,
        **patient_kwargs
) -> List[Dict[str, Any]]:
    """
    Generates a list of patient.
    :param users_num: Number of users
    :param unique_towns: Number of unique cities
    :param patient_kwargs: Arguments to generate_user function
    """
    # Limited set of cities
    towns = [fake.city() for _ in range(unique_towns)]

    # Create users
    patients = []
    for _ in range(users_num):
        patient_kwargs['city'] = patient_kwargs.get("city", choice(towns))
        patients.append(generate_patient(**patient_kwargs))

    return patients


if __name__ == '__main__':
    def print_user(user):
        [print(i, ": ", k) for i, k in user.items()]
        print()


    print_user(generate_user())
    [print_user(user) for user in generate_users(5)]
