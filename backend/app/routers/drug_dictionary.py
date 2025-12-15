"""
Drug Dictionary API Router
Provides comprehensive CRUD operations for managing drug database
"""

from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from app.db import db, crud, schemas
from typing import List
import csv
import io
import json

router = APIRouter(prefix="/api/drugs", tags=["Drug Dictionary"])

# IMPORTANT: Specific routes must come BEFORE parameterized routes
# Move specific routes like /stats, /search, /export, /resolve to the top

# Specific routes (non-parameterized)
@router.get("/stats")
def get_drug_stats():
    """Get drug dictionary statistics"""
    session = db.SessionLocal()
    try:
        from app.db.db import DrugDictionary
        from sqlalchemy import func
        
        total = session.query(DrugDictionary).count()
        
        # Count by form
        forms = session.query(
            DrugDictionary.form,
            func.count(DrugDictionary.id)
        ).group_by(DrugDictionary.form).all()
        
        form_stats = {form: count for form, count in forms if form}
        
        # Count by category
        categories = session.query(
            DrugDictionary.category,
            func.count(DrugDictionary.id)
        ).group_by(DrugDictionary.category).all()
        
        category_stats = {category: count for category, count in categories if category}
        
        # Count by drug type
        drug_types = session.query(
            DrugDictionary.drug_type,
            func.count(DrugDictionary.id)
        ).group_by(DrugDictionary.drug_type).all()
        
        drug_type_stats = {drug_type: count for drug_type, count in drug_types if drug_type}
        
        return {
            "total_drugs": total,
            "forms": form_stats,
            "categories": category_stats,
            "drug_types": drug_type_stats,
            "unique_variations": len(crud.get_all_drug_names(session))
        }
    finally:
        session.close()

@router.get("/search", response_model=schemas.DrugSearchResponse)
def search_drugs(q: str = Query(..., min_length=1), limit: int = 20):
    """Search drugs by name"""
    session = db.SessionLocal()
    try:
        results = crud.search_drug_dictionary(session, q, limit)
        return {"total": len(results), "results": results}
    finally:
        session.close()

@router.get("/resolve/{medicine_name}")
def resolve_generic_name(medicine_name: str):
    """Resolve a brand name or alternative name to its generic name"""
    session = db.SessionLocal()
    try:
        # Search for the medicine in drug dictionary
        drug_entries = crud.search_drug_dictionary(session, medicine_name, limit=5)
        
        if not drug_entries:
            return {
                "found": False,
                "original_name": medicine_name,
                "message": "No matching drug found in dictionary"
            }
        
        # Return detailed information about matches
        matches = []
        for drug in drug_entries:
            matches.append({
                "id": drug.id,
                "generic_name": drug.generic_name,
                "brand_name": drug.brand_name,
                "alternative_names": drug.alternative_names,
                "strength": drug.strength,
                "form": drug.form,
                "resolved_generic_name": drug.generic_name or drug.brand_name
            })
        
        return {
            "found": True,
            "original_name": medicine_name,
            "matches": matches,
            "best_match": matches[0]["resolved_generic_name"]
        }
    finally:
        session.close()

