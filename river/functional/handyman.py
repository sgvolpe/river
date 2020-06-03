#import geoip
try:
    import datetime, functools,gzip, json, os, requests, smtplib, time
    from functools import lru_cache
    from ipaddress import IPv4Address
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    import seaborn as sns

    from email import encoders
    from email.mime.base import MIMEBase
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText



    #from ipaddress import IPv4Address
    #from functools import lru_cache


    from sklearn.model_selection import train_test_split
    from sklearn.linear_model import LinearRegression
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import classification_report
    from sklearn.preprocessing import StandardScaler
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.metrics import classification_report,confusion_matrix
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.svm import SVC
    from sklearn.model_selection import GridSearchCV

except Exception as e: print (f'Could not load Required Librariy: {e}')




def analyze_df(df):
    df = pd.DataFrame()
    df.info()
    df.head()
    df.describe()
    df.columns
    sns.pairplot(df)
    plt.show()
    sns.distplot(df['target'])
    plt.show()
    sns.heatmap(df.corr())
    plt.show()
    sns.heatmap(df.isnull(), yticklabels=False, cbar=False, cmap='viridis')
    plt.show()
    sns.set_style('whitegrid')
    sns.countplot(x='Survived', data=df, palette='RdBu_r')
    plt.show()

def jointplot(df, x, y):
    sns.set_palette("GnBu_d")
    sns.set_style('whitegrid')
    # More time on site, more money spent.
    sns.jointplot(x='Time on Website', y='Yearly Amount Spent', data=df)
    sns.jointplot(x='Time on App', y='Length of Membership', kind='hex', data=df)
    plt.show()


# Machine Learning
# Linear Regression
class LinearRegression_:
    def __init__(self, f_path=os.path.join('Resources/data/linear_regression', 'USA_housing.csv'), cols=False, target=False, test_size=0.4, random_state=313, debug=True):
        self.df = pd.read_csv(f_path)
        self.cols = cols
        self.target = target
        self.debug = debug
        if self.debug: print('Initializing')

        if not self.cols: self.cols = ['Avg. Area Income', 'Avg. Area House Age', 'Avg. Area Number of Rooms',
                        'Avg. Area Number of Bedrooms', 'Area Population']
        if not self.target: self.target = 'Price'

        self.X = self.df[self.cols]
        self.y = self.df[self.target]
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(self.X, self.y, test_size=test_size, random_state=random_state)
        self.lm = LinearRegression()
        self.lm.fit(self.X_train, self.y_train)

    def evaluate(self):
        if self.debug: print('evaluating')
        self.lm.fit(self.X_train, self.y_train)
        print(self.lm.intercept_)
        self.coeff_df = pd.DataFrame(self.lm.coef_.T, self.X.columns, columns=['Coefficient'])
        print (self.coeff_df)

    def predict(self, context='desktop'):
        self.predictions = self.lm.predict(self.X_test)
        if context == 'desktop':
            sc = plt.scatter(self.y_test, self.predictions)
            plt.show()
            dp = sns.distplot((self.y_test - self.predictions), bins=50);
            plt.show()


class LogisticRegression_:
    def __init__(self, f_path=os.path.join('Rtesources/data/logistic_regression', 'titanic_train.csv')):
        self.train = pd.read_csv(f_path)
        sex = pd.get_dummies(self.train['Sex'], drop_first=True)
        embark = pd.get_dummies(self.train['Embarked'], drop_first=True)
        self.train.drop(['Sex', 'Embarked', 'Name', 'Ticket'], axis=1, inplace=True)
        self.train = pd.concat([self.train, sex, embark], axis=1)
        self.train = self.train.drop('Cabin', axis=1)
        self.train = self.train.dropna()

        def impute_age(cols):
            Age = cols[0]
            Pclass = cols[1]

            if pd.isnull(Age):

                if Pclass == 1:
                    return 37

                elif Pclass == 2:
                    return 29

                else:
                    return 24

            else:
                return Age

        self.train['Age'] = self.train[['Age', 'Pclass']].apply(impute_age, axis=1)
        print (self.train.info())

        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(self.train.drop('Survived', axis=1),
                                                                                self.train['Survived'], test_size=0.30,
                                                                                random_state=101)

        self.model = LogisticRegression()
        self.model.fit(self.X_train, self.y_train)


    def predict(self):
        self.predictions = self.model.predict(self.X_test)

    def evaluate(self):
        print(classification_report(self.y_test, self.predictions))


