import os
import shutil
import json
from django.shortcuts import render, HttpResponse
from django.utils.encoding import escape_uri_path
from django.db import transaction
from web_pan.settings import files_folder
from disk import models


# Create your views here.


def logined(func):
    def wrapper(request, *args, **kwargs):
        session = request.session.get('user')
        if not session:
            return render(request, 'login.html')
        else:
            return func(request, *args, **kwargs)

    return wrapper


def api_check(func):
    def wrapper(request, *args, **kwargs):
        session = request.session.get('user')
        if not session:
            res = dict(
                state_code=-3,
                error_msg="登陆过期"
            )
            return HttpResponse(json.dumps(res, ensure_ascii=False), content_type='application/json')
        else:
            return func(request, *args, **kwargs)

    return wrapper


def login(request):
    if request.method == 'GET':
        if request.session.get('user'):
            return render(request, 'index.html')
        return render(request, 'login.html')
    else:
        req = json.loads(request.body)
        user = req.get('username')
        pwd = req.get('pwd')
        obj_user = models.Users.objects.filter(user_name=user).all()
        if not obj_user:
            res = dict(
                state_code=1,
                error_msg="用户不存在"
            )
        else:
            password = obj_user.first().password
            if str(pwd) != str(password):
                res = dict(
                    state_code=2,
                    error_msg="密码错误"
                )
            else:
                request.session['user'] = user
                request.session.set_expiry(600)
                res = dict(
                    state_code=0,
                    error_msg="密码错误"
                )
        return HttpResponse(json.dumps(res, ensure_ascii=False), content_type='application/json')


def logout(request):
    if request.session.get('user'):
        del request.session['user']
    return render(request, 'login.html')


@logined
def index(request):
    return render(request, 'index.html')


@api_check
def get_dir_list(request):
    user = request.session.get('user')
    obj_dir = models.Dirs.objects.filter(user_name=user).all()
    dir_list = []
    for dirs in obj_dir:
        user_dir = dirs.dir
        dir_list.append(user_dir)
    res = dict(
        state_code=0,
        error_msg='ok',
        data={
            "dir_list": dir_list
        }
    )
    return HttpResponse(json.dumps(res, ensure_ascii=False), content_type='application/json')


@api_check
def user_mkdir(request):
    req = json.loads(request.body)
    dir_name = req.get('dir_name')
    if not dir_name:
        res = dict(
            state_code=-2,
            error_msg='参数错误'
        )
        return HttpResponse(json.dumps(res, ensure_ascii=False), content_type='application/json')
    dir_path = os.path.join(files_folder, dir_name)
    if os.path.exists(dir_path):
        res = dict(
            state_code=1,
            error_msg="该目录已被使用"
        )
    else:
        user = request.session.get('user')
        if user:
            models.Dirs.objects.create(
                user_name=user,
                dir=dir_name
            )
            os.mkdir(dir_path)
            res = dict(
                state_code=0,
                error_msg='ok'
            )
        else:
            res = dict(
                state_code=-3,
                error_msg="登陆过期"
            )
    return HttpResponse(json.dumps(res, ensure_ascii=False), content_type='application/json')


@api_check
def del_dir(request):
    req = json.loads(request.body)
    dir_name = req.get('dir_name')
    if not dir_name:
        res = dict(
            state_code=-2,
            error_msg='参数错误'
        )
        return HttpResponse(json.dumps(res, ensure_ascii=False), content_type='application/json')
    dir_path = os.path.join(files_folder, dir_name)
    if not os.path.exists(dir_path):
        res = dict(
            state_code=1,
            error_msg='目录不存在'
        )
    else:
        with transaction.atomic():
            obj_dir = models.Dirs.objects.filter(dir=dir_name).all()
            if obj_dir:
                obj_dir.delete()
            shutil.rmtree(dir_path)
        res = dict(
            state_code=0,
            eror_msg='ok'
        )
    return HttpResponse(json.dumps(res, ensure_ascii=False), content_type='application/json')


