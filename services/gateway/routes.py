from views import (
    index,
    login,
    logout,
    deposit_form,
    deposit_upload,
    deposit_submit,
    store_buckets,
    store_objects,
    services,
    services_configs,
    services_actions,
    publications,
    deposits,
    metadata
)


def setup_routes(app):

    """
    Frontend routes

    auth routes: manage authentication for dashboard views
    api routes:  serve resources from service endpoints
    """

    # auth routes
    app.router.add_get('/', index, name='index')
    app.router.add_get('/login', login, name='login')
    app.router.add_post('/login', login, name='login')
    app.router.add_get('/logout', logout, name='logout')

    # service config routes
    app.router.add_view('/services', services)
    app.router.add_view('/services/configs', services_configs)
    app.router.add_view('/services/actions', services_actions)


    # form routes
    app.router.add_get('/form', deposit_form)
    app.router.add_post('/form', deposit_form)
    app.router.add_view('/form/upload', deposit_upload)
    app.router.add_view('/form/submit', deposit_submit)

    # storage routes
    app.router.add_get('/store/buckets', store_buckets)
    app.router.add_post('/store/buckets', store_buckets)
    app.router.add_get('/store/objects', store_objects)
    app.router.add_post('/store/objects', store_objects)

    # publication routes
    app.router.add_get('/publications', publications)
    app.router.add_post('/publications', publications)

    # deposit routes
    app.router.add_get('/deposits', deposits)

    # metadata routes
    app.router.add_view('/metadata', metadata)
