from flask_sqlalchemy import SQLAlchemy

from src.db_interface.models import ReportMessage, Users


def save_report_message(db: SQLAlchemy, user: Users, message: str) -> None:
    kwargs = {
        'id_user': user.id,
        'message': message
    }
    report_message = ReportMessage(**kwargs)
    db.session.add(report_message)
    db.session.commit()
