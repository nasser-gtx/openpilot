#include "car.h"

namespace {
#define DIM 9
#define EDIM 9
#define MEDIM 9
typedef void (*Hfun)(double *, double *, double *);

double mass;

void set_mass(double x){ mass = x;}

double rotational_inertia;

void set_rotational_inertia(double x){ rotational_inertia = x;}

double center_to_front;

void set_center_to_front(double x){ center_to_front = x;}

double center_to_rear;

void set_center_to_rear(double x){ center_to_rear = x;}

double stiffness_front;

void set_stiffness_front(double x){ stiffness_front = x;}

double stiffness_rear;

void set_stiffness_rear(double x){ stiffness_rear = x;}
const static double MAHA_THRESH_25 = 3.8414588206941227;
const static double MAHA_THRESH_24 = 5.991464547107981;
const static double MAHA_THRESH_30 = 3.8414588206941227;
const static double MAHA_THRESH_26 = 3.8414588206941227;
const static double MAHA_THRESH_27 = 3.8414588206941227;
const static double MAHA_THRESH_29 = 3.8414588206941227;
const static double MAHA_THRESH_28 = 3.8414588206941227;
const static double MAHA_THRESH_31 = 3.8414588206941227;

/******************************************************************************
 *                      Code generated with SymPy 1.14.0                      *
 *                                                                            *
 *              See http://www.sympy.org/ for more information.               *
 *                                                                            *
 *                         This file is part of 'ekf'                         *
 ******************************************************************************/
void err_fun(double *nom_x, double *delta_x, double *out_9120639740928103485) {
   out_9120639740928103485[0] = delta_x[0] + nom_x[0];
   out_9120639740928103485[1] = delta_x[1] + nom_x[1];
   out_9120639740928103485[2] = delta_x[2] + nom_x[2];
   out_9120639740928103485[3] = delta_x[3] + nom_x[3];
   out_9120639740928103485[4] = delta_x[4] + nom_x[4];
   out_9120639740928103485[5] = delta_x[5] + nom_x[5];
   out_9120639740928103485[6] = delta_x[6] + nom_x[6];
   out_9120639740928103485[7] = delta_x[7] + nom_x[7];
   out_9120639740928103485[8] = delta_x[8] + nom_x[8];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_6331732684650301366) {
   out_6331732684650301366[0] = -nom_x[0] + true_x[0];
   out_6331732684650301366[1] = -nom_x[1] + true_x[1];
   out_6331732684650301366[2] = -nom_x[2] + true_x[2];
   out_6331732684650301366[3] = -nom_x[3] + true_x[3];
   out_6331732684650301366[4] = -nom_x[4] + true_x[4];
   out_6331732684650301366[5] = -nom_x[5] + true_x[5];
   out_6331732684650301366[6] = -nom_x[6] + true_x[6];
   out_6331732684650301366[7] = -nom_x[7] + true_x[7];
   out_6331732684650301366[8] = -nom_x[8] + true_x[8];
}
void H_mod_fun(double *state, double *out_7283751758290580761) {
   out_7283751758290580761[0] = 1.0;
   out_7283751758290580761[1] = 0.0;
   out_7283751758290580761[2] = 0.0;
   out_7283751758290580761[3] = 0.0;
   out_7283751758290580761[4] = 0.0;
   out_7283751758290580761[5] = 0.0;
   out_7283751758290580761[6] = 0.0;
   out_7283751758290580761[7] = 0.0;
   out_7283751758290580761[8] = 0.0;
   out_7283751758290580761[9] = 0.0;
   out_7283751758290580761[10] = 1.0;
   out_7283751758290580761[11] = 0.0;
   out_7283751758290580761[12] = 0.0;
   out_7283751758290580761[13] = 0.0;
   out_7283751758290580761[14] = 0.0;
   out_7283751758290580761[15] = 0.0;
   out_7283751758290580761[16] = 0.0;
   out_7283751758290580761[17] = 0.0;
   out_7283751758290580761[18] = 0.0;
   out_7283751758290580761[19] = 0.0;
   out_7283751758290580761[20] = 1.0;
   out_7283751758290580761[21] = 0.0;
   out_7283751758290580761[22] = 0.0;
   out_7283751758290580761[23] = 0.0;
   out_7283751758290580761[24] = 0.0;
   out_7283751758290580761[25] = 0.0;
   out_7283751758290580761[26] = 0.0;
   out_7283751758290580761[27] = 0.0;
   out_7283751758290580761[28] = 0.0;
   out_7283751758290580761[29] = 0.0;
   out_7283751758290580761[30] = 1.0;
   out_7283751758290580761[31] = 0.0;
   out_7283751758290580761[32] = 0.0;
   out_7283751758290580761[33] = 0.0;
   out_7283751758290580761[34] = 0.0;
   out_7283751758290580761[35] = 0.0;
   out_7283751758290580761[36] = 0.0;
   out_7283751758290580761[37] = 0.0;
   out_7283751758290580761[38] = 0.0;
   out_7283751758290580761[39] = 0.0;
   out_7283751758290580761[40] = 1.0;
   out_7283751758290580761[41] = 0.0;
   out_7283751758290580761[42] = 0.0;
   out_7283751758290580761[43] = 0.0;
   out_7283751758290580761[44] = 0.0;
   out_7283751758290580761[45] = 0.0;
   out_7283751758290580761[46] = 0.0;
   out_7283751758290580761[47] = 0.0;
   out_7283751758290580761[48] = 0.0;
   out_7283751758290580761[49] = 0.0;
   out_7283751758290580761[50] = 1.0;
   out_7283751758290580761[51] = 0.0;
   out_7283751758290580761[52] = 0.0;
   out_7283751758290580761[53] = 0.0;
   out_7283751758290580761[54] = 0.0;
   out_7283751758290580761[55] = 0.0;
   out_7283751758290580761[56] = 0.0;
   out_7283751758290580761[57] = 0.0;
   out_7283751758290580761[58] = 0.0;
   out_7283751758290580761[59] = 0.0;
   out_7283751758290580761[60] = 1.0;
   out_7283751758290580761[61] = 0.0;
   out_7283751758290580761[62] = 0.0;
   out_7283751758290580761[63] = 0.0;
   out_7283751758290580761[64] = 0.0;
   out_7283751758290580761[65] = 0.0;
   out_7283751758290580761[66] = 0.0;
   out_7283751758290580761[67] = 0.0;
   out_7283751758290580761[68] = 0.0;
   out_7283751758290580761[69] = 0.0;
   out_7283751758290580761[70] = 1.0;
   out_7283751758290580761[71] = 0.0;
   out_7283751758290580761[72] = 0.0;
   out_7283751758290580761[73] = 0.0;
   out_7283751758290580761[74] = 0.0;
   out_7283751758290580761[75] = 0.0;
   out_7283751758290580761[76] = 0.0;
   out_7283751758290580761[77] = 0.0;
   out_7283751758290580761[78] = 0.0;
   out_7283751758290580761[79] = 0.0;
   out_7283751758290580761[80] = 1.0;
}
void f_fun(double *state, double dt, double *out_6426753928244033810) {
   out_6426753928244033810[0] = state[0];
   out_6426753928244033810[1] = state[1];
   out_6426753928244033810[2] = state[2];
   out_6426753928244033810[3] = state[3];
   out_6426753928244033810[4] = state[4];
   out_6426753928244033810[5] = dt*((-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]))*state[6] - 9.8100000000000005*state[8] + stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*state[1]) + (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*state[4])) + state[5];
   out_6426753928244033810[6] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*state[4])) + state[6];
   out_6426753928244033810[7] = state[7];
   out_6426753928244033810[8] = state[8];
}
void F_fun(double *state, double dt, double *out_3063680048424251368) {
   out_3063680048424251368[0] = 1;
   out_3063680048424251368[1] = 0;
   out_3063680048424251368[2] = 0;
   out_3063680048424251368[3] = 0;
   out_3063680048424251368[4] = 0;
   out_3063680048424251368[5] = 0;
   out_3063680048424251368[6] = 0;
   out_3063680048424251368[7] = 0;
   out_3063680048424251368[8] = 0;
   out_3063680048424251368[9] = 0;
   out_3063680048424251368[10] = 1;
   out_3063680048424251368[11] = 0;
   out_3063680048424251368[12] = 0;
   out_3063680048424251368[13] = 0;
   out_3063680048424251368[14] = 0;
   out_3063680048424251368[15] = 0;
   out_3063680048424251368[16] = 0;
   out_3063680048424251368[17] = 0;
   out_3063680048424251368[18] = 0;
   out_3063680048424251368[19] = 0;
   out_3063680048424251368[20] = 1;
   out_3063680048424251368[21] = 0;
   out_3063680048424251368[22] = 0;
   out_3063680048424251368[23] = 0;
   out_3063680048424251368[24] = 0;
   out_3063680048424251368[25] = 0;
   out_3063680048424251368[26] = 0;
   out_3063680048424251368[27] = 0;
   out_3063680048424251368[28] = 0;
   out_3063680048424251368[29] = 0;
   out_3063680048424251368[30] = 1;
   out_3063680048424251368[31] = 0;
   out_3063680048424251368[32] = 0;
   out_3063680048424251368[33] = 0;
   out_3063680048424251368[34] = 0;
   out_3063680048424251368[35] = 0;
   out_3063680048424251368[36] = 0;
   out_3063680048424251368[37] = 0;
   out_3063680048424251368[38] = 0;
   out_3063680048424251368[39] = 0;
   out_3063680048424251368[40] = 1;
   out_3063680048424251368[41] = 0;
   out_3063680048424251368[42] = 0;
   out_3063680048424251368[43] = 0;
   out_3063680048424251368[44] = 0;
   out_3063680048424251368[45] = dt*(stiffness_front*(-state[2] - state[3] + state[7])/(mass*state[1]) + (-stiffness_front - stiffness_rear)*state[5]/(mass*state[4]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[6]/(mass*state[4]));
   out_3063680048424251368[46] = -dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(mass*pow(state[1], 2));
   out_3063680048424251368[47] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_3063680048424251368[48] = -dt*stiffness_front*state[0]/(mass*state[1]);
   out_3063680048424251368[49] = dt*((-1 - (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*pow(state[4], 2)))*state[6] - (-stiffness_front*state[0] - stiffness_rear*state[0])*state[5]/(mass*pow(state[4], 2)));
   out_3063680048424251368[50] = dt*(-stiffness_front*state[0] - stiffness_rear*state[0])/(mass*state[4]) + 1;
   out_3063680048424251368[51] = dt*(-state[4] + (-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(mass*state[4]));
   out_3063680048424251368[52] = dt*stiffness_front*state[0]/(mass*state[1]);
   out_3063680048424251368[53] = -9.8100000000000005*dt;
   out_3063680048424251368[54] = dt*(center_to_front*stiffness_front*(-state[2] - state[3] + state[7])/(rotational_inertia*state[1]) + (-center_to_front*stiffness_front + center_to_rear*stiffness_rear)*state[5]/(rotational_inertia*state[4]) + (-pow(center_to_front, 2)*stiffness_front - pow(center_to_rear, 2)*stiffness_rear)*state[6]/(rotational_inertia*state[4]));
   out_3063680048424251368[55] = -center_to_front*dt*stiffness_front*(-state[2] - state[3] + state[7])*state[0]/(rotational_inertia*pow(state[1], 2));
   out_3063680048424251368[56] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_3063680048424251368[57] = -center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_3063680048424251368[58] = dt*(-(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])*state[5]/(rotational_inertia*pow(state[4], 2)) - (-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])*state[6]/(rotational_inertia*pow(state[4], 2)));
   out_3063680048424251368[59] = dt*(-center_to_front*stiffness_front*state[0] + center_to_rear*stiffness_rear*state[0])/(rotational_inertia*state[4]);
   out_3063680048424251368[60] = dt*(-pow(center_to_front, 2)*stiffness_front*state[0] - pow(center_to_rear, 2)*stiffness_rear*state[0])/(rotational_inertia*state[4]) + 1;
   out_3063680048424251368[61] = center_to_front*dt*stiffness_front*state[0]/(rotational_inertia*state[1]);
   out_3063680048424251368[62] = 0;
   out_3063680048424251368[63] = 0;
   out_3063680048424251368[64] = 0;
   out_3063680048424251368[65] = 0;
   out_3063680048424251368[66] = 0;
   out_3063680048424251368[67] = 0;
   out_3063680048424251368[68] = 0;
   out_3063680048424251368[69] = 0;
   out_3063680048424251368[70] = 1;
   out_3063680048424251368[71] = 0;
   out_3063680048424251368[72] = 0;
   out_3063680048424251368[73] = 0;
   out_3063680048424251368[74] = 0;
   out_3063680048424251368[75] = 0;
   out_3063680048424251368[76] = 0;
   out_3063680048424251368[77] = 0;
   out_3063680048424251368[78] = 0;
   out_3063680048424251368[79] = 0;
   out_3063680048424251368[80] = 1;
}
void h_25(double *state, double *unused, double *out_4880893079725974192) {
   out_4880893079725974192[0] = state[6];
}
void H_25(double *state, double *unused, double *out_7640011665429479178) {
   out_7640011665429479178[0] = 0;
   out_7640011665429479178[1] = 0;
   out_7640011665429479178[2] = 0;
   out_7640011665429479178[3] = 0;
   out_7640011665429479178[4] = 0;
   out_7640011665429479178[5] = 0;
   out_7640011665429479178[6] = 1;
   out_7640011665429479178[7] = 0;
   out_7640011665429479178[8] = 0;
}
void h_24(double *state, double *unused, double *out_3449525235601694104) {
   out_3449525235601694104[0] = state[4];
   out_3449525235601694104[1] = state[5];
}
void H_24(double *state, double *unused, double *out_6060223081313563404) {
   out_6060223081313563404[0] = 0;
   out_6060223081313563404[1] = 0;
   out_6060223081313563404[2] = 0;
   out_6060223081313563404[3] = 0;
   out_6060223081313563404[4] = 1;
   out_6060223081313563404[5] = 0;
   out_6060223081313563404[6] = 0;
   out_6060223081313563404[7] = 0;
   out_6060223081313563404[8] = 0;
   out_6060223081313563404[9] = 0;
   out_6060223081313563404[10] = 0;
   out_6060223081313563404[11] = 0;
   out_6060223081313563404[12] = 0;
   out_6060223081313563404[13] = 0;
   out_6060223081313563404[14] = 1;
   out_6060223081313563404[15] = 0;
   out_6060223081313563404[16] = 0;
   out_6060223081313563404[17] = 0;
}
void h_30(double *state, double *unused, double *out_1019209603297472540) {
   out_1019209603297472540[0] = state[4];
}
void H_30(double *state, double *unused, double *out_5121678706922230551) {
   out_5121678706922230551[0] = 0;
   out_5121678706922230551[1] = 0;
   out_5121678706922230551[2] = 0;
   out_5121678706922230551[3] = 0;
   out_5121678706922230551[4] = 1;
   out_5121678706922230551[5] = 0;
   out_5121678706922230551[6] = 0;
   out_5121678706922230551[7] = 0;
   out_5121678706922230551[8] = 0;
}
void h_26(double *state, double *unused, double *out_2397063686351597476) {
   out_2397063686351597476[0] = state[7];
}
void H_26(double *state, double *unused, double *out_7065229089406016214) {
   out_7065229089406016214[0] = 0;
   out_7065229089406016214[1] = 0;
   out_7065229089406016214[2] = 0;
   out_7065229089406016214[3] = 0;
   out_7065229089406016214[4] = 0;
   out_7065229089406016214[5] = 0;
   out_7065229089406016214[6] = 0;
   out_7065229089406016214[7] = 1;
   out_7065229089406016214[8] = 0;
}
void h_27(double *state, double *unused, double *out_5967619728082438519) {
   out_5967619728082438519[0] = state[3];
}
void H_27(double *state, double *unused, double *out_2898084635738287334) {
   out_2898084635738287334[0] = 0;
   out_2898084635738287334[1] = 0;
   out_2898084635738287334[2] = 0;
   out_2898084635738287334[3] = 1;
   out_2898084635738287334[4] = 0;
   out_2898084635738287334[5] = 0;
   out_2898084635738287334[6] = 0;
   out_2898084635738287334[7] = 0;
   out_2898084635738287334[8] = 0;
}
void h_29(double *state, double *unused, double *out_3982463664363373105) {
   out_3982463664363373105[0] = state[1];
}
void H_29(double *state, double *unused, double *out_4611447362607838367) {
   out_4611447362607838367[0] = 0;
   out_4611447362607838367[1] = 1;
   out_4611447362607838367[2] = 0;
   out_4611447362607838367[3] = 0;
   out_4611447362607838367[4] = 0;
   out_4611447362607838367[5] = 0;
   out_4611447362607838367[6] = 0;
   out_4611447362607838367[7] = 0;
   out_4611447362607838367[8] = 0;
}
void h_28(double *state, double *unused, double *out_8861188984071969312) {
   out_8861188984071969312[0] = state[0];
}
void H_28(double *state, double *unused, double *out_8752897694032182675) {
   out_8752897694032182675[0] = 1;
   out_8752897694032182675[1] = 0;
   out_8752897694032182675[2] = 0;
   out_8752897694032182675[3] = 0;
   out_8752897694032182675[4] = 0;
   out_8752897694032182675[5] = 0;
   out_8752897694032182675[6] = 0;
   out_8752897694032182675[7] = 0;
   out_8752897694032182675[8] = 0;
}
void h_31(double *state, double *unused, double *out_7202257015681761563) {
   out_7202257015681761563[0] = state[8];
}
void H_31(double *state, double *unused, double *out_7609365703552518750) {
   out_7609365703552518750[0] = 0;
   out_7609365703552518750[1] = 0;
   out_7609365703552518750[2] = 0;
   out_7609365703552518750[3] = 0;
   out_7609365703552518750[4] = 0;
   out_7609365703552518750[5] = 0;
   out_7609365703552518750[6] = 0;
   out_7609365703552518750[7] = 0;
   out_7609365703552518750[8] = 1;
}
#include <eigen3/Eigen/Dense>
#include <iostream>

