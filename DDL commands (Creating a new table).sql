/* Create a new table called Persons with columns;id,
person_name,birth_date and phone*/
Create Table persons(
id int not null,
person_name varchar(50) not null,
birth_date date,
phone varchar(15) not null,
constraint pk_persons primary key (id)
)
SELECT * FROM PERSONS