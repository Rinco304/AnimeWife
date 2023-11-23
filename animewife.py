import hoshino, random, os, re, filetype,datetime,json
from hoshino import Service, R, priv, aiorequests
from hoshino.config import RES_DIR
from hoshino.typing import CQEvent
from hoshino.util import DailyNumberLimiter


def load_group_config(group_id: str) -> int:
    filename = os.path.join(os.path.dirname(__file__), 'config', f'{group_id}.json')
    try:
        with open(filename, encoding='utf8') as f:
            config = json.load(f)
            return config
    except:
        return None

def write_group_config(group_id: str,link_id:str,wife_name:str,date:str,config) -> int:
    config_file = os.path.join(os.path.dirname(__file__), 'config', f'{group_id}.json')
    if config != None:    
        config[link_id] = [wife_name,date]
    else:
        config = {link_id:[wife_name,date]}
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False)


imgpath = os.path.join(os.path.expanduser(RES_DIR), 'img', 'wife')
_max=1
mlmt= DailyNumberLimiter(_max)
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
    groupid = ev.group_id
    user_id = ev.user_id
    wife_name = None
    today = str(datetime.date.today())
    config = load_group_config(groupid)
    if config != None:
        if str(user_id) in list(config):
            if config[str(user_id)][1] == today:
                wife_name = config[str(user_id)][0]
            else:
                del config[str(user_id)]
    
    if wife_name is None:
        result = None
        if config != None:
            for record_id in list(config):
                if config[record_id][1] != today:
                    del config[record_id]
        wife_name = random.choice(os.listdir(imgpath))
    name = wife_name.split('.')
    result = f'你今天的二次元老婆是{name[0]}哒~\n'
    try:
        wifeimg = R.img(f'wife/{wife_name}').cqcode
        result += str(wifeimg)
    except Exception as e:
        hoshino.logger.error(f'读取老婆图片时发生错误{type(e)}')
    write_group_config(groupid,user_id,wife_name,today,config)
    await bot.send(ev,result,at_sender=True)
    
    
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
async def add_food(bot,ev:CQEvent):
    uid = ev.user_id
    # if uid not in hoshino.config.SUPERUSERS:
    #     return
    u_priv = priv.get_user_priv(ev)
    if u_priv < sv.manage_priv:
        return
    if not mlmt.check(uid):
        await bot.send(ev, max_notice, at_sender=True)
        return
    name = ev.message.extract_plain_text().strip()
    ret = re.search(r"\[CQ:image,file=(.*)?,url=(.*)\]", str(ev.message))
    if not ret:
        await bot.send(ev,'请附带二次元老婆图片~')
        return
    url = ret[2]
    await download_async(url, name)
    if uid not in hoshino.config.SUPERUSERS:
        mlmt.increase(uid)
    await bot.send(ev,'信息已增加~')
    