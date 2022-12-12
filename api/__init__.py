from fastapi import FastAPI

# コアモジュールにパスを通す
import sys
from api.util import file_rel_path
sys.path.insert(0, str(file_rel_path("../core")))

# アプリケーション構成を読み取る
from api.conf import load_config
config = load_config()

# 使用する生成器をすべてロード
from api.model import GeneratorModel
models = {
	key: GeneratorModel.load(model.file, model.name, model.description) for key, model in config.models.items()
}

