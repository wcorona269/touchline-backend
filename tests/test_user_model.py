from app.models.user_model import User


def test_register_user_success(app):
    success, user = User.register_user('validuser', 'password123')
    assert success is True
    assert user.username == 'validuser'
    assert user.check_password('password123')


def test_register_user_duplicate_username_fails(app, make_user):
    make_user('duplicateuser')
    success, message = User.register_user('duplicateuser', 'password123')
    assert success is False
    assert 'already taken' in message


def test_register_user_short_password_fails(app):
    success, message = User.register_user('shortpassuser', 'short')
    assert success is False
    assert 'at least 8 characters' in message


def test_register_user_short_username_fails(app):
    success, message = User.register_user('abc', 'password123')
    assert success is False
    assert 'at least 4 characters' in message


def test_register_user_invalid_username_characters_fails(app):
    success, message = User.register_user('invalid user!', 'password123')
    assert success is False


def test_login_user_wrong_password_fails(app, make_user):
    make_user('loginuser', 'correctpassword')
    success, message = User.login_user('loginuser', 'wrongpassword')
    assert success is False
    assert message == 'Incorrect password'


def test_login_user_correct_password_succeeds(app, make_user):
    make_user('loginuser2', 'correctpassword')
    success, data = User.login_user('loginuser2', 'correctpassword')
    assert success is True
    assert data['username'] == 'loginuser2'


def test_get_user_info_not_found_returns_tuple(app):
    result, data = User.get_user_info('doesnotexist')
    assert result is False
    assert data is None


def test_get_user_info_paginates_posts(app, make_user):
    from app.models.db import db
    from app.models.post_model import Post

    user = make_user('poster')
    for i in range(15):
        post = Post(user_id=user.id, text=f'post {i}')
        db.session.add(post)
    db.session.commit()

    success, info = User.get_user_info('poster', per_page=10)
    assert success is True
    assert len(info['posts']) == 10
    assert info['posts_total_pages'] == 2
    assert info['posts_current_page'] == 1

    success, info_page_2 = User.get_user_info('poster', posts_page=2, per_page=10)
    assert len(info_page_2['posts']) == 5
