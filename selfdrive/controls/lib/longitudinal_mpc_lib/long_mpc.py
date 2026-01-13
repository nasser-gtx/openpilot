#!/usr/bin/env python3
import os
import time
import numpy as np
from cereal import log
from opendbc.car.interfaces import ACCEL_MIN, ACCEL_MAX
from openpilot.common.realtime import DT_MDL
from openpilot.common.swaglog import cloudlog
from openpilot.selfdrive.modeld.constants import index_function
from openpilot.selfdrive.controls.radard import _LEAD_ACCEL_TAU

if __name__ == '__main__':
  from openpilot.third_party.acados.acados_template import AcadosModel, AcadosOcp, AcadosOcpSolver
else:
  from openpilot.selfdrive.controls.lib.longitudinal_mpc_lib.c_generated_code.acados_ocp_solver_pyx import AcadosOcpSolverCython

from casadi import SX, vertcat

# =============================================================================
# Constants
# =============================================================================

MODEL_NAME = 'long'
LONG_MPC_DIR = os.path.dirname(os.path.abspath(__file__))
EXPORT_DIR = os.path.join(LONG_MPC_DIR, "c_generated_code")
JSON_FILE = os.path.join(LONG_MPC_DIR, "acados_ocp_long.json")

SOURCES = ['lead0', 'lead1', 'cruise', 'e2e']

X_DIM = 3
U_DIM = 1
PARAM_DIM = 6
COST_E_DIM = 5
COST_DIM = COST_E_DIM + 1
CONSTR_DIM = 4

X_EGO_OBSTACLE_COST = 3.
X_EGO_COST = 0.
V_EGO_COST = 0.
A_EGO_COST = 0.
J_EGO_COST = 5.0
A_CHANGE_COST = 200.
DANGER_ZONE_COST = 100.
CRASH_DISTANCE = .25
LEAD_DANGER_FACTOR = 0.75
LIMIT_COST = 1e6
ACADOS_SOLVER_TYPE = 'SQP_RTI'

N = 12
MAX_T = 10.0
T_IDXS = np.array([index_function(i, max_val=MAX_T, max_idx=N) for i in range(N+1)])
FCW_IDXS = T_IDXS < 5.0
T_DIFFS = np.diff(T_IDXS, prepend=[0.])

COMFORT_BRAKE = 2.5
STOP_DISTANCE = 4.2
CRUISE_MIN_ACCEL = -1.2
CRUISE_MAX_ACCEL = 3.0

# =============================================================================
# Following logic (MODIFIED)
# =============================================================================

def get_jerk_factor(personality):
  if personality == log.LongitudinalPersonality.relaxed:
    return 1.0
  elif personality == log.LongitudinalPersonality.standard:
    return 1.0
  else:
    return 0.5


def get_T_FOLLOW(personality, v_ego):
  if personality == log.LongitudinalPersonality.relaxed:
    t_min, t_max = 1.3, 2.0
  elif personality == log.LongitudinalPersonality.standard:
    t_min, t_max = 1.1, 1.8
  else:
    t_min, t_max = 0.9, 1.5

  return float(np.clip(
    np.interp(v_ego, [11.1, 27.8], [t_min, t_max]),
    t_min, t_max
  ))


def get_stopped_equivalence_factor(v_lead):
  return (v_lead ** 2) / (2 * COMFORT_BRAKE)


def get_safe_obstacle_distance(v_ego, t_follow):
  return (v_ego ** 2) / (2 * COMFORT_BRAKE) + t_follow * v_ego + STOP_DISTANCE


# =============================================================================
# ACADOS model (UNCHANGED)
# =============================================================================

def gen_long_model():
  model = AcadosModel()
  model.name = MODEL_NAME

  x_ego = SX.sym('x_ego')
  v_ego = SX.sym('v_ego')
  a_ego = SX.sym('a_ego')
  model.x = vertcat(x_ego, v_ego, a_ego)

  j_ego = SX.sym('j_ego')
  model.u = vertcat(j_ego)

  xdot = vertcat(v_ego, a_ego, j_ego)
  model.xdot = SX.sym('xdot', 3)
  model.f_expl_expr = xdot
  model.f_impl_expr = model.xdot - xdot

  a_min = SX.sym('a_min')
  a_max = SX.sym('a_max')
  x_obstacle = SX.sym('x_obstacle')
  prev_a = SX.sym('prev_a')
  lead_t_follow = SX.sym('lead_t_follow')
  lead_danger_factor = SX.sym('lead_danger_factor')
  model.p = vertcat(a_min, a_max, x_obstacle, prev_a, lead_t_follow, lead_danger_factor)

  return model


# =============================================================================
# ACADOS OCP (UNCHANGED)
# =============================================================================

