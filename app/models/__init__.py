from app.core.database import Base
from app.models.shop import Shop
from app.models.user import User
from app.models.catalog import LaborPrice, LaborAlias, PartPrice
from app.models.estimate import Estimate, EstimateItem, AILog

# Make sure all models are imported here for Alembic to index them correctly
