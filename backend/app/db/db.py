import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Date, Boolean, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./drug_dictionary.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class LocalPrice(Base):
    __tablename__ = "local_prices"
    id = Column(Integer, primary_key=True, index=True)
    medicine_name = Column(String, index=True)
    pharmacy_name = Column(String)
    price = Column(Float)
    expiry_date = Column(Date, nullable=True)  # New: expiry date
    batch_number = Column(String, nullable=True)  # New: batch number
    updated_at = Column(DateTime, default=datetime.utcnow)

class DrugDictionary(Base):
    __tablename__ = "drug_dictionary"
    id = Column(Integer, primary_key=True, index=True)
    # Identity
    generic_name = Column(String, index=True, nullable=True)
    brand_name = Column(String, index=True, nullable=True)
    alternative_names = Column(String, nullable=True)  # Comma-separated alternatives
    
    # Strength & form
    strength = Column(String, nullable=True)
    form = Column(String, nullable=True)  # Tablet, Capsule, Syrup, etc.
    
    # Classification
    category = Column(String(150), nullable=True)  # Antibiotic, Analgesic, Antipyretic, etc.
    sub_category = Column(String(150), nullable=True)  # e.g. Macrolide (for antibiotics)
    drug_type = Column(Enum('ethical', 'generic', 'otc', name='drug_type_enum'), nullable=True, default='ethical')
    atc_code = Column(String(10), nullable=True)  # Anatomical Therapeutic Chemical Classification
    
    # Manufacturer & supply
    manufacturer = Column(String(255), nullable=True)
    country_of_origin = Column(String(100), nullable=True)
    schedule_type = Column(String(50), nullable=True)  # H, H1, X, OTC (India-specific)
    unii_code = Column(String(20), nullable=True)  # Unique Ingredient Identifier
    
    # Medical info (MVP-safe level)
    primary_use = Column(String, nullable=True)  # fever, infection, pain
    secondary_use = Column(String, nullable=True)
    common_dosage = Column(String(255), nullable=True)  # e.g. 1 tablet twice daily
    prescription_required = Column(Boolean, nullable=True, default=True)
    route_of_administration = Column(String(100), nullable=True)  # Oral, IV, IM, etc.
    
    # Safety (high-value)
    pregnancy_warning = Column(String(50), nullable=True)  # safe / caution / not safe
    alcohol_interaction = Column(String(50), nullable=True)
    common_side_effects = Column(String, nullable=True)
    contraindications = Column(String, nullable=True)  # Conditions where drug should not be used
    
    # Business & ops
    avg_mrp = Column(Float, nullable=True)
    storage_condition = Column(String(255), nullable=True)
    expiry_sensitivity = Column(String(50), nullable=True)  # high / medium / low
    
    # Regulatory & Compliance
    fda_approval = Column(Boolean, nullable=True, default=False)
    who_essential_medicine = Column(Boolean, nullable=True, default=False)
    
    # Online Pharmacy Specific Fields
    pack_size = Column(String(50), nullable=True)  # e.g., "10 tablets", "15 ml syrup"
    availability_status = Column(String(20), nullable=True)  # In Stock, Out of Stock, Discontinued
    last_updated_online = Column(DateTime, nullable=True)  # When scraped data was last updated
    
    # Price Tracking (for comparison)
    min_price = Column(Float, nullable=True)
    max_price = Column(Float, nullable=True)
    price_currency = Column(String(3), nullable=True, default='INR')
    
    # Image & Description
    image_url = Column(String, nullable=True)
    description = Column(String, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)

def update_schema():
    """Update existing database schema with new columns"""
    # This is a simplified approach for MVP
    # In production, use proper migration tools like Alembic
    try:
        # Try to add new columns if they don't exist
        # This won't work for SQLite, so we'll need to recreate tables
        pass
    except Exception as e:
        print(f"Schema update skipped: {e}")