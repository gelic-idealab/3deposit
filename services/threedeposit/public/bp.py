from flask import Blueprint, request, render_template
from threedeposit.user.gallery import get_gallery
from threedeposit.database import Deposit


public = Blueprint('public', __name__)


@public.route('/')
def index():
    args = {}
    args['collections'] = request.args.getlist('collections')
    args['tags'] = request.args.getlist('tags')
    if args:
        gallery = get_gallery(args)
    else:
        gallery = Deposit.query.all()
    return render_template('public.html', title='3D Gallery', gallery=gallery)
