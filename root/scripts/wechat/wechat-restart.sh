#!/bin/bash
pkill -9 -f /usr/bin/wechat 2>/dev/null
nohup /usr/bin/wechat >/dev/null 2>&1 &
if [ "${ENABLE_WECHAT_AUTO_LOGIN:-true}" = "true" ]; then
    nohup /lsiopy/bin/python3 /scripts/wechat/wechat-auto-login.py >/dev/null 2>&1 &
fi