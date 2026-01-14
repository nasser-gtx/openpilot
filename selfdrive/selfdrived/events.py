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


# get event name from enum
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



# ********** helper functions **********
def get_display_speed(speed_ms: float, metric: bool) -> str:
  speed = int(round(speed_ms * (CV.MS_TO_KPH if metric else CV.MS_TO_MPH)))
  unit = 'كم/س' if metric else 'ميل/س'
  return f"{speed} {unit}"


# ********** alert callback functions **********
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
  branch = get_short_branch()  # Ensure get_short_branch is cached to avoid lags on startup
  if "REPLAY" in os.environ:
    branch = "replay"

  return StartupAlert("تحذير: هذا الفرع غير مختبر", branch, alert_status=AlertStatus.userPrompt)

def below_engage_speed_alert(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int, personality) -> Alert:
  return NoEntryAlert(f"سُق فوق {get_display_speed(CP.minEnableSpeed, metric)} للتفعيل")

def below_steer_speed_alert(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int, personality) -> Alert:
  return Alert(
    f"التوجيه غير متاح تحت {get_display_speed(CP.minSteerSpeed, metric)}",
    "",
    AlertStatus.userPrompt, AlertSize.small,
    Priority.LOW, VisualAlert.none, AudibleAlert.prompt, 0.4)

def calibration_incomplete_alert(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int, personality) -> Alert:
  first_word = 'إعادة معايرة' if sm['liveCalibration'].calStatus == log.LiveCalibrationData.Status.recalibrating else 'معايرة'
  return Alert(
    f"{first_word} قيد التنفيذ: {sm['liveCalibration'].calPerc:.0f}%",
    f"سُق فوق {get_display_speed(MIN_SPEED_FILTER, metric)}",
    AlertStatus.normal, AlertSize.mid,
    Priority.LOWEST, VisualAlert.none, AudibleAlert.none, .2)

def audio_feedback_alert(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int, personality) -> Alert:
  duration = FEEDBACK_MAX_DURATION - ((sm['audioFeedback'].blockNum + 1) * SAMPLE_BUFFER / SAMPLE_RATE)
  return NormalPermanentAlert(
    "جاري تسجيل ملاحظات صوتية",
    f"متبقي {round(duration)} ثانية. اضغط مرة ثانية للحفظ مبكرًا.",
    priority=Priority.LOW)


# *** debug alerts ***
def out_of_space_alert(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int, personality) -> Alert:
  full_perc = round(100. - sm['deviceState'].freeSpacePercent)
  return NormalPermanentAlert("التخزين ممتلئ", f"المستخدم: {full_perc}%")

def posenet_invalid_alert(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int, personality) -> Alert:
  mdl = sm['modelV2'].velocity.x[0] if len(sm['modelV2'].velocity.x) else math.nan
  err = CS.vEgo - mdl
  msg = f"خطأ السرعة: {err:.1f} م/ث"
  return NoEntryAlert(msg, alert_text_1="سرعة Posenet غير صالحة")

def process_not_running_alert(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int, personality) -> Alert:
  not_running = [p.name for p in sm['managerState'].processes if not p.running and p.shouldBeRunning]
  msg = ', '.join(not_running)
  return NoEntryAlert(msg, alert_text_1="عملية لا تعمل")

def comm_issue_alert(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int, personality) -> Alert:
  bs = [s for s in sm.data.keys() if not sm.all_checks([s, ])]
  msg = ', '.join(bs[:4])
  return NoEntryAlert(msg, alert_text_1="مشكلة تواصل بين العمليات")

def camera_malfunction_alert(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int, personality) -> Alert:
  all_cams = ('roadCameraState', 'driverCameraState', 'wideRoadCameraState')
  bad_cams = [s.replace('State', '') for s in all_cams if s in sm.data.keys() and not sm.all_checks([s, ])]
  return NormalPermanentAlert("عطل في الكاميرا", ', '.join(bad_cams))

