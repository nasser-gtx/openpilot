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
  unit = 'km/h' if metric else 'mph'
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

  return StartupAlert("تحذير: هذا الفرع لم يُختبر", branch, alert_status=AlertStatus.userPrompt)

def below_engage_speed_alert(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int, personality) -> Alert:
  return NoEntryAlert(f"قُد فوق {get_display_speed(CP.minEnableSpeed, metric)} للتفعيل")


def below_steer_speed_alert(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int, personality) -> Alert:
  return Alert(
    f"التوجيه غير متاح تحت {get_display_speed(CP.minSteerSpeed, metric)}",
    "",
    AlertStatus.userPrompt, AlertSize.small,
    Priority.LOW, VisualAlert.none, AudibleAlert.prompt, 0.4)


def calibration_incomplete_alert(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int, personality) -> Alert:
  first_word = 'إعادة المعايرة' if sm['liveCalibration'].calStatus == log.LiveCalibrationData.Status.recalibrating else 'معايرة'
  return Alert(
    f"معايرة {first_word}: {sm['liveCalibration'].calPerc:.0f}%",
    f"قُد فوق {get_display_speed(MIN_SPEED_FILTER, metric)}",
    AlertStatus.normal, AlertSize.mid,
    Priority.LOWEST, VisualAlert.none, AudibleAlert.none, .2)


def audio_feedback_alert(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int, personality) -> Alert:
  duration = FEEDBACK_MAX_DURATION - ((sm['audioFeedback'].blockNum + 1) * SAMPLE_BUFFER / SAMPLE_RATE)
  return NormalPermanentAlert(
    "جاري تسجيل الصوت",
    f"{round(duration)} ثانية متبقية. اضغط مجدداً للحفظ المبكر.",
    priority=Priority.LOW)


# *** debug alerts ***

def out_of_space_alert(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int, personality) -> Alert:
  full_perc = round(100. - sm['deviceState'].freeSpacePercent)
  return NormalPermanentAlert("مساحة التخزين ممتلئة", f"{full_perc}% full")


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
  msg = ', '.join(bs[:4])  # can't fit too many on one line
  return NoEntryAlert(msg, alert_text_1="مشكلة في التواصل بين العمليات")


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
    title = "تم اكتشاف خلل في محاذاة التوجيه"
    text = f"زاوية الإزاحة مرتفعة جداً (الإزاحة: {angle_offset_deg:.1f}°)"
  elif not sm['liveParameters'].steerRatioValid:
    steer_ratio = sm['liveParameters'].steerRatio
    title = "عدم تطابق نسبة التوجيه"
    text = f"هندسة رف التوجيه قد تكون خاطئة (النسبة: {steer_ratio:.1f})"
  elif not sm['liveParameters'].stiffnessFactorValid:
    stiffness_factor = sm['liveParameters'].stiffnessFactor
    title = "صلابة إطارات غير طبيعية"
    text = f"افحص الإطارات والضغط والمحاذاة (المعامل: {stiffness_factor:.1f})"
  else:
    return NoEntryAlert("خطأ مؤقت في paramsd")

  return NoEntryAlert(alert_text_1=title, alert_text_2=text)

def overheat_alert(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int, personality) -> Alert:
  cpu = max(sm['deviceState'].cpuTempC, default=0.)
  gpu = max(sm['deviceState'].gpuTempC, default=0.)
  temp = max((cpu, gpu, sm['deviceState'].memoryTempC))
  return NormalPermanentAlert("النظام مرتفع الحرارة", f"{temp:.0f} °C")


def low_memory_alert(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int, personality) -> Alert:
  return NormalPermanentAlert("الذاكرة منخفضة", f"{sm['deviceState'].memoryUsagePercent}% used")


def high_cpu_usage_alert(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int, personality) -> Alert:
  x = max(sm['deviceState'].cpuUsagePercent, default=0.)
  return NormalPermanentAlert("استخدام المعالج مرتفع", f"{x}% used")


