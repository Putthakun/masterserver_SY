from pydantic import BaseModel
from datetime import datetime, timedelta, timezone

class TransactionRequest(BaseModel):
    emp_id: int
    camera_id: int
    timestamp: datetime

    @staticmethod
    def get_thailand_time(utc_time: datetime) -> datetime:
        # เขตเวลา UTC+7
        th_timezone = timezone(timedelta(hours=7))
        return utc_time.replace(tzinfo=timezone.utc).astimezone(th_timezone)