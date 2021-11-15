# DjangoMultTenant

django 多租户方案的一个插件，本插件的是在数据库层对租户数据进行了隔离，保证每个租户只能访问自己的数据库信息

## 安装

```shell
pip install django-mult-tenant
```

## 配置

```python

INSTALLED_APPS = [
    'mult_tenant.tenant',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    ...
    'mult_tenant.proxy',
    #  rest_framework 需要加载rest app
    'mult_tenant.rest'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    # 需要注释调官方自带的AuthenticationMiddleware，采用插件的MultTenantAuthenticationMiddleware
    # 'django.contrib.auth.middleware.AuthenticationMiddleware',
    'mult_tenant.tenant.middleware.authentication.MultTenantAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# AUTH_USER_MODEL 全局用户模型,必须指定
AUTH_USER_MODEL = 'tenant.GlobalUser'

# 租户用户模型,不指定默认为：'auth.User'
AUTH_TENANT_USER_MODEL = 'info.User'

# 租户模型,不指定默认为：'tenant.Tenant'
DEFAULT_TENANT_MODEL = 'tenant.Tenant'

## 数据库映射，这里只需要定义共用的app
DATABASE_APPS_MAPPING = {
    'tenant': 'default',
    'admin': 'default',
    'sessions': 'default'
}

## 数据库映射路由
DATABASE_ROUTERS = ['mult_tenant.tenant.utils.db.MultTenantDBRouter']

```

## 主要模块说明以及使用

### 数据库模块

1. 默认`default`数据库为主数据库,只保存公共模块数据，租户数据库可以动态创建，创建一个租户，在数据库中创建了一个对应租户的数据库，所有租户的数据库结构相同

2. 可以在`DATABASE_APPS_MAPPING`中指定某个`app`属于公共`app`,还是租户`app`,公共`app`默认数据库链接为`default`

### `mult_tenant.tenant` 多租户模块


1. `Tenant`为租户模型，当然你可以继承`AbstractTenant`来自定义自己的租户模块，并在`settings`中指定`DEFAULT_TENANT_MODEL`常量来指定租户模型

2. `GlobalUser` 为全局用户，不分数据哪个租户，这里用`GlobalUser`替代了`django.contrib.auth.models.User`模块，因此`django.contrib.auth.get_user_model` 获取的是`GlobalUser`对象，相应的`request.user`也是`GlobalUser`对象，用户可以被加入租户，也可以选择不加入租户，加入租户的用户只能访问相应租户数据，不加入租户的用户如果是超级管理员可以访问`全局用户`和`租户信息`

3. 租户用户表默认采用`django.contrib.auth.models.User`,当然你可以选择继承`django.contrib.auth.models.AbstractUser`来自定义自己的租户用户模块，并在settings中指定`AUTH_TENANT_USER_MODEL`常量来指定租户用户，用户可以在租户层面完整的使用`django.contrib.auth`所有功能，包括`User`、`Group`、`Permission`、`Admin`

4. 可以登录Admin 后台创建租户，也可以使用`createtenant`命令行来创建租户


### `mult_tenant.proxy` 代理模块

`ProxyContentType`contentType代理，因为在多租户模型中，主数据库和租户数据库数据模型不一样，在不断的迭代更新中，新的租户和老的租户模型`ContentType`数据信息也不一样，django默认自带的`ContentType`模型默认自带缓存，`ProxyContentType`模型无缓存，每次的数据访问都是直接访问数据库，这样避免了`ContentType`信息不一致导致的异常


### `mult_tenant.rest` rest_framework适配模块

1. 对`rest_framework`进行了适配,保证租户只能访问自己的租户的数据
2. 提供了一个`IsTanenatUser`权限类，判断是不是租户用户



### `migrate` 模块

1. 提供了一个`multmigrate` 命令来迁移租户数据库，参数`--all`可以一次迁移所有的租户数据，当然你也可以指定`database`来迁移某一个租户的数据库


## 支持的数据库

适配了支持`django`所有支持的数据库（`SQLite`、`MySQL`、`Posgrep`、`Oracle`）


## 例子

可以参考`examples`的使用
