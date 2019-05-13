from flask import Blueprint, render_template, flash, request, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from threedeposit.database import User, Deposit, db_session, Config
from threedeposit.admin.config import post_configs
from threedeposit.admin.upload import upload_models
from threedeposit.admin.utils import list_my_models, get_model_details, get_collections, get_collection
from threedeposit.admin.delete import delete_models
from threedeposit.admin.fetch import fetch_deposits
from threedeposit.admin.update import update_thumbnail
from threedeposit.admin.form import LoginForm


admin = Blueprint('admin', __name__, template_folder='admin_templates')


@admin.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', category='danger')
            return redirect(url_for('admin.login'))
        login_user(user)
        flash('Successfully logged in {}'.format(user.username),
              category='success')
        next_url = request.args.get('next')
        return redirect(next_url or url_for('admin.home'))
    return render_template('login.html', title='Sign In', form=form)


@admin.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('admin.login'))


@admin.route('/')
@login_required
def home():
    return render_template('home.html', title='Admin Home')


# refresh the deposit cache
@admin.route('/refresh_deposit_cache')
@login_required
def refresh_deposit_cache():
    fetch_deposits()
    return redirect(url_for('admin.deposits'))


# refresh thumbnails
@admin.route('/refresh_deposit_thumbnails')
@login_required
def refresh_deposit_thumbnails():
    update_thumbnail()
    return redirect(url_for('admin.deposits'))


@admin.route('/update_collection', methods=['POST'])
@login_required
def update_collection():
    uid = request.form.get('uid')
    cid = request.form.get('cid')
    try:
        update_item = db_session.query(Deposit).filter_by(sketchfab_uid=uid)
        update_item.deposit_collection_id = cid
        db_session.commit()
        flash('Added {} to collection: {}'.format(uid, cid),
              category='success')
    except Exception as e:
        flash('Could not add {} to collection {}: '.format(uid, cid, e),
              category='danger')
    return redirect(url_for('admin.model_details', uid=uid))


@admin.route('/uploads/collections/<collectionid>')
@login_required
def collection(collectionid):
    collection = get_collection(collectionid)
    return render_template('collection.html',
                           title=collection['name'],
                           collection=collection)


@admin.route('/deposits')
@login_required
def deposits():
    cache = Deposit.query.all()
    columns = Deposit.__table__.columns.keys()
    return render_template('deposits.html',
                           title='Deposits',
                           cache=cache,
                           columns=columns)


@admin.route('/upload')
@login_required
def upload():
    upload_models()
    return redirect(url_for('admin.deposits'))


@admin.route('/delete', methods=['POST'])
@login_required
def delete():
    scope = request.form['scope']
    delete_models(scope)
    return redirect(url_for('admin.uploads'))


@admin.route('/uploads')
@login_required
def uploads():
    models = list_my_models()
    collections = get_collections()
    return render_template('uploads.html',
                           title='Uploads',
                           models=models,
                           collections=collections)


@admin.route('/models/<uid>')
@login_required
def model_details(uid):
    model = get_model_details(uid)
    return render_template('details.html',
                           title=model['name'],
                           model=model)


@admin.route('/config', methods=['GET', 'POST'])
@login_required
def config():
    if request.method == 'POST':
        post_configs()
    folderid = Config.query.filter_by(key='folderid').value(Config.value)
    boxclientid = Config.query.filter_by(key='boxclientid').value(Config.value)
    boxclientsecret = Config.query.filter_by(key='boxclientsecret').value(Config.value)
    boxaccesstoken = Config.query.filter_by(key='boxaccesstoken').value(Config.value)
    boxrefreshtoken = Config.query.filter_by(key='boxrefreshtoken').value(Config.value)
    token = Config.query.filter_by(key='token').value(Config.value)
    collectionid = Config.query.filter_by(key='collectionid').value(Config.value)
    formid = Config.query.filter_by(key='formid').value(Config.value)
    key1 = Config.query.filter_by(key='key1').value(Config.value)
    key2 = Config.query.filter_by(key='key2').value(Config.value)
    key3 = Config.query.filter_by(key='key3').value(Config.value)
    return render_template('config.html',
                           title='Configure',
                           folderid=folderid,
                           boxclientid=boxclientid,
                           boxclientsecret=boxclientsecret,
                           boxaccesstoken=boxaccesstoken,
                           boxrefreshtoken=boxrefreshtoken,
                           token=token,
                           collectionid=collectionid,
                           formid=formid,
                           key1=key1,
                           key2=key2,
                           key3=key3)