def calibration_invalid_alert(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int, personality) -> Alert:
  rpy = sm['liveCalibration'].rpyCalib
  yaw = math.degrees(rpy[2] if len(rpy) == 3 else math.nan)
  pitch = math.degrees(rpy[1] if len(rpy) == 3 else math.nan)
  angles = f"أعد تركيب الجهاز (Pitch: {pitch:.1f}°، Yaw: {yaw:.1f}°)"
  return NormalPermanentAlert("المعايرة غير صالحة", angles)

def paramsd_invalid_alert(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int, personality) -> Alert:
  if not sm['liveParameters'].angleOffsetValid:
    angle_offset_deg = sm['liveParameters'].angleOffsetDeg
    title = "تم اكتشاف عدم اتزان في التوجيه"
    text = f"انحراف الزاوية مرتفع (Offset: {angle_offset_deg:.1f}°)"
  elif not sm['liveParameters'].steerRatioValid:
    steer_ratio = sm['liveParameters'].steerRatio
    title = "اختلاف في نسبة التوجيه"
    text = f"هندسة علبة الدركسون قد تكون غير صحيحة (Ratio: {steer_ratio:.1f})"
  elif not sm['liveParameters'].stiffnessFactorValid:
    stiffness_factor = sm['liveParameters'].stiffnessFactor
    title = "صلابة الإطارات غير طبيعية"
    text = f"افحص الكفرات/الضغط/الميزان (Factor: {stiffness_factor:.1f})"
  else:
    return NoEntryAlert("خطأ مؤقت في paramsd")

  return NoEntryAlert(alert_text_1=title, alert_text_2=text)

def overheat_alert(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int, personality) -> Alert:
  cpu = max(sm['deviceState'].cpuTempC, default=0.)
  gpu = max(sm['deviceState'].gpuTempC, default=0.)
  temp = max((cpu, gpu, sm['deviceState'].memoryTempC))
  return NormalPermanentAlert("النظام ارتفعت حرارته", f"{temp:.0f} °م")

def low_memory_alert(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int, personality) -> Alert:
  return NormalPermanentAlert("الذاكرة منخفضة", f"المستخدم: {sm['deviceState'].memoryUsagePercent}%")

def high_cpu_usage_alert(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int, personality) -> Alert:
  x = max(sm['deviceState'].cpuUsagePercent, default=0.)
  return NormalPermanentAlert("استهلاك المعالج مرتفع", f"المستخدم: {x}%")

def modeld_lagging_alert(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int, personality) -> Alert:
  return NormalPermanentAlert("تأخير في نموذج القيادة", f"تم إسقاط {sm['modelV2'].frameDropPerc:.1f}% من الإطارات")

def joystick_alert(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int, personality) -> Alert:
  gb = sm['carControl'].actuators.accel / 4.
  steer = sm['carControl'].actuators.torque
  vals = f"بنزين: {round(gb * 100.)}%، توجيه: {round(steer * 100.)}%"
  return NormalPermanentAlert("وضع الجويستيك", vals)

def longitudinal_maneuver_alert(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int, personality) -> Alert:
  ad = sm['alertDebug']
  audible_alert = AudibleAlert.prompt if 'Active' in ad.alertText1 else AudibleAlert.none
  alert_status = AlertStatus.userPrompt if 'Active' in ad.alertText1 else AlertStatus.normal
  alert_size = AlertSize.mid if ad.alertText2 else AlertSize.small
  return Alert(ad.alertText1, ad.alertText2,
               alert_status, alert_size,
               Priority.LOW, VisualAlert.none, audible_alert, 0.2)

def personality_changed_alert(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int, personality) -> Alert:
  personality = str(personality).title()
  return NormalPermanentAlert(f"شخصية القيادة: {personality}", duration=1.5)

def invalid_lkas_setting_alert(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int, personality) -> Alert:
  text = "فعّل/أوقف LKAS الأصلي للتفعيل"
  if CP.brand == "tesla":
    text = "حوّل إلى مثبت السرعة الواعي بالازدحام للتفعيل"
  elif CP.brand == "mazda":
    text = "فعّل LKAS في سيارتك للتفعيل"
  elif CP.brand == "nissan":
    text = "أوقف LKAS الأصلي في سيارتك للتفعيل"
  return NormalPermanentAlert("إعداد LKAS غير صحيح", text)