typedef Eigen::Matrix<double, DIM, DIM, Eigen::RowMajor> DDM;
typedef Eigen::Matrix<double, EDIM, EDIM, Eigen::RowMajor> EEM;
typedef Eigen::Matrix<double, DIM, EDIM, Eigen::RowMajor> DEM;

void predict(double *in_x, double *in_P, double *in_Q, double dt) {
  typedef Eigen::Matrix<double, MEDIM, MEDIM, Eigen::RowMajor> RRM;

  double nx[DIM] = {0};
  double in_F[EDIM*EDIM] = {0};

  // functions from sympy
  f_fun(in_x, dt, nx);
  F_fun(in_x, dt, in_F);


  EEM F(in_F);
  EEM P(in_P);
  EEM Q(in_Q);

  RRM F_main = F.topLeftCorner(MEDIM, MEDIM);
  P.topLeftCorner(MEDIM, MEDIM) = (F_main * P.topLeftCorner(MEDIM, MEDIM)) * F_main.transpose();
  P.topRightCorner(MEDIM, EDIM - MEDIM) = F_main * P.topRightCorner(MEDIM, EDIM - MEDIM);
  P.bottomLeftCorner(EDIM - MEDIM, MEDIM) = P.bottomLeftCorner(EDIM - MEDIM, MEDIM) * F_main.transpose();

  P = P + dt*Q;

  // copy out state
  memcpy(in_x, nx, DIM * sizeof(double));
  memcpy(in_P, P.data(), EDIM * EDIM * sizeof(double));
}

