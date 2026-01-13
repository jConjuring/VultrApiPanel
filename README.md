# Vultr 服务器管理器

基于 Flet 的桌面客户端，用于管理 Vultr 服务器。支持保存 API 密钥、获取区域/套餐/镜像、创建实例、重装系统、删除实例以及刷新列表。

## 功能
- API 密钥本地保存（`config.json`）
- 一键获取区域/套餐/镜像
- 创建、重装、删除服务器
- 列表分页与状态提示

## 运行
1. 创建并激活虚拟环境：
   - Windows: `python -m venv .venv`，然后 `\.venv\Scripts\activate`
2. 安装依赖：`pip install -r requirements.txt`
3. 启动：`python main.py`

