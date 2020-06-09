import datetime, functools, os, time
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


def generate_date_pairs(base_date=datetime.datetime.now().date(), ap_list=[7, 14], los_list=[7, 14]):
    """Returns a list of dates based on base_date and the Advanced Purchase list provided"""

    return [[str((add_days_to_date(base_date, int(ap)))), str((add_days_to_date(base_date, int(ap) + int(los))))]
            for ap in ap_list for los in los_list]



def log(log_f_folder='LOGS', log_f_name='log.txt', to_write='START'):
    if log_f_folder not in os.listdir(os.getcwd()):
        os.makedirs(os.path.join(log_f_folder))
        log = open(os.path.join(log_f_folder, log_f_name), 'w')
        log.write('# # # LOG START # # #')
        log.close()

    log = open(os.path.join(log_f_folder, log_f_name), 'a')
    log.write(to_write + '\n')
    log.close()


def timer(func):
    """Print the runtime of the decorated function"""

    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()  # 1
        value = func(*args, **kwargs)
        end_time = time.perf_counter()  # 2
        run_time = end_time - start_time  # 3
        print(f"Finished {func.__name__!r} in {run_time:.4f} secs")
        return value

    return wrapper_timer


def function_log(func):
    """Print the runtime of the decorated function"""

    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()  # 1
        value = func(*args, **kwargs)
        end_time = time.perf_counter()  # 2
        run_time = end_time - start_time  # 3
        log(log_f_folder='LOGS', log_f_name='function_log.txt', to_write=f"Finished {func.__name__!r} in {run_time} secs|")

        return value

    return wrapper_timer
