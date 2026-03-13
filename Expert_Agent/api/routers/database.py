from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import inspect, text
from typing import List, Dict, Any
from data.database import get_db
from api.auth import get_current_user, User

router = APIRouter(prefix="/admin/db", tags=["database"])

@router.get("/tables")
async def get_tables(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """List all tables and their row counts"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    inspector = inspect(db.bind)
    table_names = inspector.get_table_names()
    
    tables_info = []
    for table in table_names:
        # Get row count - Quote table name for safety
        count_query = text(f'SELECT COUNT(*) FROM "{table}"')
        count = db.execute(count_query).scalar()
        
        # Get column info
        columns = inspector.get_columns(table)
        col_list = [{"name": c["name"], "type": str(c["type"])} for c in columns]
        
        tables_info.append({
            "name": table,
            "rows": count,
            "columns": col_list
        })
    
    return {"tables": tables_info}

@router.get("/query/{table_name}")
async def query_table(
    table_name: str, 
    limit: int = 50, 
    offset: int = 0,
    order_by: str = None,
    order_dir: str = "ASC",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Fetch recent records from a specific table with optional sorting"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    inspector = inspect(db.bind)
    valid_tables = inspector.get_table_names()
    if table_name not in valid_tables:
        raise HTTPException(status_code=404, detail="Table not found")
    
    # Validate order_by column
    columns = [c["name"] for c in inspector.get_columns(table_name)]
    if order_by and order_by not in columns:
        order_by = None

    # Construct query string safely
    query_str = f'SELECT * FROM "{table_name}"'
    
    if order_by:
        direction = "DESC" if order_dir.upper() == "DESC" else "ASC"
        query_str += f' ORDER BY "{order_by}" {direction}'
    
    query_str += " LIMIT :limit OFFSET :offset"
    
    result = db.execute(text(query_str), {"limit": limit, "offset": offset})
    rows = [dict(row._mapping) for row in result]
    
    return {
        "table": table_name,
        "count": len(rows),
        "items": rows
    }