class KNN_:

    def __init__(self, f_path=os.path.join('../ML/data', 'Classified Data'), test_size=0.4, random_state=313, debug=True, n_neighbors=1):
        self.df = pd.read_csv(f_path, index_col=0)
        self.debug = debug

        self.scaler = StandardScaler()
        self.scaler.fit(self.df.drop('TARGET CLASS', axis=1))
        self.scaled_features = self.scaler.transform(self.df.drop('TARGET CLASS', axis=1))
        self.df_feat = pd.DataFrame(self.scaled_features, columns=self.df.columns[:-1])
        self.X = self.scaled_features
        self.y = self.df['TARGET CLASS']
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(self.X, self.y, test_size=test_size,
                                                                                random_state=random_state)

        self.model = KNeighborsClassifier(n_neighbors=n_neighbors)
        self.model.fit(self.X_train, self.y_train)

    def predict(self):
        self.pred = self.model.predict(self.X_test)

    def evaluate(self):
        print(confusion_matrix(self.y_test, self.pred))
        print(classification_report(self.y_test, self.pred))

    def choose_k(self):
        self.error_rate = []
        for i in range(1, 40):
            knn = KNeighborsClassifier(n_neighbors=i)
            knn.fit(self.X_train, self.y_train)
            pred_i = knn.predict(self.X_test)
            self.error_rate.append(np.mean(pred_i != self.y_test))

        plt.figure(figsize=(10, 6))
        plt.plot(range(1, 40), self.error_rate, color='blue', linestyle='dashed', marker='o',
                 markerfacecolor='red', markersize=10)
        plt.title('Error Rate vs. K Value')
        plt.xlabel('K')
        plt.ylabel('Error Rate')
        plt.show()

class DecisionTree_:

    def __init__(self, f_path=os.path.join('../ML/data', 'kyphosis.csv'), cols=False, target=False, test_size=0.4, random_state=313, debug=True):
        self.df = pd.read_csv(f_path)
        self.cols = cols
        self.target = target
        self.debug = debug
        if self.debug: print('Initializing')

        self.X = self.df.drop('Kyphosis', axis=1)
        self.y = self.df['Kyphosis']

        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(self.X, self.y, test_size=test_size, random_state=random_state)
        self.model = DecisionTreeClassifier()
        self.model.fit(self.X_train, self.y_train)

    def predict(self):
        self.predictions = self.model.predict(self.X_test)
        print(classification_report(self.y_test, self.predictions))
        print(confusion_matrix(self.y_test, self.predictions))


class SVM_:

    def __init__(self, f_path=os.path.join('../ML/data', 'kyphosis.csv'), cols=False, target=False, test_size=0.4,
                 random_state=313, debug=True):
        from sklearn.datasets import load_breast_cancer
        self.debug = debug
        self.data = load_breast_cancer()
        self.df_feat = pd.DataFrame(self.data['data'], columns=self.data['feature_names'])
        self.df_target = pd.DataFrame(self.data['target'],columns=['Cancer'])

        if self.debug: print('Initializing')


        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(self.df_feat, np.ravel(self.df_target), test_size=test_size,
                                                                                random_state=random_state)
        self.model = SVC()
        self.model.fit(self.X_train, self.y_train)

    def predict(self):
        self.predictions = self.model.predict(self.X_test)
        print(classification_report(self.y_test, self.predictions))
        print(confusion_matrix(self.y_test, self.predictions))


    def grid_search(self):
        param_grid = {'C': [0.1, 1, 10, 100, 1000], 'gamma': [1, 0.1, 0.01, 0.001, 0.0001], 'kernel': ['rbf']}
        grid = GridSearchCV(SVC(), param_grid, refit=True, verbose=3)
        grid.fit(self.X_train, self.y_train)
        print (grid.best_params_)
        print (grid.best_estimator_)
        self.grid_predictions = grid.predict(self.X_test)
        print(confusion_matrix(self.y_test, self.grid_predictions))
        print(classification_report(self.y_test, self.grid_predictions))


class KMeans:


    def __init__(self, f_path=os.path.join('../ML/data', 'kyphosis.csv'), cols=False, target=False, test_size=0.4, random_state=313, debug=True):
        from sklearn.datasets import make_blobs
        from sklearn.cluster import KMeans

        # Create Data
        self.debug = debug
        self.data = make_blobs(n_samples=200, n_features=2,centers=4, cluster_std=1.8, random_state=101)

        if self.debug: print('Initializing')
        self.model = KMeans(n_clusters=4)
        self.model.fit(self.data[0])
        print (self.model.cluster_centers_)
        print (self.model.labels_)

        f, (ax1, ax2) = plt.subplots(1, 2, sharey=True, figsize=(10, 6))
        ax1.set_title('K Means')
        ax1.scatter(self.data[0][:, 0], self.data[0][:, 1], c=self.model.labels_, cmap='rainbow')
        ax2.set_title("Original")
        ax2.scatter(self.data[0][:, 0], self.data[0][:, 1], c=self.data[1], cmap='rainbow')
        plt.show()



