from .app import db
from flask_sqlalchemy import SQLAlchemy

db.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db/bellybutton.sqlite"
db = SQLAlchemy(app)

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(db.engine, reflect=True)

# Save references to each table
Samples_metadata = Base.classes.sample_metadata
Samples = Base.classes.samples