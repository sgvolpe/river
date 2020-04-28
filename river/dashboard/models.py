import datetime, functools, time, os
from django.db import models
from django_plotly_dash import DjangoDash
from . import app
DEBUG = True

def log(log_f_folder='static/dashboard', log_f_name='stats_log.txt', to_write='# # # # # # start'):


    log = open(os.path.join(log_f_folder, log_f_name), 'a')
    log.write(to_write + '\n')
    log.close()


def try_catch(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()  # 1
        value = func(*args, **kwargs)
        end_time = time.perf_counter()  # 2
        run_time = end_time - start_time  # 3
        to_write = f"{datetime.datetime.now()},{start_time},{end_time},{run_time:.4f} secs,{func.__name__!r}"
        log(to_write=to_write)
        print(f'{func.__name__}______________________No Error: {run_time}')
        return value
    try:
        return wrapper
    except Exception as e:
        raise Exception(f'Error on: {func.__name__} | {str(e)}')


class AnalysisApp(models.Model):
    title = models.CharField(max_length=200, default="Analysis App", unique=False)
    df_path = models.FileField(upload_to='static/dashboard/dataframes')
    conf_file = models.CharField(max_length=200, default="default.txt", unique=False)


    def run(self):
        self.app = app.AnalysisApp(app_name='basic').get_app()

        """if DEBUG: print('Running Dashboard Creation')

        self.template = self.CHART_FONT = self.opacity = None

        # Create Dahs App
        self.app = DjangoDash('analysis_app', add_bootstrap_links=True, suppress_callback_exceptions=True)
        self.app.css.append_css({'external_url': 'https://codepen.io/amyoshino/pen/jzXypZ.css'})
        external_js = ["https://code.jquery.com/jquery-3.2.1.min.js", "https://codepen.io/bcd/pen/YaXojL.js"]
        for js in external_js: self.app.scripts.append_script({"external_url": js})

        # Instantiate components empty
        self.input_components, self.div_charts, self.div_tables, self.function_outputs = [], [], [], []
        self.main_inputs, self.inputs_as_output, self.function_inputs, self.parameter_inputs = [], [], [], []

        # Read Data
        self.read_data()

        # Initialize Components
        self.read_input_configuration()
        self.create_input_components()
        self.create_output_components()
        self.update_inputs()

        # Create App Layout
        self.app.layout = html.Div([
            html.H2(self.title),
            self.input_components,
            self.div_charts,
            self.div_tables,
        ], className="principal")
        
        return self.app"""