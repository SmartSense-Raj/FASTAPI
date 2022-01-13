from bentoml import env, artifacts, api, BentoService
from bentoml.adapters import DataframeInput
from bentoml.frameworks.sklearn import SklearnModelArtifact


@env(infer_pip_packages=True)
@artifacts([SklearnModelArtifact('model')])
class IrisClassifier(BentoService):

    @api(input=DataframeInput(), batch=True)
    def predict(self, df):
        dic = {0: "setosa", 1: "versicolor", 2: "virginica"}
        ans = int(self.artifacts.model.predict(df))
        return dic[ans]
