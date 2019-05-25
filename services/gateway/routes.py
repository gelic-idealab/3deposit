from views import index, login, logout, activeDepositForm


def setup_routes(app):
    # user routes
    app.router.add_get('/', index, name='index')
    app.router.add_get('/login', login, name='login')
    app.router.add_post('/login', login, name='login')
    app.router.add_get('/logout', logout, name='logout')

    # deposit form routes
    app.router.add_get('/frontend/forms/active', activeDepositForm)
    app.router.add_post('/frontend/forms/active', activeDepositForm)