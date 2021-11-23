[TOC]

## python搭建Web服务器

### 概览

客户端从发送一个 HTTP 请求到 Flask 处理请求，分别经过了 Web服务器层，WSGI层，Web框架层，这三个层次，他们的关系如下图所示。

![Web服务器，Web框架与 WSGI 的三层关系](Web服务器、Web框架与 WSGI 的三层关系.png)

本文搭建Web服务器涉及到的组成部分主要有，Nginx、Gunicorn、Flask和gevent。

### WSGI层

- WSGI 不是服务器，也不是用于与程序交互的API，更不是真实的代码，WSGI 只是一种接口，它只适用于 Python 语言，其全称为 Web Server Gateway Interface，定义了 Web服务器和 Web应用之间的接口规范。也就是说，只要 Web服务器和 Web应用都遵守WSGI协议，那么 Web服务器和 Web应用就可以随意的组合。

- 下面的代码展示了 Web服务器是如何与 Web应用组合在一起的

  ```python
  def application(env, start_response):
      start_response('200 OK', [('Content-Type', 'text/html')])
      return [b"Hello World"]
  ```

  方法 `application`由 Web服务器调用，参数`env`，`start_response` 由 Web服务器实现并传入。其中，`env`是一个字典，包含了类似 HTTP_HOST，HOST_USER_AGENT，SERVER_PROTOCO 等环境变量。`start_response`则是一个方法，该方法接受两个参数，分别是`status`，`response_headers`。`application`方法的主要作用是，设置 http 响应的状态码和 Content-Type 等头部信息，并返回响应的具体结果。

  上述代码就是一个完整的 WSGI 应用，当一个支持 WSGI 的 Web服务器接收到客户端的请求后，便会调用这个 `application` 方法。WSGI 层并不需要关心`env`，`start_response` 这两个变量是如何实现的，就像在 `application` 里面所做的，直接使用这两个变量即可。


### Web服务器

对于传统的客户端 - 服务器架构，其请求的处理过程是，客户端向服务器发送请求，服务器接收请求并处理请求，然后给客户端返回响应。Web服务器是一类特殊的服务器，其作用是主要是接收 HTTP 请求并返回响应。常见的 Web服务器有 Nginx，Apache，IIS等。

Flask自带了一个Web服务器，是在其必备依赖Werkzeug中实现的。所以在开发时，可以直接启动服务，而不需要通过Tomcat或Apache。不过，由于内置服务器自身处理能力有限，在生产环境中还是需要使用其他的Web服务器。这也是Flask官方建议的。Flask常用的Web服务器包括Gunicorn、uWSGI等，它们都支持WSGI。

#### Gunicorn
Gunicorn是一个UNIX上被广泛使用的高性能的Python WSGI UNIX HTTP Server。和大多数的Web框架兼容，并具有实现简单，轻量级，高性能等特点。

-   安装

    `pip install gunicorn`

-   gunicorn + flask 简单示例

gunicorn_demo.py

```python
from flask import Flask
app = Flask(__name__)
@app.route('/demo', methods=['GET'])
def demo():
    return "gunicorn and flask demo."
```
运行  `gunicorn gunicorn_demo:app`

-   生产环境，起停和状态的监控最好用supervisior之类的监控工具，然后在gunicorn的前端放置一个http proxy server, 譬如Nginx。

-   gunicorn 默认使用同步阻塞的网络模型(-k sync)，对于大并发的访问可能表现不够好， 它还支持其它更好的模式，比如：gevent或meinheld。

#### gevent

- **GIL**

  全称是Global Interpreter Lock(全局解释器锁)，来源是python设计之初的考虑，为了数据安全所做的决定。

  在Python多线程下，每个线程的执行方式：1.获取GIL 2.执行代码直到sleep或者是python虚拟机将其挂起。3.释放GIL

  可见，某个线程想要执行，必须先拿到GIL，我们可以把GIL看作是“通行证”，并且在一个python进程中，GIL只有一个。拿不到通行证的线程，就不允许进入CPU执行。所以，每个CPU在同一时间只能执行一个线程，在单核CPU下的多线程其实都只是并发，不是并行。