def gen_long_ocp():
  ocp = AcadosOcp()
  ocp.model = gen_long_model()
  ocp.dims.N = N
  ocp.cost.cost_type = 'NONLINEAR_LS'
  ocp.cost.cost_type_e = 'NONLINEAR_LS'

  ocp.cost.W = np.zeros((COST_DIM, COST_DIM))
  ocp.cost.W_e = np.zeros((COST_E_DIM, COST_E_DIM))

  x_ego, v_ego, a_ego = ocp.model.x
  j_ego = ocp.model.u[0]
  a_min, a_max, x_obs, prev_a, t_follow, danger = ocp.model.p

  desired_dist = get_safe_obstacle_distance(v_ego, t_follow)

  costs = [
    ((x_obs - x_ego) - desired_dist) / (v_ego + 10.),
    x_ego,
    v_ego,
    a_ego,
    a_ego - prev_a,
    j_ego
  ]

  ocp.model.cost_y_expr = vertcat(*costs)
  ocp.model.cost_y_expr_e = vertcat(*costs[:-1])

  ocp.model.con_h_expr = vertcat(
    v_ego,
    a_ego - a_min,
    a_max - a_ego,
    ((x_obs - x_ego) - danger * desired_dist) / (v_ego + 10.)
  )

  ocp.constraints.lh = np.zeros(CONSTR_DIM)
  ocp.constraints.uh = 1e4 * np.ones(CONSTR_DIM)
  ocp.constraints.idxsh = np.arange(CONSTR_DIM)

  ocp.solver_options.tf = T_IDXS[-1]
  ocp.solver_options.shooting_nodes = T_IDXS
  ocp.solver_options.nlp_solver_type = ACADOS_SOLVER_TYPE
  ocp.solver_options.qp_solver = 'PARTIAL_CONDENSING_HPIPM'
  ocp.solver_options.hessian_approx = 'GAUSS_NEWTON'
  ocp.solver_options.integrator_type = 'ERK'

  ocp.code_export_directory = EXPORT_DIR
  return ocp


# =============================================================================
# Longitudinal MPC (MODIFIED BEHAVIOR)
# =============================================================================

class LongitudinalMpc:
  def __init__(self, mode='acc', dt=DT_MDL):
    self.mode = mode
    self.dt = dt
    self.solver = AcadosOcpSolverCython(MODEL_NAME, ACADOS_SOLVER_TYPE, N)
    self.reset()
    self.source = SOURCES[2]
    self.hard_brake_timer = 0.0

  def reset(self):
    self.solver.reset()
    self.x0 = np.zeros(X_DIM)
    self.params = np.zeros((N+1, PARAM_DIM))
    self.prev_a = np.zeros(N+1)
    self.x_sol = np.zeros((N+1, X_DIM))
    self.u_sol = np.zeros((N, 1))

  def set_weights(self, personality):
    v_ego = self.x0[1]
    jerk_factor = get_jerk_factor(personality)

    response = np.interp(v_ego, [0., 11.1, 27.8], [0.4, 0.7, 1.0])
    danger_cost = np.interp(v_ego, [0., 11.1, 27.8], [20., 60., DANGER_ZONE_COST])

    W = np.diag([
      X_EGO_OBSTACLE_COST,
      X_EGO_COST,
      V_EGO_COST,
      A_EGO_COST,
      response * jerk_factor * A_CHANGE_COST,
      response * jerk_factor * J_EGO_COST
    ])

    for i in range(N):
      self.solver.cost_set(i, 'W', W)
      self.solver.cost_set(i, 'Zl', [LIMIT_COST]*3 + [danger_cost])

    self.solver.cost_set(N, 'W', W[:COST_E_DIM, :COST_E_DIM])

  def process_lead(self, lead):
    v_ego = self.x0[1]
    if lead and lead.status:
      x, v, a, tau = lead.dRel, lead.vLead, lead.aLeadK, lead.aLeadTau
    else:
      x, v, a, tau = 50., v_ego + 10., 0., _LEAD_ACCEL_TAU

    a_traj = a * np.exp(-tau * (T_IDXS ** 2) / 2.)
    v_traj = np.clip(v + np.cumsum(T_DIFFS * a_traj), 0., 1e8)
    x_traj = x + np.cumsum(T_DIFFS * v_traj)
    return np.column_stack((x_traj, v_traj))

  def update(self, radarstate, v_cruise, x, v, a, j, personality):
    v_ego = self.x0[1]
    lead = radarstate.leadOne

    hard_brake = lead.status and lead.aLeadK < -2.5 and lead.vLead < v_ego + 1.0
    self.hard_brake_timer = 0.5 if hard_brake else max(self.hard_brake_timer - self.dt, 0.)
    panic = self.hard_brake_timer > 0.

    t_follow = get_T_FOLLOW(personality, v_ego)
    if panic:
      t_follow *= 1.3

    lead_xv = self.process_lead(lead)
    obstacle = lead_xv[:,0] + get_stopped_equivalence_factor(lead_xv[:,1])

    self.params[:,0] = ACCEL_MIN
    self.params[:,1] = -0.5 if panic else ACCEL_MAX
    self.params[:,2] = obstacle
    self.params[:,3] = self.prev_a
    self.params[:,4] = t_follow
    self.params[:,5] = np.interp(-lead.aLeadK, [2.5, 5.0], [1.2, 1.6]) if panic else LEAD_DANGER_FACTOR

    self.set_weights(personality)
    self.run()

  def run(self):
    for i in range(N+1):
      self.solver.set(i, 'p', self.params[i])

    self.solver.constraints_set(0, 'lbx', self.x0)
    self.solver.constraints_set(0, 'ubx', self.x0)

    if self.solver.solve() != 0:
      cloudlog.warning("Long MPC reset")
      self.reset()
      return

    for i in range(N+1):
      self.x_sol[i] = self.solver.get(i, 'x')
    for i in range(N):
      self.u_sol[i] = self.solver.get(i, 'u')

    self.prev_a = np.interp(T_IDXS + self.dt, T_IDXS, self.x_sol[:,2])


# =============================================================================
# Codegen
# =============================================================================

if __name__ == "__main__":
  ocp = gen_long_ocp()
  AcadosOcpSolver.generate(ocp, json_file=JSON_FILE)
