# Ubuntu 24.04 部署清单

1. 安装 Python 3.12、Node.js 22、Nginx、ClamAV、Certbot、Git 和 Chromium 依赖。
2. 将代码部署到 `/srv/huali/current`，共享数据放在 `/srv/huali/shared`，创建 Python 虚拟环境 `/srv/huali/venv`。
3. 复制 `.env.example` 为 `/srv/huali/shared/.env`，填写独立强密钥、正式域名、163 授权码和销售邮箱。
4. 安装 Python/npm 依赖，运行迁移、`collectstatic`、前端构建和首次全量预渲染。
5. 将 `deploy/gunicorn`、`deploy/systemd` 文件复制到 `/etc/systemd/system/`，启用 Gunicorn 和全部 timer。
6. 用 `envsubst` 将 Nginx 模板中的 `${SITE_DOMAIN}` 替换为正式域名，再执行 `nginx -t`。
7. 运行 `certbot --nginx -d example.com -d www.example.com` 并确认自动续期 timer 正常。
8. 上线前修改开发管理员密码，登录后台为超级管理员绑定 TOTP，并离线保存恢复码。

常用验收命令：

```bash
python manage.py check --deploy --settings=huali_website.settings_production
python manage.py test
npm run build
systemctl list-timers 'huali-*'
curl -fsS https://example.com/api/v1/health/
certbot renew --dry-run
```
