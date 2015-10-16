import sys

from bunch import Bunch
from sqlalchemy import engine, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from utils import get_password


class Config(Bunch):
    """ """

    def get_db_url(self):

        if self.database_type == 'postgresql':
            self.drivername = 'postgresql+psycopg2'
        else:
            sys.exit('Only postgresql is supported at the moment')

        if not (self.database and self.host and self.username):
            raise ValueError('database, host, port and username must be set.')

        dburl = engine.url.URL(self.drivername, self.username, self.password,
                               self.host, self.port, self.database)

        if self.password is PASSWORD_NOT_SET:
            pass  # No password
        elif self.password is None:
            dburl.password = get_password('Database password: ')
        else:
            dburl.password = self.password
        return dburl

    def get_db_session(self, db_url=None):

        if getattr(self, 'session', None):
            return self.session

        engine = create_engine(db_url or self.get_db_url())
        session_factory = sessionmaker(autocommit=False, autoflush=False)
        Session = scoped_session(session_factory)
        Session.configure(bind=engine)
        db_session = Session()

        # Test connection
        try:
            db_session.bind.table_names()
        except:
            raise
        else:
            return db_session


config = Config()
config.database_type = 'postgresql'
config.host = 'localhost'
config.port = None
config.Base=declarative_base()
config.schema_name='public'


PASSWORD_NOT_SET = object()


def create_geoname_tables(db_session, recreate_tables=False):
    if recreate_tables:
        config.Base.metadata.drop_all(bind=db_session.bind)
    config.Base.metadata.create_all(bind=db_session.bind)


def purge_geoname_tables(db_session):
    for table in reversed(config.Base.metadata.sorted_tables):
        print('Purging data from {}...'.format(table.name))
        db_session.bind.execute(table.delete())
