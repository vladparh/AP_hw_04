from catboost import CatBoostClassifier


catboost = CatBoostClassifier()
catboost.load_model('ML_model/model_catboost')


def model_predict(x):
    predict = catboost.predict(x)
    return predict


