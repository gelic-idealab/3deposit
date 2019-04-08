from flask import Blueprint, render_template, request
from threedeposit.user.gallery import get_gallery, get_facets
from threedeposit.database import Deposit


user = Blueprint('user', __name__, template_folder='user_templates')


@user.route('/gallery')
def gallery():
    args = {}
    args['collections'] = request.args.getlist('collections')
    args['tags'] = request.args.getlist('tags')
    if args:
        gallery = get_gallery(args)
        public_args = []
        if args['collections']:
            public_args.extend(['collection={}&'.format(arg) for arg in args['collections']])
        if args['tags']:
            public_args.extend(['tags={}&'.format(arg) for arg in args['tags']])
        public_args = ''.join(public_args)[:-1]
    else:
        gallery = Deposit.query.filter_by(sketchfab_uid != 'None').all()
    facets = get_facets(gallery)

    return render_template('gallery.html', title='Gallery', gallery=gallery, facets=facets, public_args=public_args)
