from fastapi import APIRouter, BackgroundTasks,Request
from .utils import search_key,generate_key,search_url,record_visit
from .database import SessionDep
from fastapi.responses import Response,RedirectResponse,JSONResponse
from .models import URL, URLSCHEMA, CreateCode,Visit,VisitSchema,ShortStats
from sqlalchemy  import func

router = APIRouter(prefix='')



@router.post('/')
async def create_shortened(url_create:CreateCode,db:SessionDep):
    #first we search if it already exists
    url = url_create.url
    code = search_url(url,db)
    if code:
        exists = True
    else:
        exists = False
    
    #we generate a code
    code = generate_key()
    while(search_key(code,db)):
        code = generate_key()
    link = URL(
        original_url = url,
        short_code = code,
        description = url_create.description if url_create.description else None
    )
    db.add(link)
    db.commit()
    db.refresh(link)
    return JSONResponse({
        'detail' : 'this link is already registered' if exists else 'this link has been saved successfully',
        'code' : code
    },status_code=201)


@router.get('/links',response_model=list[URLSCHEMA])
async def get_all_links(db:SessionDep):
    links = db.query(URL).order_by(URL.original_url).all()
    return links

@router.get('/short_codes/',response_model=list[URLSCHEMA])
async def short_codes_for_url(url:str,db:SessionDep):
    links = db.query(URL).filter(URL.original_url == url).all()
    return links
    

@router.get('/{shortened_url}')
async def redirect_url(request:Request ,shortened_url:str,db:SessionDep,background_tasks: BackgroundTasks):
    #fetch the original link
    link = db.query(URL).filter(URL.short_code == shortened_url).first()
    if not link:
        return RedirectResponse('https://www.google.com/')
    background_tasks.add_task(record_visit,link.id,request,db)
    link.clicks+=1
    db.commit()
    return RedirectResponse(link.original_url)

from typing import Union 
@router.get('/stats/shortened/',response_model=ShortStats)
async def get_shortened_url_stats(shortened_url:str,db:SessionDep):
    link = db.query(URL).filter(URL.short_code == shortened_url).first()
    if not link:
        return JSONResponse('this shortened url has not been registered within our system',404)
    
    visits_per_day = (
        db.query(func.date(Visit.timestamp).label("date"), func.count(Visit.id).label("count"))
        .filter(Visit.url_id == link.id)
        .group_by("date")
        .order_by(func.date(Visit.timestamp).asc())
        .all()
    )
    visits_per_day = [{v[0]:v[1]} for v in visits_per_day]
    all_visits = db.query(Visit).filter(Visit.url_id == link.id).all()
    return {
        'visits_per_day' : visits_per_day,
        'all_visits' : all_visits
    }




@router.delete('/delete/{shortened_url}')
async def delete_shortened_url(shortened_url:str, db:SessionDep):
    link = db.query(URL).filter(URL.short_code == shortened_url)
    if not link:
        return JSONResponse('this shortened url has not been registered within our system',404)
    db.delete(link)
    db.commit()
    return JSONResponse(f'the shortened link {shortened_url} has been deleted successfully',200)


@router.delete('/delete/original_url/')
async def deleted_original_url(org_url:str,db:SessionDep):
    db.query(URL).filter(URL.original_url == org_url).delete(synchronize_session=False)
    db.commit()
    return JSONResponse('the shortened links for the url has been deleted successfully',200)

    