from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy import event
from sqlalchemy.engine import Engine

bcrypt = Bcrypt()
db = SQLAlchemy()

# created_at columns are db.DateTime (no tz awareness), so the wall-clock
# value Postgres stores on INSERT depends entirely on the session's
# TimeZone setting at that moment. Forcing every connection to UTC makes
# func.now() always store a true UTC instant, so it can be serialized
# with a trustworthy 'Z' suffix instead of a timezone-ambiguous string
# (which browsers can parse inconsistently - or as the wrong instant
# entirely - breaking "sort by created_at" across environments/viewers).
@event.listens_for(Engine, "connect")
def _set_utc_timezone(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("SET TIME ZONE 'UTC'")
    cursor.close()
    # SET TIME ZONE is transactional - without committing here, SQLAlchemy's
    # first ROLLBACK on this connection (which it issues routinely, e.g. to
    # reset state before reuse) silently reverts it to the server default.
    dbapi_connection.commit()