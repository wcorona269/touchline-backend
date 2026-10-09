from app.models.notification_model import Notification, NotificationType


def test_read_all_marks_every_notification_read_in_one_call(app, make_user):
    recipient = make_user('recipient1')
    sender = make_user('sender1')

    for i in range(5):
        Notification.add_notification(recipient.id, sender.id, NotificationType.POST_LIKE, i)

    success, notifs = Notification.read_all(recipient.id)
    assert success is True
    assert all(n.read for n in notifs)

    unread_count = Notification.query.filter_by(recipient_id=recipient.id, read=False).count()
    assert unread_count == 0


def test_read_all_unknown_user_returns_false(app):
    success = Notification.read_all(999999)
    assert success is False


def test_add_notification_rejects_self_notification(app, make_user):
    user = make_user('selfnotifier')
    result = Notification.add_notification(user.id, user.id, NotificationType.POST_LIKE, 1)
    assert result is False
