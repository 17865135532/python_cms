### 纳税申报平台

#### 一、启动方式：

```
# 安装扩展
pip install -r requirements.txt 
# 启动项目
python manage.py runserver
或
gunicorn -c gunicorn.py application:app
```

#### 二、文档地址

- 普通用户接口地址：`http://{{host}}:5000/api/v1`

- 管理员&机器人接口地址：`http://{{host}}:5000/api/v1/ad`

#### 三、后台管理系统地址

- `http://{{host}}:5000/admin`

#### 四、测试代码覆盖执行指令

```
pytest --cov=./ --cov-report=html --cov-config .coveragerc -s
# 测试目录
./ 
# 报告生成
--cov-report=html
# 配置文件
--cov-config .coveragerc
```

