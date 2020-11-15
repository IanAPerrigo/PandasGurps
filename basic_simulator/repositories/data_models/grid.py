from sqlalchemy import Column, Integer, LargeBinary, ForeignKey, ForeignKeyConstraint
from sqlalchemy.orm import relationship

from . import Base


class Entity(Base):
    __tablename__ = 'entity'

    entity_id = Column(Integer, primary_key=True)

    chunk = relationship(
        'Location',
        secondary='locationentity',
        back_populates='entities'
    )


class Location(Base):
    __tablename__ = 'location'

    location_id = Column(LargeBinary, primary_key=True)

    entities = relationship(
        "Entity",
        secondary='locationentity'
    )

    chunk = relationship(
        'Chunk',
        secondary='chunklocation',
        back_populates='locations'
    )


class Chunk(Base):
    __tablename__ = 'chunk'

    chunk_id = Column(LargeBinary, primary_key=True)

    grid = relationship(
        "Grid",
        secondary='gridchunk',
        back_populates='chunks'
    )

    locations = relationship(
        "Location",
        secondary='chunklocation',
        back_populates='chunk'
    )


class Grid(Base):
    __tablename__ = 'grid'
    sqlite_autoincrement = True

    grid_id = Column(Integer, primary_key=True)

    chunks = relationship(
        "Chunk",
        secondary='gridchunk',
        back_populates='grid'
    )


class GridChunk(Base):
    __tablename__ = 'gridchunk'

    grid_id = Column(Integer, primary_key=True)
    chunk_id = Column(LargeBinary, ForeignKey(Chunk.chunk_id), primary_key=True)

    __table_args__ = (
        ForeignKeyConstraint(
            ['grid_id'],
            ['grid.grid_id']
        ),
    )


class ChunkLocation(Base):
    __tablename__ = 'chunklocation'

    chunk_id = Column(LargeBinary, primary_key=True)
    location_id = Column(LargeBinary, ForeignKey(Location.location_id), primary_key=True)

    __table_args__ = (
        ForeignKeyConstraint(
            ['chunk_id'],
            ['chunk.chunk_id']
        ),
    )


class LocationEntity(Base):
    __tablename__ = 'locationentity'

    location_id = Column(LargeBinary, ForeignKey(Location.location_id), primary_key=True)
    entity_id = Column(Integer, primary_key=True)

    __table_args__ = (
        ForeignKeyConstraint(
            ['entity_id'],
            ['entity.entity_id']
        ),
    )

#
# if __name__ == '__main__':
#     Base.metadata.create_all(engine)
#     session = Session()
#
#     chunk = Chunk(
#         chunk_id="0,1,1".encode(encoding="utf-8"),
#         grid_id=1
#     )
#
#     location = Location(location_id="1,1,1".encode(encoding="utf-8"))
#
#     chunk.locations.append(location)
#
#     session.add(chunk)
#     session.add(location)
#     session.commit()
#
#     a_chunk = session.query(Chunk).\
#         filter_by(grid_id=1, chunk_id="0,1,1".encode(encoding="utf-8"))\
#         .one()
#
#     e = Entity(
#         entity_id="12345".encode(encoding='utf-8')
#     )
#
#     loc = session.query(Location).\
#         filter_by(location_id=location.location_id).\
#         join(Location.chunk).\
#         filter_by(
#             grid_id=a_chunk.grid_id,
#             chunk_id=a_chunk.chunk_id
#         ).\
#         one()
#
#     loc.entities.append(e)
#     session.add(e)
#     session.commit()
