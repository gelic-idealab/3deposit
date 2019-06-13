from views import (
    index, 
    login, 
    logout, 
    deposit_form_active, 
    deposit_upload,
    minio_buckets, 
    services, 
    services_configs
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
    app.router.add_view('/services/configs', services_configs)

    # deposit form routes
    app.router.add_get('/deposit/forms/active', deposit_form_active)
    app.router.add_post('/deposit/forms/active', deposit_form_active)
    app.router.add_view('/deposit/upload', deposit_upload)

    # object storage routes
    app.router.add_get('/minio/buckets', minio_buckets)
    app.router.add_post('/minio/buckets', minio_buckets)