@api_check
def upload_file(request):
    dir_name = request.POST.get('dir_name')
    if not dir_name:
        res = dict(
            state_code=-2,
            error_msg='参数错误'
        )
        return HttpResponse(json.dumps(res, ensure_ascii=False), content_type='application/json')
    dir_path = os.path.join(files_folder, dir_name)
    if not os.path.exists(dir_path):
        res = dict(
            state_code=1,
            error_msg='目录不存在'
        )
        return HttpResponse(json.dumps(res, ensure_ascii=False), content_type='application/json')
    # 获取上传的文件,如果没有文件,则默认为None;
    File = request.FILES.get("file", None)
    if File is None:
        res = dict(
            state_code=-2,
            error_msg='参数错误'
        )
        return HttpResponse(json.dumps(res, ensure_ascii=False), content_type='application/json')
    file_name = File.name
    file_path = os.path.join(dir_path, file_name)
    # 打开特定的文件进行二进制的写操作;
    with open(file_path, 'wb+') as f:
        # 分块写入文件;
        for chunk in File.chunks():
            f.write(chunk)
    res = dict(
        state_code=0,
        error_msg='ok',
    )
    return HttpResponse(json.dumps(res), content_type='application/json')


@api_check
def query_file(request):
    req = json.loads(request.body)
    dir_name = req.get('dir_name')
    dir_path = os.path.join(files_folder, dir_name)
    cmd_info = os.popen("ls -l -h {}".format(dir_path)).read()
    file_list = cmd_info.split('\n')[1:-1]
    file_list_data = []
    for file_info_cmd in file_list:
        file_info_list = file_info_cmd.split(' ')
        file_info = list(filter(None, file_info_list))
        file = file_info[-1]
        file_size = file_info[4]
        name_type = file.rsplit('.', 1)
        if len(name_type) < 2:
            name_type.append('未知')
        file_name, file_type = name_type
        file_list_data.append({
            'file_name': file_name,
            'file_type': file_type,
            'file_size': file_size
        })
    res = dict(
        state_code=0,
        error_msg='ok',
        data={
            'file_list': file_list_data
        }
    )
    return HttpResponse(json.dumps(res, ensure_ascii=False), content_type='application/json')


@api_check
def del_file(request):
    req = json.loads(request.body)
    dir_name = req.get('dir_name')
    file_name = req.get('file_name')
    file_type = req.get('file_type')
    file = file_name + '.' + file_type if file_type != '未知' else file_name
    file_path = os.path.join(os.path.join(files_folder,dir_name),file)
    if not os.path.exists(file_path):
        res = dict(
            state_code=1,
            error_msg='文件不存在'
        )
    else:
        os.remove(file_path)
        res = dict(
            state_code=0,
            error_msg='ok'
        )
    return HttpResponse(json.dumps(res, ensure_ascii=False), content_type='application/json')


@api_check
def download_file(request):
    req = json.loads(request.body)
    dir_name = req.get('dir_name')
    file_name = req.get('file_name')
    file_type = req.get('file_type')
    file = file_name+'.'+file_type if file_type != '未知' else file_name
    file_path = os.path.join(os.path.join(files_folder,dir_name),file)
    if not os.path.exists(file_path):
        res = dict(
            state_code=1,
            error_msg='文件不存在'
        )
        return HttpResponse(json.dumps(res, ensure_ascii=False), content_type='application/json')
    from django.http import StreamingHttpResponse
    file_size = os.path.getsize(file_path)
    def file_iterator(file_name, chunk_size=512):  # 用于形成二进制数据
        with open(file_name, 'rb') as f:
            while True:
                c = f.read(chunk_size)
                if c:
                    yield c
                else:
                    break
    the_file_name = file_path  # 要下载的文件路径
    res = file_iterator(the_file_name)
    response = StreamingHttpResponse(res)  # 这里创建返回
    response['Content-Type'] = 'application/octet-stream; charset=UTF-8'  # 注意格式
    response['Content-Length'] = file_size
    response['Content-Disposition'] = 'attachment;filename="{}"'.format(escape_uri_path(file))  # 注意filename 这个是下载后的名字
    return response
