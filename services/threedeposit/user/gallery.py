from sqlalchemy import select, or_
from threedeposit.database import Deposit, db_session


def get_gallery(facets):
    query = select([Deposit]).where(Deposit.sketchfab_uid != 'None')
    conditions = []
    if facets['collections']:
        conditions.append(Deposit.deposit_collection_id.in_(facets['collections']))
    if facets['tags']:
        for tag in facets['tags']:
            conditions.append(Deposit.deposit_tags.contains(tag))
    query = query.where(or_(*conditions))
    gallery = [item for item in db_session.execute(query)]
    return gallery


def get_facets(gallery):
    facets = {}
    collection_ids, tags = [], []
    for item in gallery:
        if item.deposit_collection_id:
            collection_ids.append(item.deposit_collection_id)
        if item.deposit_tags:
            for tag in item.deposit_tags.split():
                tags.append(tag.replace(',', ''))
    facets['collections'] = collection_ids
    facets['tags'] = tags
    return facets