def modeld_lagging_alert(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int, personality) -> Alert:
  return NormalPermanentAlert("تأخر في نموذج القيادة", f"{sm['modelV2'].frameDropPerc:.1f}% frames dropped")


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
  personality = str(personality).title()
  return NormalPermanentAlert(f"أسلوب القيادة: {personality}", duration=1.5)


def invalid_lkas_setting_alert(CP: car.CarParams, CS: car.CarState, sm: messaging.SubMaster, metric: bool, soft_disable_time: int, personality) -> Alert:
  text = "شغّل أو أوقف LKAS للتفعيل"
  if CP.brand == "tesla":
    text = "انتقل لمثبّت السرعة المدرك للحركة للتفعيل"
  elif CP.brand == "mazda":
    text = "فعّل LKAS في سيارتك للتفعيل"
  elif CP.brand == "nissan":
    text = "أوقف LKAS الأصلي في سيارتك للتفعيل"
  return NormalPermanentAlert("إعداد LKAS غير صالح", text)



EVENTS: dict[int, dict[str, Alert | AlertCallbackType]] = {
  # ********** events with no alerts **********

  EventName.stockFcw: {},
  EventName.actuatorsApiUnavailable: {},

  # ********** events only containing alerts displayed in all states **********

  EventName.joystickDebug: {
    ET.WARNING: joystick_alert,
    ET.PERMANENT: NormalPermanentAlert("وضع عصا التحكم"),
  },

  EventName.longitudinalManeuver: {
    ET.WARNING: longitudinal_maneuver_alert,
    ET.PERMANENT: NormalPermanentAlert("وضع المناورة الطولية",
                                       "تأكد من خلو الطريق أمامك"),
  },

  EventName.selfdriveInitializing: {
    ET.NO_ENTRY: NoEntryAlert("جاري تهيئة النظام"),
  },

  EventName.startup: {
    ET.PERMANENT: StartupAlert("كن مستعداً لتولّي القيادة في أي وقت")
  },

  EventName.startupMaster: {
    ET.PERMANENT: startup_master_alert,
  },

  EventName.startupNoControl: {
    ET.PERMANENT: StartupAlert("وضع كاميرا التسجيل"),
    ET.NO_ENTRY: NoEntryAlert("وضع كاميرا التسجيل"),
  },

  EventName.startupNoCar: {
    ET.PERMANENT: StartupAlert("وضع كاميرا التسجيل (سيارة غير مدعومة)"),
  },

  EventName.startupNoSecOcKey: {
    ET.PERMANENT: NormalPermanentAlert("وضع كاميرا التسجيل",
                                       "مفتاح الأمان غير متاح",
                                       priority=Priority.HIGH),
  },

  EventName.dashcamMode: {
    ET.PERMANENT: NormalPermanentAlert("وضع كاميرا التسجيل",
                                       priority=Priority.LOWEST),
  },

  EventName.invalidLkasSetting: {
    ET.PERMANENT: invalid_lkas_setting_alert,
    ET.NO_ENTRY: NoEntryAlert("إعداد LKAS غير صالح"),
  },

  EventName.cruiseMismatch: {
    #ET.PERMANENT: ImmediateDisableAlert("openpilot failed to cancel cruise"),
  },

  # openpilot doesn't recognize the car. This switches openpilot into a
  # read-only mode. This can be solved by adding your fingerprint.
  # See https://github.com/commaai/openpilot/wiki/Fingerprinting for more information
  EventName.carUnrecognized: {
    ET.PERMANENT: NormalPermanentAlert("وضع كاميرا التسجيل",
                                       "السيارة غير معروفة",
                                       priority=Priority.LOWEST),
  },

  EventName.aeb: {
    ET.PERMANENT: Alert(
      "فرامل!",
      "فرامل طارئة: خطر تصادم",
      AlertStatus.critical, AlertSize.full,
      Priority.HIGHEST, VisualAlert.fcw, AudibleAlert.none, 2.),
    ET.NO_ENTRY: NoEntryAlert("نظام AEB: خطر تصادم"),
  },

  EventName.stockAeb: {
    ET.PERMANENT: Alert(
      "فرامل!",
      "نظام AEB الأصلي: خطر تصادم",
      AlertStatus.critical, AlertSize.full,
      Priority.HIGHEST, VisualAlert.fcw, AudibleAlert.none, 2.),
    ET.NO_ENTRY: NoEntryAlert("نظام AEB الأصلي: خطر تصادم"),
  },

  EventName.fcw: {
    ET.PERMANENT: Alert(
      "فرامل!",
      "خطر تصادم",
      AlertStatus.critical, AlertSize.full,
      Priority.HIGHEST, VisualAlert.fcw, AudibleAlert.warningSoft, 2.),
  },

  EventName.ldw: {
    ET.PERMANENT: Alert(
      "تم اكتشاف مغادرة المسار",
      "",
      AlertStatus.userPrompt, AlertSize.small,
      Priority.LOW, VisualAlert.ldw, AudibleAlert.prompt, 3.),
  },

  # ********** events only containing alerts that display while engaged **********

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
      "السائق مشتت الانتباه",
      AlertStatus.userPrompt, AlertSize.mid,
      Priority.MID, VisualAlert.steerRequired, AudibleAlert.promptDistracted, .1),
  },

  EventName.driverDistracted: {
    ET.PERMANENT: Alert(
      "أوقف التفعيل فوراً",
      "السائق مشتت الانتباه",
      AlertStatus.critical, AlertSize.full,
      Priority.HIGH, VisualAlert.steerRequired, AudibleAlert.warningImmediate, .1),
  },

  EventName.preDriverUnresponsive: {
    ET.PERMANENT: Alert(
      "أمسك عجلة القيادة: لم يتم الكشف عن وجه",
      "",
      AlertStatus.normal, AlertSize.small,
      Priority.LOW, VisualAlert.steerRequired, AudibleAlert.none, .1),
  },

  EventName.promptDriverUnresponsive: {
    ET.PERMANENT: Alert(
      "أمسك عجلة القيادة",
      "السائق لا يستجيب",
      AlertStatus.userPrompt, AlertSize.mid,
      Priority.MID, VisualAlert.steerRequired, AudibleAlert.promptDistracted, .1),
  },

  EventName.driverUnresponsive: {
    ET.PERMANENT: Alert(
      "أوقف التفعيل فوراً",
      "السائق لا يستجيب",
      AlertStatus.critical, AlertSize.full,
      Priority.HIGH, VisualAlert.steerRequired, AudibleAlert.warningImmediate, .1),
  },

  EventName.manualRestart: {
    ET.WARNING: Alert(
      "تولّ القيادة",
      "استأنف القيادة يدوياً",
      AlertStatus.userPrompt, AlertSize.mid,
      Priority.LOW, VisualAlert.none, AudibleAlert.none, .2),
  },

  EventName.resumeRequired: {
    ET.WARNING: Alert(
      "اضغط استئناف للخروج من التوقف",
      "",
      AlertStatus.userPrompt, AlertSize.small,
      Priority.LOW, VisualAlert.none, AudibleAlert.none, .2),
  },

  EventName.belowSteerSpeed: {
    ET.WARNING: below_steer_speed_alert,
  },

  EventName.preLaneChangeLeft: {
    ET.WARNING: Alert(
      "وجّه يساراً لبدء تغيير المسار عند الأمان",
      "",
      AlertStatus.normal, AlertSize.small,
      Priority.LOW, VisualAlert.none, AudibleAlert.none, .1),
  },

  EventName.preLaneChangeRight: {
    ET.WARNING: Alert(
      "وجّه يميناً لبدء تغيير المسار عند الأمان",
      "",
      AlertStatus.normal, AlertSize.small,
      Priority.LOW, VisualAlert.none, AudibleAlert.none, .1),
  },

  EventName.laneChangeBlocked: {
    ET.WARNING: Alert(
      "يوجد سيارة في النقطة العمياء",
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
      "تولّ القيادة",
      "الانعطاف يتجاوز حد التوجيه",
      AlertStatus.userPrompt, AlertSize.mid,
      Priority.LOW, VisualAlert.steerRequired, AudibleAlert.promptRepeat, 2.),
  },

  # Thrown when the fan is driven at >50% but is not rotating
  EventName.fanMalfunction: {
    ET.PERMANENT: NormalPermanentAlert("عطل في المروحة", "على الأرجح عطل في الأجهزة"),
  },

  # Camera is not outputting frames
  EventName.cameraMalfunction: {
    ET.PERMANENT: camera_malfunction_alert,
    ET.SOFT_DISABLE: soft_disable_alert("عطل في الكاميرا"),
    ET.NO_ENTRY: NoEntryAlert("عطل في الكاميرا: أعد تشغيل الجهاز"),
  },
  # Camera framerate too low
  EventName.cameraFrameRate: {
    ET.PERMANENT: NormalPermanentAlert("معدل إطارات الكاميرا منخفض", "أعد تشغيل الجهاز"),
    ET.SOFT_DISABLE: soft_disable_alert("معدل إطارات الكاميرا منخفض"),
    ET.NO_ENTRY: NoEntryAlert("معدل إطارات الكاميرا منخفض: أعد تشغيل الجهاز"),
  },

  # Unused

  EventName.locationdTemporaryError: {
    ET.NO_ENTRY: NoEntryAlert("خطأ مؤقت في locationd"),
    ET.SOFT_DISABLE: soft_disable_alert("خطأ مؤقت في locationd"),
  },

  EventName.locationdPermanentError: {
    ET.NO_ENTRY: NoEntryAlert("خطأ دائم في locationd"),
    ET.IMMEDIATE_DISABLE: ImmediateDisableAlert("خطأ دائم في locationd"),
    ET.PERMANENT: NormalPermanentAlert("خطأ دائم في locationd"),
  },

  # openpilot tries to learn certain parameters about your car by observing
  # how the car behaves to steering inputs from both human and openpilot driving.
  # This includes:
  # - steer ratio: gear ratio of the steering rack. Steering angle divided by tire angle
  # - tire stiffness: how much grip your tires have
  # - angle offset: most steering angle sensors are offset and measure a non zero angle when driving straight
  # This alert is thrown when any of these values exceed a sanity check. This can be caused by
  # bad alignment or bad sensor data. If this happens consistently consider creating an issue on GitHub
  EventName.paramsdTemporaryError: {
    ET.NO_ENTRY: paramsd_invalid_alert,
    ET.SOFT_DISABLE: soft_disable_alert("خطأ مؤقت في paramsd"),
  },

  EventName.paramsdPermanentError: {
    ET.NO_ENTRY: NoEntryAlert("خطأ دائم في paramsd"),
    ET.IMMEDIATE_DISABLE: ImmediateDisableAlert("خطأ دائم في paramsd"),
    ET.PERMANENT: NormalPermanentAlert("خطأ دائم في paramsd"),
  },

  # ********** events that affect controls state transitions **********

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
    ET.NO_ENTRY: NoEntryAlert("تم الإلغاء"),
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
    ET.NO_ENTRY: NoEntryAlert("الفرامل اليدوية مفعّلة"),
  },

  EventName.pedalPressed: {
    ET.USER_DISABLE: EngagementAlert(AudibleAlert.disengage),
    ET.NO_ENTRY: NoEntryAlert("الدواسة مضغوطة",
                              visual_alert=VisualAlert.brakePressed),
  },

  EventName.steerDisengage: {
    ET.USER_DISABLE: EngagementAlert(AudibleAlert.disengage),
    ET.NO_ENTRY: NoEntryAlert("تم الضغط على التوجيه"),
  },

  EventName.preEnableStandstill: {
    ET.PRE_ENABLE: Alert(
      "أترك الفرامل للتفعيل",
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
    ET.NO_ENTRY: NoEntryAlert("مثبّت السرعة التكيّفي معطّل"),
  },

  EventName.steerTempUnavailable: {
    ET.SOFT_DISABLE: soft_disable_alert("التوجيه غير متاح مؤقتاً"),
    ET.NO_ENTRY: NoEntryAlert("التوجيه غير متاح مؤقتاً"),
  },

  EventName.steerTimeLimit: {
    ET.SOFT_DISABLE: soft_disable_alert("تجاوز حد وقت التوجيه"),
    ET.NO_ENTRY: NoEntryAlert("تجاوز حد وقت التوجيه"),
  },

  EventName.outOfSpace: {
    ET.PERMANENT: out_of_space_alert,
    ET.NO_ENTRY: NoEntryAlert("مساحة التخزين ممتلئة"),
  },

  EventName.belowEngageSpeed: {
    ET.NO_ENTRY: below_engage_speed_alert,
  },

  EventName.sensorDataInvalid: {
    ET.PERMANENT: Alert(
      "بيانات المستشعر غير صالحة",
      "احتمال عطل في الأجهزة",
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
    ET.SOFT_DISABLE: soft_disable_alert("النظام مرتفع الحرارة"),
    ET.NO_ENTRY: NoEntryAlert("النظام مرتفع الحرارة"),
  },

  EventName.wrongGear: {
    ET.SOFT_DISABLE: user_soft_disable_alert("ناقل الحركة ليس في وضع D"),
    ET.NO_ENTRY: NoEntryAlert("ناقل الحركة ليس في وضع D"),
  },

  # This alert is thrown when the calibration angles are outside of the acceptable range.
  # For example if the device is pointed too much to the left or the right.
  # Usually this can only be solved by removing the mount from the windshield completely,
  # and attaching while making sure the device is pointed straight forward and is level.
  # See https://comma.ai/setup for more information
  EventName.calibrationInvalid: {
    ET.PERMANENT: calibration_invalid_alert,
    ET.SOFT_DISABLE: soft_disable_alert("معايرة غير صالحة: أعد التركيب وأعد المعايرة"),
    ET.NO_ENTRY: NoEntryAlert("معايرة غير صالحة: أعد التركيب وأعد المعايرة"),
  },

  EventName.calibrationIncomplete: {
    ET.PERMANENT: calibration_incomplete_alert,
    ET.SOFT_DISABLE: soft_disable_alert("المعايرة غير مكتملة"),
    ET.NO_ENTRY: NoEntryAlert("جاري المعايرة"),
  },

  EventName.calibrationRecalibrating: {
    ET.PERMANENT: calibration_incomplete_alert,
    ET.SOFT_DISABLE: soft_disable_alert("تم اكتشاف إعادة تركيب: جاري المعايرة"),
    ET.NO_ENTRY: NoEntryAlert("Remount Detected: Recalibrating"),
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
    ET.SOFT_DISABLE: soft_disable_alert("نظام الاستقرار الإلكتروني معطّل"),
    ET.NO_ENTRY: NoEntryAlert("نظام الاستقرار الإلكتروني معطّل"),
  },

  EventName.lowBattery: {
    ET.SOFT_DISABLE: soft_disable_alert("البطارية منخفضة"),
    ET.NO_ENTRY: NoEntryAlert("البطارية منخفضة"),
  },

  # Different openpilot services communicate between each other at a certain
  # interval. If communication does not follow the regular schedule this alert
  # is thrown. This can mean a service crashed, did not broadcast a message for
  # ten times the regular interval, or the average interval is more than 10% too high.
  EventName.commIssue: {
    ET.SOFT_DISABLE: soft_disable_alert("مشكلة في التواصل بين العمليات"),
    ET.NO_ENTRY: comm_issue_alert,
  },
  EventName.commIssueAvgFreq: {
    ET.SOFT_DISABLE: soft_disable_alert("معدل تواصل منخفض بين العمليات"),
    ET.NO_ENTRY: NoEntryAlert("معدل تواصل منخفض بين العمليات"),
  },

  EventName.selfdrivedLagging: {
    ET.SOFT_DISABLE: soft_disable_alert("تأخر في النظام"),
    ET.NO_ENTRY: NoEntryAlert("تأخر في القيادة: أعد تشغيل الجهاز"),
  },

  # Thrown when manager detects a service exited unexpectedly while driving
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

  # Every frame from the camera should be processed by the model. If modeld
  # is not processing frames fast enough they have to be dropped. This alert is
  # thrown when over 20% of frames are dropped.
  EventName.modeldLagging: {
    ET.SOFT_DISABLE: soft_disable_alert("تأخر في نموذج القيادة"),
    ET.NO_ENTRY: NoEntryAlert("تأخر في نموذج القيادة"),
    ET.PERMANENT: modeld_lagging_alert,
  },

  # Besides predicting the path, lane lines and lead car data the model also
  # predicts the current velocity and rotation speed of the car. If the model is
  # very uncertain about the current velocity while the car is moving, this
  # usually means the model has trouble understanding the scene. This is used
  # as a heuristic to warn the driver.
  EventName.posenetInvalid: {
    ET.SOFT_DISABLE: soft_disable_alert("سرعة Posenet غير صالحة"),
    ET.NO_ENTRY: posenet_invalid_alert,
  },

  # When the localizer detects an acceleration of more than 40 m/s^2 (~4G) we
  # alert the driver the device might have fallen from the windshield.
  EventName.deviceFalling: {
    ET.SOFT_DISABLE: soft_disable_alert("سقط الجهاز من الحامل"),
    ET.NO_ENTRY: NoEntryAlert("سقط الجهاز من الحامل"),
  },

  EventName.lowMemory: {
    ET.SOFT_DISABLE: soft_disable_alert("الذاكرة منخفضة: أعد تشغيل الجهاز"),
    ET.PERMANENT: low_memory_alert,
    ET.NO_ENTRY: NoEntryAlert("الذاكرة منخفضة: أعد تشغيل الجهاز"),
  },

  EventName.accFaulted: {
    ET.IMMEDIATE_DISABLE: ImmediateDisableAlert("خطأ مثبّت السرعة: أعد تشغيل السيارة"),
    ET.PERMANENT: NormalPermanentAlert("خطأ مثبّت السرعة: أعد تشغيل السيارة للتفعيل"),
    ET.NO_ENTRY: NoEntryAlert("خطأ مثبّت السرعة: أعد تشغيل السيارة"),
  },

  EventName.espActive: {
    ET.SOFT_DISABLE: soft_disable_alert("نظام الاستقرار الإلكتروني نشط"),
    ET.NO_ENTRY: NoEntryAlert("نظام الاستقرار الإلكتروني نشط"),
  },

  EventName.controlsMismatch: {
    ET.IMMEDIATE_DISABLE: ImmediateDisableAlert("عدم تطابق في التحكم"),
    ET.NO_ENTRY: NoEntryAlert("عدم تطابق في التحكم"),
  },

  # Sometimes the USB stack on the device can get into a bad state
  # causing the connection to the panda to be lost
  EventName.usbError: {
    ET.SOFT_DISABLE: soft_disable_alert("خطأ USB: أعد تشغيل الجهاز"),
    ET.PERMANENT: NormalPermanentAlert("خطأ USB: أعد تشغيل الجهاز"),
    ET.NO_ENTRY: NoEntryAlert("خطأ USB: أعد تشغيل الجهاز"),
  },

  # This alert can be thrown for the following reasons:
  # - No CAN data received at all
  # - CAN data is received, but some message are not received at the right frequency
  # If you're not writing a new car port, this is usually cause by faulty wiring
  EventName.canError: {
    ET.IMMEDIATE_DISABLE: ImmediateDisableAlert("خطأ CAN"),
    ET.PERMANENT: Alert(
      "خطأ CAN: افحص التوصيلات",
      "",
      AlertStatus.normal, AlertSize.small,
      Priority.LOW, VisualAlert.none, AudibleAlert.none, 1., creation_delay=1.),
    ET.NO_ENTRY: NoEntryAlert("خطأ CAN: افحص التوصيلات"),
  },

  EventName.canBusMissing: {
    ET.IMMEDIATE_DISABLE: ImmediateDisableAlert("قناة CAN مقطوعة"),
    ET.PERMANENT: Alert(
      "قناة CAN مقطوعة: احتمال عطل في الكابل",
      "",
      AlertStatus.normal, AlertSize.small,
      Priority.LOW, VisualAlert.none, AudibleAlert.none, 1., creation_delay=1.),
    ET.NO_ENTRY: NoEntryAlert("قناة CAN مقطوعة: افحص التوصيلات"),
  },

  EventName.steerUnavailable: {
    ET.IMMEDIATE_DISABLE: ImmediateDisableAlert("خطأ LKAS: أعد تشغيل السيارة"),
    ET.PERMANENT: NormalPermanentAlert("خطأ LKAS: أعد تشغيل السيارة للتفعيل"),
    ET.NO_ENTRY: NoEntryAlert("خطأ LKAS: أعد تشغيل السيارة"),
  },

  EventName.reverseGear: {
    ET.PERMANENT: Alert(
      "الرجوع\nللخلف",
      "",
      AlertStatus.normal, AlertSize.full,
      Priority.LOWEST, VisualAlert.none, AudibleAlert.none, .2, creation_delay=0.5),
    ET.USER_DISABLE: ImmediateDisableAlert("الرجوع للخلف"),
    ET.NO_ENTRY: NoEntryAlert("الرجوع للخلف"),
  },

  # On cars that use stock ACC the car can decide to cancel ACC for various reasons.
  # When this happens we can no long control the car so the user needs to be warned immediately.
  EventName.cruiseDisabled: {
    ET.IMMEDIATE_DISABLE: ImmediateDisableAlert("مثبّت السرعة معطّل"),
  },

  # When the relay in the harness box opens the CAN bus between the LKAS camera
  # and the rest of the car is separated. When messages from the LKAS camera
  # are received on the car side this usually means the relay hasn't opened correctly
  # and this alert is thrown.
  EventName.relayMalfunction: {
    ET.IMMEDIATE_DISABLE: ImmediateDisableAlert("عطل في مرحّل الحزام"),
    ET.PERMANENT: NormalPermanentAlert("عطل في مرحّل الحزام", "افحص الأجهزة"),
    ET.NO_ENTRY: NoEntryAlert("عطل في مرحّل الحزام"),
  },

  EventName.speedTooLow: {
    ET.IMMEDIATE_DISABLE: Alert(
      "تم إلغاء القائد الآلي",
      "السرعة منخفضة جداً",
      AlertStatus.normal, AlertSize.mid,
      Priority.HIGH, VisualAlert.none, AudibleAlert.disengage, 3.),
  },

  # When the car is driving faster than most cars in the training data, the model outputs can be unpredictable.
  EventName.speedTooHigh: {
    ET.WARNING: Alert(
      "السرعة مرتفعة جداً",
      "النموذج غير متأكد عند هذه السرعة",
      AlertStatus.userPrompt, AlertSize.mid,
      Priority.HIGH, VisualAlert.steerRequired, AudibleAlert.promptRepeat, 4.),
    ET.NO_ENTRY: NoEntryAlert("خفّف السرعة للتفعيل"),
  },

  EventName.vehicleSensorsInvalid: {
    ET.IMMEDIATE_DISABLE: ImmediateDisableAlert("مستشعرات السيارة غير صالحة"),
    ET.PERMANENT: NormalPermanentAlert("جاري معايرة مستشعرات السيارة", "قُد لإجراء المعايرة"),
    ET.NO_ENTRY: NoEntryAlert("جاري معايرة مستشعرات السيارة"),
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
  # print all alerts by type and priority
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
