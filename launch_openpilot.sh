#!/usr/bin/env bash
# NMK-Ai launcher — Offline mode (mr-one.cn disabled)
# لتفعيل خادم خاص مستقبلاً، عدّل المتغيرات أدناه:
# export ATHENA_HOST='wss://athena.YOUR_DOMAIN'
# export API_HOST='https://api.YOUR_DOMAIN'

# لو الجهاز في وضع offline (الافتراضي):
export ATHENA_HOST=''
export API_HOST=''

exec ./launch_chffrplus.sh
