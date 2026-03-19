from app.core.database import Base
from app.models.shop import Shop, ShopPartsSettings, ShopAISettings
from app.models.user import User
from app.models.catalog import LaborPrice, LaborAlias, PartPrice, PartsCatalog, Supplier, SupplierLink
from app.models.estimate import Estimate, EstimateItem, AILog
from app.models.market import MarketLaborPrice, MarketPartPrice, RegionMultiplier
from app.models.system import GlobalAISettings, SystemLog, SubscriptionPlan

# Make sure all models are imported here for Alembic to index them correctly
