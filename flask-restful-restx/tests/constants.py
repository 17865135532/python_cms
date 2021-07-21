from datetime import datetime, timedelta


TODAY = datetime.today()
YESTERDAY = TODAY - timedelta(days=1)
TOMORROW = TODAY + timedelta(days=1)
