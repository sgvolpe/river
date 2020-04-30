
import os as os

from django.db import models
from django.conf import settings
from django.urls import reverse

from . import assistant as AS
from . import SWS as Sabre_SWS_Handler


# Create your models here.
DEBUG = True


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


    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("bfm_app:benchmark_view",kwargs={"pk": self.pk})


    def run_analysis(self):
        '''
        Generate the folders: Ok
        Generate the Templates: Ok
        Generate the requests: Ok
        Generate the responses: ok
        Generate the dataframes: ok
        Generate the summary:
        '''

        'Make folders scaffold'
        directory = 'bfm_app/static/benchmark/'+str(self.pk)
        [os.makedirs(dir) for dir in [directory, directory+'/requests', directory+'/templates', directory+'/responses', directory+'/dataframes'] if not os.path.exists(dir)]

        'Create files'
        rq_1 = directory + '/templates/' + str(1) + '.xml'
        rq_2 = directory + '/templates/' + str(2) + '.xml'
        files_path = [directory + '/configuration.csv', directory + '/summary.csv', directory + '/log.txt',rq_1,rq_2 ]
        for fi_path in files_path:
            if not os.path.exists(fi_path):
                f = open(fi_path, 'w')
                f.close()


        'Write on Templates'
        f = open(rq_1, 'w')
        f.write(self.bfm_template_1)
        f.close()
        f = open(rq_2, 'w')
        f.write(self.bfm_template_2)
        f.close()
        templates = []
        repeats = self.repeats
        ond_list = self.onds.split(',')
        dates = AS.generate_dates(self.ap.split(','), self.los.split(','))


        parameters_list = [{'repeat': str(repeat),'origin': ond.split('-')[0],'destination': ond.split('-')[1],'dep_date': date_comb.split('/')[0]
        ,'ret_date': date_comb.split('/')[1]} for  repeat in range(repeats) for ond in ond_list  for date_comb in dates]

        for params in parameters_list:
            payload = self.bfm_template_1
            new_payload = AS.payload_change(payload, params)
            f_name = '_'.join(params.values()).replace('/','_')+'_rq_1'
            f_loc = directory + '/requests/'+f_name
            f = open(f_loc, 'w')
            f.write(new_payload)
            f.close()

            bfm_rs = Sabre_SWS_Handler.send_BFM(new_payload)
            f_loc = directory + '/responses/'+f_name
            f = open(f_loc, 'w')
            f.write(bfm_rs)
            f.close()

            payload = self.bfm_template_2
            new_payload = AS.payload_change(payload, params)
            f_name = '_'.join(params.values()).replace('/','_')+'_rq_2'
            f_loc = directory + '/requests/'+f_name
            f = open(f_loc, 'w')
            f.write(new_payload)
            f.close()

            bfm_rs = Sabre_SWS_Handler.send_BFM(new_payload)
            f_loc = directory + '/responses/'+f_name
            f = open(f_loc, 'w')
            f.write(bfm_rs)
            f.close()


            folder = directory + '/responses/'

            for fi in os.listdir(folder) :
                if DEBUG: print (fi)
                bfmdf = AS.bfm_rs(folder+fi)
                bfmdf.bfm_rs_to_df(save=True,output_path=directory+'/dataframes/'+fi)





#######


class bfm_rs(models.Model):
    title = models.CharField(max_length=50, blank=True)
    description = models.CharField(max_length=255, blank=True)
    bfm_file = models.FileField(upload_to='bfm_app/static/bfm_app/bfm_rs_xml')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    bfm_rs_df = models.FileField(upload_to='bfm_app/static/bfm_app/bfm_rs_df', blank=True)
    #creator = models.ForeignKey('accounts.user',on_delete=models.CASCADE)

    def __str__(self):
        return self.bfm_file.url

    def get_absolute_url(self):
        return reverse("bfm_app:view",kwargs={"pk": self.pk})

    def get_xml_name(self):
        return str(self.bfm_file.name).split('/')[-1]

    def get_df_name(self):
        return str(self.bfm_rs_df.name).split('/')[-1]


class bfm_rs_option(models.Model):
    bfm_rs = models.ForeignKey('bfm_rs',on_delete=models.CASCADE)
    rph = models.IntegerField()

    def __str__(self):
        return str(self.rph)


    def parse(self):
        return 'TEST PARSE'


class mfv(models.Model):
    title = models.CharField(max_length=255, blank=True)
    xml_file = models.FileField(upload_to='bfm_app/static/bfm_app/mfv_xml')

    def __str__(self):
        return self.xml_file.url

    def get_absolute_url(self):
        return reverse("bfm_app:mfv_view",kwargs={"pk": self.pk})

    def parse_to_df(self):
        if DEBUG: print ('Parsing DF for MFV')
        return AS.parse_mfv(self.xml_file.url)
