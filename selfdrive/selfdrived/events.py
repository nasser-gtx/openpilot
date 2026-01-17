#!/usr/bin/env python3
import math
import os

from cereal import log, car
import cereal.messaging as messaging
from openpilot.common.constants import CV
from openpilot.common.git import get_short_branch
from openpilot.common.realtime import DT_CTRL
from openpilot.selfdrive.locationd.calibrationd import MIN_SPEED_FILTER
from openpilot.system.micd import SAMPLE_RATE, SAMPLE_BUFFER
from openpilot.selfdrive.ui.feedback.feedbackd import FEEDBACK_MAX_DURATION

from openpilot.sunnypilot.selfdrive.selfdrived.events_base import EventsBase, Priority, ET, Alert, \
  NoEntryAlert, SoftDisableAlert, UserSoftDisableAlert, ImmediateDisableAlert, EngagementAlert, NormalPermanentAlert, \
  StartupAlert, AlertCallbackType, wrong_car_mode_alert


AlertSize = log.SelfdriveState.AlertSize
AlertStatus = log.SelfdriveState.AlertStatus
VisualAlert = car.CarControl.HUDControl.VisualAlert
AudibleAlert = car.CarControl.HUDControl.AudibleAlert
EventName = log.OnroadEvent.EventName


# الحصول على اسم الحدث من التعداد
EVENT_NAME = {v: k for k, v in EventName.schema.enumerants.items()}


class Events(EventsBase):
  def __init__(self):
    super().__init__()
    self.event_counters = dict.fromkeys(EVENTS.keys(), 0)

  def get_events_mapping(self) -> dict[int, dict[str, Alert | AlertCallbackType]]:
    return EVENTS

  def get_event_name(self, event: int):
    return EVENT_NAME[event]

  def get_event_msg_type(self):
    return log.OnroadEvent



# ********** دوال مساعدة **********
def get_display_speed(speed_ms: float, metric: bool) -> str:
  speed = int(round(speed_ms * (CV.MS_TO_KPH if metric else CV.MS_TO_MPH)))
  unit = 'كم/س' if metric else 'ميل/س'
  return f"{speed} {unit}"


# ********** دوال استدعاء التنبيهات **********


def soft_disable_alert(alert_text_2: str) -> AlertCallbackType:
  def func(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int, personality) -> Alert:
    if soft_disable_time < int(0.5 / DT_CTRL):
      return ImmediateDisableAlert(alert_text_2)
    return SoftDisableAlert(alert_text_2)
  return func

def user_soft_disable_alert(alert_text_2: str) -> AlertCallbackType:
  def func(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int, personality) -> Alert:
    if soft_disable_time < int(0.5 / DT_CTRL):
      return ImmediateDisableAlert(alert_text_2)
    return UserSoftDisableAlert(alert_text_2)
  return func

def startup_master_alert(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int, personality) -> Alert:
  branch = get_short_branch()  # التأكد من تخزين get_short_branch مؤقتاً لتجنب التأخير عند بدء التشغيل
  if "REPLAY" in os.environ:
    branch = "إعادة تشغيل"

  return StartupAlert("تحذير: هذا الفرع غير مُختبر", branch, alert_status=AlertStatus.userPrompt)

def below_engage_speed_alert(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int, personality) -> Alert:
  return NoEntryAlert(f"قُد بسرعة أعلى من {get_display_speed(CP.minEnableSpeed, metric)} للتفعيل")


def below_steer_speed_alert(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int, personality) -> Alert:
  return Alert(
    f"التوجيه غير متاح تحت {get_display_speed(CP.minSteerSpeed, metric)}",
    "",
    AlertStatus.userPrompt, AlertSize.small,
    Priority.LOW, VisualAlert.none, AudibleAlert.prompt, 0.4)


def calibration_incomplete_alert(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int, personality) -> Alert:
  first_word = 'إعادة المعايرة' if sm['liveCalibration'].calStatus == log.LiveCalibrationData.Status.recalibrating else 'المعايرة'
  return Alert(
    f"{first_word} قيد التقدم: {sm['liveCalibration'].calPerc:.0f}%",
    f"قُد بسرعة أعلى من {get_display_speed(MIN_SPEED_FILTER, metric)}",
    AlertStatus.normal, AlertSize.mid,
    Priority.LOWEST, VisualAlert.none, AudibleAlert.none, .2)


def audio_feedback_alert(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int, personality) -> Alert:
  duration = FEEDBACK_MAX_DURATION - ((sm['audioFeedback'].blockNum + 1) * SAMPLE_BUFFER / SAMPLE_RATE)
  seconds_text = "ثانية" if round(duration) == 1 else "ثوانٍ"
  return NormalPermanentAlert(
    "جاري تسجيل الملاحظات الصوتية",
    f"متبقي {round(duration)} {seconds_text}. اضغط مرة أخرى للحفظ المبكر.",
    priority=Priority.LOW)


# *** تنبيهات التصحيح ***

def out_of_space_alert(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int, personality) -> Alert:
  full_perc = round(100. - sm['deviceState'].freeSpacePercent)
  return NormalPermanentAlert("نفدت مساحة التخزين", f"ممتلئ بنسبة {full_perc}%")