// note: extra_args dim only correct when null space projecting
// otherwise 1
template <int ZDIM, int EADIM, bool MAHA_TEST>
void update(double *in_x, double *in_P, Hfun h_fun, Hfun H_fun, Hfun Hea_fun, double *in_z, double *in_R, double *in_ea, double MAHA_THRESHOLD) {
  typedef Eigen::Matrix<double, ZDIM, ZDIM, Eigen::RowMajor> ZZM;
  typedef Eigen::Matrix<double, ZDIM, DIM, Eigen::RowMajor> ZDM;
  typedef Eigen::Matrix<double, Eigen::Dynamic, EDIM, Eigen::RowMajor> XEM;
  //typedef Eigen::Matrix<double, EDIM, ZDIM, Eigen::RowMajor> EZM;
  typedef Eigen::Matrix<double, Eigen::Dynamic, 1> X1M;
  typedef Eigen::Matrix<double, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor> XXM;

  double in_hx[ZDIM] = {0};
  double in_H[ZDIM * DIM] = {0};
  double in_H_mod[EDIM * DIM] = {0};
  double delta_x[EDIM] = {0};
  double x_new[DIM] = {0};


  // state x, P
  Eigen::Matrix<double, ZDIM, 1> z(in_z);
  EEM P(in_P);
  ZZM pre_R(in_R);

  // functions from sympy
  h_fun(in_x, in_ea, in_hx);
  H_fun(in_x, in_ea, in_H);
  ZDM pre_H(in_H);

  // get y (y = z - hx)
  Eigen::Matrix<double, ZDIM, 1> pre_y(in_hx); pre_y = z - pre_y;
  X1M y; XXM H; XXM R;
  if (Hea_fun){
    typedef Eigen::Matrix<double, ZDIM, EADIM, Eigen::RowMajor> ZAM;
    double in_Hea[ZDIM * EADIM] = {0};
    Hea_fun(in_x, in_ea, in_Hea);
    ZAM Hea(in_Hea);
    XXM A = Hea.transpose().fullPivLu().kernel();


    y = A.transpose() * pre_y;
    H = A.transpose() * pre_H;
    R = A.transpose() * pre_R * A;
  } else {
    y = pre_y;
    H = pre_H;
    R = pre_R;
  }
  // get modified H
  H_mod_fun(in_x, in_H_mod);
  DEM H_mod(in_H_mod);
  XEM H_err = H * H_mod;

  // Do mahalobis distance test
  if (MAHA_TEST){
    XXM a = (H_err * P * H_err.transpose() + R).inverse();
    double maha_dist = y.transpose() * a * y;
    if (maha_dist > MAHA_THRESHOLD){
      R = 1.0e16 * R;
    }
  }

  // Outlier resilient weighting
  double weight = 1;//(1.5)/(1 + y.squaredNorm()/R.sum());

  // kalman gains and I_KH
  XXM S = ((H_err * P) * H_err.transpose()) + R/weight;
  XEM KT = S.fullPivLu().solve(H_err * P.transpose());
  //EZM K = KT.transpose(); TODO: WHY DOES THIS NOT COMPILE?
  //EZM K = S.fullPivLu().solve(H_err * P.transpose()).transpose();
  //std::cout << "Here is the matrix rot:\n" << K << std::endl;
  EEM I_KH = Eigen::Matrix<double, EDIM, EDIM>::Identity() - (KT.transpose() * H_err);

  // update state by injecting dx
  Eigen::Matrix<double, EDIM, 1> dx(delta_x);
  dx  = (KT.transpose() * y);
  memcpy(delta_x, dx.data(), EDIM * sizeof(double));
  err_fun(in_x, delta_x, x_new);
  Eigen::Matrix<double, DIM, 1> x(x_new);

  // update cov
  P = ((I_KH * P) * I_KH.transpose()) + ((KT.transpose() * R) * KT);

  // copy out state
  memcpy(in_x, x.data(), DIM * sizeof(double));
  memcpy(in_P, P.data(), EDIM * EDIM * sizeof(double));
  memcpy(in_z, y.data(), y.rows() * sizeof(double));
}




}
extern "C" {

void car_update_25(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<1, 3, 0>(in_x, in_P, h_25, H_25, NULL, in_z, in_R, in_ea, MAHA_THRESH_25);
}
void car_update_24(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<2, 3, 0>(in_x, in_P, h_24, H_24, NULL, in_z, in_R, in_ea, MAHA_THRESH_24);
}
void car_update_30(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<1, 3, 0>(in_x, in_P, h_30, H_30, NULL, in_z, in_R, in_ea, MAHA_THRESH_30);
}
void car_update_26(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<1, 3, 0>(in_x, in_P, h_26, H_26, NULL, in_z, in_R, in_ea, MAHA_THRESH_26);
}
void car_update_27(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<1, 3, 0>(in_x, in_P, h_27, H_27, NULL, in_z, in_R, in_ea, MAHA_THRESH_27);
}
void car_update_29(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<1, 3, 0>(in_x, in_P, h_29, H_29, NULL, in_z, in_R, in_ea, MAHA_THRESH_29);
}
void car_update_28(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<1, 3, 0>(in_x, in_P, h_28, H_28, NULL, in_z, in_R, in_ea, MAHA_THRESH_28);
}
void car_update_31(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<1, 3, 0>(in_x, in_P, h_31, H_31, NULL, in_z, in_R, in_ea, MAHA_THRESH_31);
}
void car_err_fun(double *nom_x, double *delta_x, double *out_9120639740928103485) {
  err_fun(nom_x, delta_x, out_9120639740928103485);
}
void car_inv_err_fun(double *nom_x, double *true_x, double *out_6331732684650301366) {
  inv_err_fun(nom_x, true_x, out_6331732684650301366);
}
void car_H_mod_fun(double *state, double *out_7283751758290580761) {
  H_mod_fun(state, out_7283751758290580761);
}
void car_f_fun(double *state, double dt, double *out_6426753928244033810) {
  f_fun(state,  dt, out_6426753928244033810);
}
void car_F_fun(double *state, double dt, double *out_3063680048424251368) {
  F_fun(state,  dt, out_3063680048424251368);
}
void car_h_25(double *state, double *unused, double *out_4880893079725974192) {
  h_25(state, unused, out_4880893079725974192);
}
void car_H_25(double *state, double *unused, double *out_7640011665429479178) {
  H_25(state, unused, out_7640011665429479178);
}
void car_h_24(double *state, double *unused, double *out_3449525235601694104) {
  h_24(state, unused, out_3449525235601694104);
}
void car_H_24(double *state, double *unused, double *out_6060223081313563404) {
  H_24(state, unused, out_6060223081313563404);
}
void car_h_30(double *state, double *unused, double *out_1019209603297472540) {
  h_30(state, unused, out_1019209603297472540);
}
void car_H_30(double *state, double *unused, double *out_5121678706922230551) {
  H_30(state, unused, out_5121678706922230551);
}
void car_h_26(double *state, double *unused, double *out_2397063686351597476) {
  h_26(state, unused, out_2397063686351597476);
}
void car_H_26(double *state, double *unused, double *out_7065229089406016214) {
  H_26(state, unused, out_7065229089406016214);
}
void car_h_27(double *state, double *unused, double *out_5967619728082438519) {
  h_27(state, unused, out_5967619728082438519);
}
void car_H_27(double *state, double *unused, double *out_2898084635738287334) {
  H_27(state, unused, out_2898084635738287334);
}
void car_h_29(double *state, double *unused, double *out_3982463664363373105) {
  h_29(state, unused, out_3982463664363373105);
}
void car_H_29(double *state, double *unused, double *out_4611447362607838367) {
  H_29(state, unused, out_4611447362607838367);
}
void car_h_28(double *state, double *unused, double *out_8861188984071969312) {
  h_28(state, unused, out_8861188984071969312);
}
void car_H_28(double *state, double *unused, double *out_8752897694032182675) {
  H_28(state, unused, out_8752897694032182675);
}
void car_h_31(double *state, double *unused, double *out_7202257015681761563) {
  h_31(state, unused, out_7202257015681761563);
}
void car_H_31(double *state, double *unused, double *out_7609365703552518750) {
  H_31(state, unused, out_7609365703552518750);
}
void car_predict(double *in_x, double *in_P, double *in_Q, double dt) {
  predict(in_x, in_P, in_Q, dt);
}
void car_set_mass(double x) {
  set_mass(x);
}
void car_set_rotational_inertia(double x) {
  set_rotational_inertia(x);
}
void car_set_center_to_front(double x) {
  set_center_to_front(x);
}
void car_set_center_to_rear(double x) {
  set_center_to_rear(x);
}
void car_set_stiffness_front(double x) {
  set_stiffness_front(x);
}
void car_set_stiffness_rear(double x) {
  set_stiffness_rear(x);
}
}

