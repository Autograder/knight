from pytz import UTC as utc, timezone as tzone
from datetime import datetime, timezone, timedelta
import dateutil.parser


class TimeUtil(object):
    '''
    Utility functions used to handle things with time.
    '''

    PST = tzone('US/Pacific')

    @staticmethod
    def get_current_time() -> str:
        '''
        Util method to get the time. Import this object
        and use it so that we don't have to manually configure time.\n
        @author npcompletenate
        '''
        utc_dt = datetime.now(timezone.utc)
        return utc_dt.astimezone(TimeUtil.PST).isoformat()

    @staticmethod
    def get_current_year() -> str:
        '''
        Util method to get the current year.\n
        @author YixuanZhou
        '''
        utc_dt = datetime.now(timezone.utc)
        return utc_dt.astimezone(TimeUtil.PST).isoformat().split('-')[0]

    @staticmethod
    def convert_str_to_datetime(time: str) -> datetime:
        '''
        Util method to read a time and convert it into datetime obejct.\n
        This function should give us back a datetime object so that we can
        work with for time calculations.\n
        Inputs:\n
        time --> the str representation of the time.\n
        Returns:\n
        datetime object that consist of the current time.\n
        @authoer YixuanZhou
        '''
        return dateutil.parser.parse(time)

    @staticmethod
    def naive_to_aware(time: datetime):
        '''
        Util method to convert a naive datetime to an aware datetime (PST).\n
        Inputs:\n
        time --> naive datetime.\n
        Returns:\n
        aware datetime of the passed in time.\n
        @author nouryehia
        '''
        return utc.localize(time).astimezone(TimeUtil.PST)

    @staticmethod
    def get_time_diff(time_a: str, time_b: str) -> str:
        '''
        Util method to calculate time difference.\n
        Inputs:\n
        time_a --> the str representation of the time.\n
        time_b --> the str representation of the time.\n
        Returns:\n
        str representation of the timedelta (a-b), but not in isoformat.\n
        @authoer YixuanZhou
        '''
        d_a = TimeUtil.convert_str_to_datetime(time_a)
        d_b = TimeUtil.convert_str_to_datetime(time_b)
        return (str(d_a - d_b))

    @staticmethod
    def get_time_before(hours: float = 0,
                        mins: float = 0, secs: float = 0) -> str:
        '''
        Util method to get the time given a period of time before.\n
        Inputs:\n
        hours --> Number of hours to go before.\n
        mins --> Number of mins to go before.\n
        secs --> Number of secs to go before.\n
        Returns\n
        Isoformated string time.
        @author YixuanZhou
        '''
        curr = TimeUtil.get_current_time()
        curr_d = TimeUtil.convert_str_to_datetime(curr)
        diff = timedelta(hours=hours, minutes=mins, seconds=secs)
        ret_d = curr_d - diff
        return ret_d.astimezone(TimeUtil.PST).isoformat()

    @staticmethod
    def min_time() -> str:
        '''
        Get the min time of datetime but with timezome being set to PST
        '''
        return datetime.min.astimezone(TimeUtil.PST).isoformat()
