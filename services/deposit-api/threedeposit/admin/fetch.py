import pandas as pd
import urllib
import os
from flask import flash
from datetime import datetime
from threedeposit.database import db_session, Deposit, Config
from threedeposit.admin.box import push_to_box


def fetch_deposits():
    try:
        last_fetch = Deposit.query.order_by(Deposit.id.desc()).first()
        if last_fetch is None:
            last_fetch_dt = '20180101000000'
        else:
            last_fetch_dt = last_fetch.deposit_submitted
            last_fetch_dt = datetime.strptime(last_fetch_dt.replace('.', ''),
                                              '%m/%d/%Y %I:%M:%S %p')
            last_fetch_dt = datetime.strftime(last_fetch_dt, '%Y%m%d%H%M%S')
        new_deposits = []
        folderid = Config.query.filter_by(key='folderid').value(Config.value)
        formid = Config.query.filter_by(key='formid').value(Config.value)
        key1 = Config.query.filter_by(key='key1').value(Config.value)
        key2 = Config.query.filter_by(key='key2').value(Config.value)
        key3 = Config.query.filter_by(key='key3').value(Config.value)
        form_path = 'https://forms.illinois.edu/export/{}.csv?timestamp={}&key1={}&key2={}&key3={}'\
                    .format(formid, last_fetch_dt, key1, key2, key3)
        deposits = pd.read_csv(form_path)
        deposit_count = len(deposits)

        if not deposits.empty:
                for i in range(deposit_count):
                        deposit_netid = deposits.iloc[i]['Logged in User ID']
                        deposit_submitted = deposits.iloc[i]['Submitted On']
                        deposit_author = deposits.iloc[i]['Q1:Creator(s):']
                        deposit_title = deposits.iloc[i]['Q10:Title:']
                        deposit_description = deposits.iloc[i]['Q11:Description:']
                        deposit_tags = str(deposits.iloc[i]['Q23:Tags:'])
                        deposit_url = deposits.iloc[i]['Q24:Upload model file here:']

                        deposit_file_name = deposit_url.split('/')[-1]
                        deposit_file_url = 'https://forms.illinois.edu/exportFile/{}?key1={}&key2={}&key3={}'\
                                           .format(deposit_file_name, key1, key2, key3)

                        # TODO generate metadata and save

                        # Download the file and save it locally
                        dirname = os.path.dirname(__file__)
                        tmp_path = os.path.join(dirname,
                                                'tmp',
                                                deposit_file_name)
                        with urllib.request.urlopen(deposit_file_url) as response, open(tmp_path, 'wb') as tmp_file:
                                file_data = response.read()
                                tmp_file.write(file_data)
                                tmp_file.close()
                        # upload to Box, return download path
                        box_model_path = push_to_box(folderid, tmp_path)
                        os.remove(tmp_path)
                        # save new deposit data to database
                        new_deposit = Deposit(deposit_netid=deposit_netid,
                                              deposit_submitted=deposit_submitted,
                                              deposit_author=deposit_author,
                                              deposit_title=deposit_title,
                                              deposit_description=deposit_description,
                                              deposit_tags=deposit_tags,
                                              deposit_url=deposit_url,
                                              box_model_path=box_model_path)
                        db_session.add(new_deposit)
                        db_session.commit()
                        new_deposits.append(new_deposit)
                flash('Cache refreshed', category='success')
                return new_deposits
        flash('No new deposits', category='info')
    except Exception as e:
        flash('Failed to refresh cache: {}'.format(e), category='danger')
