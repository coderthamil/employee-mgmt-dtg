from sqlalchemy import create_engine;
from sqlalchemy.orm import sessionmaker,declarative_base;
from dotenv import load_dotenv;
import os;
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
#engine connect to database by create engine function with url
engine = create_engine(DATABASE_URL);
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine);
Base = declarative_base();

