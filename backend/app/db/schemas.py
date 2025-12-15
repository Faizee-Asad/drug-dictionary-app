from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

# ========== COMPARE SCHEMAS ==========
class CompareResponse(BaseModel):
    source_prices: dict  # {source_name: price_or_null}
    local: List[dict]    # List of local pharmacy prices
    cheapest_source: Optional[str] = None  # Name of cheapest source
    cheapest_price: Optional[float] = None  # Lowest price found
    resolved_generic_name: Optional[str] = None  # Resolved generic name
    original_name: Optional[str] = None  # Original name searched

class PrescriptionResponse(BaseModel):
    extracted_medicines: List[str]
    results: List[dict]  # List of compare results for each medicine

class LocalPriceCreate(BaseModel):
    medicine_name: str
    pharmacy_name: str
    price: float
    expiry_date: Optional[str] = None  # Format: YYYY-MM-DD
    batch_number: Optional[str] = None

# ========== DRUG DICTIONARY SCHEMAS ==========
class DrugType(str, Enum):
    ethical = "ethical"
    generic = "generic"
    otc = "otc"

class DrugBase(BaseModel):
    # Identity
    generic_name: Optional[str] = None
    brand_name: Optional[str] = None
    alternative_names: Optional[str] = None  # Comma-separated
    atc_code: Optional[str] = None  # Anatomical Therapeutic Chemical Classification
    
    # Strength & form
    strength: Optional[str] = None
    form: Optional[str] = None
    
    # Classification
    category: Optional[str] = None  # Antibiotic, Analgesic, Antipyretic, etc.
    sub_category: Optional[str] = None  # e.g. Macrolide (for antibiotics)
    drug_type: Optional[DrugType] = None
    
    # Manufacturer & supply
    manufacturer: Optional[str] = None
    country_of_origin: Optional[str] = None
    schedule_type: Optional[str] = None  # H, H1, X, OTC (India-specific)
    unii_code: Optional[str] = None  # Unique Ingredient Identifier
    
    # Medical info (MVP-safe level)
    primary_use: Optional[str] = None  # fever, infection, pain
    secondary_use: Optional[str] = None
    common_dosage: Optional[str] = None  # e.g. 1 tablet twice daily
    prescription_required: Optional[bool] = None
    route_of_administration: Optional[str] = None  # Oral, IV, IM, etc.
    
    # Safety (high-value)
    pregnancy_warning: Optional[str] = None  # safe / caution / not safe
    alcohol_interaction: Optional[str] = None
    common_side_effects: Optional[str] = None
    contraindications: Optional[str] = None  # Conditions where drug should not be used
    
    # Business & ops
    avg_mrp: Optional[float] = None
    storage_condition: Optional[str] = None
    expiry_sensitivity: Optional[str] = None  # high / medium / low
    
    # Regulatory & Compliance
    fda_approval: Optional[bool] = None
    who_essential_medicine: Optional[bool] = None
    
    # Online Pharmacy Specific Fields
    pack_size: Optional[str] = None  # e.g., "10 tablets", "15 ml syrup"
    availability_status: Optional[str] = None  # In Stock, Out of Stock, Discontinued
    last_updated_online: Optional[str] = None  # When scraped data was last updated
    
    # Price Tracking (for comparison)
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    price_currency: Optional[str] = None
    
    # Image & Description
    image_url: Optional[str] = None
    description: Optional[str] = None

class DrugCreate(DrugBase):
    pass

class DrugUpdate(DrugBase):
    pass

class DrugResponse(DrugBase):
    id: int
    
    class Config:
        from_attributes = True

class DrugBulkImport(BaseModel):
    drugs: List[DrugBase]

class DrugSearchResponse(BaseModel):
    total: int
    results: List[DrugResponse]