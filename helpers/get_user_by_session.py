from typing import Optional

from flask.sessions import SessionMixin

from models import User


def get_user_by_session(ses: SessionMixin) -> Optional[User]:
    # Get user-id from session
    user_id = ses.get("user_id")

    # Has session connected
    if user_id is None:
        return None

    # Get user from database
    user: User = User.query.filter_by(id=user_id).first()

    # Check if user exists
    if user is None:
        # Session remove 'connected' user
        ses.pop("user_id")
        return None

    return user
