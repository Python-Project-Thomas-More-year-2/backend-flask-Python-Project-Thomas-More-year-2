from typing import Optional

from flask.sessions import SessionMixin
from werkzeug.exceptions import Unauthorized

from models import User


def get_user_by_session(ses: SessionMixin, throw_unauthorized=False) -> Optional[User]:
    # Get user-id from session
    user_id = ses.get("user_id")

    # Has session connected
    if user_id is None:
        if throw_unauthorized:
            raise Unauthorized("User has no connected session")

        return None

    # Get user from database
    user: User = User.query.filter_by(id=user_id).first()

    # Check if user exists
    if user is None:
        # Session remove 'connected' user
        ses.pop("user_id")

        if throw_unauthorized:
            raise Unauthorized("User has no connected session")

        return None

    return user
