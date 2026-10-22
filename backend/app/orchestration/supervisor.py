"""多智能体 Supervisor。意图路由留代码策略，模型只提候选。"""


class Supervisor:
    def route(self, session: dict) -> str:
        raise NotImplementedError
