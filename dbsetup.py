# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring


from psycopg2 import OperationalError, connect  # type: ignore


def setup_database(host_name: str, db_name: str, schema_name: str) -> int:
    try:
        connection = connect(
            f"host={host_name} dbname={db_name} user=postgres password=test options='-c search_path={schema_name}'"
        )
        connection.close()
        result = 0
    except OperationalError:
        try:
            connection = connect(
                f"host={host_name} dbname=postgres user=postgres password=test"
            )
            connection.autocommit = True
            cursor = connection.cursor()
            cursor.execute(f"CREATE DATABASE {db_name}")
            cursor.close()
            connection.close()
            connection = connect(
                f"host={host_name} dbname={db_name} user=postgres password=test"
            )
            connection.autocommit = True
            cursor = connection.cursor()
            cursor.execute(f"CREATE SCHEMA {schema_name}")
            cursor.close()
            connection.close()
            connection = connect(
                f"host={host_name} dbname={db_name} user=postgres password=test options='-c search_path={schema_name}'"
            )
            connection.autocommit = True
            cursor = connection.cursor()
            cursor.execute(
                """
                            CREATE TABLE IF NOT EXISTS app1.buildings
                        (
                            id serial NOT NULL,
                            address character varying(255) COLLATE pg_catalog."default" NOT NULL,
                            CONSTRAINT buildings_pkey PRIMARY KEY (id)
                        )
                        """
            )
            cursor.execute(
                """
                            CREATE TABLE IF NOT EXISTS app1.services
                        (
                            id serial NOT NULL ,
                            name character varying(255) COLLATE pg_catalog."default" NOT NULL,
                            CONSTRAINT services_pkey PRIMARY KEY (id)
                        )
                        """
            )
            cursor.execute(
                """
                            CREATE TABLE IF NOT EXISTS app1.people
                        (
                            id serial NOT NULL ,
                            name character varying(255) COLLATE pg_catalog."default" NOT NULL,
                            phone_number character varying(255) COLLATE pg_catalog."default" NOT NULL,
                            building_id bigint NOT NULL,
                            CONSTRAINT people_pkey PRIMARY KEY (id),
                            CONSTRAINT "Building Relationship" FOREIGN KEY (building_id)
                                REFERENCES app1.buildings (id) MATCH SIMPLE
                                ON UPDATE NO ACTION
                                ON DELETE NO ACTION
                                NOT VALID
                        )
                        """
            )
            cursor.execute(
                """
                            CREATE TABLE IF NOT EXISTS app1.buildings_services
                        (
                            id serial NOT NULL,
                            building_id bigint NOT NULL,
                            service_id bigint NOT NULL,
                            CONSTRAINT buildings_services_pkey PRIMARY KEY (id),
                            CONSTRAINT "Building Relationship" FOREIGN KEY (building_id)
                                REFERENCES app1.buildings (id) MATCH SIMPLE
                                ON UPDATE NO ACTION
                                ON DELETE NO ACTION
                                NOT VALID,
                            CONSTRAINT "Service Relationship" FOREIGN KEY (service_id)
                                REFERENCES app1.services (id) MATCH SIMPLE
                                ON UPDATE NO ACTION
                                ON DELETE NO ACTION
                                NOT VALID
                        )
                        """
            )
            cursor.close()
            connection.close()
            result = 0
        except Exception:  # pylint: disable=broad-except
            result = 100

    return result
