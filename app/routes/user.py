from flask import Blueprint, request, jsonify
from ..models import db, User
from azure.storage.blob import BlobServiceClient
from datetime import datetime
import os

bp = Blueprint('users', __name__, url_prefix='/users')

@bp.route('/update-avatar/<username>', methods=['POST'])
def update_avatar(username):
    # access container
    from .. import container_client
    try:
        file = request.files['file']
        # Upload the file to Azure Storage Blob
        blob_name = f"avatars/{username}/avatar"  # Customize the blob name as needed
        blob_client = container_client.get_blob_client(blob_name)
        blob_client.upload_blob(file.stream, overwrite=True)
        user = User.query.filter_by(username=username).first()
        if user:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            timestamped_url = f"{blob_client.url}?t={timestamp}"
            user.avatar_url = timestamped_url  # Update the 'avatar_url' field with the blob URL
            db.session.commit()
            message, user_info = User.get_user_info(username)
            return jsonify({
                'message': 'User info fetched successfully',
                'user': user.to_dict(),
                'user_info': user_info
            }), 200
        else:
            return jsonify({
                'message': 'Invalid request data'
            }), 404
    except Exception as e:
        print(str(e))
        return jsonify({'error': 'Failed to upload file'}), 500

@bp.route('/info/<username>', methods=['GET'])
def get_user_info(username):
    result, user = User.get_user_info(username)
    if result == True:
        return jsonify({
            'message': 'User info fetched successfully',
            'user': user
        }), 200
    else:
        return jsonify({
            'message': 'Invalid request data'
        }), 404