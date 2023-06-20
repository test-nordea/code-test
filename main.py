"""
    Module providing 3 entities (Service,Building,People) and user can generate random data for each of them.

    Application assigns specific number of services to each building randomly by considering this condition that
    a Building can host multiple Services and a Service can be available in multiple Buildings, this number can be
    specified by user as input value in the terminal.

    Application assigns only one building to each people.
"""
import dataclasses
import os
import random
import sys
from typing import Any, List

from faker import Faker  # type: ignore
from psycopg2 import connect, extensions, extras  # type: ignore

from dbsetup import setup_database


@dataclasses.dataclass
class ServiceEntity:
    """
    This class represents a Service entity.

    Attributes
    ----------
    name : str
        Name of the Service
    """

    name: str


@dataclasses.dataclass
class BuildingEntity:
    """
    This class represents a Building entity.

    Attributes
    ----------
    address : str
        Address of the Building
    """

    address: str


@dataclasses.dataclass
class PersonEntity:
    """
    This class represents a Person entity.

    Attributes
    ----------
    name : str
        Person Name
    phone_number : str
        Person Phone Number
    building_id: int
        Building ID which assigned to person
    """

    name: str
    phone_number: str
    building_id: int


class Services:
    """
    This class represents the below methods for Service entities.

    Methods
    -------
    data_generator : Generate data randomly of Service entities
    insert_data:  Inserting data into "services" table
    """

    def data_generator(self, number: int) -> List[Any]:
        """
        Generate data randomly using Faker library
        :param number: Number of entities which should be generated randomly
        :return: A list of generated data
        """
        fake = Faker()
        services_list = []
        for _ in range(number):
            service_name = fake.company()
            (services_list.append(ServiceEntity(service_name)))
        return services_list

    def insert_data(
        self, db_connection: extensions.connection, services_list: List[Any]
    ) -> Any:
        """
        Insert provided data in service_list parameter into the database
        :param db_connection: Connection object for connecting to Postgresql database
        :param services_list: A list of services which should be imported to the database
        :return: A list of all service IDs from "Services" table for assigning to buildings
        """
        with db_connection.cursor() as cursor:
            all_service = ({"name": service.name} for service in services_list)
            query = """
                            INSERT INTO services (name) VALUES (%(name)s) RETURNING id
                        """
            extras.execute_batch(cursor, query, all_service)
            db_connection.commit()
            query = """
                    SELECT id FROM services order by id
                """
            cursor.execute(query)
            service_id_list = cursor.fetchall()
            return service_id_list


class Buildings:
    """
    This class represents the below methods for Building entities.

    Methods
    -------
    data_generator : Generate data randomly of Building entities
    insert_data: Inserting data into "Buildings" table
    """

    def data_generator(self, number: int) -> List[Any]:
        """
        Generate data randomly using Faker library
        :param number: Number of entities which should be generated randomly
        :return: A list of generated data
        """
        fake = Faker()
        buildings_list = []
        for _ in range(number):
            building_address = fake.address()
            (buildings_list.append(BuildingEntity(building_address)))
        return buildings_list

    def insert_data(
        self, db_connection: extensions.connection, building_list: List[Any]
    ) -> Any:
        """
        Insert provided data in building_list parameter into the database.

        :param db_connection: An object for connecting to Postgresql database
        :param building_list: A list of buildings which should be imported to the database
        :return: A list of new building IDs for assigning to services
        """
        with db_connection.cursor() as cursor:
            query = """
                                SELECT id FROM buildings order by id desc
                            """
            cursor.execute(query)
            try:
                last_building_id = cursor.fetchone()[0]
            except TypeError:
                last_building_id = 0

            all_building = ({"address": building.address} for building in building_list)
            query = """
                            INSERT INTO buildings (address) VALUES (%(address)s) RETURNING id
                        """
            extras.execute_batch(cursor, query, all_building)

            db_connection.commit()
            building_id_list = range(last_building_id + 1, cursor.fetchone()[0] + 1)
            return building_id_list

    def assign_service(
        self,
        db_connection: extensions.connection,
        building_id_list: List[Any],
        service_id_list: List[Any],
        number: int,
    ) -> Any:
        """
        Assign services to building randomly and insert the data into "buildings_services" table which designed for
        Many-to-Many relationship.

        :param db_connection: An object for connecting to Postgresql database
        :param building_id_list: A list of buildings
        :param service_id_list: A list of available services for assign to new buildings
        :param number: The number of services which should be assigned for each building
        :return: None
        """
        buildings_services_list = []
        for building_id in building_id_list:
            random_list = random.sample(service_id_list, number)
            for i in range(number):
                buildings_services_list.append(
                    {"building_id": building_id, "service_id": random_list[i][0]}
                )
        with db_connection.cursor() as cursor:
            query = """
                INSERT INTO buildings_services (building_id,service_id) VALUES (%(building_id)s,%(service_id)s) RETURNING id
                  """
            extras.execute_batch(cursor, query, buildings_services_list)
            db_connection.commit()


