from fastapi import APIRouter, Depends, UploadFile
from fastapi.responses import JSONResponse
from main import fastapi_users
from sqlalchemy import select, insert, update
from sqlalchemy.ext.asyncio import AsyncSession
from auth.database import get_async_session
from ML_model.ml_model import model_predict
from ML_model.models import mushroom
from ML_model.schemas import Mushroom
from fastapi_cache.decorator import cache
from catboost import CatboostError
from typing import List
import pandas as pd
import json
import io

router = APIRouter(
    prefix='/model',
    tags=['use model']
)

current_user = fastapi_users.current_user()


@router.get('/prediction')
@cache(expire=15)
async def get_prediction(user=Depends(current_user), session: AsyncSession = Depends(get_async_session)):
    '''Function for model prediction'''
    query = select(mushroom).where(mushroom.c.id == user.id)
    result = await session.execute(query)
    df = pd.DataFrame(result.one()[1])
    try:
       pred = model_predict(df)
    except CatboostError as e:
        return JSONResponse(status_code=400, content={'message': 'Error in prediction'})
    df['prediction'] = pred
    return json.loads(df.to_json(orient='records'))


@router.post('/add_data')
async def add_data(data: List[Mushroom], user=Depends(current_user), session: AsyncSession = Depends(get_async_session)):
    '''Function for saving features for a mushroom'''
    df = pd.DataFrame([vars(d) for d in data])
    df.rename(columns={'cap_shape': 'cap-shape',
                       'cap_surface': 'cap-surface',
                       'cap_color': 'cap-color',
                       'gill_attachment': 'gill-attachment',
                       'gill_spacing': 'gill-spacing',
                       'gill_size': 'gill-size',
                       'gill_color': 'gill-color',
                       'stalk_shape': 'stalk-shape',
                       'stalk_root': 'stalk-root',
                       'stalk_surface_above_ring': 'stalk-surface-above-ring',
                       'stalk_surface_below_ring': 'stalk-surface-below-ring',
                       'stalk_color_above_ring': 'stalk-color-above-ring',
                       'stalk_color_below_ring': 'stalk-color-below-ring',
                       'veil_type': 'veil-type',
                       'veil_color': 'veil-color',
                       'ring_number': 'ring-number',
                       'ring_type': 'ring-type',
                       'spore_print_color': 'spore-print-color'}, inplace=True)
    result = await session.execute(select(mushroom).where(mushroom.c.id == user.id))
    if len(result.all()) == 0:
        await session.execute(insert(mushroom).values(id=user.id, Info=json.loads(df.to_json(orient='records'))))
        await session.commit()
    else:
        stmt = update(mushroom).where(mushroom.c.id == user.id).values(Info=json.loads(df.to_json(orient='records')))
        await session.execute(stmt)
        await session.commit()
    return {"status": "success"}


@router.post('/add_csv')
async def add_csv(file: UploadFile, user=Depends(current_user), session: AsyncSession = Depends(get_async_session)):
    '''Function for saving features for several mushroom'''
    content = file.file.read()
    buffer = io.BytesIO(content)
    df = pd.read_csv(buffer)
    columns_list = ['cap-shape', 'cap-surface', 'cap-color', 'bruises', 'odor',
       'gill-attachment', 'gill-spacing', 'gill-size', 'gill-color',
       'stalk-shape', 'stalk-root', 'stalk-surface-above-ring',
       'stalk-surface-below-ring', 'stalk-color-above-ring',
       'stalk-color-below-ring', 'veil-type', 'veil-color', 'ring-number',
       'ring-type', 'spore-print-color', 'population', 'habitat']
    if list(df.columns) == columns_list:
        result = await session.execute(select(mushroom).where(mushroom.c.id == user.id))
        if len(result.all()) == 0:
           await session.execute(insert(mushroom).values(id=user.id, Info=json.loads(df.to_json(orient='records'))))
           await session.commit()
        else:
           stmt = update(mushroom).where(mushroom.c.id == user.id).values(Info=json.loads(df.to_json(orient='records')))
           await session.execute(stmt)
           await session.commit()
        return {"status": "success"}
    else:
        return JSONResponse(status_code=400, content={'message': 'Invalid columns names'})
