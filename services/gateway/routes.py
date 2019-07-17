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
    metadata,
    metadata_keys
)


def setup_routes(app):

    """
    Frontend routes

    auth routes: manage authentication for dashboard views
    api routes:  serve resources from service endpoints
    """

    # auth routes
    app.router.add_get('/api/', index, name='index')
    app.router.add_get('/api/login', login, name='login')
    app.router.add_post('/api/login', login, name='login')
    app.router.add_get('/api/logout', logout, name='logout')

    # service config routes
    app.router.add_view('/api/services', services)
    app.router.add_view('/api/services/configs', services_configs)
    app.router.add_view('/api/services/actions', services_actions)

    # form routes
    app.router.add_get('/api/form', deposit_form)
    app.router.add_post('/api/form', deposit_form)
    app.router.add_view('/api/form/upload', deposit_upload)
    app.router.add_view('/api/form/submit', deposit_submit)

    # storage routes
    app.router.add_get('/api/store/buckets', store_buckets)
    app.router.add_post('/api/store/buckets', store_buckets)
    app.router.add_get('/api/store/objects', store_objects)
    app.router.add_post('/api/store/objects', store_objects)

    # publication routes
    app.router.add_get('/api/publications', publications)
    app.router.add_post('/api/publications', publications)

    # deposit routes
    app.router.add_get('/api/deposits', deposits)

    # metadata routes
    app.router.add_view('/api/metadata', metadata)
    app.router.add_view('/api/metadata/keys', metadata_keys)
