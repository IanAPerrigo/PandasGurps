from .chunked_grid import *
from repositories.data_models import Database
import repositories.data_models.grid as grid_db_model


class DatabaseBackedGridModel(ChunkedGrid):
    def __init__(self, grid_id=None, chunk_radius=None, max_chunk_radius=None, procedural=False, db: Database = None):
        super(DatabaseBackedGridModel, self).__init__(chunk_radius=chunk_radius)

        self.grid_id = grid_id
        self.db_session = db.get_session()

        self.procedural = procedural
        self.max_chunk_radius = max_chunk_radius

        if self.grid_id is None:
            self._db_grid = grid_db_model.Grid()
            self.db_session.add(self._db_grid)
            self.db_session.commit()
        else:
            self._db_grid = self.db_session.query(grid_db_model.Grid). \
                filter_by(grid_id=self.grid_id)

        # Having _obj_chunk always loaded in memory allows chunks to be saved off to disk when they are not needed.
        # The only thing that needs to be done to ensure that _obj_chunk is saved before the application is shut down.

    def _load_chunk(self, chunk_id):
        # Load the chunk based on its ID.
        existing_chunk = self.db_session.query(grid_db_model.Chunk). \
            filter_by(chunk_id=chunk_id). \
            join(grid_db_model.Grid.chunks). \
            one_or_none()

        if self.procedural and existing_chunk is None:
            # If there is a procedural limit, just return no chunk.
            if self.max_chunk_radius is not None:
                chunk_pos = self._buf2vec(chunk_id)
                d = cubic_manhattan(chunk_pos, np.array([0, 0, 0]))
                if d > self.max_chunk_radius:
                    return

            # If procedural generation is on, just create the new chunk.
            new_chunk = grid_db_model.Chunk(chunk_id=chunk_id)
            self._db_grid.chunks.append(new_chunk)
            self.db_session.add(new_chunk)
            self.db_session.commit()

            existing_chunk = new_chunk
        elif existing_chunk is None:
            raise Exception("Tried to load a chunk that doesn't exist.")

        chunk = super(DatabaseBackedGridModel, self)._load_chunk(chunk_id)

        for location in existing_chunk.locations:
            entity_ids = set(map(lambda e: e.entity_id, location.entities))
            # TODO: load terrain

            loc_data = Location()
            loc_data.entities.update(entity_ids)

            chunk.pos_to_location[location.location_id] = loc_data
            for entity_id in entity_ids:
                chunk.entity_to_pos[entity_id] = location.location_id

        return chunk

    def _unload_chunk(self, chunk_id):
        # Load the chunk based on its ID.
        existing_chunk = self.db_session.query(grid_db_model.Chunk). \
            filter_by(chunk_id=chunk_id). \
            join(grid_db_model.Grid.chunks). \
            one_or_none()

        # TODO: fill in all information relevant to the chunk.

    def chunk_exists(self, chunk_id):
        existing_chunk = self.db_session.query(grid_db_model.Chunk). \
            filter_by(chunk_id=chunk_id). \
            join(grid_db_model.Grid.chunks). \
            one_or_none()

        return existing_chunk is not None
