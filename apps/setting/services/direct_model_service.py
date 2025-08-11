from typing import Dict, Any, List, Union
from setting.models_provider.base_model_provider import IModelProvider
from setting.models_provider.impl.base_chat_open_ai import BaseChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage


class DirectModelService:
    """
    直接调用大语言模型服务
    """
    @staticmethod
    def chat(model_id: str, messages: list, **kwargs) -> Dict[str, Any]:
        """
        直接调用大语言模型进行对话
        :param model_id: 模型ID
        :param messages: 消息列表
        :param kwargs: 其他参数
        :return: 模型响应
        """
        from setting.models_provider.tools import get_model_instance_by_model_user_id

        # 提取用户ID（用于私有模型权限校验）
        user_id = kwargs.pop('user_id', None)

        # 获取模型实例
        model_instance = get_model_instance_by_model_user_id(model_id, user_id)
        
        if not isinstance(model_instance, BaseChatOpenAI):
            raise ValueError("该模型不支持直接对话调用")
            
        # 将 dict 消息转换为 LangChain 消息对象
        def convert_messages(msgs: List[Union[dict, BaseMessage]]) -> List[BaseMessage]:
            converted: List[BaseMessage] = []
            for m in msgs:
                if isinstance(m, BaseMessage):
                    converted.append(m)
                    continue
                role = m.get('role')
                content = m.get('content', '')
                if role == 'system':
                    converted.append(SystemMessage(content=content))
                elif role == 'assistant':
                    converted.append(AIMessage(content=content))
                else:
                    converted.append(HumanMessage(content=content))
            return converted

        lc_messages: List[BaseMessage] = convert_messages(messages)

        # 调用模型
        response = model_instance.invoke(lc_messages, **kwargs)
        
        return {
            "content": response.content,
            "metadata": response.response_metadata
        }

    @staticmethod
    def stream(model_id: str, messages: list, **kwargs):
        """
        流式对话，返回模型的分片生成器
        """
        from setting.models_provider.tools import get_model_instance_by_model_user_id

        user_id = kwargs.pop('user_id', None)
        model_instance = get_model_instance_by_model_user_id(model_id, user_id)

        if not isinstance(model_instance, BaseChatOpenAI):
            raise ValueError("该模型不支持直接对话调用")

        def convert_messages(msgs: List[Union[dict, BaseMessage]]) -> List[BaseMessage]:
            converted: List[BaseMessage] = []
            for m in msgs:
                if isinstance(m, BaseMessage):
                    converted.append(m)
                    continue
                role = m.get('role')
                content = m.get('content', '')
                if role == 'system':
                    converted.append(SystemMessage(content=content))
                elif role == 'assistant':
                    converted.append(AIMessage(content=content))
                else:
                    converted.append(HumanMessage(content=content))
            return converted

        lc_messages: List[BaseMessage] = convert_messages(messages)
        return model_instance.stream(lc_messages, **kwargs)
        
    @staticmethod
    def get_available_models() -> list:
        """
        获取所有可用的模型列表
        :return: 模型列表
        """
        from setting.models_provider.impl import ModelProvideConstants
        
        models = []
        for provider in ModelProvideConstants.__members__.values():
            provider_instance = provider.value
            if isinstance(provider_instance, IModelProvider):
                for model_type in provider_instance.get_model_type_list():
                    for model in provider_instance.get_model_list(model_type["value"]):
                        models.append({
                            "id": f"{provider.name}_{model_type['value']}_{model.name}",
                            "name": model.name,
                            "type": model_type["value"],
                            "provider": provider.name
                        })
        return models
