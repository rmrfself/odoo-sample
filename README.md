### how to launch your server?

Before start, you need to：

* install python2.7， including of pip。

* install postgresql database with version 9.5 and above(安装9.5以上版本的postgresql)

Then install some dependicies（安装python的依赖包）：

firstoff, install the pip(please google it on how to install pip)

```
pip install -r ./requirements.txt
```

In the project root, run below command directly:

```
启动命令如下:

./odoo-bin --db_user odoo_master --db_password db_password --db_host localhost --db_port 5432 --addons-path="addons,extra-addons" --db-filter=odoo_develop  --save --dev=reload
```

### Database recovery

For localhost， input below link in your browser:

http://localhost:8069/web/database/manager

![](https://github.com/rmrfself/odoo-sample/blob/master/odoo-how-to-recover-db.gif)

### Page screenshots(页面截屏)

![](https://github.com/rmrfself/odoo-sample/blob/master/2018-11-13_23-18-52.gif)

完善中...