def posenet_invalid_alert(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int, personality) -> Alert:
  mdl = sm['modelV2'].velocity.x[0] if len(sm['modelV2'].velocity.x) else math.nan
  err = CS.vEgo - mdl
  msg = f"خطأ في السرعة: {err:.1f} م/ث"
  return NoEntryAlert(msg, alert_text_1="سرعة Posenet غير صالحة")


def process_not_running_alert(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int, personality) -> Alert:
  not_running = [p.name for p in sm['managerState'].processes if not p.running and p.shouldBeRunning]
  msg = ', '.join(not_running)
  return NoEntryAlert(msg, alert_text_1="العملية لا تعمل")


def comm_issue_alert(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int, personality) -> Alert:
  bs = [s for s in sm.data.keys() if not sm.all_checks([s, ])]
  msg = ', '.join(bs[:4])  # لا يمكن احتواء الكثير في سطر واحد
  return NoEntryAlert(msg, alert_text_1="مشكلة في الاتصال بين العمليات")


def camera_malfunction_alert(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int, personality) -> Alert:
  all_cams = ('roadCameraState', 'driverCameraState', 'wideRoadCameraState')
  bad_cams = [s.replace('State', '') for s in all_cams if s in sm.data.keys() and not sm.all_checks([s, ])]
  return NormalPermanentAlert("عطل في الكاميرا", ', '.join(bad_cams))


def calibration_invalid_alert(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int, personality) -> Alert:
  rpy = sm['liveCalibration'].rpyCalib
  yaw = math.degrees(rpy[2] if len(rpy) == 3 else math.nan)
  pitch = math.degrees(rpy[1] if len(rpy) == 3 else math.nan)
  angles = f"أعد تركيب الجهاز (الميل: {pitch:.1f}°، الانحراف: {yaw:.1f}°)"
  return NormalPermanentAlert("المعايرة غير صالحة", angles)


def paramsd_invalid_alert(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int, personality) -> Alert:
  if not sm['liveParameters'].angleOffsetValid:
    angle_offset_deg = sm['liveParameters'].angleOffsetDeg
    title = "تم اكتشاف عدم محاذاة التوجيه"
    text = f"إزاحة الزاوية عالية جداً (الإزاحة: {angle_offset_deg:.1f}°)"
  elif not sm['liveParameters'].steerRatioValid:
    steer_ratio = sm['liveParameters'].steerRatio
    title = "عدم تطابق نسبة التوجيه"
    text = f"قد تكون هندسة جهاز التوجيه غير صحيحة (النسبة: {steer_ratio:.1f})"
  elif not sm['liveParameters'].stiffnessFactorValid:
    stiffness_factor = sm['liveParameters'].stiffnessFactor
    title = "صلابة إطار غير طبيعية"
    text = f"افحص الإطارات والضغط أو المحاذاة (المعامل: {stiffness_factor:.1f})"
  else:
    return NoEntryAlert("خطأ مؤقت في paramsd")

  return NoEntryAlert(alert_text_1=title, alert_text_2=text)

def overheat_alert(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int, personality) -> Alert:
  cpu = max(sm['deviceState'].cpuTempC, default=0.)
  gpu = max(sm['deviceState'].gpuTempC, default=0.)
  temp = max((cpu, gpu, sm['deviceState'].memoryTempC))
  return NormalPermanentAlert("ارتفاع حرارة النظام", f"{temp:.0f} °م")


def low_memory_alert(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int, personality) -> Alert:
  return NormalPermanentAlert("ذاكرة منخفضة", f"مستخدم {sm['deviceState'].memoryUsagePercent}%")


def high_cpu_usage_alert(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int, personality) -> Alert:
  x = max(sm['deviceState'].cpuUsagePercent, default=0.)
  return NormalPermanentAlert("استخدام عالي للمعالج", f"مستخدم {x}%")


def modeld_lagging_alert(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int, personality) -> Alert:
  return NormalPermanentAlert("تأخر نموذج القيادة", f"تم إسقاط {sm['modelV2'].frameDropPerc:.1f}% من الإطارات")


def joystick_alert(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int, personality) -> Alert:
  gb = sm['carControl'].actuators.accel / 4.
  steer = sm['carControl'].actuators.torque
  vals = f"الوقود: {round(gb * 100.)}%، التوجيه: {round(steer * 100.)}%"
  return NormalPermanentAlert("وضع عصا التحكم", vals)


def longitudinal_maneuver_alert(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int, personality) -> Alert:
  ad = sm['alertDebug']
  audible_alert = AudibleAlert.prompt if 'Active' in ad.alertText1 else AudibleAlert.none
  alert_status = AlertStatus.userPrompt if 'Active' in ad.alertText1 else AlertStatus.normal
  alert_size = AlertSize.mid if ad.alertText2 else AlertSize.small
  return Alert(ad.alertText1, ad.alertText2,
               alert_status, alert_size,
               Priority.LOW, VisualAlert.none, audible_alert, 0.2)


def personality_changed_alert(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int, personality) -> Alert:
  personality_names = {
    'aggressive': 'عدواني',
    'standard': 'قياسي',
    'relaxed': 'مريح'
  }
  personality_str = str(personality).lower()
  personality_ar = personality_names.get(personality_str, personality_str.title())
  return NormalPermanentAlert(f"شخصية القيادة: {personality_ar}", duration=1.5)


