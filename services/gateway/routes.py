from views import index, login, logout, activeDepositForm


def setup_routes(app):
    app.router.add_get('/', index, name='index')
    app.router.add_get('/login', login, name='login')
    app.router.add_post('/login', login, name='login')
    app.router.add_get('/logout', logout, name='logout')
    app.router.add_get('/activeDepositForm', activeDepositForm, name='activeDepositForm')
    app.router.add_post('/activeDepositForm', activeDepositForm, name='activeDepositForm')