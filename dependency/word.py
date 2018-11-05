# -*- coding: utf-8 -*-
# @Time    : 2018/11/5 22:12
# @Author  : wingood
# @Email   : 122782387@qq.com

from nameko.extensions import DependencyProvider
import jieba


class JiebaDependency(DependencyProvider):
    def __init__(self):
        print("init run")

    def setup(self):
        """
            注意：由于__init__方法在依赖绑定和实例化对象事都会执行,为了防止出错，因此用setup方法进行初始化操作
        """
        print("setup run")
        self.model = jieba.Tokenizer()

    def get_dependency(self, worker_ctx):
        """
        该方法会在请求进入，工作器生命周期内执行，也就是此方法的返回值是依赖注入的实际执行方法
        :param worker_ctx:
        :return:
        """
        print("get_dependency run")

        class Inner(object):
            def __init__(self, model):
                self.model = model

            def cut(self, text):
                return self.model.cut(text)

        return Inner(self.model)
