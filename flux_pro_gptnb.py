import requests
import plugins
from plugins import *
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from common.log import logger

BASE_URL = 'https://goapi.gptnb.ai/v1/images/generations'

@plugins.register(name="flux_pro_gptnb",
                  desc="flux_pro_gptnb插件",
                  version="1.0",
                  author="Ray",
                  desire_priority=100)
class flux_pro_pic(Plugin):
    content = None
    config_data = None

    def __init__(self):
        super().__init__()
        self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
        logger.info(f"[{__class__.__name__}] inited")

    def get_help_text(self, **kwargs):
        help_text = f"输入“FP”开头，获取相关图片(flux pro)"
        return help_text

    def on_handle_context(self, e_context: EventContext):
        # 只处理文本消息
        if e_context['context'].type != ContextType.TEXT:
            return
        self.content = e_context["context"].content.strip()

        isExist = self.content.startswith("FP")

        if isExist:
            logger.info(f"[{__class__.__name__}] 收到消息: {self.content}")
            # 读取配置文件
            config_path = os.path.join(os.path.dirname(__file__), "config.json")
            if os.path.exists(config_path):
                with open(config_path, 'r') as file:
                    self.config_data = json.load(file)
            else:
                logger.error(f"请先配置{config_path}文件")
                return

            reply = Reply()
            result = self.flux_pro_pic()
            if result != None:
                reply.type = ReplyType.IMAGE_URL
                reply.content = result
                e_context["reply"] = reply
                e_context.action = EventAction.BREAK_PASS
            else:
                reply.type = ReplyType.ERROR
                reply.content = "获取失败,等待修复⌛️"
                e_context["reply"] = reply
                e_context.action = EventAction.BREAK_PASS

    def flux_pro_pic(self):
        logger.info(self.config_data)

        key = self.config_data.get('flux_pro_api_token', '')

        logger.info(key)

        try:

            payload = {
                "prompt": self.content,
                "n": 1,
                "model": "flux-pro",
                "size": "1024x1024"
            }
            headers = {
                'Authorization': 'Bearer '+ key,
                'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
                'Content-Type': 'application/json'
            }
            
            logger.info(headers)

            response = requests.post(BASE_URL, json=payload, headers=headers).json()

            logger.info(response)

            img = response['data'][0]['url']
            logger.info(img)
            return img
        except Exception as e:
                logger.error(f"接口抛出异常:{e}")
        return None