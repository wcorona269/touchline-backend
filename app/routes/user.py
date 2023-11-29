from flask import Blueprint, request, jsonify
from ..models import db, User
from azure.storage.blob import BlobServiceClient
import os


bp = Blueprint('users', __name__, url_prefix='/users')

@bp.route('/update-avatar/<username>', methods=['POST'])
def update_avatar(username):
    # access container
    from .. import container_client
    try:
        file = request.files['file']
        # Upload the file to Azure Storage Blob
        blob_name = f"avatars/{username}/{file.filename}"  # Customize the blob name as needed
        blob_client = container_client.get_blob_client(blob_name)
        blob_client.upload_blob(file.stream, overwrite=True)

        user = User.query.filter_by(username=username).first()
        user.avatar_url = blob_client.url  # Update the 'avatar_url' field with the blob URL
        print(blob_client.url)
        db.session.commit()
        result, user_info = User.get_user_info(username)
        if result == True:
           return jsonify({
                'message': 'User info fetched successfully',
                'user': user_info
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