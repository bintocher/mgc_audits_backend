from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.crud import dictionary as crud_dictionary
from app.schemas.dictionary import (
    DictionaryTypeCreate,
    DictionaryTypeUpdate,
    DictionaryTypeResponse,
    DictionaryCreate,
    DictionaryUpdate,
    DictionaryResponse
)


router = APIRouter(prefix="/dictionaries", tags=["dictionaries"])


@router.get("/types", response_model=List[DictionaryTypeResponse])
async def get_dictionary_types(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_session)
):
    """
    Получить список типов справочников с пагинацией.
    
    Args:
        skip: Количество записей для пропуска
        limit: Максимальное количество записей для возврата (1-100)
        db: Сессия базы данных
    
    Returns:
        Список типов справочников
    """
    dictionary_types = await crud_dictionary.get_dictionary_types(
        db=db,
        skip=skip,
        limit=limit
    )
    return dictionary_types


@router.post("/types", response_model=DictionaryTypeResponse, status_code=status.HTTP_201_CREATED)
async def create_dictionary_type(
    dictionary_type: DictionaryTypeCreate,
    db: AsyncSession = Depends(get_session)
):
    """
    Создать новый тип справочника.
    
    Args:
        dictionary_type: Данные для создания типа справочника
        db: Сессия базы данных
    
    Returns:
        Созданный тип справочника
    
    Raises:
        HTTPException: Если тип справочника с таким кодом уже существует
    """
    existing_type = await crud_dictionary.get_dictionary_type_by_code(db, dictionary_type.code)
    if existing_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dictionary type with this code already exists"
        )
    
    return await crud_dictionary.create_dictionary_type(db=db, dictionary_type=dictionary_type)


@router.get("/types/{dictionary_type_id}", response_model=DictionaryTypeResponse)
async def get_dictionary_type(
    dictionary_type_id: UUID,
    db: AsyncSession = Depends(get_session)
):
    """
    Получить информацию о типе справочника по ID.
    
    Args:
        dictionary_type_id: UUID типа справочника
        db: Сессия базы данных
    
    Returns:
        Информация о типе справочника
    
    Raises:
        HTTPException: Если тип справочника не найден
    """
    dictionary_type = await crud_dictionary.get_dictionary_type(db, dictionary_type_id)
    if not dictionary_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dictionary type not found"
        )
    return dictionary_type


@router.put("/types/{dictionary_type_id}", response_model=DictionaryTypeResponse)
async def update_dictionary_type(
    dictionary_type_id: UUID,
    dictionary_type_update: DictionaryTypeUpdate,
    db: AsyncSession = Depends(get_session)
):
    """
    Обновить информацию о типе справочника.
    
    Args:
        dictionary_type_id: UUID типа справочника
        dictionary_type_update: Данные для обновления
        db: Сессия базы данных
    
    Returns:
        Обновленная информация о типе справочника
    
    Raises:
        HTTPException: Если тип справочника не найден
    """
    updated_type = await crud_dictionary.update_dictionary_type(db, dictionary_type_id, dictionary_type_update)
    if not updated_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dictionary type not found"
        )
    return updated_type


@router.delete("/types/{dictionary_type_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dictionary_type(
    dictionary_type_id: UUID,
    db: AsyncSession = Depends(get_session)
):
    """
    Деактивировать тип справочника (мягкое удаление).
    
    Args:
        dictionary_type_id: UUID типа справочника
        db: Сессия базы данных
    
    Raises:
        HTTPException: Если тип справочника не найден
    """
    success = await crud_dictionary.delete_dictionary_type(db, dictionary_type_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dictionary type not found"
        )


@router.get("/", response_model=List[DictionaryResponse])
async def get_dictionaries(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    dictionary_type_id: Optional[UUID] = None,
    enterprise_id: Optional[UUID] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_session)
):
    """
    Получить список элементов справочников с пагинацией и фильтрацией.
    
    Args:
        skip: Количество записей для пропуска
        limit: Максимальное количество записей для возврата (1-100)
        dictionary_type_id: Фильтр по типу справочника
        enterprise_id: Фильтр по предприятию
        is_active: Фильтр по статусу активности
        db: Сессия базы данных
    
    Returns:
        Список элементов справочников
    """
    dictionaries = await crud_dictionary.get_dictionaries(
        db=db,
        skip=skip,
        limit=limit,
        dictionary_type_id=dictionary_type_id,
        enterprise_id=enterprise_id,
        is_active=is_active
    )
    return dictionaries


@router.post("/", response_model=DictionaryResponse, status_code=status.HTTP_201_CREATED)
async def create_dictionary(
    dictionary: DictionaryCreate,
    db: AsyncSession = Depends(get_session)
):
    """
    Создать новый элемент справочника.
    
    Args:
        dictionary: Данные для создания элемента справочника
        db: Сессия базы данных
    
    Returns:
        Созданный элемент справочника
    
    Raises:
        HTTPException: Если тип справочника не найден
    """
    dictionary_type = await crud_dictionary.get_dictionary_type(db, dictionary.dictionary_type_id)
    if not dictionary_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dictionary type not found"
        )
    
    return await crud_dictionary.create_dictionary(db=db, dictionary=dictionary)


@router.get("/{dictionary_id}", response_model=DictionaryResponse)
async def get_dictionary(
    dictionary_id: UUID,
    db: AsyncSession = Depends(get_session)
):
    """
    Получить информацию об элементе справочника по ID.
    
    Args:
        dictionary_id: UUID элемента справочника
        db: Сессия базы данных
    
    Returns:
        Информация об элементе справочника
    
    Raises:
        HTTPException: Если элемент справочника не найден
    """
    dictionary = await crud_dictionary.get_dictionary(db, dictionary_id)
    if not dictionary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dictionary not found"
        )
    return dictionary


@router.put("/{dictionary_id}", response_model=DictionaryResponse)
async def update_dictionary(
    dictionary_id: UUID,
    dictionary_update: DictionaryUpdate,
    db: AsyncSession = Depends(get_session)
):
    """
    Обновить информацию об элементе справочника.
    
    Args:
        dictionary_id: UUID элемента справочника
        dictionary_update: Данные для обновления
        db: Сессия базы данных
    
    Returns:
        Обновленная информация об элементе справочника
    
    Raises:
        HTTPException: Если элемент справочника не найден
    """
    updated_dictionary = await crud_dictionary.update_dictionary(db, dictionary_id, dictionary_update)
    if not updated_dictionary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dictionary not found"
        )
    return updated_dictionary


@router.delete("/{dictionary_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dictionary(
    dictionary_id: UUID,
    db: AsyncSession = Depends(get_session)
):
    """
    Деактивировать элемент справочника (мягкое удаление).
    
    Args:
        dictionary_id: UUID элемента справочника
        db: Сессия базы данных
    
    Raises:
        HTTPException: Если элемент справочника не найден
    """
    success = await crud_dictionary.delete_dictionary(db, dictionary_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dictionary not found"
        )

