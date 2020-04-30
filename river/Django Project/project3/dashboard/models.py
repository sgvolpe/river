
import os, datetime
import pandas as pd

from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django import forms
from django.forms.widgets import CheckboxSelectMultiple

from multiselectfield import MultiSelectField
from . import assistant as AS
from . import SWS as Sabre_SWS_Handler


DEBUG=True

# Create your models here.

#########################
# Benchmark
#########################

class Benchmark(models.Model):
    title = models.CharField(max_length=50, blank=True)
    description = models.CharField(max_length=255, blank=True)
    #bfm_rqs
    #configuration_file =
    ap = models.CharField(max_length=500, blank=True)
    los = models.CharField(max_length=500, blank=True)
    onds = models.CharField(max_length=500, blank=True)
    bfm_template_1 =  models.TextField(null=True, blank=True)
    bfm_template_2 =  models.TextField(null=True, blank=True)
    repeats = models.IntegerField()
    total_queries= models.IntegerField(default=0)
    analysis_finished = models.DateTimeField(blank=True, null=True)

    def log(self, text):
        log_path = self.directory + '/log.txt'
        log_file = open(log_path, 'a')
        log_file.write(str( datetime.datetime.now() ) + ',' + str(text) + '\n')
        log_file.close()


    def __str__(self):
        return 'dashboard/static/benchmark/'+str(self.pk)+ '/summary.csv'

    def get_summary_name(self):
        return 'dashboard/static/benchmark/'+str(self.pk)+ '/summary.csv'

    def get_absolute_url(self):
        self.total_queries = len(self.ap)*len(self.los)*(self.repeats)*2
        self.save()
        return reverse("dashboard:benchmark_view",kwargs={"pk": self.pk})


    def process_summary(self):
        self.log('Process Summary')
        dicts = []
        input_dir = self.path + '/dataframes/'
        conf = open(self.path + '/configuration.csv')
        dicts = []
        self.log('Opening Configuration File.')
        for line in conf:
            self.log('Processing: '+line)
            line = line.replace('\n','')
            df1 = pd.read_csv(self.path + '/dataframes/' + line + '_rq_1', sep=',')
            df2 = pd.read_csv(self.path + '/dataframes/' + line+'_rq_2', sep=',')
            self.log('Dataframes opened correctly.')
            df1['provider'] = 'rq_1'
            df2['provider'] = 'rq_2'
            df1['itinerary_carrier'] = df1['itinerary'].apply(lambda x: '-'.join (sorted(list(set([flight[:2] for flight in x.split('-')]))) ))
            df2['itinerary_carrier'] = df2['itinerary'].apply(lambda x: '-'.join (sorted(list(set([flight[:2] for flight in x.split('-')]))) ))

            it1, it2 = list(df1['itinerary']), list(df2['itinerary'])

            unique_1,unique_2,overlap = 0,0,0
            for it in it1:
                if it in it2:overlap += 1
                else: unique_1+=1
            for it in it2:
                if it in it1: overlap += 1
                else: unique_2+=1

            di = {'rq_1_only':unique_1,'rq_2_only':unique_2,'both':overlap}
            di['ond'] = line.split('_')[1]+'_'+line.split('_')[2]
            di['ap_los'] = 'N/a'#df1['ap_los'][0]
            di['search_date'] = 'N/a'#df1['search_date'][0]

            #Fare
            di['rq_1_fare_mean']=df1['price'].mean()
            di['rq_2_fare_mean']=df2['price'].mean()
            di['rq_1_fare_std']=df1['price'].std()
            di['rq_2_fare_std']=df2['price'].std()

            di['rq_1_cheapest']=df1.loc[df1['price'].idxmin()]['price']
            di['rq_2_cheapest']=df2.loc[df2['price'].idxmin()]['price']
            di['lfe_fare_difference'] = (di['rq_1_cheapest'].astype(float) - di['rq_2_cheapest'].astype(float) ) / di['rq_1_cheapest'].astype(float)

            if di['lfe_fare_difference'] == 0:  di['lfe'] = 'tie'
            elif di['lfe_fare_difference'] > 0: di['lfe'] = 'rq_2'
            elif di['lfe_fare_difference'] < 0: di['lfe'] = 'rq_1'

            # Time
            di['rq_1_time_mean'] = df1['travel_time'].mean()
            di['rq_2_time_mean_sabre'] = df2['travel_time'].mean()
            di['rq_1_time_std'] = df1['travel_time'].std()
            di['rq_2_time_std'] = df2['travel_time'].std()
            di['rq_1_time_max'] = df1['travel_time'].max()
            di['rq_2_time_max'] = df2['travel_time'].max()
            di['rq_1_time_min'] = df1['travel_time'].min()
            di['rq_2_time_min'] = df2['travel_time'].min()


            if di['rq_1_time_min']- di['rq_2_time_min'] == 0:  di['quickest'] = 'tie'
            elif di['rq_1_time_min']- di['rq_2_time_min']  > 0: di['quickest'] = 'rq_2'
            elif di['rq_1_time_min']- di['rq_2_time_min']  < 0: di['quickest'] = 'rq_1'


            di['rq_1_min_carrier'] = dict( df1.groupby(['itinerary_carrier'])['price'].min() )
            di['rq_2_min_carrier'] = dict( df2.groupby(['itinerary_carrier'])['price'].min() )

            di['rq_1_cxr_div'] = len (di['rq_1_min_carrier'].keys() )
            di['rq_2_cxr_div'] = len (di['rq_2_min_carrier'].keys() )

            if di['rq_1_cxr_div']- di['rq_2_cxr_div'] == 0:  di['cxr_div'] = 'tie'
            elif di['rq_1_cxr_div']- di['rq_2_cxr_div'] > 0: di['cxr_div'] = 'rq_1'
            elif di['rq_1_cxr_div']- di['rq_2_cxr_div'] < 0: di['cxr_div'] = 'rq_2'

            dicts.append(di)
            self.log('Processed correctly.')
        out_df = pd.DataFrame(dicts)
        out_df.to_csv(self.path + '/summary.csv' )
        self.log('Summary File Generated.')

    def run_analysis(self):
        '''
        Generate the folders: Ok
        Generate the Templates: Ok
        Generate the requests: Ok
        Generate the responses: ok
        Generate the dataframes: ok
        Generate the summary: ok
        '''
        directory = 'dashboard/static/benchmark/'+str(self.pk)
        self.directory=directory
        self.save()


        [os.makedirs(dir) for dir in [directory, directory+'/requests', directory+'/templates', directory+'/responses', directory+'/dataframes'] if not os.path.exists(dir)]

        'Create files'
        rq_1 = directory + '/templates/' + str(1) + '.xml'
        rq_2 = directory + '/templates/' + str(2) + '.xml'
        files_path = [directory + '/configuration.csv', directory + '/summary.csv', directory + '/log.txt',rq_1,rq_2 ]
        for fi_path in files_path:
            if not os.path.exists(fi_path):
                f = open(fi_path, 'w')
                f.close()
        self.log('Folder Scaffold dONE: '+directory)

        self.log('Write on Templates')
        f = open(rq_1, 'w')
        f.write(self.bfm_template_1)
        f.close()
        f = open(rq_2, 'w')
        f.write(self.bfm_template_2)
        f.close()
        self.log('->OK.')
        templates = []
        repeats = self.repeats
        ond_list = self.onds.split(',')
        dates = AS.generate_dates(self.ap.split(','), self.los.split(','))

        parameters_list = [{'repeat': str(repeat),'origin': ond.split('-')[0],'destination': ond.split('-')[1],'dep_date': date_comb.split('/')[0]
        ,'ret_date': date_comb.split('/')[1]} for  repeat in range(repeats) for ond in ond_list  for date_comb in dates]
        self.log('Setting Configuration File.')
        cnf = open(directory + '/configuration.csv','w')
        cnf.close()
        cnf = open(directory + '/configuration.csv','a')

        for params in parameters_list:
            cnf.write('_'.join(params.values())+'\n')
            self.log('-> '+str(params))

            payload = self.bfm_template_1
            new_payload = AS.payload_change(payload, params)

            f_name = '_'.join(params.values()).replace('/','_')+'_rq_1'
            if f_name not in os.listdir(directory + '/requests/'):
                self.log('Writting Payload 1.')
                f_loc = directory + '/requests/'+f_name
                f = open(f_loc, 'w')
                f.write(new_payload)
                f.close()

            self.log('Sending Payload 1.')

            bfm_rs = Sabre_SWS_Handler.send_BFM(new_payload)
            f_loc = directory + '/responses/'+f_name
            self.log('Saving RS Payload 1.')
            f = open(f_loc, 'w')
            f.write(bfm_rs)
            f.close()

            payload = self.bfm_template_2
            new_payload = AS.payload_change(payload, params)

            f_name = '_'.join(params.values()).replace('/','_')+'_rq_2'
            if f_name not in os.listdir(directory + '/requests/'):
                self.log('Writting Payload 2.')

                f_loc = directory + '/requests/'+f_name
                f = open(f_loc, 'w')
                f.write(new_payload)
                f.close()

            self.log('Sending Payload 2.')
            bfm_rs = Sabre_SWS_Handler.send_BFM(new_payload)
            f_loc = directory + '/responses/'+f_name
            self.log('Saving RS Payload 2.')
            f = open(f_loc, 'w')
            f.write(bfm_rs)
            f.close()

        folder = directory + '/responses/'
        self.log('Creating Individual Dataframes')
        for fi in os.listdir(folder) :
            #if DEBUG: print (fi)

            bfmdf = AS.bfm_rs(folder+fi)
            bfmdf.bfm_rs_to_df(save=True,output_path=directory+'/dataframes/'+fi, parameters=params)
            self.log('->OK.')
        self.path = directory

        cnf.close()
        self.process_summary()
        self.analysis_finished = timezone.now()
        self.save()
        print (self.analysis_finished)
        self.log('FINISHED.')




