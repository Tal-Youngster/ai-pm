from app.db.base import SessionLocal
from app.db.models import Project

session = SessionLocal()
print('count', session.query(Project).count())
session.close()
