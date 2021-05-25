# Third-Party Imports
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String

# Project Imports
import db_details as db

engine = create_engine("mysql+mysqldb://%s:%s@%s:3306/%s" %
                                   (db.DB_USER, db.DB_PASSWORD, db.DB_HOST, db.DB_DATABASE), echo=False)
meta = MetaData()

users = Table(
    'user', meta,
    Column('id', Integer, primary_key=True),
    Column('username', String(50), unique=True),
    Column('password', String(30)),
    Column('email', String(50)),
    Column('phone_no', Integer),
    mysql_engine='InnoDB',
    mysql_charset='utf8mb4',
    mysql_key_block_size="1024"

)
meta.create_all(engine)
