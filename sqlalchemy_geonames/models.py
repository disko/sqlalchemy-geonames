from __future__ import absolute_import

from geoalchemy2 import Geography
from sqlalchemy import func
from sqlalchemy import (Column, ForeignKey, Integer, String, Text, BigInteger,
                        DateTime, Numeric)
from sqlalchemy import or_
from sqlalchemy.orm import relationship

from sqlalchemy_geonames.sqla import config
from sqlalchemy_geonames.utils import simple_repr


class GeonameMetadata(config.Base):
    __tablename__ = 'metadata'
    __table_args__ = {'schema': config.schema_name, }
    id = Column(Integer, primary_key=True)
    # TODO: Use this to keep track of data to download
    last_updated = Column(DateTime(timezone=True), nullable=False)


class GeonameCountry(config.Base):
    __tablename__ = 'country'
    __table_args__ = {'schema': config.schema_name, }
    __repr__ = simple_repr('country')

    iso = Column(String(2), primary_key=True)
    iso3 = Column(String(3), nullable=False)
    iso_numeric = Column(Integer, nullable=False)
    fips = Column(String(2), nullable=False)
    country = Column(String(255), nullable=False)
    capital = Column(String(255), nullable=False)
    area_in_sq_km = Column(Integer)
    population = Column(Integer, nullable=False)
    continent = Column(String(255), nullable=False)
    tld = Column(String(3), nullable=False)
    currency_code = Column(String(3), nullable=False)
    currency_name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False)
    postal_code_format = Column(String(255), nullable=False)
    postal_code_regex = Column(String(255), nullable=False)
    languages = Column(String(255), nullable=False)
    geonameid = Column(Integer)
    neighbours = Column(String(255), nullable=False)
    equivalent_fips_code = Column(String(255), nullable=False)


class GeonameTimezone(config.Base):
    __tablename__ = 'timezone'
    __table_args__ = {'schema': config.schema_name, }
    __repr__ = simple_repr('timezone_id')

    # the timezone id (see file timeZone.txt) varchar(40)
    # (Renamed from timezone)
    timezone_id = Column(String(40), primary_key=True)

    country_code = Column(String(2), nullable=False)
    gmt_offset = Column(Numeric(3, 1), nullable=False)
    dst_offset = Column(Numeric(3, 1), nullable=False)
    raw_offset = Column(Numeric(3, 1), nullable=False)


class GeonameFeature(config.Base):
    __tablename__ = 'feature'
    __table_args__ = {'schema': config.schema_name, }
    __repr__ = simple_repr('name')

    # see http://www.geonames.org/export/codes.html, varchar(10)
    feature_code = Column(String(10), primary_key=True)

    # see http://www.geonames.org/export/codes.html, char(1)
    feature_class = Column(String(1), nullable=False)

    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)


class Geoname(config.Base):
    __tablename__ = 'geoname'
    __table_args__ = {'schema': config.schema_name, }
    __repr__ = simple_repr('name')

    # integer id of record in geonames database
    geonameid = Column(Integer, primary_key=True)

    # name of geographical point (utf8) varchar(200)
    name = Column(String(200), nullable=False)

    # name of geographical point in plain ascii characters, varchar(200)
    asciiname = Column(String(200), nullable=False)

    # alternatenames, comma separated varchar(5000)
    alternatenames = Column(Text, nullable=False)

    # latitude in decimal degrees (wgs84)
    # latitude = Column(Numeric(10, 7), nullable=False)

    # longitude in decimal degrees (wgs84)
    # longitude = Column(Numeric(10, 7), nullable=False)

    # Custom. A point made from `latitude` and `longitude`.
    # SRID #4326 = WGS84
    point = Column(Geography(geometry_type='POINT', srid=4326), nullable=False)

    feature_code = Column(String(10), ForeignKey(GeonameFeature.feature_code))
    feature = relationship(GeonameFeature)

    # ISO-3166 2-letter country code, 2 characters
    country_code = Column(String(2), ForeignKey(GeonameCountry.iso))
    country = relationship(GeonameCountry)

    # alternate country codes, comma separated, ISO-3166 2-letter country
    # code, 60 characters
    cc2 = Column(String(60), nullable=False)

    # fipscode (subject to change to iso code), see exceptions below, see
    # file admin1Codes.txt for display names of this code; varchar(20)
    admin1_code = Column(String(20), nullable=False)

    # code for the second administrative division, a county in the US, see
    # file admin2Codes.txt; varchar(80)
    admin2_code = Column(String(80), nullable=False)

    # code for third level administrative division, varchar(20)
    admin3_code = Column(String(20), nullable=False)

    # code for fourth level administrative division, varchar(20)
    admin4_code = Column(String(20), nullable=False)

    # bigint (8 byte int)
    population = Column(BigInteger, nullable=False)

    # in meters, integer
    elevation = Column(Integer)

    # digital elevation model, srtm3 or gtopo30, average elevation
    # of 3''x3'' (ca 90mx90m) or 30''x30'' (ca 900mx900m) area in
    # meters, integer. srtm processed by cgiar/ciat.
    dem = Column(Integer, nullable=False)

    # (Renamed from timezone)
    timezone_id = Column(String(40), ForeignKey(GeonameTimezone.timezone_id))
    timezone = relationship(GeonameFeature)


class GeonamePostalCode(config.Base):
    __tablename__ = 'postal_code'
    __table_args__ = {'schema': config.schema_name, }
    __repr__ = simple_repr('country_code', 'postal_code')

    # iso country code
    country_code = Column(String(2), ForeignKey(GeonameCountry.iso),
                          nullable=False, primary_key=True)

    postal_code = Column(String(20), nullable=False, primary_key=True)
    place_name = Column(String(180), nullable=False, primary_key=True)

    # 1. order subdivision (state)
    admin_name1 = Column(String(100), nullable=False)
    admin_code1 = Column(String(20), nullable=False)

    # 2. order subdivision (state)
    admin_name2 = Column(String(100), nullable=False)
    admin_code2 = Column(String(20), nullable=False)

    # 3. order subdivision (state)
    admin_name3 = Column(String(100), nullable=False)
    admin_code3 = Column(String(20), nullable=False)

    # latitude in decimal degrees (wgs84)
    # latitude = Column(Numeric(10, 7), nullable=False)
    # longitude in decimal degrees (wgs84)
    # longitude = Column(Numeric(10, 7), nullable=False)

    point = Column(Geography(geometry_type='POINT', srid=4326), nullable=False)

    accuracy = Column(Integer())

    def within_a_radius_of(self, radius):
        """ Find all other postal codes within the given radius.

        Args:
            self, km

        Returns:
            list of :class:`GeonamePostalCode`
        """

        session = config.get_db_session()

        return session.query(GeonamePostalCode).filter(
            func.ST_DWithin(GeonamePostalCode.point, self.point, radius * 1000)
        )

    @classmethod
    def postal_codes_around(cls, postal_code, radius):
        """ List of postal codes within ``radius`` km around ``postal code``

        """

        session = config.get_db_session()
        conditions = []

        for center in session.query(cls).filter(
                        cls.postal_code == postal_code).all():
            conditions.append(
                func.ST_DWithin(cls.point, center.point, radius * 1000)
            )

        return session.query(cls).filter(or_(*conditions))


