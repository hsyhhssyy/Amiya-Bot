from amiyabot import AmiyaBot, KOOKBotInstance
from amiyabot.database import *
from core.config import cos_config
from core.database import config, is_mysql
from core.cosChainBuilder import COSQQGroupChainBuilder
from typing import Union

from amiyabot.adapters.tencent.qqGuild import qq_guild_shards
from amiyabot.adapters.tencent.qqGlobal import qq_global
from amiyabot.adapters.tencent.qqGroup import qq_group, QQGroupChainBuilderOptions
from amiyabot.adapters.cqhttp import cq_http
from amiyabot.adapters.mirai import mirai_api_http
from amiyabot.adapters.onebot.v11 import onebot11
from amiyabot.adapters.onebot.v12 import onebot12
from amiyabot.adapters.comwechat import com_wechat
from amiyabot.adapters.test import test_instance

db = connect_database('amiya_bot' if is_mysql else 'database/amiya_bot.db', is_mysql, config)


class BotBaseModel(ModelClass):
    class Meta:
        database = db


@table
class Admin(BotBaseModel):
    account: Union[CharField, str] = CharField(unique=True)
    remark: Union[CharField, str] = CharField(null=True)

    @classmethod
    def is_super_admin(cls, user_id: str):
        return bool(cls.get_or_none(account=user_id))


@table
class BotAccounts(BotBaseModel):
    appid: str = CharField(unique=True)
    token: str = CharField()
    private: int = SmallIntegerField(default=0)
    is_start: int = SmallIntegerField(default=1)
    is_main: int = SmallIntegerField(default=0)
    console_channel: str = CharField(null=True)
    adapter: str = CharField(default='qq_guild')

    host: str = CharField(null=True)
    ws_port: int = IntegerField(null=True)
    http_port: int = IntegerField(null=True)
    client_secret: str = CharField(null=True)

    sandbox: int = SmallIntegerField(default=0)
    shard_index: int = SmallIntegerField(default=0)
    shards: int = SmallIntegerField(default=1)

    @classmethod
    def get_all_account(cls):
        select: List[cls] = cls.select()
        account = []

        for item in select:
            if not item.is_start:
                continue

            conf = cls.build_conf(item)
            account.append(AmiyaBot(**conf))

        return account

    @classmethod
    def build_conf(cls, item):
        net_adapters = {
            'mirai_api_http': mirai_api_http,
            'cq_http': cq_http,
            'onebot11': onebot11,
            'onebot12': onebot12,
            'com_wechat': com_wechat,
        }
        tx_adapters = {
            'qq_guild': qq_guild_shards,
            'qq_group': qq_group,
            'qq_global': qq_global,
        }

        conf = {
            'appid': item.appid,
            'token': item.token,
            'private': bool(item.private),
        }

        if item.adapter in net_adapters:
            conf['adapter'] = net_adapters[item.adapter](
                host=item.host,
                ws_port=item.ws_port,
                http_port=item.http_port,
            )

        if item.adapter in tx_adapters:
            adapter = tx_adapters[item.adapter]
            shards = {
                'shard_index': item.shard_index,
                'shards': item.shards,
            }
            if item.adapter == 'qq_guild':
                conf['adapter'] = adapter(**shards, sandbox=bool(item.sandbox))
            else:
                opt = QQGroupChainBuilderOptions(
                    item.host or '0.0.0.0', item.http_port or 8086, './resource/group_temp'
                )
                if cos_config.activate:
                    conf['adapter'] = adapter(
                        item.client_secret,
                        default_chain_builder=COSQQGroupChainBuilder(opt),
                        **shards,
                    )
                else:
                    conf['adapter'] = adapter(
                        item.client_secret,
                        default_chain_builder_options=opt,
                        **shards,
                    )

        if item.adapter == 'websocket':
            conf['adapter'] = test_instance(item.host, item.ws_port)

        if item.adapter == 'kook':
            conf['adapter'] = KOOKBotInstance

        return conf


@table
class FunctionUsed(BotBaseModel):
    function_id: str = CharField(primary_key=True)
    use_num: int = IntegerField(default=1)


@table
class DisabledFunction(BotBaseModel):
    function_id: str = CharField(null=True)
    channel_id: str = CharField(null=True)


@table
class OperatorIndex(BotBaseModel):
    name: Union[CharField, str] = CharField()
    en_name: Union[CharField, str] = CharField()
    rarity: Union[CharField, str] = CharField()
    classes: Union[CharField, str] = CharField()
    classes_sub: Union[CharField, str] = CharField()
    classes_code: Union[CharField, str] = CharField()
    type: Union[CharField, str] = CharField()


@table
class OperatorConfig(BotBaseModel):
    operator_name: str = CharField()
    operator_type: int = IntegerField()


@table
class Pool(BotBaseModel):
    pool_name: Union[CharField, str] = CharField(unique=True)
    pickup_6: Union[CharField, str] = CharField(null=True, default='')
    pickup_5: Union[CharField, str] = CharField(null=True, default='')
    pickup_4: Union[CharField, str] = CharField(null=True, default='')
    pickup_s: Union[CharField, str] = CharField(null=True, default='')
    limit_pool: int = IntegerField()


@table
class TextReplace(BotBaseModel):
    user_id: str = CharField()
    group_id: str = CharField()
    origin: Union[TextField, str] = TextField()
    replace: Union[TextField, str] = TextField()
    in_time: int = BigIntegerField()
    is_user_only: int = IntegerField(default=0)
    is_global: int = IntegerField(default=0)
    is_active: int = IntegerField(default=1)


@table
class TextReplaceSetting(BotBaseModel):
    text: str = CharField(unique=True)
    status: int = IntegerField()