def invalid_lkas_setting_alert(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int, personality) -> Alert:
  text = "شغّل أو أطفئ LKAS الأصلي للتفعيل"
  if CP.brand == "tesla":
    text = "انتقل إلى مثبت السرعة المُدرك للمرور للتفعيل"
  elif CP.brand == "mazda":
    text = "فعّل LKAS في سيارتك للتفعيل"
  elif CP.brand == "nissan":
    text = "عطّل LKAS الأصلي في سيارتك للتفعيل"
  return NormalPermanentAlert("إعداد LKAS غير صالح", text)



EVENTS: dict[int, dict[str, Alert | AlertCallbackType]] = {
  # ********** أحداث بدون تنبيهات **********

  EventName.stockFcw: {},
  EventName.actuatorsApiUnavailable: {},

  # ********** أحداث تحتوي فقط على تنبيهات تُعرض في جميع الحالات **********

  EventName.joystickDebug: {
    ET.WARNING: joystick_alert,
    ET.PERMANENT: NormalPermanentAlert("وضع عصا التحكم"),
  },

  EventName.longitudinalManeuver: {
    ET.WARNING: longitudinal_maneuver_alert,
    ET.PERMANENT: NormalPermanentAlert("وضع المناورة الطولية",
                                       "تأكد من أن الطريق أمامك خالٍ"),
  },

  EventName.selfdriveInitializing: {
    ET.NO_ENTRY: NoEntryAlert("النظام قيد التهيئة"),
  },

  EventName.startup: {
    ET.PERMANENT: StartupAlert("كن مستعداً للسيطرة في أي وقت")
  },

  EventName.startupMaster: {
    ET.PERMANENT: startup_master_alert,
  },

  EventName.startupNoControl: {
    ET.PERMANENT: StartupAlert("وضع كاميرا السيارة"),
    ET.NO_ENTRY: NoEntryAlert("وضع كاميرا السيارة"),
  },

  EventName.startupNoCar: {
    ET.PERMANENT: StartupAlert("وضع كاميرا السيارة لسيارة غير مدعومة"),
  },

  EventName.startupNoSecOcKey: {
    ET.PERMANENT: NormalPermanentAlert("وضع كاميرا السيارة",
                                       "مفتاح الأمان غير متاح",
                                       priority=Priority.HIGH),
  },

  EventName.dashcamMode: {
    ET.PERMANENT: NormalPermanentAlert("وضع كاميرا السيارة",
                                       priority=Priority.LOWEST),
  },

  EventName.invalidLkasSetting: {
    ET.PERMANENT: invalid_lkas_setting_alert,
    ET.NO_ENTRY: NoEntryAlert("إعداد LKAS غير صالح"),
  },

  EventName.cruiseMismatch: {
    #ET.PERMANENT: ImmediateDisableAlert("فشل القائد الآلي في إلغاء مثبت السرعة"),
  },

  # القائد الآلي لا يتعرف على السيارة. هذا يحوّل القائد الآلي إلى
  # وضع القراءة فقط. يمكن حل هذا بإضافة بصمة سيارتك.
  # انظر https://github.com/commaai/openpilot/wiki/Fingerprinting لمزيد من المعلومات
  EventName.carUnrecognized: {
    ET.PERMANENT: NormalPermanentAlert("وضع كاميرا السيارة",
                                       "السيارة غير معروفة",
                                       priority=Priority.LOWEST),
  },

  EventName.aeb: {
    ET.PERMANENT: Alert(
      "فرامل!",
      "فرملة طارئة: خطر اصطدام",
      AlertStatus.critical, AlertSize.full,
      Priority.HIGHEST, VisualAlert.fcw, AudibleAlert.none, 2.),
    ET.NO_ENTRY: NoEntryAlert("AEB: خطر اصطدام"),
  },

  EventName.stockAeb: {
    ET.PERMANENT: Alert(
      "فرامل!",
      "AEB الأصلي: خطر اصطدام",
      AlertStatus.critical, AlertSize.full,
      Priority.HIGHEST, VisualAlert.fcw, AudibleAlert.none, 2.),
    ET.NO_ENTRY: NoEntryAlert("AEB الأصلي: خطر اصطدام"),
  },

  EventName.fcw: {
    ET.PERMANENT: Alert(
      "فرامل!",
      "خطر اصطدام",
      AlertStatus.critical, AlertSize.full,
      Priority.HIGHEST, VisualAlert.fcw, AudibleAlert.warningSoft, 2.),
  },

  EventName.ldw: {
    ET.PERMANENT: Alert(
      "تم اكتشاف انحراف عن المسار",
      "",
      AlertStatus.userPrompt, AlertSize.small,
      Priority.LOW, VisualAlert.ldw, AudibleAlert.prompt, 3.),
  },

  # ********** أحداث تحتوي فقط على تنبيهات تُعرض أثناء التفعيل **********

  EventName.steerTempUnavailableSilent: {
    ET.WARNING: Alert(
      "التوجيه غير متاح مؤقتاً",
      "",
      AlertStatus.userPrompt, AlertSize.small,
      Priority.LOW, VisualAlert.steerRequired, AudibleAlert.prompt, 1.8),
  },

  EventName.preDriverDistracted: {
    ET.PERMANENT: Alert(
      "انتبه",
      "",
      AlertStatus.normal, AlertSize.small,
      Priority.LOW, VisualAlert.none, AudibleAlert.none, .1),
  },

  EventName.promptDriverDistracted: {
    ET.PERMANENT: Alert(
      "انتبه",
      "السائق مشتت",
      AlertStatus.userPrompt, AlertSize.mid,
      Priority.MID, VisualAlert.steerRequired, AudibleAlert.promptDistracted, .1),
  },

  EventName.driverDistracted: {
    ET.PERMANENT: Alert(
      "فُك الارتباط فوراً",
      "السائق مشتت",
      AlertStatus.critical, AlertSize.full,
      Priority.HIGH, VisualAlert.steerRequired, AudibleAlert.warningImmediate, .1),
  },

  EventName.preDriverUnresponsive: {
    ET.PERMANENT: Alert(
      "المس عجلة القيادة: لم يُكتشف وجه",
      "",
      AlertStatus.normal, AlertSize.small,
      Priority.LOW, VisualAlert.steerRequired, AudibleAlert.none, .1),
  },

  EventName.promptDriverUnresponsive: {
    ET.PERMANENT: Alert(
      "المس عجلة القيادة",
      "السائق لا يستجيب",
      AlertStatus.userPrompt, AlertSize.mid,
      Priority.MID, VisualAlert.steerRequired, AudibleAlert.promptDistracted, .1),
  },

  EventName.driverUnresponsive: {
    ET.PERMANENT: Alert(
      "فُك الارتباط فوراً",
      "السائق لا يستجيب",
      AlertStatus.critical, AlertSize.full,
      Priority.HIGH, VisualAlert.steerRequired, AudibleAlert.warningImmediate, .1),
  },

  EventName.manualRestart: {
    ET.WARNING: Alert(
      "تحكّم",
      "استأنف القيادة يدوياً",
      AlertStatus.userPrompt, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.none, .2),
  },

  EventName.resumeRequired: {
    ET.WARNING: Alert(
      "اضغط استئناف للخروج من وضع التوقف",
      "",
      AlertStatus.userPrompt, AlertSize.small,
      Priority.LOW, VisualAlert.none, AudibleAlert.none, .2),
  },

  EventName.belowSteerSpeed: {
    ET.WARNING: below_steer_speed_alert,
  },

  EventName.preLaneChangeLeft: {
    ET.WARNING: Alert(
      "وجّه يساراً لبدء تغيير المسار عندما يكون آمناً",
      "",
      AlertStatus.normal, AlertSize.small,
      Priority.LOW, VisualAlert.none, AudibleAlert.none, .1),
  },

  EventName.preLaneChangeRight: {
    ET.WARNING: Alert(
      "وجّه يميناً لبدء تغيير المسار عندما يكون آمناً",
      "",
      AlertStatus.normal, AlertSize.small,
      Priority.LOW, VisualAlert.none, AudibleAlert.none, .1),
  },

  EventName.laneChangeBlocked: {
    ET.WARNING: Alert(
      "تم اكتشاف سيارة في النقطة العمياء",
      "",
      AlertStatus.userPrompt, AlertSize.small,
      Priority.LOW, VisualAlert.none, AudibleAlert.prompt, .1),
  },

  EventName.laneChange: {
    ET.WARNING: Alert(
      "جاري تغيير المسار",
      "",
      AlertStatus.normal, AlertSize.small,
      Priority.LOW, VisualAlert.none, AudibleAlert.none, .1),
  },

  EventName.steerSaturated: {
    ET.WARNING: Alert(
      "تحكّم",
      "الدوران يتجاوز حد التوجيه",
      AlertStatus.userPrompt, AlertSize.mid,
      Priority.LOW, VisualAlert.steerRequired, AudibleAlert.promptRepeat, 2.),
  },

  # يُطرح عندما تعمل المروحة بأكثر من 50% ولكنها لا تدور
  EventName.fanMalfunction: {
    ET.PERMANENT: NormalPermanentAlert("عطل في المروحة", "مشكلة محتملة في الأجهزة"),
  },

  # الكاميرا لا تُخرج إطارات
  EventName.cameraMalfunction: {
    ET.PERMANENT: camera_malfunction_alert,
    ET.SOFT_DISABLE: soft_disable_alert("عطل في الكاميرا"),
    ET.NO_ENTRY: NoEntryAlert("عطل في الكاميرا: أعد تشغيل جهازك"),
  },
  # معدل إطارات الكاميرا منخفض جداً
  EventName.cameraFrameRate: {
    ET.PERMANENT: NormalPermanentAlert("معدل إطارات الكاميرا منخفض", "أعد تشغيل جهازك"),
    ET.SOFT_DISABLE: soft_disable_alert("معدل إطارات الكاميرا منخفض"),
    ET.NO_ENTRY: NoEntryAlert("معدل إطارات الكاميرا منخفض: أعد تشغيل جهازك"),
  },

  # غير مستخدم

  EventName.locationdTemporaryError: {
    ET.NO_ENTRY: NoEntryAlert("خطأ مؤقت في locationd"),
    ET.SOFT_DISABLE: soft_disable_alert("خطأ مؤقت في locationd"),
  },

  EventName.locationdPermanentError: {
    ET.NO_ENTRY: NoEntryAlert("خطأ دائم في locationd"),
    ET.IMMEDIATE_DISABLE: ImmediateDisableAlert("خطأ دائم في locationd"),
    ET.PERMANENT: NormalPermanentAlert("خطأ دائم في locationd"),
  },

  # يحاول القائد الآلي تعلم معلمات معينة عن سيارتك من خلال مراقبة
  # كيف تستجيب السيارة لمدخلات التوجيه من القيادة البشرية والقائد الآلي.
  # يشمل هذا:
  # - نسبة التوجيه: نسبة التروس لجهاز التوجيه. زاوية التوجيه مقسومة على زاوية الإطار
  # - صلابة الإطار: مقدار التماسك لإطاراتك
  # - إزاحة الزاوية: معظم مستشعرات زاوية التوجيه لديها إزاحة وتقيس زاوية غير صفرية عند القيادة بشكل مستقيم
  # يُطرح هذا التنبيه عندما تتجاوز أي من هذه القيم فحص السلامة. يمكن أن يحدث هذا بسبب
  # محاذاة سيئة أو بيانات مستشعر سيئة. إذا حدث هذا باستمرار فكر في إنشاء مشكلة على GitHub
  EventName.paramsdTemporaryError: {
    ET.NO_ENTRY: paramsd_invalid_alert,
    ET.SOFT_DISABLE: soft_disable_alert("خطأ مؤقت في paramsd"),
  },

  EventName.paramsdPermanentError: {
    ET.NO_ENTRY: NoEntryAlert("خطأ دائم في paramsd"),
    ET.IMMEDIATE_DISABLE: ImmediateDisableAlert("خطأ دائم في paramsd"),
    ET.PERMANENT: NormalPermanentAlert("خطأ دائم في paramsd"),
  },

  # ********** أحداث تؤثر على انتقالات حالة التحكم **********

  EventName.pcmEnable: {
    ET.ENABLE: EngagementAlert(AudibleAlert.engage),
  },

  EventName.buttonEnable: {
    ET.ENABLE: EngagementAlert(AudibleAlert.engage),
  },

  EventName.pcmDisable: {
    ET.USER_DISABLE: EngagementAlert(AudibleAlert.disengage),
  },

  EventName.buttonCancel: {
    ET.USER_DISABLE: EngagementAlert(AudibleAlert.disengage),
    ET.NO_ENTRY: NoEntryAlert("تم الضغط على إلغاء"),
  },

  EventName.brakeHold: {
    ET.WARNING: Alert(
      "اضغط استئناف للخروج من تثبيت الفرامل",
      "",
      AlertStatus.userPrompt, AlertSize.small,
      Priority.LOW, VisualAlert.none, AudibleAlert.none, .2),
  },

  EventName.parkBrake: {
    ET.USER_DISABLE: EngagementAlert(AudibleAlert.disengage),
    ET.NO_ENTRY: NoEntryAlert("فرامل الانتظار مُفعّلة"),
  },

  EventName.pedalPressed: {
    ET.USER_DISABLE: EngagementAlert(AudibleAlert.disengage),
    ET.NO_ENTRY: NoEntryAlert("تم الضغط على الدواسة",
                              visual_alert=VisualAlert.brakePressed),
  },

  EventName.steerDisengage: {
    ET.USER_DISABLE: EngagementAlert(AudibleAlert.disengage),
    ET.NO_ENTRY: NoEntryAlert("تم الضغط على التوجيه"),
  },

  EventName.preEnableStandstill: {
    ET.PRE_ENABLE: Alert(
      "حرر الفرامل للتفعيل",
      "",
      AlertStatus.normal, AlertSize.small,
      Priority.LOWEST, VisualAlert.none, AudibleAlert.none, .1, creation_delay=1.),
  },

  EventName.gasPressedOverride: {
    ET.OVERRIDE_LONGITUDINAL: Alert(
      "",
      "",
      AlertStatus.normal, AlertSize.none,
      Priority.LOWEST, VisualAlert.none, AudibleAlert.none, .1),
  },

  EventName.steerOverride: {
    ET.OVERRIDE_LATERAL: Alert(
      "",
      "",
      AlertStatus.normal, AlertSize.none,
      Priority.LOWEST, VisualAlert.none, AudibleAlert.none, .1),
  },

  EventName.wrongCarMode: {
    ET.USER_DISABLE: EngagementAlert(AudibleAlert.disengage),
    ET.NO_ENTRY: wrong_car_mode_alert,
  },

  EventName.resumeBlocked: {
    ET.NO_ENTRY: NoEntryAlert("اضغط Set للتفعيل"),
  },

  EventName.wrongCruiseMode: {
    ET.USER_DISABLE: EngagementAlert(AudibleAlert.disengage),
    ET.NO_ENTRY: NoEntryAlert("مثبت السرعة التكيفي مُعطّل"),
  },

  EventName.steerTempUnavailable: {
    ET.SOFT_DISABLE: soft_disable_alert("التوجيه غير متاح مؤقتاً"),
    ET.NO_ENTRY: NoEntryAlert("التوجيه غير متاح مؤقتاً"),
  },

  EventName.steerTimeLimit: {
    ET.SOFT_DISABLE: soft_disable_alert("تم تجاوز حد وقت توجيه السيارة"),
    ET.NO_ENTRY: NoEntryAlert("تم تجاوز حد وقت توجيه السيارة"),
  },

  EventName.outOfSpace: {
    ET.PERMANENT: out_of_space_alert,
    ET.NO_ENTRY: NoEntryAlert("نفدت مساحة التخزين"),
  },

  EventName.belowEngageSpeed: {
    ET.NO_ENTRY: below_engage_speed_alert,
  },

  EventName.sensorDataInvalid: {
    ET.PERMANENT: Alert(
      "بيانات المستشعر غير صالحة",
      "مشكلة محتملة في الأجهزة",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOWER, VisualAlert.none, AudibleAlert.none, .2, creation_delay=1.),
    ET.NO_ENTRY: NoEntryAlert("بيانات المستشعر غير صالحة"),
    ET.SOFT_DISABLE: soft_disable_alert("بيانات المستشعر غير صالحة"),
  },

  EventName.noGps: {
  },

  EventName.tooDistracted: {
    ET.NO_ENTRY: NoEntryAlert("مستوى التشتت مرتفع جداً"),
  },

  EventName.excessiveActuation: {
    ET.SOFT_DISABLE: soft_disable_alert("تشغيل مفرط"),
    ET.NO_ENTRY: NoEntryAlert("تشغيل مفرط"),
  },

  EventName.overheat: {
    ET.PERMANENT: overheat_alert,
    ET.SOFT_DISABLE: soft_disable_alert("ارتفاع حرارة النظام"),
    ET.NO_ENTRY: NoEntryAlert("ارتفاع حرارة النظام"),
  },

  EventName.wrongGear: {
    ET.SOFT_DISABLE: user_soft_disable_alert("الناقل ليس على D"),
    ET.NO_ENTRY: NoEntryAlert("الناقل ليس على D"),
  },

  # يُطرح هذا التنبيه عندما تكون زوايا المعايرة خارج النطاق المقبول.
  # على سبيل المثال إذا كان الجهاز موجهاً بشكل كبير إلى اليسار أو اليمين.
  # عادةً لا يمكن حل هذا إلا بإزالة الحامل من الزجاج الأمامي بالكامل،
  # وإعادة التركيب مع التأكد من أن الجهاز موجه بشكل مستقيم للأمام ومستوٍ.
  # انظر https://comma.ai/setup لمزيد من المعلومات
  EventName.calibrationInvalid: {
    ET.PERMANENT: calibration_invalid_alert,
    ET.SOFT_DISABLE: soft_disable_alert("المعايرة غير صالحة: أعد تركيب الجهاز وأعد المعايرة"),
    ET.NO_ENTRY: NoEntryAlert("المعايرة غير صالحة: أعد تركيب الجهاز وأعد المعايرة"),
  },

  EventName.calibrationIncomplete: {
    ET.PERMANENT: calibration_incomplete_alert,
    ET.SOFT_DISABLE: soft_disable_alert("المعايرة غير مكتملة"),
    ET.NO_ENTRY: NoEntryAlert("المعايرة قيد التقدم"),
  },

  EventName.calibrationRecalibrating: {
    ET.PERMANENT: calibration_incomplete_alert,
    ET.SOFT_DISABLE: soft_disable_alert("تم اكتشاف إعادة تركيب الجهاز: جاري إعادة المعايرة"),
    ET.NO_ENTRY: NoEntryAlert("تم اكتشاف إعادة التركيب: جاري إعادة المعايرة"),
  },

  EventName.doorOpen: {
    ET.SOFT_DISABLE: user_soft_disable_alert("الباب مفتوح"),
    ET.NO_ENTRY: NoEntryAlert("الباب مفتوح"),
  },

  EventName.seatbeltNotLatched: {
    ET.SOFT_DISABLE: user_soft_disable_alert("حزام الأمان غير مربوط"),
    ET.NO_ENTRY: NoEntryAlert("حزام الأمان غير مربوط"),
  },

  EventName.espDisabled: {
    ET.SOFT_DISABLE: soft_disable_alert("نظام التحكم الإلكتروني بالثبات مُعطّل"),
    ET.NO_ENTRY: NoEntryAlert("نظام التحكم الإلكتروني بالثبات مُعطّل"),
  },

  EventName.lowBattery: {
    ET.SOFT_DISABLE: soft_disable_alert("البطارية منخفضة"),
    ET.NO_ENTRY: NoEntryAlert("البطارية منخفضة"),
  },

  # تتواصل خدمات القائد الآلي المختلفة مع بعضها البعض على
  # فترات معينة. إذا لم يتبع الاتصال الجدول المنتظم يُطرح هذا التنبيه.
  # يمكن أن يعني هذا أن خدمة تعطلت، أو لم تبث رسالة لعشر
  # مرات الفترة المنتظمة، أو أن متوسط الفترة أعلى بأكثر من 10%.
  EventName.commIssue: {
    ET.SOFT_DISABLE: soft_disable_alert("مشكلة في الاتصال بين العمليات"),
    ET.NO_ENTRY: comm_issue_alert,
  },
  EventName.commIssueAvgFreq: {
    ET.SOFT_DISABLE: soft_disable_alert("معدل اتصال منخفض بين العمليات"),
    ET.NO_ENTRY: NoEntryAlert("معدل اتصال منخفض بين العمليات"),
  },

  EventName.selfdrivedLagging: {
    ET.SOFT_DISABLE: soft_disable_alert("تأخر في النظام"),
    ET.NO_ENTRY: NoEntryAlert("تأخر عملية القيادة الذاتية: أعد تشغيل جهازك"),
  },

  # يُطرح عندما يكتشف المدير خروج خدمة بشكل غير متوقع أثناء القيادة
  EventName.processNotRunning: {
    ET.NO_ENTRY: process_not_running_alert,
    ET.SOFT_DISABLE: soft_disable_alert("العملية لا تعمل"),
  },

  EventName.radarFault: {
    ET.SOFT_DISABLE: soft_disable_alert("خطأ في الرادار: أعد تشغيل السيارة"),
    ET.NO_ENTRY: NoEntryAlert("خطأ في الرادار: أعد تشغيل السيارة"),
  },

  EventName.radarTempUnavailable: {
    ET.SOFT_DISABLE: soft_disable_alert("الرادار غير متاح مؤقتاً"),
    ET.NO_ENTRY: NoEntryAlert("الرادار غير متاح مؤقتاً"),
  },

  # يجب معالجة كل إطار من الكاميرا بواسطة النموذج. إذا
  # لم يعالج modeld الإطارات بسرعة كافية يجب إسقاطها. يُطرح هذا التنبيه
  # عند إسقاط أكثر من 20% من الإطارات.
  EventName.modeldLagging: {
    ET.SOFT_DISABLE: soft_disable_alert("تأخر نموذج القيادة"),
    ET.NO_ENTRY: NoEntryAlert("تأخر نموذج القيادة"),
    ET.PERMANENT: modeld_lagging_alert,
  },

  # إلى جانب التنبؤ بالمسار وخطوط المسار وبيانات السيارة الأمامية، يتنبأ النموذج أيضاً
  # بالسرعة الحالية وسرعة الدوران للسيارة. إذا كان النموذج
  # غير متأكد جداً من السرعة الحالية بينما السيارة تتحرك، فهذا
  # يعني عادةً أن النموذج يواجه صعوبة في فهم المشهد. يُستخدم هذا
  # كمقياس لتحذير السائق.
  EventName.posenetInvalid: {
    ET.SOFT_DISABLE: soft_disable_alert("سرعة Posenet غير صالحة"),
    ET.NO_ENTRY: posenet_invalid_alert,
  },

  # عندما يكتشف محدد الموقع تسارعاً يزيد عن 40 م/ث² (~4G) نحن
  # ننبه السائق أن الجهاز ربما سقط من الزجاج الأمامي.
  EventName.deviceFalling: {
    ET.SOFT_DISABLE: soft_disable_alert("سقط الجهاز من الحامل"),
    ET.NO_ENTRY: NoEntryAlert("سقط الجهاز من الحامل"),
  },

  EventName.lowMemory: {
    ET.SOFT_DISABLE: soft_disable_alert("ذاكرة منخفضة: أعد تشغيل جهازك"),
    ET.PERMANENT: low_memory_alert,
    ET.NO_ENTRY: NoEntryAlert("ذاكرة منخفضة: أعد تشغيل جهازك"),
  },

  EventName.accFaulted: {
    ET.IMMEDIATE_DISABLE: ImmediateDisableAlert("عطل في مثبت السرعة: أعد تشغيل السيارة"),
    ET.PERMANENT: NormalPermanentAlert("عطل في مثبت السرعة: أعد تشغيل السيارة للتفعيل"),
    ET.NO_ENTRY: NoEntryAlert("عطل في مثبت السرعة: أعد تشغيل السيارة"),
  },

  EventName.espActive: {
    ET.SOFT_DISABLE: soft_disable_alert("نظام التحكم الإلكتروني بالثبات نشط"),
    ET.NO_ENTRY: NoEntryAlert("نظام التحكم الإلكتروني بالثبات نشط"),
  },

  EventName.controlsMismatch: {
    ET.IMMEDIATE_DISABLE: ImmediateDisableAlert("عدم تطابق التحكم"),
    ET.NO_ENTRY: NoEntryAlert("عدم تطابق التحكم"),
  },

  # أحياناً يمكن أن يدخل مكدس USB على الجهاز في حالة سيئة
  # مما يتسبب في فقدان الاتصال بالباندا
  EventName.usbError: {
    ET.SOFT_DISABLE: soft_disable_alert("خطأ USB: أعد تشغيل جهازك"),
    ET.PERMANENT: NormalPermanentAlert("خطأ USB: أعد تشغيل جهازك"),
    ET.NO_ENTRY: NoEntryAlert("خطأ USB: أعد تشغيل جهازك"),
  },

  # يمكن طرح هذا التنبيه للأسباب التالية:
  # - لم يتم استلام أي بيانات CAN على الإطلاق
  # - تم استلام بيانات CAN، لكن بعض الرسائل لا تُستلم بالتردد الصحيح
  # إذا لم تكن تكتب منفذاً لسيارة جديدة، فهذا عادةً بسبب أسلاك معيبة
  EventName.canError: {
    ET.IMMEDIATE_DISABLE: ImmediateDisableAlert("خطأ CAN"),
    ET.PERMANENT: Alert(
      "خطأ CAN: تحقق من التوصيلات",
      "",
      AlertStatus.normal, AlertSize.small,
      Priority.LOW, VisualAlert.none, AudibleAlert.none, 1., creation_delay=1.),
    ET.NO_ENTRY: NoEntryAlert("خطأ CAN: تحقق من التوصيلات"),
  },

  EventName.canBusMissing: {
    ET.IMMEDIATE_DISABLE: ImmediateDisableAlert("ناقل CAN مفصول"),
    ET.PERMANENT: Alert(
      "ناقل CAN مفصول: كابل معيب على الأرجح",
      "",
      AlertStatus.normal, AlertSize.small,
      Priority.LOW, VisualAlert.none, AudibleAlert.none, 1., creation_delay=1.),
    ET.NO_ENTRY: NoEntryAlert("ناقل CAN مفصول: تحقق من التوصيلات"),
  },

  EventName.steerUnavailable: {
    ET.IMMEDIATE_DISABLE: ImmediateDisableAlert("عطل LKAS: أعد تشغيل السيارة"),
    ET.PERMANENT: NormalPermanentAlert("عطل LKAS: أعد تشغيل السيارة للتفعيل"),
    ET.NO_ENTRY: NoEntryAlert("عطل LKAS: أعد تشغيل السيارة"),
  },

  EventName.reverseGear: {
    ET.PERMANENT: Alert(
      "الرجوع\nللخلف",
      "",
      AlertStatus.normal, AlertSize.full,
      Priority.LOWEST, VisualAlert.none, AudibleAlert.none, .2, creation_delay=0.5),
    ET.USER_DISABLE: ImmediateDisableAlert("ناقل الرجوع للخلف"),
    ET.NO_ENTRY: NoEntryAlert("ناقل الرجوع للخلف"),
  },

  # في السيارات التي تستخدم ACC الأصلي يمكن للسيارة أن تقرر إلغاء ACC لأسباب مختلفة.
  # عندما يحدث هذا لا يمكننا التحكم في السيارة بعد الآن لذا يجب تحذير المستخدم فوراً.
  EventName.cruiseDisabled: {
    ET.IMMEDIATE_DISABLE: ImmediateDisableAlert("مثبت السرعة مُعطّل"),
  },

  # عندما يفتح المرحل في صندوق الحزام، ينفصل ناقل CAN بين كاميرا LKAS
  # وبقية السيارة. عندما يتم استلام رسائل من كاميرا LKAS
  # على جانب السيارة يعني هذا عادةً أن المرحل لم يفتح بشكل صحيح
  # ويُطرح هذا التنبيه.
  EventName.relayMalfunction: {
    ET.IMMEDIATE_DISABLE: ImmediateDisableAlert("عطل في مرحل الحزام"),
    ET.PERMANENT: NormalPermanentAlert("عطل في مرحل الحزام", "تحقق من الأجهزة"),
    ET.NO_ENTRY: NoEntryAlert("عطل في مرحل الحزام"),
  },

  EventName.speedTooLow: {
    ET.IMMEDIATE_DISABLE: Alert(
      "تم إلغاء القائد الآلي",
      "السرعة منخفضة جداً",
      AlertStatus.normal, AlertSize.mid,
      Priority.HIGH, VisualAlert.none, AudibleAlert.disengage, 3.),
  },

  # عندما تسير السيارة أسرع من معظم السيارات في بيانات التدريب، يمكن أن تكون مخرجات النموذج غير متوقعة.
  EventName.speedTooHigh: {
    ET.WARNING: Alert(
      "السرعة عالية جداً",
      "النموذج غير متأكد عند هذه السرعة",
      AlertStatus.userPrompt, AlertSize.mid,
      Priority.HIGH, VisualAlert.steerRequired, AudibleAlert.promptRepeat, 4.),
    ET.NO_ENTRY: NoEntryAlert("أبطئ للتفعيل"),
  },

  EventName.vehicleSensorsInvalid: {
    ET.IMMEDIATE_DISABLE: ImmediateDisableAlert("مستشعرات السيارة غير صالحة"),
    ET.PERMANENT: NormalPermanentAlert("مستشعرات السيارة تُعاير", "قُد للمعايرة"),
    ET.NO_ENTRY: NoEntryAlert("مستشعرات السيارة تُعاير"),
  },

  EventName.personalityChanged: {
    ET.WARNING: personality_changed_alert,
  },

  EventName.userBookmark: {
    ET.PERMANENT: NormalPermanentAlert("تم حفظ الإشارة المرجعية", duration=1.5),
  },

  EventName.audioFeedback: {
    ET.PERMANENT: audio_feedback_alert,
  },
}


if __name__ == '__main__':
  # طباعة جميع التنبيهات حسب النوع والأولوية
  from cereal.services import SERVICE_LIST
  from collections import defaultdict

  event_names = {v: k for k, v in EventName.schema.enumerants.items()}
  alerts_by_type: dict[str, dict[Priority, list[str]]] = defaultdict(lambda: defaultdict(list))

  CP = car.CarParams.new_message()
  CS = car.CarState.new_message()
  sm = messaging.SubMaster(list(SERVICE_LIST.keys()))

  for i, alerts in EVENTS.items():
    for et, alert in alerts.items():
      if callable(alert):
        alert = alert(CP, CS, sm, False, 1, log.LongitudinalPersonality.standard)
      alerts_by_type[et][alert.priority].append(event_names[i])

  all_alerts: dict[str, list[tuple[Priority, list[str]]]] = {}
  for et, priority_alerts in alerts_by_type.items():
    all_alerts[et] = sorted(priority_alerts.items(), key=lambda x: x[0], reverse=True)

  for status, evs in sorted(all_alerts.items(), key=lambda x: x[0]):
    print(f"**** {status} ****")
    for p, alert_list in evs:
      print(f"  {repr(p)}:")
      print("   ", ', '.join(alert_list), "\n")
