from typing import Optional

from fastapi import APIRouter, HTTPException, Form, File, UploadFile

from src.models import ContextReference
from src.services import storage_service

router = APIRouter()


@router.post('/', response_model=ContextReference)
async def add_context_reference_route(
        user_id: str = Form(...),
        context_template_uid: str = Form(...),
        name: str = Form(...),
        scenario_schema_id: str = Form(None),
        reference_type: str = Form(...),  # You may want to validate this to be either 'string' or 'file'
        text_data: Optional[str] = Form(None),
        file_data: Optional[UploadFile] = File(None)
) -> ContextReference:
    try:
        if text_data and file_data:
            raise HTTPException(status_code=400, detail="Either text_data or file_data must be provided, but not both.")

        if not text_data and not file_data:
            raise HTTPException(status_code=400, detail="Either text_data or file_data must be provided.")

        data = text_data if text_data else await file_data.read()
        content_type = file_data.content_type if file_data else 'text/plain'

        return storage_service.add_context_reference(
            user_id,
            context_template_uid,
            name,
            scenario_schema_id,
            reference_type,
            content_type,
            data,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete('/{user_id}/{context_reference_uid}')
async def delete_context_reference_route(user_id: str, context_reference_uid: str):
    try:
        storage_service.delete_context_reference(user_id, context_reference_uid)
        return {'success': True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)
