import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import warnings
import statsmodels.api as sm
import sklearn
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split,GridSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier,AdaBoostClassifier,GradientBoostingClassifier
from imblearn.over_sampling import SMOTE
from statsmodels.stats.outliers_influence import variance_inflation_factor
from sklearn.metrics import confusion_matrix
from sklearn.metrics import roc_curve

def add(a,b):
    return a+b

def eviter_warnings():
    print("test")
    warnings.filterwarnings("ignore", category=FutureWarning) # empêcher les warning de s'afficher

## Recupération des données brut sous forme d'un dataframe
df = pd.read_csv(r"./data/drinking_water_potability.csv")
# print(df.shape)
# print(df) # Affichage des données dataframe
# print(df.head()) # tête du dataframe
# print(df.describe()) # statistiques descriptives du dataframe

## Affichage des variables explicatives
data = df.to_numpy() # convertir le dataframe en array
fig = plt.figure(figsize=(15,9)) # création de la fenetre
fig.canvas.set_window_title('Drinking Water Potability - Variable Distribution') # titre de la fenêtre
plt.style.use('seaborn-whitegrid') # style de grille
for i in range(len(data[0][:-1])):
    ax = plt.subplot(3,3,1+i) # changer de subplot
    sns.distplot(df[df.columns[i]], color = '#2a7bff') # afficher le barplot et la repartition
plt.suptitle("Histogrammes des variables explicatives", fontsize=20) # titre principal
plt.show() # afficher le tout

## Check for null values
# print(df.isnull().sum()) # afficher les valeurs manquantes au dataset

## Clean dataset by replacing missing values
df['ph'] = df['ph'].fillna(df['ph'].mean()) # remplacer les valeurs manquantes par la moyenne (distribution normale)
df['Sulfate'] = df['Sulfate'].fillna(df['Sulfate'].mean()) # remplacer les valeurs manquantes par la moyenne (distribution normale)
df['Trihalomethanes'] = df['Trihalomethanes'].fillna(df['Trihalomethanes'].median()) # remplacer les valeurs manquantes par la moyenne (distribution normale)

## Exploratory Data Analysis
columns = [x for x in df.columns if x != 'Potability'] # selection des variables explicatives
plt.figure(figsize=(15,9)) # création de la fenetre
plt.suptitle("Diagramme moustache en fonction de la potabilité", fontsize=20) # titre principal
for i in range(9):
    plt.subplot(3,3,i+1) # choix du subplot
    sns.boxplot(data=df,x = 'Potability' ,y= columns[i],showfliers=False) # diagrammes moustaches
plt.show() # afficher le tout

plt.figure(figsize=(9,9)) # création de la fenetre
plt.suptitle("Matrice de correlation des variables", fontsize=20) # titre principal
sns.heatmap(df.corr(), annot=True, cmap = 'RdYlGn', vmin=-1, vmax=1) # matrice de corrélation
plt.show() # afficher le tout

## Séparer les données en train set et test set
X_train, X_test, y_train, y_test = train_test_split(df[[c for c in df.columns if c != 'Potability']],df['Potability'],train_size = 0.7,random_state = 1)

## Scaling des données des variables explicatives
sc = StandardScaler()
X_train[X_train.columns] = sc.fit_transform(X_train)
X_test[X_test.columns] = sc.transform(X_test)
X_train, y_train = SMOTE(random_state=1,n_jobs=-1).fit_resample(X_train,y_train)
X_train_sm = sm.add_constant(X_train)
lm = sm.GLM(y_train,X_train_sm,family=sm.families.Binomial()).fit()
print(lm.summary())

def vif(data):
    res = pd.DataFrame()
    res['Feature'] = data.columns
    res['VIF'] = [variance_inflation_factor(data.values,i) for i in range(data.shape[1])]
    return res
print(vif(X_train_sm))

X_test_sm = sm.add_constant(X_test)
y_train_pred = lm.predict(X_train_sm)

def tp_fp(cf):
    fp = cf[0,1]/(cf[0,0] + cf[0,1])
    tp = cf[1,1]/(cf[1,0] + cf[1,1])
    return fp,tp


def plot_roc(data,truth):
    cutoff = [0.001*i for i in range(1,1000)]
    x = []
    y = []
    for c in cutoff:
        #print(data)
        data_temp = data.apply(lambda x: 1 if x>=c else 0)
        cf = confusion_matrix(truth,data_temp)
        x.append(tp_fp(cf)[0])
        y.append(tp_fp(cf)[1])
    plt.plot(x,y)
    plt.show()

plot_roc(y_train_pred,y_train)

fp,tp,_ = roc_curve(y_train,y_train_pred)
plt.plot(fp,tp)

y_test_pred = lm.predict(X_test_sm).apply(lambda x: 1 if x>= 0.5 else 0)

cf = confusion_matrix(y_test,y_test_pred)
acc = (cf[0,0] + cf[1,1])/(cf[0,0] + cf[0,1] + cf[1,1] +cf[1,0])
tpr = cf[1,1]/(cf[1,0] + cf[1,1])
print(f"tpr = {tpr} accuracy = {acc}")

dt = DecisionTreeClassifier(random_state=1)
params = {
    "min_samples_split": [10,20,100],
    "max_depth": [5,10,50],
    "min_samples_leaf": [10,20,50],
    "max_leaf_nodes": [10,20,100]
}

dt_grid = GridSearchCV(estimator=dt,param_grid=params,cv=5,scoring='balanced_accuracy',verbose=10,n_jobs = -1).fit(X_train,y_train)

# gb = cv.best_estimator_

# y_train_pred = gb.predict(X_train)
# cf = confusion_matrix(y_train,y_train_pred)

# print(cf)
# acc = (cf[0,0] + cf[1,1])/np.sum(cf)
# recall = (cf[1,1])/(cf[1,1] + cf[1,0])
# spec = (cf[0,0])/(cf[0,1] + cf[0,0])
# print(f"Accuracy = {acc} Recall = {recall} Specificity = {spec}")