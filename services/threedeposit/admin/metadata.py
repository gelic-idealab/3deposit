import json
from threedeposit.database import Deposit


data = {
    "deposit_id": "",
    "submitted": "",
    "netid": "",
    "title": "",
    "sketchfab_uid": "",
    "box_file": ""
}


def generate_metadata(id):
    deposit = Deposit.query.get(id)
    data['deposit_id'] = deposit.id
    data['submitted'] = deposit.deposit_submitted
    data['netid'] = deposit.deposit_netid
    data['title'] = deposit.deposit_title
    data['sketchfab_uid'] = deposit.sketchfab_uid
    data['box_file'] = deposit.box_model_path

    json_data = json.dumps(data)

    with open('threedeposit/tmp/{}.json'.format(deposit.id), 'w') as f:
        f.write(json_data)

    return f