class People:
    """
    This class represents the below methods for People entities.

    Methods
    -------
    data_generator : Generate data randomly of Person entity
    assign_building : Assign only one building to each person
    insert_data: Insert data into "People" table
    """

    def data_generator(self, number: int) -> List[Any]:
        """
        Generate data randomly using Faker library
        :param number: Number of entities which should be generated randomly
        :return: A list of generated data
        """
        fake = Faker()
        people_list = []
        for _ in range(number):
            person_name = fake.name()
            person_phone_number = fake.phone_number()
            (people_list.append(PersonEntity(person_name, person_phone_number, 0)))
        return people_list

    def assign_building(
        self, building_id_list: List[Any], people_list: List[Any]
    ) -> Any:
        """
        Function for assigning one building to each person.

        :param building_id_list: A list of available buildings for assign to people
        :param people_list: List of people which generated randomly
        :return: A list of dictionary including name,phone_number,building ID of each person
        """
        people_final_list = []
        for person in people_list:
            person.building_id = random.choice(building_id_list)
            people_final_list.append(
                {
                    "name": person.name,
                    "phone_number": person.phone_number,
                    "building_id": person.building_id,
                }
            )
        return people_final_list

    def insert_data(
        self, db_connection: extensions.connection, people_list: List[Any]
    ) -> Any:
        """
        Insert provided data in people_list parameter into the database
        :param db_connection: Connection object for connecting to Postgresql database
        :param people_list: A list of people which should be imported to the database
        :return: None
        """
        with db_connection.cursor() as cursor:
            all_people = tuple(people_list)
            query = """
                        INSERT INTO people (name,phone_number,building_id) VALUES (%(name)s,%(phone_number)s,%(building_id)s)
                         RETURNING id
                    """
            extras.execute_batch(cursor, query, all_people)
            db_connection.commit()


def input_func(input_message: str) -> int:
    """
    This function get value from user and check type to make sure it is integer and return the value to main stream.
    :param input_message: Text for show to user
    :return: Getting value from user
    """
    input_value = 0
    while True:
        try:
            input_value = int(input(input_message))
        except ValueError:
            print("Please enter integer value ..")
            continue
        else:
            break
    return input_value


def main() -> None:
    """
    This is the main function of application and user interface for getting input values from end user

    """
    host_name = str(os.getenv("DB_HOST"))
    db_name = "nordea"
    schema_name = "app1"
    if setup_database(host_name, db_name, schema_name) != 0:
        print("There is an issue during database creation, please check with Dev team")
        sys.exit()
    connection = connect(
        f"host={host_name} dbname={db_name} user=postgres password=test options='-c search_path={schema_name}'"
    )
    with connection.cursor() as cursor:
        cursor.execute("SELECT count(id) FROM services")
        print("Total number of registered services: ", cursor.fetchone()[0])
        cursor.execute("SELECT count(id) FROM buildings")
        print("Total number of registered buildings: ", cursor.fetchone()[0])
        cursor.execute("SELECT count(id) FROM people")
        print("Total number of registered people: ", cursor.fetchone()[0])

    number = input_func("\r\nPlease enter the number of new services:")
    service_obj = Services()
    generated_service_data = service_obj.data_generator(number)
    total_service_id_list = service_obj.insert_data(connection, generated_service_data)
    print(
        f"{len(generated_service_data)} services generated and inserted into the database"
    )

    number = input_func("\r\nPlease enter the number of buildings: ")
    building_obj = Buildings()
    generated_building_data = building_obj.data_generator(number)
    building_id_list = building_obj.insert_data(connection, generated_building_data)
    print(
        f"{len(generated_building_data)} buildings generated and inserted into the database"
    )
    service_building_num = input_func(
        "\r\nPlease specify number of services per building: "
    )

    building_obj.assign_service(
        connection, building_id_list, total_service_id_list, service_building_num
    )

    number = input_func("\r\nPlease enter the number of people: ")
    people_obj = People()
    generated_people_data = people_obj.data_generator(number)
    people_obj.insert_data(
        connection, people_obj.assign_building(building_id_list, generated_people_data)
    )
    print(
        f"{len(generated_people_data)} people generated and inserted into the database also "
        f"one building assigned to each people"
    )


if __name__ == "__main__":
    main()
