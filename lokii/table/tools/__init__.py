from .faker import FakerTool
from .random import RandomTool
from .context import ContextTool
from .constant import ConstantTool
from .param import ParamTool
from .string import JoinTool, ReplaceTool, SlugifyTool

tools = {
    'constant': ConstantTool(),
    'param': ParamTool(),
    'context': ContextTool(),
    'faker': FakerTool(),
    'random': RandomTool(),
    'string.join': JoinTool(),
    'string.replace': ReplaceTool(),
    'string.slugify': SlugifyTool(),
}
