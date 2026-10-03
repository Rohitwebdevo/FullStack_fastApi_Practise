from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

db_url = "postgressql://postgres:05051993@localhost:5432/rohitFirstDB"
        #  "db name":// username: password@localhost:port/db_name
engine = create_engine(db_url)
session = sessionmaker(autocommit=False, autoflush=False, bind=engine)