- **协程**

  协程，又称微线程，纤程，英文名Coroutine。协程的作用是在执行函数A时可以随时中断去执行函数B，然后中断函数B继续执行函数A（可以自由切换）。但这一过程并不是函数调用，这一整个过程看似像多线程，然而协程只有一个线程执行。

  协程相比于线程，执行效率极高，因为子程序切换（函数）不是线程切换，由程序自身控制，没有切换线程的开销。所以与多线程相比，线程的数量越多，协程性能的优势越明显。

  协程不需要多线程的锁机制，因为只有一个线程，也不存在同时写变量冲突，在控制共享资源时也不需要加锁，因此执行效率高很多。

  一个简单的协程例子（在Python3.5以上版本使用）

  ```
  #-*- coding:utf8 -*-
  import asyncio

  async def test(i):
      print('test_1', i)
      await asyncio.sleep(1)
      print('test_2', i)

  if __name__ == '__main__':
      loop = asyncio.get_event_loop()
      tasks = [test(i) for i in range(3)]
      loop.run_until_complete(asyncio.wait(tasks))
      loop.close()
  ```

- **gevent模块**

  Gevent是一个基于Greenlet实现的网络库，通过greenlet实现协程。基本思想是一个greenlet就认为是一个协程，当一个greenlet遇到IO操作的时候，比如访问网络，就会自动切换到其他的greenlet，等到IO操作完成，再在适当的时候切换回来继续执行。由于IO操作非常耗时，经常使程序处于等待状态，有了gevent为我们自动切换协程，就保证总有greenlet在运行，而不是等待IO操作。

  开发者可以在不改变编程习惯的同时，以同步的方式编写异步IO代码。

- **安装 **

  `pip install gevent`

- **gevent配合gunicorn**

  配置gunicorn的配置文件gunicorn.py

  ```
  import gevent.monkey

  gevent.monkey.patch_all()

  bind = '0.0.0.0:8004'
  workers = 4
  backlog = 2048
  worker_class = 'gunicorn.workers.ggevent.GeventWorker'
  x_forwarded_for_header = 'X-FORWARDED-FOR'
  proc_name = 'gunicorn.proc'
  pidfile = 'logs/gunicorn.pid'
  ```

  使用gunicorn来启动

  `gunicorn -c gunicorn.py gunicorn_demo:app`

#### nginx

作为反向代理服务器

配置`proxy_pass`

```shell
server {
	listen       8001 default_server;
	server_name  10.2.1.92;
	root         /usr/share/nginx/html;
	
	include /etc/nginx/default.d/*.conf;
	
	location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    
    error_page 404 /404.html;
    	location = /40x.html {
    }

	error_page 500 502 503 504 /50x.html;
      location = /50x.html {
    }
}
```




### Web框架层

Web框架的作用主要是方便我们开发 Web应用程序，HTTP请求的动态数据就是由Web框架层来提供的。常见的 Web框架有Flask，Django等。

#### [Flask](https://dormousehole.readthedocs.io/en/latest/)

一个简单的例子

```
from flask import Flask
app = Flask(__name__)

@app.route('/hello')
def hello_world():
    return 'Hello World!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
```

以上简单的几行代码，就创建了一个 Web应用程序对象 `app`。`app` 监听机器所有 ip 的 8080 端口，接受用户的请求连接。我们知道，HTTP 协议使用 URL 来定位资源，上面的程序会将路径 `/hello` 的请求交由 `hello_world` 方法处理，`hello_world` 返回 ‘Hello World!’ 字符串。对于 web框架的使用者来说，他们并不关心如何接收 HTTP 请求，也不关心如何将请求路由到具体方法处理并将响应结果返回给用户。Web框架的使用者在大部分情况下，只需要关心如何实现业务的逻辑即可。

#### [Flask-RESTful](http://www.pythondoc.com/Flask-RESTful/index.html)

Flask-RESTful 是一个 Flask 扩展，它添加了快速构建 REST APIs 的支持。它当然也是一个能够跟你现有的ORM/库协同工作的轻量级的扩展。

一个最小的 Flask-RESTful API 像这样:

