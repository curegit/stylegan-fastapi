# コアモジュールにパスを通す
import sys
from api import util
sys.path.insert(0, str(util.file_rel_path("../core")))

# アプリケーション構成を読み取る
from api import conf
config = conf.load_config()

# 使用する生成器をすべてロード
from api.model import GeneratorModel
models = {
	key: GeneratorModel.load(
		model.file,
		model.name,
		model.description,
		model.gpu
	) for key, model in config.models.items()
}

# エイリアスを張る
from api import api
StyleGANFastAPI = api.StyleGANFastAPI
