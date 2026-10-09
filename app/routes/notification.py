from flask import Blueprint, request, jsonify
from ..models.user_model import User
from ..models.notification_model import Notification, NotificationType

bp = Blueprint('notification', __name__, url_prefix='/notifications')

def map_target_type(target_type):
    type_mapping = {
        'POST_LIKE': NotificationType.POST_LIKE,
        'POST_COMMENT': NotificationType.POST_COMMENT,
        'COMMENT_LIKE': NotificationType.COMMENT_LIKE,
        'REPOST': NotificationType.REPOST
    }
    return type_mapping.get(target_type, None)

@bp.route('/create', methods=['POST'])
def add_notification():
  data = request.json
  recipient_id = data.get('recipient_id')
  sender_id = data.get('sender_id')
  target_id = data.get('target_id')
  target_type_str = data['target_type']
  target_type = map_target_type(target_type_str)
  
  if not recipient_id or not sender_id or not target_id or not target_type:
    return jsonify({
				'message': 'Invalid request data'
    }), 400
  
  notification = Notification.add_notification(
    recipient_id,
    sender_id,
    target_type,
    target_id
  )
  
  if notification == True:
    return jsonify({
				'message': 'Notification created successfully'
		}), 200
  else:
    return jsonify({
        'message': 'Invalid request data'
    }), 400
    
@bp.route('/delete/<notifId>', methods=['DELETE'])
def delete_notification(notifId):
  if not notifId:
    return jsonify({
			'message': 'Invalid request data'
		}), 401
  
  
  result = Notification.delete_notification(notifId)
  if result == True:
    return jsonify({
			'message': 'Notification deleted successfully'
		}), 200
  else:
    return jsonify({
			'message': 'Invalid request data'
		}), 401

@bp.route('/fetch/<int:userId>', methods=['GET'])
def fetchNotifications(userId):
	user = User.query.get(int(userId))
	if user is None:
		return jsonify({
			'message': 'User not found'
		}), 404

	page = request.args.get('page', 1, type=int)
	per_page = request.args.get('per_page', 20, type=int)

	notifications = Notification.query.filter_by(recipient_id=int(userId)).order_by(
		Notification.created_at.desc()
	).paginate(page=page, per_page=per_page, error_out=False)

	notifications_list = {notification.id: notification.to_dict() for notification in notifications.items}

	return jsonify({
		'notifications': notifications_list,
		'total_pages': notifications.pages,
		'current_page': notifications.page,
		'total_notifications': notifications.total
	}), 200
 
@bp.route('/read-all/<int:userId>', methods=['POST'])
def read_all_notifs(userId):
  success, notifs = Notification.read_all(userId)
  
  notifications_list = {notification.id: notification.to_dict() for notification in notifs}
  if success:
    return jsonify({
      'message': 'User notifications read successfully',
      'notifications': notifications_list
    }), 200
  else:
    return jsonify({
      'message': 'User not found or no notifications to mark as read'
    }), 404
    
@bp.route('/read/<int:notifId>', methods=['POST'])
def set_as_read(notifId):
  success, notif = Notification.set_as_read(notifId)
  if success:
    return jsonify({
      'message': 'Notification read successfully',
      'notification': notif.to_dict()
    }), 200
  else:
    return jsonify({
      'message': 'Notification not found'
    }), 404