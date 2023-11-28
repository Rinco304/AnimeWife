import hoshino, random, os, re, filetype,datetime,json
from hoshino import Service, R, priv, aiorequests
from hoshino.config import RES_DIR
from hoshino.typing import CQEvent
from hoshino.util import DailyNumberLimiter

# 加载json数据
def load_group_config(group_id: str) -> int:
    filename = os.path.join(os.path.dirname(__file__), 'config', f'{group_id}.json')
    try:
        with open(filename, encoding='utf8') as f:
            config = json.load(f)
            return config
    except:
        return None

# 写入json数据
def write_group_config(group_id: str,link_id:str,wife_name:str,date:str,config) -> int:
    config_file = os.path.join(os.path.dirname(__file__), 'config', f'{group_id}.json')
    if config != None:    
        config[link_id] = [wife_name,date]
    else:
        config = {link_id:[wife_name,date]}
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False)

# 图片路径
imgpath = os.path.join(os.path.expanduser(RES_DIR), 'img', 'wife')
# 群管理员每天可添加老婆的次数
_max=1
mlmt= DailyNumberLimiter(_max)
# 当超出次数时的提示
max_notice = f'为防止滥用，管理员一天最多可添加{_max}次，若需添加更多请使用 来杯咖啡 联系维护组'

sv_help = '''
[抽老婆] 看看今天的二次元老婆是谁
[添加老婆+人物名称+图片] 群管理员每天可以添加一次人物
※为防止bot被封号和数据污染请勿上传太涩与功能无关的图片※
'''.strip()

sv = Service(
    name = '抽老婆',  #功能名
    use_priv = priv.NORMAL, #使用权限   
    manage_priv = priv.ADMIN, #管理权限
    visible = True, #可见性
    enable_on_default = True, #默认启用
    bundle = '娱乐', #分组归类
    help_ = sv_help #帮助说明
    )

@sv.on_fullmatch('抽老婆')
async def animewife(bot, ev: CQEvent):
    # 获取QQ群、群用户QQ信息
    groupid = ev.group_id
    user_id = ev.user_id
    wife_name = None
    # 获取今天的日期，转换为字符串格式
    today = str(datetime.date.today())
    # 载入群组信息
    config = load_group_config(groupid)
    if config != None:
        # 检查用户QQ号是否在配置中
        if str(user_id) in list(config):
            # 检查用户的老婆信息是否是今天
            if config[str(user_id)][1] == today:
                # 是今天，直接返回（一天只能有一个老婆）
                wife_name = config[str(user_id)][0]
            else:
                # 如果不是今天的信息，删除该用户信息重新获取老婆信息
                del config[str(user_id)]
    
    # 如果没有老婆信息，则进行随机选择
    if wife_name is None:
        result = None
        if config != None:
            # 删除不是今天的所有老婆信息
            for record_id in list(config):
                if config[record_id][1] != today:
                    del config[record_id]
        # 随机选择一张老婆的图片，用于获取图片名
        wife_name = random.choice(os.listdir(imgpath))
    # 分割文件名和扩展名，只取图片名返回给用户
    name = wife_name.split('.')
    # 生成返回结果
    result = f'你今天的二次元老婆是{name[0]}哒~\n'
    try:
        # 尝试读取老婆图片，并添加到结果中
        wifeimg = R.img(f'wife/{wife_name}').cqcode
        result += str(wifeimg)
    except Exception as e:
        hoshino.logger.error(f'读取老婆图片时发生错误{type(e)}')
    # 将选择的老婆信息写入群组配置
    write_group_config(groupid,user_id,wife_name,today,config)
    # 发送消息
    await bot.send(ev,result,at_sender=True)
    
#下载图片
async def download_async(url: str, name: str):
    resp= await aiorequests.get(url, stream=True)
    if resp.status_code == 404:
        raise ValueError('文件不存在')
    content = await resp.content
    try:
        extension = filetype.guess_mime(content).split('/')[1]
    except:
        raise ValueError('不是有效文件类型')
    abs_path = os.path.join(imgpath, f'{name}.{extension}')
    with open(abs_path, 'wb') as f:
        f.write(content)

@sv.on_prefix(('添老婆','添加老婆'))
@sv.on_suffix(('添老婆','添加老婆'))
async def add_wife(bot,ev:CQEvent):
    # 获取QQ信息
    uid = ev.user_id
    # 此注释的代码是仅限bot超级管理员使用，有需可启用并将下面判断权限的代码注释掉
    # if uid not in hoshino.config.SUPERUSERS:
    #     return

    # 判断权限，只有用户为群管理员或为bot设置的超级管理员才能使用
    u_priv = priv.get_user_priv(ev)
    if u_priv < sv.manage_priv:
        return
    # 检查用户今天是否已添加过老婆信息
    if not mlmt.check(uid):
        await bot.send(ev, max_notice, at_sender=True)
        return
    # 提取老婆的名字
    name = ev.message.extract_plain_text().strip()
    # 获得图片信息
    ret = re.search(r"\[CQ:image,file=(.*)?,url=(.*)\]", str(ev.message))
    if not ret:
        # 未获得图片信息
        await bot.send(ev,'请附带二次元老婆图片~')
        return
    # 获取下载url
    url = ret[2]
    # 下载图片保存到本地
    await download_async(url, name)
    # 如果不是超级管理员，增加用户的添加老婆次数（管理员可一天增加多次）
    if uid not in hoshino.config.SUPERUSERS:
        mlmt.increase(uid)
    await bot.send(ev,'信息已增加~')
    