@router.get("/export/csv")
def export_drugs_csv():
    """Export all drugs to CSV format"""
    from fastapi.responses import StreamingResponse
    
    session = db.SessionLocal()
    try:
        all_drugs = crud.get_all_drugs(session, skip=0, limit=10000)
        drugs = all_drugs["results"]
        
        # Create CSV
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=[
            "id", "generic_name", "brand_name", "alternative_names", "strength", "form",
            "category", "sub_category", "drug_type", "manufacturer", "country_of_origin",
            "schedule_type", "primary_use", "secondary_use", "common_dosage",
            "prescription_required", "pregnancy_warning", "alcohol_interaction",
            "common_side_effects", "avg_mrp", "storage_condition", "expiry_sensitivity"
        ])
        writer.writeheader()
        
        for drug in drugs:
            writer.writerow({
                "id": drug.id,
                "generic_name": drug.generic_name or "",
                "brand_name": drug.brand_name or "",
                "alternative_names": drug.alternative_names or "",
                "strength": drug.strength or "",
                "form": drug.form or "",
                "category": drug.category or "",
                "sub_category": drug.sub_category or "",
                "drug_type": drug.drug_type or "",
                "manufacturer": drug.manufacturer or "",
                "country_of_origin": drug.country_of_origin or "",
                "schedule_type": drug.schedule_type or "",
                "primary_use": drug.primary_use or "",
                "secondary_use": drug.secondary_use or "",
                "common_dosage": drug.common_dosage or "",
                "prescription_required": drug.prescription_required or "",
                "pregnancy_warning": drug.pregnancy_warning or "",
                "alcohol_interaction": drug.alcohol_interaction or "",
                "common_side_effects": drug.common_side_effects or "",
                "avg_mrp": drug.avg_mrp or "",
                "storage_condition": drug.storage_condition or "",
                "expiry_sensitivity": drug.expiry_sensitivity or ""
            })
        
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=drugs.csv"}
        )
    finally:
        session.close()

@router.post("/bulk-import")
async def bulk_import_drugs(file: UploadFile = File(...)):
    """
    Bulk import drugs from CSV or JSON file
    
    CSV Format: generic_name,brand_name,alternative_names,strength,form
    JSON Format: [{"generic_name": "...", "brand_name": "...", ...}, ...]
    """
    session = db.SessionLocal()
    
    try:
        contents = await file.read()
        
        drugs_data = []
        
        # Handle CSV
        if file.filename.endswith('.csv'):
            csv_data = contents.decode('utf-8')
            reader = csv.DictReader(io.StringIO(csv_data))
            
            for row in reader:
                drugs_data.append({
                    "generic_name": row.get("generic_name") or None,
                    "brand_name": row.get("brand_name") or None,
                    "alternative_names": row.get("alternative_names") or None,
                    "strength": row.get("strength") or None,
                    "form": row.get("form") or None
                })
        
        # Handle JSON
        elif file.filename.endswith('.json'):
            drugs_data = json.loads(contents)
        
        else:
            raise HTTPException(status_code=400, detail="File must be CSV or JSON")
        
        # Bulk create
        created = crud.bulk_create_drugs(session, drugs_data)
        
        return {
            "success": True,
            "imported": len(created),
            "message": f"Successfully imported {len(created)} drugs"
        }
        
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()

# Parameterized routes (must come after specific routes)
@router.get("/", response_model=schemas.DrugSearchResponse)
def list_drugs(skip: int = 0, limit: int = 100):
    """Get all drugs with pagination"""
    session = db.SessionLocal()
    try:
        result = crud.get_all_drugs(session, skip, limit)
        return result
    finally:
        session.close()

@router.post("/", response_model=schemas.DrugResponse)
def create_drug(drug: schemas.DrugCreate):
    """Create a new drug entry"""
    session = db.SessionLocal()
    try:
        result = crud.create_drug(session, drug.dict())
        return result
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()

@router.get("/{drug_id}", response_model=schemas.DrugResponse)
def get_drug(drug_id: int):
    """Get drug by ID"""
    session = db.SessionLocal()
    try:
        drug = crud.get_drug_by_id(session, drug_id)
        if not drug:
            raise HTTPException(status_code=404, detail="Drug not found")
        return drug
    finally:
        session.close()

@router.put("/{drug_id}", response_model=schemas.DrugResponse)
def update_drug(drug_id: int, drug: schemas.DrugUpdate):
    """Update drug entry"""
    session = db.SessionLocal()
    try:
        result = crud.update_drug(session, drug_id, drug.dict(exclude_unset=True))
        if not result:
            raise HTTPException(status_code=404, detail="Drug not found")
        return result
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()

@router.delete("/{drug_id}")
def delete_drug(drug_id: int):
    """Delete drug entry"""
    session = db.SessionLocal()
    try:
        success = crud.delete_drug(session, drug_id)
        if not success:
            raise HTTPException(status_code=404, detail="Drug not found")
        return {"success": True, "message": "Drug deleted successfully"}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()