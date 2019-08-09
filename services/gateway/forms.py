import db
from security import check_password_hash


async def validate_login_form(conn, form):

    username = form['username']
    password = form['password']

    if not username:
        return 'username is required'
    if not password:
        return 'password is required'

    user = await db.get_user_by_name(conn, username)

    if not user:
        return 'Invalid username'
    if not check_password_hash(password, user['password_hash']):
        return 'Invalid password'
    else:
        return None

    return 'error'

async def validate_new_user_form(conn, form):

    username = form['username']
    email = form['email']
    password = form['password']
    confirm = form['confirm']

    if not username:
        return 'username is required'
    if not email:
        return 'email is required'
    if not password:
        return 'password is required'
    if not confirm:
        return 'please confirm password'
    if password != confirm:
        return 'passwords do not match'

    user = await db.get_user_by_name(conn, username)
    if user:
        return 'username not available'

    else:
        return None

    return 'error'