EVENTS: dict[int, dict[str, Alert | AlertCallbackType]] = {
  # ********** events with no alerts **********
  EventName.stockFcw: {},
  EventName.actuatorsApiUnavailable: {},

  # ********** events only containing alerts displayed in all states **********
  EventName.joystickDebug: {
    ET.WARNING: joystick_alert,
    ET.PERMANENT: NormalPermanentAlert("وضع الجويستيك"),
  },

  EventName.longitudinalManeuver: {
    ET.WARNING: longitudinal_maneuver_alert,
    ET.PERMANENT: NormalPermanentAlert("وضع مناورة الطولي",
                                       "تأكد أن الطريق أمامك خالي"),
  },

  EventName.selfdriveInitializing: {
    ET.NO_ENTRY: NoEntryAlert("جاري تهيئة النظام"),
  },

  EventName.startup: {
    ET.PERMANENT: StartupAlert("كن مستعدًا للاستلام في أي لحظة")
  },

  EventName.startupMaster: {
    ET.PERMANENT: startup_master_alert,
  },

  EventName.startupNoControl: {
    ET.PERMANENT: StartupAlert("وضع الداش كام"),
    ET.NO_ENTRY: NoEntryAlert("وضع الداش كام"),
  },

  EventName.startupNoCar: {
    ET.PERMANENT: StartupAlert("وضع الداش كام لسيارة غير مدعومة"),
  },

  EventName.startupNoSecOcKey: {
    ET.PERMANENT: NormalPermanentAlert("وضع الداش كام",
                                       "مفتاح الأمان غير متوفر",
                                       priority=Priority.HIGH),
  },

  EventName.dashcamMode: {
    ET.PERMANENT: NormalPermanentAlert("وضع الداش كام",
                                       priority=Priority.LOWEST),
  },

  EventName.invalidLkasSetting: {
    ET.PERMANENT: invalid_lkas_setting_alert,
    ET.NO_ENTRY: NoEntryAlert("إعداد LKAS غير صحيح"),
  },

  EventName.cruiseMismatch: {
    #ET.PERMANENT: ImmediateDisableAlert("القائد الآلي فشل في إلغاء مثبت السرعة"),
  },

  EventName.carUnrecognized: {
    ET.PERMANENT: NormalPermanentAlert("وضع الداش كام",
                                       "السيارة غير معروفة",
                                       priority=Priority.LOWEST),
  },

  EventName.aeb: {
    ET.PERMANENT: Alert(
      "فرامل!",
      "فرملة طوارئ: خطر اصطدام",
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
      "تم رصد خروج عن المسار",
      "",
      AlertStatus.userPrompt, AlertSize.small,
      Priority.LOW, VisualAlert.ldw, AudibleAlert.prompt, 3.),
  },

  # ********** engaged-only examples (translated in provided section) **********
  EventName.steerTempUnavailableSilent: {
    ET.WARNING: Alert(
      "التوجيه غير متاح مؤقتًا",
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
      "افصل فورًا",
      "السائق مشتت",
      AlertStatus.critical, AlertSize.full,
      Priority.HIGH, VisualAlert.steerRequired, AudibleAlert.warningImmediate, .1),
  },

  EventName.preDriverUnresponsive: {
    ET.PERMANENT: Alert(
      "المس الدركسون: لم يتم رصد وجه",
      "",
      AlertStatus.normal, AlertSize.small,
      Priority.LOW, VisualAlert.steerRequired, AudibleAlert.none, .1),
  },

  EventName.promptDriverUnresponsive: {
    ET.PERMANENT: Alert(
      "المس الدركسون",
      "السائق غير مستجيب",
      AlertStatus.userPrompt, AlertSize.mid,
      Priority.MID, VisualAlert.steerRequired, AudibleAlert.promptDistracted, .1),
  },

  EventName.driverUnresponsive: {
    ET.PERMANENT: Alert(
      "افصل فورًا",
      "السائق غير مستجيب",
      AlertStatus.critical, AlertSize.full,
      Priority.HIGH, VisualAlert.steerRequired, AudibleAlert.warningImmediate, .1),
  },

  EventName.manualRestart: {
    ET.WARNING: Alert(
      "استلم التحكم",
      "كمّل قيادة يدويًا",
      AlertStatus.userPrompt, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.none, .2),
  },

  EventName.resumeRequired: {
    ET.WARNING: Alert(
      "اضغط Resume للخروج من التوقف",
      "",
      AlertStatus.userPrompt, AlertSize.small,
      Priority.LOW, VisualAlert.none, AudibleAlert.none, .2),
  },

  EventName.belowSteerSpeed: {
    ET.WARNING: below_steer_speed_alert,
  },

  EventName.preLaneChangeLeft: {
    ET.WARNING: Alert(
      "وجّه يسار لبدء تغيير المسار عند الأمان",
      "",
      AlertStatus.normal, AlertSize.small,
      Priority.LOW, VisualAlert.none, AudibleAlert.none, .1),
  },

  EventName.preLaneChangeRight: {
    ET.WARNING: Alert(
      "وجّه يمين لبدء تغيير المسار عند الأمان",
      "",
      AlertStatus.normal, AlertSize.small,
      Priority.LOW, VisualAlert.none, AudibleAlert.none, .1),
  },

  EventName.laneChangeBlocked: {
    ET.WARNING: Alert(
      "تم رصد سيارة في النقطة العمياء",
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
      "استلم التحكم",
      "المنعطف يتجاوز حد التوجيه",
      AlertStatus.userPrompt, AlertSize.mid,
      Priority.LOW, VisualAlert.steerRequired, AudibleAlert.promptRepeat, 2.),
  },

  EventName.fanMalfunction: {
    ET.PERMANENT: NormalPermanentAlert("عطل بالمروحة", "غالبًا مشكلة هاردوير"),
  },

  EventName.cameraMalfunction: {
    ET.PERMANENT: camera_malfunction_alert,
    ET.SOFT_DISABLE: soft_disable_alert("عطل في الكاميرا"),
    ET.NO_ENTRY: NoEntryAlert("عطل في الكاميرا: أعد تشغيل الجهاز"),
  },

  EventName.cameraFrameRate: {
    ET.PERMANENT: NormalPermanentAlert("انخفاض معدل إطارات الكاميرا", "أعد تشغيل الجهاز"),
    ET.SOFT_DISABLE: soft_disable_alert("انخفاض معدل إطارات الكاميرا"),
    ET.NO_ENTRY: NoEntryAlert("انخفاض معدل إطارات الكاميرا: أعد تشغيل الجهاز"),
  },

  EventName.locationdTemporaryError: {
    ET.NO_ENTRY: NoEntryAlert("خطأ مؤقت في locationd"),
    ET.SOFT_DISABLE: soft_disable_alert("خطأ مؤقت في locationd"),
  },

  EventName.locationdPermanentError: {
    ET.NO_ENTRY: NoEntryAlert("خطأ دائم في locationd"),
    ET.IMMEDIATE_DISABLE: ImmediateDisableAlert("خطأ دائم في locationd"),
    ET.PERMANENT: NormalPermanentAlert("خطأ دائم في locationd"),
  },

  EventName.paramsdTemporaryError: {
    ET.NO_ENTRY: paramsd_invalid_alert,
    ET.SOFT_DISABLE: soft_disable_alert("خطأ مؤقت في paramsd"),
  },

  EventName.paramsdPermanentError: {
    ET.NO_ENTRY: NoEntryAlert("خطأ دائم في paramsd"),
    ET.IMMEDIATE_DISABLE: ImmediateDisableAlert("خطأ دائم في paramsd"),
    ET.PERMANENT: NormalPermanentAlert("خطأ دائم في paramsd"),
  },

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
      "اضغط Resume للخروج من تثبيت الفرامل",
      "",
      AlertStatus.userPrompt, AlertSize.small,
      Priority.LOW, VisualAlert.none, AudibleAlert.none, .2),
  },

  EventName.parkBrake: {
    ET.USER_DISABLE: EngagementAlert(AudibleAlert.disengage),
    ET.NO_ENTRY: NoEntryAlert("فرامل اليد مفعّلة"),
  },

  EventName.pedalPressed: {
    ET.USER_DISABLE: EngagementAlert(AudibleAlert.disengage),
    ET.NO_ENTRY: NoEntryAlert("تم الضغط على دواسة",
                              visual_alert=VisualAlert.brakePressed),
  },

  EventName.steerDisengage: {
    ET.USER_DISABLE: EngagementAlert(AudibleAlert.disengage),
    ET.NO_ENTRY: NoEntryAlert("تم الضغط على الدركسون"),
  },

  EventName.preEnableStandstill: {
    ET.PRE_ENABLE: Alert(
      "ارفع رجلك عن الفرامل للتفعيل",
      "",
      AlertStatus.normal, AlertSize.small,
      Priority.LOWEST, VisualAlert.none, AudibleAlert.none, .1, creation_delay=1.),
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
    ET.NO_ENTRY: NoEntryAlert("تم تعطيل مثبت السرعة التكيفي"),
  },

  EventName.steerTempUnavailable: {
    ET.SOFT_DISABLE: soft_disable_alert("التوجيه غير متاح مؤقتًا"),
    ET.NO_ENTRY: NoEntryAlert("التوجيه غير متاح مؤقتًا"),
  },

  EventName.steerTimeLimit: {
    ET.SOFT_DISABLE: soft_disable_alert("حد زمن توجيه السيارة"),
    ET.NO_ENTRY: NoEntryAlert("حد زمن توجيه السيارة"),
  },

  EventName.outOfSpace: {
    ET.PERMANENT: out_of_space_alert,
    ET.NO_ENTRY: NoEntryAlert("التخزين ممتلئ"),
  },

  EventName.belowEngageSpeed: {
    ET.NO_ENTRY: below_engage_speed_alert,
  },

  EventName.sensorDataInvalid: {
    ET.PERMANENT: Alert(
      "بيانات الحساسات غير صحيحة",
      "احتمال مشكلة هاردوير",
      AlertStatus.normal, AlertSize.mid,
      Priority.LOWER, VisualAlert.none, AudibleAlert.none, .2, creation_delay=1.),
    ET.NO_ENTRY: NoEntryAlert("بيانات الحساسات غير صحيحة"),
    ET.SOFT_DISABLE: soft_disable_alert("بيانات الحساسات غير صحيحة"),
  },

  EventName.tooDistracted: {
    ET.NO_ENTRY: NoEntryAlert("مستوى التشتت مرتفع جدًا"),
  },

  EventName.excessiveActuation: {
    ET.SOFT_DISABLE: soft_disable_alert("تحكم مفرط"),
    ET.NO_ENTRY: NoEntryAlert("تحكم مفرط"),
  },

  EventName.overheat: {
    ET.PERMANENT: overheat_alert,
    ET.SOFT_DISABLE: soft_disable_alert("النظام ارتفعت حرارته"),
    ET.NO_ENTRY: NoEntryAlert("النظام ارتفعت حرارته"),
  },

  EventName.wrongGear: {
    ET.SOFT_DISABLE: user_soft_disable_alert("القير ليس على D"),
    ET.NO_ENTRY: NoEntryAlert("القير ليس على D"),
  },

  EventName.calibrationInvalid: {
    ET.PERMANENT: calibration_invalid_alert,
    ET.SOFT_DISABLE: soft_disable_alert("المعايرة غير صالحة: أعد تركيب الجهاز وأعد المعايرة"),
    ET.NO_ENTRY: NoEntryAlert("المعايرة غير صالحة: أعد تركيب الجهاز وأعد المعايرة"),
  },

  EventName.calibrationIncomplete: {
    ET.PERMANENT: calibration_incomplete_alert,
    ET.SOFT_DISABLE: soft_disable_alert("المعايرة غير مكتملة"),
    ET.NO_ENTRY: NoEntryAlert("المعايرة قيد التنفيذ"),
  },

  EventName.calibrationRecalibrating: {
    ET.PERMANENT: calibration_incomplete_alert,
    ET.SOFT_DISABLE: soft_disable_alert("تم رصد إعادة تركيب الجهاز: جاري إعادة المعايرة"),
    ET.NO_ENTRY: NoEntryAlert("تم رصد إعادة تركيب الجهاز: جاري إعادة المعايرة"),
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
    ET.SOFT_DISABLE: soft_disable_alert("تم تعطيل نظام الثبات الإلكتروني"),
    ET.NO_ENTRY: NoEntryAlert("تم تعطيل نظام الثبات الإلكتروني"),
  },

  EventName.lowBattery: {
    ET.SOFT_DISABLE: soft_disable_alert("البطارية منخفضة"),
    ET.NO_ENTRY: NoEntryAlert("البطارية منخفضة"),
  },

  EventName.commIssue: {
    ET.SOFT_DISABLE: soft_disable_alert("مشكلة تواصل بين العمليات"),
    ET.NO_ENTRY: comm_issue_alert,
  },

  EventName.commIssueAvgFreq: {
    ET.SOFT_DISABLE: soft_disable_alert("معدل تواصل منخفض بين العمليات"),
    ET.NO_ENTRY: NoEntryAlert("معدل تواصل منخفض بين العمليات"),
  },

  EventName.selfdrivedLagging: {
    ET.SOFT_DISABLE: soft_disable_alert("النظام فيه تأخير"),
    ET.NO_ENTRY: NoEntryAlert("عملية القيادة الذاتية فيها تأخير: أعد تشغيل الجهاز"),
  },

  EventName.processNotRunning: {
    ET.NO_ENTRY: process_not_running_alert,
    ET.SOFT_DISABLE: soft_disable_alert("عملية لا تعمل"),
  },

  EventName.radarFault: {
    ET.SOFT_DISABLE: soft_disable_alert("خطأ بالرادار: أعد تشغيل السيارة"),
    ET.NO_ENTRY: NoEntryAlert("خطأ بالرادار: أعد تشغيل السيارة"),
  },

  EventName.radarTempUnavailable: {
    ET.SOFT_DISABLE: soft_disable_alert("الرادار غير متاح مؤقتًا"),
    ET.NO_ENTRY: NoEntryAlert("الرادار غير متاح مؤقتًا"),
  },

  EventName.modeldLagging: {
    ET.SOFT_DISABLE: soft_disable_alert("تأخير في نموذج القيادة"),
    ET.NO_ENTRY: NoEntryAlert("تأخير في نموذج القيادة"),
    ET.PERMANENT: modeld_lagging_alert,
  },

  EventName.posenetInvalid: {
    ET.SOFT_DISABLE: soft_disable_alert("سرعة Posenet غير صالحة"),
    ET.NO_ENTRY: posenet_invalid_alert,
  },

  EventName.deviceFalling: {
    ET.SOFT_DISABLE: soft_disable_alert("الجهاز سقط من القاعدة"),
    ET.NO_ENTRY: NoEntryAlert("الجهاز سقط من القاعدة"),
  },

  EventName.lowMemory: {
    ET.SOFT_DISABLE: soft_disable_alert("الذاكرة منخفضة: أعد تشغيل الجهاز"),
    ET.PERMANENT: low_memory_alert,
    ET.NO_ENTRY: NoEntryAlert("الذاكرة منخفضة: أعد تشغيل الجهاز"),
  },

  EventName.accFaulted: {
    ET.IMMEDIATE_DISABLE: ImmediateDisableAlert("عطل في مثبت السرعة: أعد تشغيل السيارة"),
    ET.PERMANENT: NormalPermanentAlert("عطل في مثبت السرعة: أعد تشغيل السيارة للتفعيل"),
    ET.NO_ENTRY: NoEntryAlert("عطل في مثبت السرعة: أعد تشغيل السيارة"),
  },

  EventName.espActive: {
    ET.SOFT_DISABLE: soft_disable_alert("نظام الثبات الإلكتروني يعمل"),
    ET.NO_ENTRY: NoEntryAlert("نظام الثبات الإلكتروني يعمل"),
  },

  EventName.controlsMismatch: {
    ET.IMMEDIATE_DISABLE: ImmediateDisableAlert("عدم تطابق في التحكم"),
    ET.NO_ENTRY: NoEntryAlert("عدم تطابق في التحكم"),
  },

  EventName.usbError: {
    ET.SOFT_DISABLE: soft_disable_alert("خطأ USB: أعد تشغيل الجهاز"),
    ET.PERMANENT: NormalPermanentAlert("خطأ USB: أعد تشغيل الجهاز"),
    ET.NO_ENTRY: NoEntryAlert("خطأ USB: أعد تشغيل الجهاز"),
  },

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
    ET.IMMEDIATE_DISABLE: ImmediateDisableAlert("تم فصل CAN Bus"),
    ET.PERMANENT: Alert(
      "تم فصل CAN Bus: غالبًا سلك/كيبل تالف",
      "",
      AlertStatus.normal, AlertSize.small,
      Priority.LOW, VisualAlert.none, AudibleAlert.none, 1., creation_delay=1.),
    ET.NO_ENTRY: NoEntryAlert("تم فصل CAN Bus: تحقق من التوصيلات"),
  },

  EventName.steerUnavailable: {
    ET.IMMEDIATE_DISABLE: ImmediateDisableAlert("عطل LKAS: أعد تشغيل السيارة"),
    ET.PERMANENT: NormalPermanentAlert("عطل LKAS: أعد تشغيل السيارة للتفعيل"),
    ET.NO_ENTRY: NoEntryAlert("عطل LKAS: أعد تشغيل السيارة"),
  },

  EventName.reverseGear: {
    ET.PERMANENT: Alert(
      "ريوس\nقير",
      "",
      AlertStatus.normal, AlertSize.full,
      Priority.LOWEST, VisualAlert.none, AudibleAlert.none, .2, creation_delay=0.5),
    ET.USER_DISABLE: ImmediateDisableAlert("ريوس قير"),
    ET.NO_ENTRY: NoEntryAlert("ريوس قير"),
  },

  EventName.cruiseDisabled: {
    ET.IMMEDIATE_DISABLE: ImmediateDisableAlert("مثبت السرعة مطفّى"),
  },

  EventName.relayMalfunction: {
    ET.IMMEDIATE_DISABLE: ImmediateDisableAlert("عطل ريليه الهارنس"),
    ET.PERMANENT: NormalPermanentAlert("عطل ريليه الهارنس", "تحقق من الهاردوير"),
    ET.NO_ENTRY: NoEntryAlert("عطل ريليه الهارنس"),
  },

  EventName.speedTooLow: {
    ET.IMMEDIATE_DISABLE: Alert(
      "تم إلغاء القائد الآلي",
      "السرعة منخفضة جدًا",
      AlertStatus.normal, AlertSize.mid,
      Priority.HIGH, VisualAlert.none, AudibleAlert.disengage, 3.),
  },

  EventName.speedTooHigh: {
    ET.WARNING: Alert(
      "السرعة عالية جدًا",
      "النموذج غير واثق عند هذه السرعة",
      AlertStatus.userPrompt, AlertSize.mid,
      Priority.HIGH, VisualAlert.steerRequired, AudibleAlert.promptRepeat, 4.),
    ET.NO_ENTRY: NoEntryAlert("خفف السرعة للتفعيل"),
  },

  EventName.vehicleSensorsInvalid: {
    ET.IMMEDIATE_DISABLE: ImmediateDisableAlert("حساسات السيارة غير صحيحة"),
    ET.PERMANENT: NormalPermanentAlert("جاري معايرة حساسات السيارة", "سُق لاستكمال المعايرة"),
    ET.NO_ENTRY: NoEntryAlert("جاري معايرة حساسات السيارة"),
  },

  EventName.personalityChanged: {
    ET.WARNING: personality_changed_alert,
  },

  EventName.userBookmark: {
    ET.PERMANENT: NormalPermanentAlert("تم حفظ العلامة", duration=1.5),
  },

  EventName.audioFeedback: {
    ET.PERMANENT: audio_feedback_alert,
  },
}


if __name__ == '__main__':
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
