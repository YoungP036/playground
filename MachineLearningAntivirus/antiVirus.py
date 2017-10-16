import pandas as pd
import numpy as np 
import pickle
import sklearn.ensemble as ske 
from sklearn import cross_validation, tree, linear_model
from sklearn.feature_selection import SelectFromModel
from sklearn.externals import joblib
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import confusion_matrix

####ALL FEATURES####
# Name|md5|Machine|SizeOfOptionalHeader|Characteristics|MajorLinkerVersion|MinorLinkerVersion
# |SizeOfCode|SizeOfInitializedData|SizeOfUninitializedData|AddressOfEntryPoint|BaseOfCode
# |BaseOfData|ImageBase|SectionAlignment|FileAlignment|MajorOperatingSystemVersion
# |MinorOperatingSystemVersion|MajorImageVersion|MinorImageVersion|MajorSubsystemVersion
# |MinorSubsystemVersion|SizeOfImage|SizeOfHeaders|CheckSum|Subsystem|DllCharacteristics
# |SizeOfStackReserve|SizeOfStackCommit|SizeOfHeapReserve|SizeOfHeapCommit|LoaderFlags
# |NumberOfRvaAndSizes|SectionsNb|SectionsMeanEntropy|SectionsMinEntropy|SectionsMaxEntropy
# |SectionsMeanRawsize|SectionsMinRawsize|SectionMaxRawsize|SectionsMeanVirtualsize
# |SectionsMinVirtualsize|SectionMaxVirtualsize|ImportsNbDLL|ImportsNb|ImportsNbOrdinal
# |ExportNb|ResourcesNb|ResourcesMeanEntropy|ResourcesMinEntropy|ResourcesMaxEntropy
# |ResourcesMeanSize|ResourcesMinSize|ResourcesMaxSize|LoadConfigurationSize|VersionInformationSize|legitimate

#load data
data = pd.read_csv('data.csv',sep='|')
X=data.drop(['Name','md5','legitimate'],axis=1).values
y=data['legitimate'].values

print("Based on %i total features\n" % X.shape[1])

#select features with tree classifier
fsel = ske.ExtraTreesClassifier().fit(X,y)
model = SelectFromModel(fsel, prefit=True)
X_new = model.transform(X)
nb_features=X_new.shape[1]

X_train, X_test, y_train, y_test = cross_validation.train_test_split(X_new, y, test_size=0.2)

features=[]

print('%i features are important:\n' % nb_features)

#sort
indices = np.argsort(fsel.feature_importances_)[::-1][:nb_features]
for f in range(nb_features):
	print("%d, feature %s (%f)" % (f+1, data.columns[2+indices[f]], fsel.feature_importances_[indices[f]]))

#take care of feature order
for f in sorted(np.argsort(fsel.feature_importances_)[::-1][:nb_features]):
	features.append(data.columns[2+f])

#compare some algorithms
algorithms={
	"DecisionTree": tree.DecisionTreeClassifier(max_depth=10),
	"RandomForest": ske.RandomForestClassifier(n_estimators=50),
	"GradientBoosting": ske.GradientBoostingClassifier(n_estimators=50),
	"AdaBoost": ske.AdaBoostClassifier(n_estimators=100),
	"GNB": GaussianNB()
}

results={}
print("Alg Comparison Test")
for algo in algorithms:
	clf=algorithms[algo]
	clf.fit(X_train, y_train)
	score=clf.score(X_test,y_test)
	print("%s : %f %%" % (algo, score*100))
	results[algo]=score

winner = max(results,key=results.get)
print("\n Winner is %s with %f %% success" % (winner,results[winner]*100))

print("Saving")
joblib.dump(algorithms[winner],'classifier/classifier.pkl')
open('classifier/features.pk1','w').write(pickle.dumps(features))
print('Saved')

#expose false and true positive rates
clf = algorithms[winner]
res=clf.predict(X_test)
mt=confusion_matrix(y_test,res)
print("False positive rate : %f %%" % ((mt[0][1] / float(sum(mt[0])))*100))
print("False negative rate : %f %%" % ((mt[1][0] / float(sum(mt[1]))*100)))
# False positive rate : 0.489766 %
# False negative rate : 0.840131 %