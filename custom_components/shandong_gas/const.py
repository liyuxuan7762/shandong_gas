from datetime import timedelta

DOMAIN = "shandong_gas"
PLATFORMS = ["sensor"]

CONF_REFRESH_TOKEN = "refresh_token"
CONF_ACCESS_TOKEN = "access_token"
CONF_SUBS_ID = "subs_id"
CONF_ORG_ID = "org_id"
CONF_SUBS_CODE = "subs_code"

API_BASE = "https://weixin.shandongtowngas.com.cn"
SCAN_INTERVAL = timedelta(minutes=15)
