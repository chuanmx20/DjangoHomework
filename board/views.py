import re
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
import json
from .models import User, Message
from django.core.exceptions import ValidationError

def gen_response(code: int, data: str):
        return JsonResponse({
            'code': code,
            'data': data
        }, status=code)

# Create your views here.
def message(request):

    if request.method == 'GET':
        limit = request.GET.get('limit', default='100')
        offset = request.GET.get('offset', default='0')
        if not limit.isdigit():
            return gen_response(400, '{} is not a number'.format(limit))
        if not offset.isdigit():
            return gen_response(400, '{} is not a number'.format(offset))

        return gen_response(200, [
                {
                    'title': msg.title,
                    'content': msg.content,
                    'user': msg.user.name,
                    'timestamp': int(msg.pub_date.timestamp())
                }
                for msg in Message.objects.all().order_by('-pub_date')[int(offset) : int(offset) + int(limit)]
            ])

    elif request.method == 'POST':
        # 从cookie中获得user的名字，如果user不存在则新建一个
        # 如果cookie中没有user则使用"Unknown"作为默认用户名
        name = request.COOKIES['user'] if 'user' in request.COOKIES else 'Unknown'
        user = User.objects.filter(name=name).first()
        if not user:
            user = User(name = name)
            try:
                user.full_clean()
                user.save()
            except ValidationError as e:
                return gen_response(400, "Validation Error of user: {}".format(e))


        # 验证请求的数据格式是否符合json规范，如果不符合则返回code 400
        # -------------------------------------------------------------------------------
        json_obj = None
        try:
            json_obj = json.loads(request.body)
        except ValidationError as e:
            return gen_response(400, "Validation Error of data format: {}".format(e))

        if 'title' not in json_obj.keys() or 'content' not in json_obj.keys():
            return gen_response(400, "Validation Error of data format")

        message = Message(user=user, title=json_obj["title"], content=json_obj["content"])
        try:
            message.full_clean()
            message.save()
        except ValidationError as e:
            return gen_response(400, "Validation Error of data format: {}".format(e))

        # 验证请求数据是否满足接口要求，若通过所有的验证，则将新的消息添加到数据库中
        # PS: {"title": "something", "content": "someting"} title和content均有最大长度限制
        # -------------------------------------------------------------------------------


        # 添加成功返回code 201
        return gen_response(201, "message was sent successfully")

    else:
        return gen_response(405, 'method {} not allowd'.format(request.method))


# 一键清空留言板接口 TODO
def clear_message(request):
    if request.method == 'GET':
        Message.objects.all().delete()
        return gen_response(200, 'Messages has been cleared')
    else:
        return gen_response(400, 'Request method is denied')

# 返回某个用户的所有留言 TODO
def messages_for_user(request):
    if request.method == 'GET':
        return gen_response(400, 'Request method is denied')
    else:
        username = None
        try:
            username = json.loads(request.body)['user']
        except ValidationError as e:
            return gen_response(400, f'Validation Error of data format: {e}')

        user = User.objects.filter(name=username).first()
        if (user):
            return gen_response(200, [{'title': i.title, 'content': i.content, 'timestamp': i.pub_date.timestamp()} for i in Message.objects.filter(user=user).order_by('-pub_date')])
        else:
            return gen_response(400, "User not found")