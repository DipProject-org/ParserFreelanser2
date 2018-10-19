from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///workbase.db')

db_session = scoped_session(sessionmaker(bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()
Base.metadata.create_all(bind=engine)

class Workbase(Base):
	__tablename__ = 'works'
	id = Column(Integer, unique=True, primary_key=True)
	skill = Column(Text)
	title = Column(Text)
	time = Column(Text)
	description = Column(Text)
	list_skill = Column(Text)
	link = Column(Text)
	price = Column(Text)
	verified = Column(Text)
	bids = Column(Integer)

	def __init__(self, skill=None, title=None, time=None, description=None, list_skill=None, link=None, price=None, verified=None, bids=None):
		self.skill=skill
		self.title=title
		self.time=time
		self.description=description
		self.list_skill=list_skill
		self.link=link
		self.price=price
		self.verified=verified
		self.bids=bids

	#def __repr__(self):
		#return 'По навыку {} найдено {} предложений!>'.format(self.skill, self.work_count)

def create_work_base():
	Base.metadata.create_all(bind=engine)