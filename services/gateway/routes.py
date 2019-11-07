from views import (
    index,
    login,
    logout,
    signup,
    success,
    current_user,
    users,
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
    metadata_keys,
    gallery,
    service_logs
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
    app.router.add_get('/api/user', current_user, name='user')
    app.router.add_view('/api/users', users, name='users')
    app.router.add_view('/api/signup', signup, name='signup')

    # service routes
    app.router.add_view('/api/services', services)
    app.router.add_view('/api/services/configs', services_configs)
    app.router.add_view('/api/services/actions', services_actions)
    app.router.add_get('/api/services/logs', service_logs)

    # form routes
    app.router.add_get('/api/form', deposit_form)
    app.router.add_post('/api/form', deposit_form)
    app.router.add_view('/api/form/upload', deposit_upload)
    app.router.add_view('/api/form/submit', deposit_submit)
    app.router.add_view('/api/form/success', success, name='success')

    # storage routes
    app.router.add_get('/api/store/buckets', store_buckets)
    app.router.add_post('/api/store/buckets', store_buckets)
    app.router.add_get('/api/store/objects', store_objects)
    app.router.add_post('/api/store/objects', store_objects)
    app.router.add_delete('/api/store/objects', store_objects)

    # publication routes
    app.router.add_get('/api/publications', publications)
    app.router.add_post('/api/publications', publications)
    app.router.add_delete('/api/publications', publications)

    # deposit routes
    app.router.add_get('/api/deposits', deposits)

    # metadata routes
    app.router.add_view('/api/metadata', metadata)
    app.router.add_view('/api/metadata/keys', metadata_keys)

    # gallery routes
    app.router.add_get('/api/gallery', gallery)


