# Nordea Project

This application is designed to generate random data for three entities (Service,Building,People) by considering following conditions :

- People can work in a Building , only in one at a time
- Buildings provide Services, a Building can host multiple Services and a Service can be available in multiple Buildings

In each run of the application, user should specify the below requirements:

- The number of new services which should be generated and imported into the database
- The number of new buildings which should be generated and imported into the database
- The number of services which system should select randomly and assign to the buildings (System choice services from all data which are exist in the database)
- The number of people which should be generated and import into the database also in this section , system choice one building randomly from new generated buildings

# Database Structure

- Table "Services" for storing data related to Service entity
- Table "Buildings" for storing data related to Building entity
- Table "Buildings_Services" for storing the relationship data between buildings and services (Many-to-Many Relationship)
- Table "People" for storing data related to People entity

# Installation

- Make sure both docker and docker-compose are installed
- Create a directory with naming "Nordea-Project"
- Extract "nordeaproject.tar.gz" file into "Nordea-Project" directory
- Make sure below files and directory exists:
  - NordeaProject (Directory)
  - docker-compose.yml
  - Dockerfile-db
  - Dockerfile-app
- Run the below commands:
  - docker-compose build
  - docker-compose up -d
- Now two containers "app" and "postgres" are up and running
- login to "app" container: "docker exec -it [container-Name(probably "nordea-project-app-1")] bash"

# Run the application

- After login to the app container, working directory is "NordeaProject" and the application can be run by "python main.py",
  git and pre-commit are also configured
