"""
Template routes for Threadr
Handles template-related endpoints
"""

from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

@router.get("/templates")
async def get_templates():
    """Get all available templates"""
    # Stub implementation - returns mock data
    return {
        "templates": [
            {
                "id": "1",
                "name": "Product Launch",
                "description": "Perfect for announcing new products",
                "category": "marketing",
                "isPro": False
            },
            {
                "id": "2", 
                "name": "Thread Storm",
                "description": "Create viral thread storms",
                "category": "engagement",
                "isPro": True
            }
        ],
        "categories": ["marketing", "engagement", "educational"]
    }

@router.get("/templates/{template_id}")
async def get_template(template_id: str):
    """Get a specific template"""
    # Stub implementation
    return {
        "id": template_id,
        "name": "Sample Template",
        "description": "Template description",
        "category": "general",
        "isPro": False
    }