@lru_cache(1024)
def country_of(ip):
    """Add geo information to IPs"""

    headers = {
        'X-GEOIP-TOKEN': 'l3tm3in',
    }
    base_url = 'http://localhost:8988/geoip'

    headers = {
        'X-GEOIP-TOKEN': 'l3tm3in',
    }
    base_url = 'http://localhost:8988/geoip'
    params = {
        'ip': ip,
    }
    resp = requests.get(base_url, params=params, headers=headers)
    if not resp.ok:
        return ''
    reply = resp.json()
    if not reply['found']:
        return ''

    return reply['name']
#country_of('81.100.141.67')


def log(log_f_folder, log_f_name, to_write):
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
        start_time = time.perf_counter()    # 1
        value = func(*args, **kwargs)
        end_time = time.perf_counter()      # 2
        run_time = end_time - start_time    # 3
        print(f"Finished {func.__name__!r} in {run_time:.4f} secs")
        return value
    return wrapper_timer

def get_credentials(what_for, creds_path=os.path.join('..', 'Resources', 'credentials.txt')):
    #file_open = open(creds_path)
    with open(creds_path) as json_file:
        print (json_file)
        json_creds = json.load(json_file, encoding='cp1252')

    json_file.close()
    return json_creds[what_for]


def send_email(email_from='sgvolpe1@gmail.com', email_to='sgvolpe1@gmail.com', email_subject="HTML Message",
                email_body="""<html><body><h1>Test Email</h1></body></html>""", attachments=[]):

    # Treat Message
    message = MIMEMultipart()
    message['From'] = email_from
    message['To'] = email_to
    message['Subject'] = email_subject
    msg1 = MIMEText(email_body, 'html')
    message.attach(msg1)

    # Treat Attachments
    for file_name in attachments:
        openfile = open(file_name, 'rb')
        mimref = MIMEBase('application', 'octet_stream')
        mimref.set_payload((openfile.read()))
        encoders.encode_base64(mimref)
        mimref.add_header('Content-Disposition', f'openfile;filename={file_name}')
        message.attach(mimref)

    # Treat Connection
    creds = get_credentials(what_for='email')
    host, port, username, password = creds['server'], creds['port'], creds['username'], creds['password']
    connection = smtplib.SMTP(host, port)
    connection.ehlo()
    connection.starttls()

    connection.login(username, password)
    connection.sendmail(email_from, email_to, message.as_string())
    connection.quit()
#send_email( attachments=['../Resources/test.txt'])

def facebook_post():
    import facebook

    def get_token():
        return 'EAAHoT7BxOjUBAIRDoYlT9SIZBxiZAYqeXxa5BfjLTEWa1CADPZC5mJyBPKZCN3NSIjFDrtaZAkZBbKV0tByEpFZATYqeQXBcYrZAMyHplRDpZCF4VkaIAnQDeNd48Gs2EzASvMNfzMzfsJvXCmWMHZA2aJsln8f3rZCZBgEkBmZAbMn5FKFY2XxyHojUHyvXw0GUtDbyfa6hcLlN2G5gBdxKCFQQRpzZC4Oucmh479iP4tvt5KZCwZDZD'

    host = 'graph.facebook.com'

    graph = facebook.GraphAPI(access_token=get_token(), version="7.0")

    print(graph.get_object(id='10156973440365966', fields='photos'))
    print(graph.get_object(id='2304301603151927', fields='photos'))


    """graph.put_object(
        parent_object="me",
        connection_name="feed",
        message="This is a great website. Everyone should visit it.",
    #    link="https://www.facebook.com"
    )"""



import facebook

def main():
   # Fill in the values noted in previous steps here
   cfg = {
   "page_id"      : "10156973440365966",  # Step 1
   "access_token" : "EAAHoT7BxOjUBAKTVZAhiL4xqM0reZACyDpLfeCvMdd4dTKA3gMOLHI5zpZCDKN42cRtwOrR3nfKMt9ILuquZBll9hTaprdQMrZBThzlmNqSqCdmaPJJO82t0K1bh7ZBs3ZBaqAFmTGYRZBpUXqNnubUMH6tzhWWCQrbUwxU60xbOpLicYaGFTfvBu1UCSxxbxiJOR5vazYtrYtuYZCOxfYyjqkvOWmc625klipv5selGhIQZDZD"   # Step 3
    }
   api = get_api(cfg)
   msg = "Hello, world!"
   status = api.put_wall_post(msg)

def get_api(cfg):

    graph = facebook.GraphAPI(access_token=cfg['access_token'], version="2.7")
    resp = graph.get_object('me/accounts')
    print (resp)
    page_access_token = None
    for page in resp['data']:
        if page['id'] == cfg['page_id']:
            page_access_token = page['access_token']
        graph = facebook.GraphAPI(page_access_token)
        return graph

if __name__ == "__main__":
    main()