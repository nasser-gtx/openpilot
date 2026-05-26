import cereal.messaging as messaging
from cereal import log, car, custom
from openpilot.common.constants import CV
from openpilot.sunnypilot.selfdrive.selfdrived.events_base import EventsBase, Priority, ET, Alert, \
  NoEntryAlert, ImmediateDisableAlert, EngagementAlert, NormalPermanentAlert, AlertCallbackType, wrong_car_mode_alert
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit import PCM_LONG_REQUIRED_MAX_SET_SPEED, CONFIRM_SPEED_THRESHOLD

AlertSize = log.SelfdriveState.AlertSize
AlertStatus = log.SelfdriveState.AlertStatus
VisualAlert = car.CarControl.HUDControl.VisualAlert
AudibleAlert = car.CarControl.HUDControl.AudibleAlert
AudibleAlertSP = custom.SelfdriveStateSP.AudibleAlert
EventNameSP = custom.OnroadEventSP.EventName

EVENT_NAME_SP = {v: k for k, v in EventNameSP.schema.enumerants.items()}

def speed_limit_adjust_alert(CP, CS, sm, metric, soft_disable_time, personality):
  speedLimit = sm['longitudinalPlanSP'].speedLimit.resolver.speedLimit
  speed = round(speedLimit * (CV.MS_TO_KPH if metric else CV.MS_TO_MPH))
  message = f'جاري الضبط على حد السرعة {speed} {"كم/س" if metric else "ميل/س"}'
  return Alert(message, "", AlertStatus.normal, AlertSize.small, Priority.LOW, VisualAlert.none, AudibleAlert.none, 4.)

def speed_limit_pre_active_alert(CP, CS, sm, metric, soft_disable_time, personality):
  speed_conv = CV.MS_TO_KPH if metric else CV.MS_TO_MPH
  speed_limit_final_last = sm['longitudinalPlanSP'].speedLimit.resolver.speedLimitFinalLast
  speed_limit_final_last_conv = round(speed_limit_final_last * speed_conv)
  alert_1_str = ""
  alert_2_str = ""
  alert_size = AlertSize.none
  if CP.openpilotLongitudinalControl and CP.pcmCruise:
    cst_low, cst_high = PCM_LONG_REQUIRED_MAX_SET_SPEED[metric]
    pcm_long_required_max = cst_low if speed_limit_final_last_conv < CONFIRM_SPEED_THRESHOLD[metric] else cst_high
    pcm_long_required_max_set_speed_conv = round(pcm_long_required_max * speed_conv)
    speed_unit = "كم/س" if metric else "ميل/س"
    alert_1_str = "مساعد حد السرعة: مطلوب تفعيل"
    alert_2_str = f"غيّر السرعة المضبوطة يدوياً إلى {pcm_long_required_max_set_speed_conv} {speed_unit} للتفعيل"
    alert_size = AlertSize.mid
  return Alert(alert_1_str, alert_2_str, AlertStatus.normal, alert_size, Priority.LOW, VisualAlert.none, AudibleAlertSP.promptSingleLow, .1)

class EventsSP(EventsBase):
  def __init__(self):
    super().__init__()
    self.event_counters = dict.fromkeys(EVENTS_SP.keys(), 0)
  def get_events_mapping(self):
    return EVENTS_SP
  def get_event_name(self, event):
    return EVENT_NAME_SP[event]
  def get_event_msg_type(self):
    return custom.OnroadEventSP.Event

