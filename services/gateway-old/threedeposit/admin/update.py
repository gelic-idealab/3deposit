from flask import flash
from threedeposit.database import Deposit, db_session
from threedeposit.admin.utils import get_model_details


def update_thumbnail():
    cache = Deposit.query.all()
    for item in cache:
        if item.sketchfab_uid:
            md = get_model_details(item.sketchfab_uid)
            if md['status']['processing'] == 'SUCCEEDED':
                try:
                    update_item = db_session.query(Deposit).get(item.id)
                    update_item.sketchfab_thumbnail = md['thumbnails']['images'][1]['url']
                    db_session.commit()
                    flash('Thumbnail updated for {}'.format(item.sketchfab_uid), category='success')
                except Exception as e:
                    flash('Could not update thumbnail for {}: {}'.format(item.sketchfab_uid, e), category='danger')
