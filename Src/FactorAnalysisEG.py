from sklearn.datasets import load_iris
from sklearn.decomposition import FactorAnalysis
iris = load_iris()
X, y = iris.data, iris.target
factor = FactorAnalysis(n_components=4, random_state=101).fit(X)
import pandas as pd
print(pd.DataFrame(factor.components_,columns=iris.feature_names))


from sklearn.decomposition import PCA
import pandas as pd
pca = PCA().fit(X)
print('Explained variance by component: %s' % pca.explained_variance_ratio_)


print(pd.DataFrame(pca.components_,columns=iris.feature_names))
