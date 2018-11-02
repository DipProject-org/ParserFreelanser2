from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///skillbase.db')

db_session = scoped_session(sessionmaker(bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()
Base.metadata.create_all(bind=engine)

class Skillbase(Base):
	__tablename__ = 'skills'
	id = Column(Integer, primary_key=True)
	skill = Column(Text, unique=True)
	link = Column(Text)
	work_count = Column(Integer)
	skill_words = Column(Text)

	def __init__(self, skill=None, link=None, work_count=None, skill_words=None):
		self.skill=skill
		self.link=link
		self.work_count=work_count
		self.skill_words=skill_words

	def __repr__(self):
		return 'По навыку {} найдено {} предложений!'.format(self.skill, 
			self.work_count)

def create_base():
	Base.metadata.create_all(bind=engine)

def add_skill(skill):
	skill_db = Skillbase(
		skill['skill'], 
		skill['link'], 
		skill['work_count'], 
		skill['skill_words']
		)
	db_session.add(skill_db)
	db_session.commit()