```python
from flask import Flask
from flask.ext import restful

app = Flask(__name__)
api = restful.Api(app)

class HelloWorld(restful.Resource):
    def get(self):
        return {'hello': 'world'}

api.add_resource(HelloWorld, '/')

if __name__ == '__main__':
    app.run(debug=True)
```

具体如何在 Flask 中使用 Flask-RESTful参照[Flask-RESTful](http://www.pythondoc.com/Flask-RESTful/index.html)

 #### [Flask-RESTX](https://flask-restx.readthedocs.io/en/latest/#)

Flask-RESTX与Flask-RESTful的接口基本一致，相比Flask-RESTful，它可以自动生成Swagger API文档，可支持更多配置，具体实现参照文档[Flask-RESTX-Swagger文档](https://flask-restx.readthedocs.io/en/latest/swagger.html)

#### 数据模型models

sqlalchemy是python web项目中最普遍使用的ORM工具库

创建一个新的表模型如下

- 创建模型类，继承自BaseModel，如果需记录创建时间、创建人则继承CreationMixin，如果需记录更新时间、更新人则继承UpdationMixin

  ```python
  class Demo(BaseModel, CreationMixin, UpdationMixin):
    __tablename__ = "dat_demo"
    __table_args__ = {'comment': 'demo表'}

    demo_id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='demo id')
    demo_name = db.Column(db.String(15), nullable=False, unique=True, index=True, comment="demo名称")
    demo_state = db.Column(db.String(10), nullable=False, default=ResourceState.active.name, comment='demo状态')

    def __str__(self):
        return self.demo_name
  ```


- 如果需要记录该表日志，则可以配置增删改监听事件函数

  ```python
  event.listen(Demo, 'after_insert', partial(audit_log, constants.Operation.create))
  event.listen(Demo, 'after_update', partial(audit_log, constants.Operation.update))
  event.listen(Demo, 'after_delete', partial(audit_log, constants.Operation.delete))
  ```

- 用户认证和授权可直接使用demo中的ResourceModel、Permission、Role、User，实现基于角色的权限访问控制。


##### Flask-Migrate

创建模型完成后，可使用该工具自动创建或更新数据表

- 初始化migrate仓库  `python manage.py db init`
- 每次更新数据模型后执行，生成一个迁移脚本 `python manage.py db migrate`，生成迁移脚本完成后，务必查看该脚本是否无误
- 根据记录文件生成数据表 `python manage.py db upgrade`

#### templates 

前后端不分离的情况，需要配置templates又接口返回html。

前后端分离的情况下，不需要开发templates，直接返回json数据。

##### [flask-admin](https://flask-admin.readthedocs.io/en/latest/)

flask-admin是一个简单易用的flask扩展，基于数据模型迅速生成后台管理页面。配置简单，如下：

```python
class DemoView(BaseModelView):
    can_edit = True
    column_list = ['create_user', 'created_at', 'update_user', 'updated_at']
    column_filters = column_searchable_list = []
    column_sortable_list = ['created_at', 'updated_at']
    column_default_sort = ('updated_at', True)
    column_details_list = []
    form_columns = []
    form_extra_fields = {}
    inline_models = []
    form_choices = column_choices = {}

    def on_model_change(self, form, obj, is_created=False):
        ...
        
        
demo_view = DemoView(DemoModel, db.session)
```

继承自BaseModelView，配置其他可选参数如列表页字段、筛选项字段、查询项字段、排序项字段等。

可配置参数参照[`flask_admin.model`](https://flask-admin.readthedocs.io/en/latest/api/mod_model/#flask_admin.model.BaseModelView)

然后将demo_view与admin绑定 `admin.add_view(demo_view)`

##### [Bootstrap-Flask](https://bootstrap-flask.readthedocs.io/en/stable/)

该库需要开发者自行配置views和templates，可以自由选择bootstrap样式和自定义样式， 同时支持快速渲染表单、表格等，相比于flask-admin自由度更高。

模板中渲染表单可使用

`{{ render_form(telephone_form) }}`

模板中渲染表格可使用

```
{{ render_table(messages, show_actions=True,primary_key="user_id",                view_url=url_for('web_v1.view_message', message_id=':primary_key'),                edit_url=url_for('web_v1.edit_message', message_id=':primary_key'),                delete_url=url_for('web_v1.delete_message', message_id=':primary_key')) }}
```

#### views

对于前后端分离的接口，主要遵循RESTFUL软件架构风格，提供资源创建接口、资源查询接口，资源批量查询接口、资源更新接口即可。

示例如下

```python
@demo_api.route('')
class Demos(Resource):
    logger = logger.getChild('Demos')

    @demo_api.expect(json_parser_with_auth)
    @demo_api.marshal_with(crud_resp)
    @check_request(json_parser_with_auth, creation_schema)
    @authentication_required(
        resource_name=constants.ResourceEnum.demo.name,
        permission_name=constants.Operation.create.name)
    @sign_required
    def post(self):
        """资源创建接口"""
        demo = DemoModel(demo_name=g.args['demo_name'])
        try:
            demo.save(user=g.user)
        except errors.Error as e:
            logger.log(level=e.log_level, msg=e.log)
            return e.to_dict_response()
        return {
            'return_code': 200,
            'return_msg': '',
            'data': demo
        }

    search_parser = list_parser_with_auth.copy()
    search_parser.add_argument('demo_name', type=str)
    search_parser.add_argument('demo_state', type=str, choices=[v.value for k, v in constants.ResourceState.__members__.items()])

    @demo_api.expect(search_parser)
    @demo_api.marshal_with(list_resp)
    @check_request(search_parser)
    @authentication_required(
        resource_name=constants.ResourceEnum.demo.name,
        permission_name=constants.Operation.query.name)
    @sign_required
    def get(self):
        """资源批量查询接口"""
        cursor = db.session.query(DemoModel)
        if g.args.get('demo_name') is not None:
            cursor = cursor.filter(DemoModel.demo_name.contains(g.args['demo_name']))
        if g.args.get('demo_state') is not None:
            cursor = cursor.filter(DemoModel.demo_state == g.args['demo_state'])
        cursor = cursor.filter_by_create_date_and_page(
            create_date_start=g.args.get('create_date_start'),
            create_date_end=g.args.get('create_date_end'),
            per_page=g.args.get('per_page'), page=g.args.get('page')
        )
        demos = cursor.record().all()
        if not demos:
            err = errors.ResourceNotFound(errmsg='Demos not found')
            logger.log(level=err.log_level, msg=err.log)
            return err.to_dict_response()
        return {
            'return_code': 200,
            'return_msg': '',
            'data': {'demos': demos}
        }


@demo_api.route('/<int:demo_id>')
@demo_api.param('demo_id', description='demo id', _in='path')
class Demo(Resource):
    logger = logger.getChild('Demo')

    @demo_api.expect(json_parser_with_auth)
    @demo_api.marshal_with(crud_resp)
    @check_request(json_parser_with_auth, update_schema)
    @authentication_required(
        resource_name=constants.ResourceEnum.demo.name,
        permission_name=constants.Operation.update.name)
    @sign_required
    def post(self, demo_id):
        """资源更新接口"""
        demo = db.session.query(DemoModel).get(demo_id)
        if not demo:
            err = errors.ResourceNotFound(errmsg='Demo not found.')
            logger.log(level=err.log_level, msg=err.log)
            return err.to_dict_response()
        try:
            demo.update(g.args, user=g.user)
        except errors.Error as e:
            logger.log(level=e.log_level, msg=e.log)
            return e.to_dict_response()
        return {
            'return_code': 200,
            'return_msg': '',
            'data': demo
        }

    @demo_api.expect(parser_with_auth)
    @demo_api.marshal_with(crud_resp)
    @check_request(parser_with_auth)
    @authentication_required(
        resource_name=constants.ResourceEnum.demo.name,
        permission_name=constants.Operation.query.name)
    @sign_required
    def get(self, demo_id):
        """资源查询接口"""
        demo = db.session.query(DemoModel).get_active(demo_id, record=True)
        if not demo:
            err = errors.ResourceNotFound(errmsg='Demo not found.')
            logger.log(level=err.log_level, msg=err.log)
            return err.to_dict_response()
        return {
            'return_code': 200,
            'return_msg': '',
            'data': demo
        }
```

需要配置`creation_schema`和`update_schema`用以校验数据格式，示例如下
```python
creation_schema = {
    "type": "object",
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "demo_creation",
    "description": "添加demo",
    "properties": {
        "demo_name": {"description": "demo名称", "type": "string", "max_bytes_len": 15},
    },
    "required": ["demo_name"],
    "additionalProperties": False
}
```
```python
update_schema = {
    "type": "object",
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "demo_update",
    "description": "更新demo",
    "properties": {
        "demo_name": {"description": "demo名称", "type": "string", "max_bytes_len": 15},
    },
    "additionalProperties": False
}
```
还可以配置固定的资源格式，保证响应格式的标准化
```python
demo_model = resource_model.clone('demo', {
    "demo_id": fields.Integer(title="demo id"),
    'demo_name': fields.String(title="demo名称"),
    'demo_state': fields.String(title="demo状态")
})
```

#### dao

该目录包含存储服务及其拓展，目前主要提供mysql数据库和fastdfs文件存储服务

##### mysql数据库

创建mysql事务时可直接调用

```python
from app.dao.mysql import db
db.session
```

拓展后的db支持一下功能：

- 通过`with`使用上下文管理器提交事务，自动回滚

- 使用query查询时，添加`.active`只返回激活状态的资源，使用`get_active`进行id查询，只在资源未激活状态的情况下返回

- 使用query查询时，使用`get_active`/`get`函数进行id查询时，可传入`record`参数，`record`为`True`时自动记录查询操作记录

- `filter_by_create_date_and_page`简化分页查询和创建时间范围查询

##### fastdfs文件存储

拓展后的`FastDFSStorage`支持`upload`/`download`/`delete`，上传和下载函数自动对文件进行加密，保证文件安全。

#### services

可放置一些对Model的拓展类

#### jobs

定时任务和异步任务可使用celery调度。

将任务函数放在`tasks.py`中，示例

```python
@celery_app.task()
def demo():
    pass
```

定时任务的schedule可配置在`celery_config`的`beat_schedule`变量上，例如

```python
beat_schedule = CELERYBEAT_SCHEDULE = {
    'demo': {
        'task': 'app.jobs.tasks.demo',
        'schedule': crontab(0, 0, day_of_month='1')
    },
}
```

#### utils

##### decorators.py

- `check_request`：根据传入的parser和schema校验请求体参数
- `authentication_required`：从请求头中获取认证信息并校验，设置全局的user
- `sign_required`：签名校验，确保请求体未被篡改，且未超时。执行此装饰器前必须执行`authentication_required`

##### errors.py

此文档包含了目前支持的所有的异常类，如需新增异常类，可在此文件下继承`Error`类添加，示例

```python
class ParamError(Error):
    code = ErrorCode.ParamError.value
    errmsg = ErrorCode.ParamError.name
    log_level = logging.WARNING
```

抛出异常示例`raise errors.Error(errmsg=f'上传文件到FastDFS失败: {result}')`

捕获异常示例

```python
try:
	demo.save(user=g.user)
except errors.Error as e:
	logger.log(level=e.log_level, msg=e.log) # 输出日志
	return e.to_dict_response() # 返回标准响应
```

##### message.py

用于发送通知信息的函数，目前仅支持邮件发送

##### timer.py

计时器函数

##### validators.py

jsonshema的校验函数拓展，支持检查述职、字节长度、日期格式

#### configs

配置信息可直接从`CONFIG`类中读取

#### parsers.py

用于存放请求体校验parser

- base_parser校验timestamp/nonce/sign，parser_with_auth额外支持对api_key/token的校验

- json_parser_with_auth校验加密后的json请求体data和密钥key

- form_parser校验加密后的form请求体data和密钥key

- list_parser_with_auth用于列表查询校验，支持校验page/per_page/create_date_start/create_date_end
#### marshalling_models.py

用于存放响应模型

#### 文档

`flask_restx`使用`api.expect`和`api.marshal_with`装饰器后，根据parser和model自动生成文档，示例如下

```
@demo_api.expect(search_parser)
@demo_api.marshal_with(list_resp)
```

#### 日志

使用`logging.config.dictConfig`配置日志格式，配置存放于`app.configs.CONFIG`的`LOGGING_CONFIG`属性中





