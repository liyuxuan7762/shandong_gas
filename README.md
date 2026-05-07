# Shandong Gas Home Assistant Integration

这是一个 Home Assistant 自定义集成，用于获取山东燃气用户余额和最后抄表日期。

## 功能

- 支持通过 `refresh_token` / `access_token` 进行身份验证
- 自动刷新过期的 Access Token
- 获取并显示：
  - `availableBalance` 余额
  - `lastMeterReadingDate` 最后抄表日期

## 安装方式

### 方式 1：直接复制到 HA

1. 将整个仓库克隆或复制到 Home Assistant 的 `config` 目录下。
2. 确保目录结构为：
   - `config/custom_components/shandong_gas/`
3. 重启 Home Assistant。
4. 在 UI 中添加集成，输入以下字段：
   - `refresh_token`
   - `access_token`
   - `subsId`
   - `orgId`
   - `subsCode`

### 方式 2：通过 HACS 自定义仓库安装

1. 将本仓库推送到 GitHub。
2. 在 HACS 中添加自定义仓库，类型选择 `Integration`。
3. 使用 HACS 安装 `Shandong Gas`。
4. 重启 Home Assistant。

## 配置

这个集成会创建两个传感器：

- `燃气余额`
- `最后抄表日期`

## 目录结构

- `custom_components/shandong_gas/manifest.json`
- `custom_components/shandong_gas/config_flow.py`
- `custom_components/shandong_gas/coordinator.py`
- `custom_components/shandong_gas/sensor.py`
- `custom_components/shandong_gas/__init__.py`
- `custom_components/shandong_gas/const.py`

## 说明

为了方便你上传到 GitHub，建议先执行：

```bash
cd /path/to/shandong_gas
git init
git add .
git commit -m "Initial Shandong Gas Home Assistant integration"
```

然后将仓库推送到 GitHub。
