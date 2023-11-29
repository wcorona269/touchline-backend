from seeds import post_seeds, user_seeds, favorite_seeds
import random
from dotenv import load_dotenv
import pdb
load_dotenv(".flaskenv")
from  app.models import db, User, Favorite, FavoriteType, Post, PostLike, CommentLike, Comment, Repost, Notification, NotificationType

def seed_database(app):
    with app.app_context():
        db.drop_all()
        db.create_all()
        
        # create users
        for user in user_seeds:
            username = user[0]
            email = user[1]
            bio = user[2]
            avatar_url = user[3]
            new_user = User(username=username, email=email, bio=bio, avatar_url=avatar_url)
            new_user.set_password('touchline123')
            db.session.add(new_user)
        
        db.session.commit()
        user_ids = [user.id for user in User.query.all()]
        
        # create posts
        for _ in range(0, 300):
            new_post = Post(user_id=random.choice(user_ids), text=random.choice(post_seeds));
            db.session.add(new_post);
        db.session.commit()
        
        # create comments
        for _ in range(0, 300):
            target_post = random.choice(Post.query.all())
            sender_id = random.choice(user_ids)
        
            # create post comment
            new_comment = Comment(user_id=sender_id, post_id=target_post.id, text=random.choice(post_seeds))
            db.session.add(new_comment)
        
            # create notification for post comment
            new_notification = Notification(sender_id=sender_id, recipient_id=target_post.user_id, target_id=target_post.id, target_type=NotificationType.POST_COMMENT)
            db.session.add(new_notification)
        db.session.commit()
        
        # create post likes
        for _ in range(0, 300):
            target_post = random.choice(Post.query.all())
            sender_id = random.choice(user_ids)
            
            # create post like
            post_like = PostLike(user_id=sender_id, post_id=target_post.id)
            db.session.add(post_like)
            
            # create notification for post like
            new_notification = Notification(sender_id=sender_id, recipient_id=target_post.user_id, target_id=target_post.id, target_type=NotificationType.POST_LIKE)
            db.session.add(new_notification)
        db.session.commit()
        
        # create coments and comment likes
        for _ in range(0, 300):
            comment = random.choice(Comment.query.all())
            sender_id = random.choice(user_ids)
            
            comment_like = CommentLike(user_id=sender_id, comment_id=comment.id)
            db.session.add(comment_like)
            
            # create notification
            new_notification = Notification(sender_id=sender_id, recipient_id=comment.user_id, target_id=comment.id, target_type=NotificationType.COMMENT_LIKE)
            db.session.add(new_notification)
        db.session.commit()
        
        # create reposts and favorites
        for sender_id in user_ids:
            target_post = random.choice(Post.query.all())
            for _ in range(random.randint(0, 10)):
                # create repost
                new_repost = Repost(user_id=sender_id, post_id=target_post.id)
                db.session.add(new_repost)
                # create repost notification
                notif = Notification(sender_id=sender_id, recipient_id=comment.user_id, target_id=target_post.id, target_type=NotificationType.REPOST)
                db.session.add(notif)
        
            for favorite in favorite_seeds:
                new_fav = Favorite(user_id=sender_id, name=favorite[0], target_type=favorite[1], target_id=favorite[2])
                db.session.add(new_fav)
        
        
        db.session.commit()