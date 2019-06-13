from views import (
    index, 
    login, 
    logout, 
    deposit_form_active, 
    deposit_upload,
    store_buckets,
    store_objects,
    services, 
    services_configs,
    publish
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
    app.router.add_get('/services', services)
    app.router.add_get('/services/configs', services_configs)
    app.router.add_post('/services/configs', services_configs)


    # deposit form routes
    app.router.add_get('/deposit/forms/active', deposit_form_active)
    app.router.add_post('/deposit/forms/active', deposit_form_active)
    app.router.add_view('/deposit/upload', deposit_upload)

    # storage routes
    app.router.add_get('/store/buckets', store_buckets)
    app.router.add_post('/store/buckets', store_buckets)
    app.router.add_get('/store/objects', store_objects)
    app.router.add_post('/store/objects', store_objects)

    # publication routes
    app.router.add_get('/publish', publish)
    app.router.add_post('/publish', publish)