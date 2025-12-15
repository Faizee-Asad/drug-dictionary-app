from .db import SessionLocal, LocalPrice, DrugDictionary
from typing import List, Optional
from sqlalchemy import func, text
from datetime import datetime, date, timedelta

def get_local_prices_by_name(session, medicine: str, limit: int = 10):
    q = session.query(LocalPrice).filter(LocalPrice.medicine_name.ilike(f"%{medicine}%")).order_by(LocalPrice.updated_at.desc()).limit(limit)
    return q.all()

def add_local_price(session, medicine_name: str, pharmacy_name: str, price: float):
    lp = LocalPrice(medicine_name=medicine_name, pharmacy_name=pharmacy_name, price=price)
    session.add(lp)
    session.commit()
    session.refresh(lp)
    return lp

def add_local_price_with_expiry(session, medicine_name: str, pharmacy_name: str, price: float, 
                                 expiry_date: Optional[str] = None, batch_number: Optional[str] = None):
    """Add local price with expiry date and batch number"""
    exp_date = None
    if expiry_date:
        try:
            exp_date = datetime.strptime(expiry_date, "%Y-%m-%d").date()
        except ValueError:
            pass
    
    lp = LocalPrice(
        medicine_name=medicine_name,
        pharmacy_name=pharmacy_name,
        price=price,
        expiry_date=exp_date,
        batch_number=batch_number
    )
    session.add(lp)
    session.commit()
    session.refresh(lp)
    return lp

def get_expiry_status(expiry_date) -> dict:
    """Calculate expiry status and badge based on expiry date"""
    if not expiry_date:
        return {"status": None, "badge": None, "days_remaining": None}
    
    try:
        if isinstance(expiry_date, str):
            exp_date = datetime.strptime(expiry_date, "%Y-%m-%d").date()
        else:
            exp_date = expiry_date
        
        days_remaining = (exp_date - date.today()).days
        
        if days_remaining < 0:
            return {"status": "expired", "badge": "Expired", "days_remaining": days_remaining}
        elif days_remaining < 60:
            return {"status": "clearance", "badge": "Clearance Stock", "days_remaining": days_remaining}
        elif days_remaining < 90:
            return {"status": "near_expiry", "badge": "Near-Expiry Discount", "days_remaining": days_remaining}
        else:
            return {"status": "valid", "badge": None, "days_remaining": days_remaining}
    except:
        return {"status": None, "badge": None, "days_remaining": None}

def get_near_expiry_deals(session, limit: int = 50):
    """Get medicines expiring within 90 days"""
    ninety_days_from_now = date.today() + timedelta(days=90)
    
    # Filter for items expiring in the future but within 90 days, or already expired (optional, maybe exclude expired)
    # Let's show active deals, so exclude expired
    
    q = session.query(LocalPrice).filter(
        LocalPrice.expiry_date.isnot(None),
        LocalPrice.expiry_date >= date.today(),
        LocalPrice.expiry_date <= ninety_days_from_now
    ).order_by(LocalPrice.expiry_date.asc()).limit(limit)
    
    return q.all()

def search_drug_dictionary(session, query: str, limit: int = 20):
    """
    Search drug dictionary by generic name, brand name, or alternative names.
    Returns list of matching drugs.
    """
    from sqlalchemy import or_
    
    # Search in generic_name, brand_name, and alternative_names
    results = session.query(DrugDictionary).filter(
        or_(
            DrugDictionary.generic_name.ilike(f"%{query}%"),
            DrugDictionary.brand_name.ilike(f"%{query}%"),
            DrugDictionary.alternative_names.ilike(f"%{query}%")
        )
    ).limit(limit).all()
    
    return results

def get_all_drug_names(session):
    """Get all unique medicine names from drug dictionary for fuzzy matching"""
    
    drugs = session.query(DrugDictionary).all()
    names = set()
    
    for drug in drugs:
        if drug.generic_name:
            names.add(drug.generic_name)
        if drug.brand_name:
            names.add(drug.brand_name)
        if drug.alternative_names:
            # Split comma-separated alternatives
            alts = [alt.strip() for alt in drug.alternative_names.split(',')]
            names.update(alts)
    
    return list(names)

# ========== DRUG DICTIONARY CRUD ==========
def create_drug(session, drug_data: dict):
    """Create a new drug entry"""
    
    drug = DrugDictionary(**drug_data)
    session.add(drug)
    session.commit()
    session.refresh(drug)
    return drug

def get_drug_by_id(session, drug_id: int):
    """Get drug by ID"""
    return session.query(DrugDictionary).filter(DrugDictionary.id == drug_id).first()

def update_drug(session, drug_id: int, drug_data: dict):
    """Update drug entry"""
    
    drug = session.query(DrugDictionary).filter(DrugDictionary.id == drug_id).first()
    if not drug:
        return None
    
    for key, value in drug_data.items():
        if value is not None:
            setattr(drug, key, value)
    
    session.commit()
    session.refresh(drug)
    return drug

def delete_drug(session, drug_id: int):
    """Delete drug entry"""
    drug = session.query(DrugDictionary).filter(DrugDictionary.id == drug_id).first()
    if not drug:
        return False
    
    session.delete(drug)
    session.commit()
    return True

def get_all_drugs(session, skip: int = 0, limit: int = 100):
    """Get all drugs with pagination"""
    
    total = session.query(DrugDictionary).count()
    drugs = session.query(DrugDictionary).offset(skip).limit(limit).all()
    return {"total": total, "results": drugs}

def bulk_create_drugs(session, drugs_data: list):
    """Bulk create drug entries"""
    
    created = []
    for drug_data in drugs_data:
        drug = DrugDictionary(**drug_data)
        session.add(drug)
        created.append(drug)
    
    session.commit()
    return created