EVENTS_SP = {
  EventNameSP.lkasEnable: {ET.ENABLE: EngagementAlert(AudibleAlert.engage)},
  EventNameSP.lkasDisable: {ET.USER_DISABLE: EngagementAlert(AudibleAlert.disengage)},
  EventNameSP.manualSteeringRequired: {
    ET.USER_DISABLE: Alert("مركزية المسار التلقائية: إيقاف", "مطلوب توجيه يدوي",
      AlertStatus.normal, AlertSize.mid, Priority.LOW, VisualAlert.none, AudibleAlert.disengage, 1.),
  },
  EventNameSP.manualLongitudinalRequired: {
    ET.WARNING: Alert("مثبّت السرعة التكيّفي: إيقاف", "مطلوب تحكم يدوي في السرعة",
      AlertStatus.normal, AlertSize.mid, Priority.LOW, VisualAlert.none, AudibleAlert.none, 1.),
  },
  EventNameSP.silentLkasEnable: {ET.ENABLE: EngagementAlert(AudibleAlert.none)},
  EventNameSP.silentLkasDisable: {ET.USER_DISABLE: EngagementAlert(AudibleAlert.none)},
  EventNameSP.silentBrakeHold: {
    ET.WARNING: EngagementAlert(AudibleAlert.none),
    ET.NO_ENTRY: NoEntryAlert("تثبيت الفرامل نشط"),
  },
  EventNameSP.silentWrongGear: {
    ET.WARNING: Alert("", "", AlertStatus.normal, AlertSize.none, Priority.LOWEST, VisualAlert.none, AudibleAlert.none, 0.),
    ET.NO_ENTRY: Alert("ناقل الحركة ليس في وضع D", "القائد الآلي غير متاح",
      AlertStatus.normal, AlertSize.mid, Priority.LOW, VisualAlert.none, AudibleAlert.none, 0.),
  },
  EventNameSP.silentReverseGear: {
    ET.PERMANENT: Alert("الرجوع\nللخلف", "", AlertStatus.normal, AlertSize.full,
      Priority.LOWEST, VisualAlert.none, AudibleAlert.none, .2, creation_delay=0.5),
    ET.NO_ENTRY: NoEntryAlert("الرجوع للخلف"),
  },
  EventNameSP.silentDoorOpen: {
    ET.WARNING: Alert("", "", AlertStatus.normal, AlertSize.none, Priority.LOWEST, VisualAlert.none, AudibleAlert.none, 0.),
    ET.NO_ENTRY: NoEntryAlert("الباب مفتوح"),
  },
  EventNameSP.silentSeatbeltNotLatched: {
    ET.WARNING: Alert("", "", AlertStatus.normal, AlertSize.none, Priority.LOWEST, VisualAlert.none, AudibleAlert.none, 0.),
    ET.NO_ENTRY: NoEntryAlert("حزام الأمان غير مربوط"),
  },
  EventNameSP.silentParkBrake: {
    ET.WARNING: Alert("", "", AlertStatus.normal, AlertSize.none, Priority.LOWEST, VisualAlert.none, AudibleAlert.none, 0.),
    ET.NO_ENTRY: NoEntryAlert("الفرامل اليدوية مفعّلة"),
  },
  EventNameSP.controlsMismatchLateral: {
    ET.IMMEDIATE_DISABLE: ImmediateDisableAlert("عدم تطابق في التحكم: الجانبي"),
    ET.NO_ENTRY: NoEntryAlert("عدم تطابق في التحكم: الجانبي"),
  },
  EventNameSP.experimentalModeSwitched: {
    ET.WARNING: NormalPermanentAlert("تم تبديل الوضع التجريبي", duration=1.5)
  },
  EventNameSP.wrongCarModeAlertOnly: {ET.WARNING: wrong_car_mode_alert},
  EventNameSP.pedalPressedAlertOnly: {ET.WARNING: NoEntryAlert("الدواسة مضغوطة")},
  EventNameSP.laneTurnLeft: {
    ET.WARNING: Alert("الانعطاف يساراً", "", AlertStatus.normal, AlertSize.small,
      Priority.LOW, VisualAlert.none, AudibleAlert.none, 1.),
  },
  EventNameSP.laneTurnRight: {
    ET.WARNING: Alert("الانعطاف يميناً", "", AlertStatus.normal, AlertSize.small,
      Priority.LOW, VisualAlert.none, AudibleAlert.none, 1.),
  },
  EventNameSP.speedLimitActive: {
    ET.WARNING: Alert("جاري الضبط التلقائي على حد السرعة المحدد", "", AlertStatus.normal, AlertSize.small,
      Priority.LOW, VisualAlert.none, AudibleAlertSP.promptSingleHigh, 5.),
  },
  EventNameSP.speedLimitChanged: {
    ET.WARNING: Alert("تم تغيير السرعة المضبوطة", "", AlertStatus.normal, AlertSize.small,
      Priority.LOW, VisualAlert.none, AudibleAlertSP.promptSingleHigh, 5.),
  },
  EventNameSP.speedLimitPreActive: {ET.WARNING: speed_limit_pre_active_alert},
  EventNameSP.speedLimitPending: {
    ET.WARNING: Alert("جاري الضبط على آخر حد سرعة مسجّل", "", AlertStatus.normal, AlertSize.small,
      Priority.LOW, VisualAlert.none, AudibleAlertSP.promptSingleHigh, 5.),
  },
  EventNameSP.e2eChime: {
    ET.PERMANENT: Alert("", "", AlertStatus.normal, AlertSize.none,
      Priority.MID, VisualAlert.none, AudibleAlert.prompt, 3.),
  },
}
