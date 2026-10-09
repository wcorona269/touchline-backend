from app.models.db import db
from app.models.post_model import Post
from app.models.notification_model import Notification, NotificationType


def test_cors_allowed_origins_locked_down(app):
    assert 'http://localhost:3000' in app.config['ALLOWED_ORIGINS']
    assert '*' not in app.config['ALLOWED_ORIGINS']


def test_register_and_login_flow(client):
    register_resp = client.post('/auth/register', json={
        'username': 'routeuser', 'password': 'password123'
    })
    assert register_resp.status_code == 201

    login_resp = client.post('/auth/login', json={
        'username': 'routeuser', 'password': 'password123'
    })
    assert login_resp.status_code == 200
    assert login_resp.json['user']['username'] == 'routeuser'


def test_register_short_password_returns_400(client):
    resp = client.post('/auth/register', json={
        'username': 'routeuser2', 'password': 'short'
    })
    assert resp.status_code == 400


def test_posts_index_pagination(client, make_user):
    user = make_user('indexposter')
    for i in range(15):
        Post.create_post(user.id, f'post {i}')

    resp = client.get('/posts/index?page=1&per_page=10')
    assert resp.status_code == 200
    data = resp.json
    assert len(data['posts']) == 10
    assert data['total_pages'] == 2
    assert data['total_posts'] == 15


def test_notifications_fetch_is_paginated(client, make_user):
    recipient = make_user('notifrecipient')
    sender = make_user('notifsender')
    for i in range(25):
        Notification.add_notification(recipient.id, sender.id, NotificationType.POST_LIKE, i)

    resp = client.get(f'/notifications/fetch/{recipient.id}?per_page=10')
    assert resp.status_code == 200
    data = resp.json
    assert len(data['notifications']) == 10
    assert data['total_pages'] == 3
    assert data['total_notifications'] == 25


def test_user_info_route_paginates_and_merges(client, make_user):
    user = make_user('profileuser')
    for i in range(12):
        Post.create_post(user.id, f'post {i}')

    resp = client.get('/users/info/profileuser')
    assert resp.status_code == 200
    data = resp.json['user']
    assert len(data['posts']) == 10
    assert data['posts_total_pages'] == 2

    resp_page_2 = client.get('/users/info/profileuser?posts_page=2')
    assert len(resp_page_2.json['user']['posts']) == 2


def test_user_info_route_404_for_missing_user(client):
    resp = client.get('/users/info/nosuchuser')
    assert resp.status_code == 404