const EKF car = {
  .name = "car",
  .kinds = { 25, 24, 30, 26, 27, 29, 28, 31 },
  .feature_kinds = {  },
  .f_fun = car_f_fun,
  .F_fun = car_F_fun,
  .err_fun = car_err_fun,
  .inv_err_fun = car_inv_err_fun,
  .H_mod_fun = car_H_mod_fun,
  .predict = car_predict,
  .hs = {
    { 25, car_h_25 },
    { 24, car_h_24 },
    { 30, car_h_30 },
    { 26, car_h_26 },
    { 27, car_h_27 },
    { 29, car_h_29 },
    { 28, car_h_28 },
    { 31, car_h_31 },
  },
  .Hs = {
    { 25, car_H_25 },
    { 24, car_H_24 },
    { 30, car_H_30 },
    { 26, car_H_26 },
    { 27, car_H_27 },
    { 29, car_H_29 },
    { 28, car_H_28 },
    { 31, car_H_31 },
  },
  .updates = {
    { 25, car_update_25 },
    { 24, car_update_24 },
    { 30, car_update_30 },
    { 26, car_update_26 },
    { 27, car_update_27 },
    { 29, car_update_29 },
    { 28, car_update_28 },
    { 31, car_update_31 },
  },
  .Hes = {
  },
  .sets = {
    { "mass", car_set_mass },
    { "rotational_inertia", car_set_rotational_inertia },
    { "center_to_front", car_set_center_to_front },
    { "center_to_rear", car_set_center_to_rear },
    { "stiffness_front", car_set_stiffness_front },
    { "stiffness_rear", car_set_stiffness_rear },
  },
  .extra_routines = {
  },
};

ekf_lib_init(car)
