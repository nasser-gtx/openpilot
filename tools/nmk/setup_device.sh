#!/usr/bin/env bash
# NMK: توحيد دخول SSH عبر إنشاء مستخدم nmk
# يعمل مع AuthorizedKeysFile العام (/data/params/d/GithubSshKeys) على كل أجهزة comma
set -e
[ -f /AGNOS ] || exit 0
id nmk >/dev/null 2>&1 && exit 0   # موجود مسبقاً، لا شيء نفعله

# احفظ حالة الجذر (rw/ro) لإرجاعها كما كانت
ROOT_WAS_RO=0
if grep -qE ' / [^ ]+ ro[, ]' /proc/mounts; then ROOT_WAS_RO=1; fi
[ "$ROOT_WAS_RO" = 1 ] && sudo mount -o remount,rw /

# انسخ نفس مجموعات comma الثانوية (شامل sudo) إلى nmk
COMMA_GROUPS=$(id -nG comma 2>/dev/null | tr ' ' ',')
sudo useradd -m -s /bin/bash ${COMMA_GROUPS:+-G "$COMMA_GROUPS"} nmk || true

[ "$ROOT_WAS_RO" = 1 ] && sudo mount -o remount,ro /
exit 0
