import datetime
from datetime import timedelta

def parse_date(raw_date):
    date_formats = ["%Y-%m-%d", "%d-%m-%Y", "%m-%d-%Y", "%Y/%m/%d", "%d/%m/%Y", "%m/%d/%Y", "%Y.%m.%d", "%d.%m.%Y",
                    "%m.%d.%Y"]
    for date_format in date_formats:
        try:
            return datetime.datetime.strptime(datetime.datetime.strptime(str(raw_date), date_format).date().isoformat(),
                                              '%Y-%m-%d').date()
        except:
            pass


def add_days_to_date(raw_date: str, plus_days: int) -> str:
    return datetime.datetime.strftime(parse_date(raw_date) + timedelta(days=plus_days), '%Y-%m-%d')
