import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from numpy import set_printoptions
from sklearn.utils import resample
from imblearn.over_sampling import SMOTE
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import f_classif
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
import xgboost as xgb
from sklearn import metrics
from sklearn.svm import SVC
from imblearn.under_sampling import RandomUnderSampler
from imblearn.over_sampling import RandomOverSampler
from sklearn.model_selection import RandomizedSearchCV
import pickle
import time
from sklearn.model_selection import cross_validate
from sklearn.metrics import recall_score

acc_veh_df = pd.read_csv('acc_veh.csv', low_memory=False)

# severity_1 = acc_veh_df[acc_veh_df.accident_severity == 1]
# severity_2 = acc_veh_df[acc_veh_df.accident_severity == 2]
# severity_3 = acc_veh_df[acc_veh_df.accident_severity == 3]


target = acc_veh_df['accident_severity']
acc_veh_df = acc_veh_df.drop('accident_index', axis=1)
acc_veh_df = acc_veh_df.drop('accident_reference', axis=1)
acc_veh_df = acc_veh_df.drop('road_type', axis=1)
# fig, ax = plt.subplots(figsize=(15, 16))
# acc_veh_df.corr().to_csv('correlation.csv', index=True)
# seaborn.heatmap(acc_veh_df.corr(), annot=True, cmap="YlGnBu", fmt='.2f', ax=ax, )
# plt.savefig("correlation.png")
# plt.close()
acc_veh_df = acc_veh_df.drop('accident_severity', axis=1)
input_array = acc_veh_df.values
target_array = target.values
X = acc_veh_df
Y = target

# feature extraction
test = SelectKBest(score_func=f_classif, k=4)
fit = test.fit(X, Y)
# summarize scores
set_printoptions(precision=3)
print(fit.scores_)
print(list(X.columns))
features = fit.transform(X)
# summarize selected features
print(features[0:5, :])

col_names = []
for col in acc_veh_df.columns:
    col_names.append(col)
features_index = np.argsort(fit.scores_)[-5:]
print(features_index)
features_names = []
for i in features_index:
    features_names.append(col_names[i])
print(features_names)


# upsampling
def upsampling(X, Y):
    sm = SMOTE(random_state=2)
    x_sm, y_sm = sm.fit_resample(X, Y.ravel())
    return x_sm, y_sm


# def randomoversampling(X, Y): # for knn
#     # define oversampling strategy
#     over = RandomOverSampler(sampling_strategy='not majority')
#     # fit and apply the transform
#     x, y = over.fit_resample(X, Y)
#     return x, y
#

X, Y = upsampling(X, Y)

X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.3, random_state=0, stratify=Y)
print(len(y_train))

clf = RandomForestClassifier(n_estimators=100)
scores = cross_validate(clf, X, Y,return_train_score=True,cv=5)
print(scores)

# knn
# start_time = time.time()
# knn = KNeighborsClassifier(n_neighbors=408)
# # 166502
# knn.fit(X_train, y_train)
# y_knn_pred = knn.predict(X_test)
# end_time = round(time.time()-start_time, 3)
# print("Accuracy:", metrics.accuracy_score(y_test, y_knn_pred))
# report = classification_report(y_true=y_test, y_pred=y_knn_pred, output_dict=True)
# report_df = pd.DataFrame(report).transpose()
# print(report_df)
# report_df.loc['time'] = [end_time, end_time, end_time, end_time]
# report_df.to_csv('knn/test_size0.7.csv', index=True)

# naive bayes classifier
# start_time = time.time()
# bayes = GaussianNB()
# bayes.fit(X_train, y_train)
# y_bayes_pred = bayes.predict(X_test)
# end_time = round(time.time()-start_time, 3)
# print("Accuracy:", metrics.accuracy_score(y_test, y_bayes_pred))
# report = classification_report(y_true=y_test, y_pred=y_bayes_pred,output_dict=True)
# report_df = pd.DataFrame(report).transpose()
# report_df.loc['time'] = [end_time, end_time, end_time, end_time]
# report_df.to_csv('naive_bayes/test_size0.7.csv', index=True)


# random forest
# start_time = time.time()
# rfc = RandomForestClassifier(n_estimators=100)
# rfc.fit(X_train, y_train)
# y_rfc_pred = rfc.predict(X_test)
# end_time = round(time.time()-start_time, 3)
# print("Accuracy:", metrics.accuracy_score(y_test, y_rfc_pred))
# report = classification_report(y_true=y_test, y_pred=y_rfc_pred,output_dict=True)
# report_df = pd.DataFrame(report).transpose()
# report_df.loc['time'] = [end_time, end_time, end_time, end_time]
# report_df.to_csv('random_forest/test_size0.7.csv', index=True)
# save the model to disk
# filename = 'finalized_model.sav'
# pickle.dump(rfc, open(filename, 'wb'))

# svm
# start_time = time.time()
# svm = SVC(kernel='rbf', C=1, degree=3)
# svm.fit(X_train, y_train)
# y_svm_pred = svm.predict(X_test)
# end_time = round(time.time()-start_time, 3)
# print("Accuracy:",metrics.accuracy_score(y_test, y_svm_pred))
# report = classification_report(y_true=y_test, y_pred=y_svm_pred,output_dict=True)
# report_df = pd.DataFrame(report).transpose()
# report_df.loc['time'] = [end_time, end_time, end_time, end_time]
# report_df.to_csv('svm/test_size0.7.csv', index=True)


# xgboost
# start_time = time.time()
# xgb_cl = xgb.XGBClassifier()
# xgb_cl.fit(X_train, y_train)
# y_xgb_pred = xgb_cl.predict(X_test)
# end_time = round(time.time()-start_time, 3)
# print("Accuracy:", metrics.accuracy_score(y_test, y_xgb_pred))
# report = classification_report(y_true=y_test, y_pred=y_xgb_pred,output_dict=True)
# report_df = pd.DataFrame(report).transpose()
# report_df.loc['time'] = [end_time, end_time, end_time, end_time]
# report_df.to_csv('xgboost/test_size0.7.csv', index=True)
