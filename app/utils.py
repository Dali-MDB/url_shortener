from fastapi import Request
import random,string
from sqlalchemy.orm import Session
from app.models import URL,Visit
import geoip2.database

def generate_key(size:int=6):
    zok = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(size))
    return zok


def search_key(key:str,db:Session)->str|None:
    link = db.query(URL).filter(URL.short_code == key).first()
    if link:
        return link.original_url
    return None


def search_url(url:str,db:Session)->str|None:
    link = db.query(URL).filter(URL.original_url == url).first()
    if link:
        return link.short_code
    return None

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GEOIP_DB = os.path.join(BASE_DIR, "GeoLite2-City.mmdb")

def get_location(ip:str):
    with geoip2.database.Reader(GEOIP_DB) as reader:
        try:
            #ip = '128.101.101.101'  for test only
            response = reader.city(ip)
            return response.country.name , response.city.name
        except:
            return {"country": None, "city": None}

def record_visit(url_id:int,request:Request,db:Session):
    ip = request.headers.get("x-forwarded-for", request.client.host)   # client IP
    country, city = get_location(ip)
    visit = Visit(
        url_id = url_id,
        ip = ip,
        referrer = request.headers.get("referer"), # site where they came from
        agent = request.headers.get("user-agent"), # browser/device
        country = country,
        city = city
    )
    db.add(visit)
    db.commit()