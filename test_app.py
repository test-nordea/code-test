from main import Services,Buildings,People,ServiceEntity,BuildingEntity,PersonEntity
import pytest

def test_data_generator_in_services_class():
    service=Services()
    n=10
    assert len(service.data_generator(n))==n and isinstance(service.data_generator(n)[0],ServiceEntity)

def test_data_generator_in_buildings_class():
    building=Buildings()
    n=5
    assert len(building.data_generator(n))==n and isinstance(building.data_generator(n)[0],BuildingEntity)

def test_data_generator_in_people_class():
    people=People()
    n=50
    assert len(people.data_generator(n))==n and isinstance(people.data_generator(n)[n-1],PersonEntity)

def test_assign_building_in_people_class():
    people=People()
    person=PersonEntity('David','11111',0)
    people_list=[person]
    result=people.assign_building(range(1, 4), people_list)
    assert result == [{'name':'David','phone_number':'11111','building_id': 1}] or \
           result==[{'name':'David','phone_number':'11111','building_id': 2}] or \
           result==[{'name':'David','phone_number':'11111','building_id': 3}]