########
#ancillaries

class AncillariesComparison(models.Model):

    CHART_TYPES = (
        ('Carriers','Carriers'),('CarriersComplementary','CarriersComplementary'),
        ('Bookings','Bookings'),('BookingsComplementary','BookingsComplementary'),
    )
    ANCILLARY_TYPES = (
        ('Seats','Seats'),('Baggage','Baggage'),('Pets','Pets'),
        ('Lounge','Lounge'),('Meals','Meals'),('Medical','Medical')
    )

    title = models.CharField(max_length=50, blank=True)
    description = models.CharField(max_length=255, blank=True)
    bookings_file = models.FileField(upload_to='dashboard/static/booking_files/', blank=False)
    charts = MultiSelectField(choices=CHART_TYPES, blank=True )
    ancillaries = MultiSelectField(choices=ANCILLARY_TYPES, blank=True )#forms.MultipleChoiceField(required=False,label='Ancillaries', widget=CheckboxSelectMultiple(),choices=ANCILLARY_TYPES)



    def __str__(self):
        return self.bookings_file.url

    def get_absolute_url(self):
        return reverse("dashboard:ancillariescomparison_view",kwargs={"pk": self.pk})






################
#SummaryDashboard


class SummaryDashboard(models.Model):
    title = models.CharField(max_length=50, blank=True)
    description = models.CharField(max_length=255, blank=True)
    csv_file = models.FileField(upload_to='dashboard/static/sumary_files/', blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    #uploaded_by = models.ForeignKey('accounts.user',on_delete=models.CASCADE)
    onds = models.CharField(max_length=500, blank=True)
    ap_los = models.CharField(max_length=500, blank=True)

    #shopping_comparison = models.ForeignKey(ShoppingComparison, related_name='shopping_comparison', on_delete=models.CASCADE, default=0)

    def __str__(self):
        return self.csv_file.url

    def get_absolute_url(self):
        return reverse("dashboard:summary_view",kwargs={"pk": self.pk})




class IndividualDashboard(models.Model):
    title = models.CharField(max_length=50, blank=True)
    description = models.CharField(max_length=255, blank=True)
    csv_file = models.FileField(upload_to='dashboard/static/individual_files/', blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    #uploaded_by = models.ForeignKey('accounts.user',on_delete=models.CASCADE,)
    summary_dashboard = models.ForeignKey(SummaryDashboard, related_name='individual_dashboards',on_delete=models.CASCADE, default=0)
    ond = models.CharField(max_length=500, blank=True)
    ap_los = models.CharField(max_length=500, blank=True)
    search_date = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.csv_file.url

    def get_absolute_url(self):
        return reverse("dashboard:individual_view",kwargs={"pk": self.pk})



class ShoppingComparison(models.Model):
    title = models.CharField(max_length=50, blank=True)
    description = models.CharField(max_length=255, blank=True)
    csv_file = models.FileField(upload_to='dashboard/static/absolute_files/', blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    onds = models.CharField(max_length=500, blank=True)
    ap_los = models.CharField(max_length=500, blank=True)
    analysis_finished = models.DateTimeField(blank=True, null=True)
    summary_dashboard = models.ForeignKey(SummaryDashboard, related_name='s_dashboard',on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.title
        #return self.csv_file.url

    def get_absolute_url(self):
        return reverse("dashboard:shoppingcomparison_view",kwargs={"pk": self.pk})




    def run_analysis(self):
        'Make folders scaffold'

        directory = 'dashboard/static/shopping_comparison/'+str(self.pk)
        [os.makedirs(dir) for dir in [directory, directory+'/input', directory+'/output', directory+'/query_files'] if not os.path.exists(dir)]


        files_path = [directory + '/configuration.csv', directory + '/summary.csv', directory + '/log.txt']
        for fi_path in files_path:
            if not os.path.exists(fi_path):
                f = open(fi_path, 'w')
                f.close()

        pd.DataFrame(pd.read_csv(self.csv_file)).to_csv(directory + '/configuration.csv', sep=',', index=False)



        mf = AS.MichalFile(self)
        mf.generate_id_list()
        mf.generate_ind_files()
        mf.advanced_processing()
        mf.process_summary()

        #Create Summary Dashboard
        nsd = SummaryDashboard(title=self.title)
        nsd.csv_file = mf.path + '/summary.csv'
        nsd.save()

        #Create individual dashboards
        for fi in os.listdir( directory +'/output'):
            nid = IndividualDashboard(csv_file=fi , summary_dashboard=nsd ) #TODO: find a way to add the path to the file
            nid.save()

        self.summary_dashboard = nsd
        self.analysis_finished = timezone.now()
        self.save()


        #Send email


class StatelessApp(models.Model):
    '''
    A stateless Dash app.

    An instance of this model represents a dash app without any specific state
    '''

    app_name = models.CharField(max_length=100, blank=False, null=False, unique=True)
    slug = models.SlugField(max_length=110, unique=True, blank=True)

    def as_dash_app(self):
        '''
        Return a DjangoDash instance of the dash application
        '''
        app = DjangoDash('dash2', external_stylesheets='https://codepen.io/amyoshino/pen/jzXypZ.css',serve_locally=False)
        #app.append_css({'external_stylesheets':'https://codepen.io/amyoshino/pen/jzXypZ.css'})
        app.layout = html.Div([
            html.Div([],className='row', id="header"),

            html.Div([
                html.Div([html.H4('Itinerary Table')],className='six columns'),
                html.Div([html.H4('Itinerary Table')],className='six columns'),
                html.Div(["a"],className='six.columns'),
                html.Div(["a"],className='six.columns'),
            ],className='row justify-content-md-center', id="middle"),

            html.Div([],className='row', id="footer"),


        ] ,className='ten columns' )
        return app


class DashApp(models.Model):
    '''
    An instance of this model represents a Dash application and its internal state
    '''
    stateless_app = models.ForeignKey(StatelessApp, on_delete=models.PROTECT,
                                      unique=False, null=False, blank=False)
    instance_name = models.CharField(max_length=100, unique=True, blank=True, null=False)
    slug = models.SlugField(max_length=110, unique=True, blank=True)
    base_state = models.TextField(null=False, default="{}")
    creation = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)
    save_on_change = models.BooleanField(null=False,default=False)



    def current_state(self):
        '''
        Return the current internal state of the model instance
        '''

    def update_current_state(self, wid, key, value):
        '''
        Update the current internal state, ignorning non-tracked objects
        '''

    def populate_values(self):
        '''
        Add values from the underlying dash layout configuration
        '''
