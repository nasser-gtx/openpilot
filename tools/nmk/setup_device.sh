#!/usr/bin/env bash
# NMK: توحيد دخول SSH عبر المستخدم nmk على كل أجهزة القائد الآلي (idempotent، يعمل عند كل إقلاع)
#   1) ينشئ المستخدم nmk (بنفس مجموعات comma، شامل sudo) إن لم يكن موجوداً
#   2) يجهّز مفتاح nmk الخاص من الملف العام GithubSshKeys (لأن sshd يقرأ المفاتيح بصلاحيات المستخدم)
#   3) يضمن أن AuthorizedKeysFile يتضمّن %h/.ssh/authorized_keys (مع بوابة sshd -t + reload)
# كل تعديل على /etc محاط بـ remount rw/ro مع استعادة الحالة الأصلية.
set -e
[ -f /AGNOS ] || exit 0

SSHD_CONFIG=/etc/ssh/sshd_config
KEYS_SRC=/data/params/d/GithubSshKeys

# احفظ حالة الجذر (rw/ro) لإرجاعها كما كانت بعد أي كتابة على /etc
ROOT_WAS_RO=0
if grep -qE ' / [^ ]+ ro[, ]' /proc/mounts; then ROOT_WAS_RO=1; fi
remount_rw()   { [ "$ROOT_WAS_RO" = 1 ] && sudo mount -o remount,rw / || true; }
remount_back() { [ "$ROOT_WAS_RO" = 1 ] && sudo mount -o remount,ro / || true; }

# 1) المستخدم nmk (يكتب /etc/passwd → يحتاج rw) — idempotent
if ! id nmk >/dev/null 2>&1; then
  remount_rw
  COMMA_GROUPS=$(id -nG comma 2>/dev/null | tr ' ' ',')
  sudo useradd -m -s /bin/bash ${COMMA_GROUPS:+-G "$COMMA_GROUPS"} nmk || true
  remount_back
fi

# 2) مفتاح nmk الخاص من الملف العام (/home قابل للكتابة، لا حاجة remount) — idempotent
if [ -f "$KEYS_SRC" ] && id nmk >/dev/null 2>&1; then
  NMK_HOME=$(getent passwd nmk | cut -d: -f6)
  if [ -n "$NMK_HOME" ]; then
    sudo mkdir -p "$NMK_HOME/.ssh"
    if ! sudo cmp -s "$KEYS_SRC" "$NMK_HOME/.ssh/authorized_keys"; then
      sudo cp "$KEYS_SRC" "$NMK_HOME/.ssh/authorized_keys"
    fi
    sudo chown -R nmk:nmk "$NMK_HOME/.ssh"
    sudo chmod 700 "$NMK_HOME/.ssh"
    sudo chmod 600 "$NMK_HOME/.ssh/authorized_keys"
  fi
fi

# 3) ضمان %h/.ssh/authorized_keys ضمن AuthorizedKeysFile — idempotent + بوابة أمان
if [ -f "$SSHD_CONFIG" ] && ! grep -qE '^AuthorizedKeysFile.*%h/\.ssh/authorized_keys' "$SSHD_CONFIG"; then
  remount_rw
  sudo cp -a "$SSHD_CONFIG" "${SSHD_CONFIG}.nmk.bak"
  if grep -qE '^AuthorizedKeysFile ' "$SSHD_CONFIG"; then
    # أضف %h في بداية القيمة مع إبقاء المسار العام
    sudo sed -i -E 's#^(AuthorizedKeysFile )(.*)$#\1%h/.ssh/authorized_keys \2#' "$SSHD_CONFIG"
  else
    echo 'AuthorizedKeysFile %h/.ssh/authorized_keys /data/params/d/GithubSshKeys' | sudo tee -a "$SSHD_CONFIG" >/dev/null
  fi
  # بوابة إلزامية: لا reload إلا إذا نجح الفحص؛ وإلا استرجاع فوري
  if sudo sshd -t 2>/dev/null; then
    sudo systemctl reload ssh 2>/dev/null || sudo systemctl reload sshd 2>/dev/null || sudo pkill -HUP sshd || true
  else
    sudo cp -a "${SSHD_CONFIG}.nmk.bak" "$SSHD_CONFIG"
  fi
  remount_back
fi

exit 0
