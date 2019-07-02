from views import (
    index, 
    login, 
    logout, 
    deposit_form_active, 
    deposit_upload,
    deposit_submit,
    store_buckets,
    store_objects,
    services, 
    services_configs,
    services_actions,
    publish_models,
    deposits
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
    app.router.add_get('/form/active', deposit_form_active)
    app.router.add_post('/form/active', deposit_form_active)
    app.router.add_view('/form/upload', deposit_upload)
    app.router.add_view('/form/submit', deposit_submit)

    # storage routes
    app.router.add_get('/store/buckets', store_buckets)
    app.router.add_post('/store/buckets', store_buckets)
    app.router.add_get('/store/objects', store_objects)
    app.router.add_post('/store/objects', store_objects)

    # publication routes
    app.router.add_get('/publish/models', publish_models)
    app.router.add_post('/publish/models', publish_models)

    # deposit routes
    app.router.add_get('/deposits', deposits)