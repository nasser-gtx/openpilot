#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void car_update_25(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_24(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_30(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_26(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_27(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_29(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_28(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_update_31(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void car_err_fun(double *nom_x, double *delta_x, double *out_9120639740928103485);
void car_inv_err_fun(double *nom_x, double *true_x, double *out_6331732684650301366);
void car_H_mod_fun(double *state, double *out_7283751758290580761);
void car_f_fun(double *state, double dt, double *out_6426753928244033810);
void car_F_fun(double *state, double dt, double *out_3063680048424251368);
void car_h_25(double *state, double *unused, double *out_4880893079725974192);
void car_H_25(double *state, double *unused, double *out_7640011665429479178);
void car_h_24(double *state, double *unused, double *out_3449525235601694104);
void car_H_24(double *state, double *unused, double *out_6060223081313563404);
void car_h_30(double *state, double *unused, double *out_1019209603297472540);
void car_H_30(double *state, double *unused, double *out_5121678706922230551);
void car_h_26(double *state, double *unused, double *out_2397063686351597476);
void car_H_26(double *state, double *unused, double *out_7065229089406016214);
void car_h_27(double *state, double *unused, double *out_5967619728082438519);
void car_H_27(double *state, double *unused, double *out_2898084635738287334);
void car_h_29(double *state, double *unused, double *out_3982463664363373105);
void car_H_29(double *state, double *unused, double *out_4611447362607838367);
void car_h_28(double *state, double *unused, double *out_8861188984071969312);
void car_H_28(double *state, double *unused, double *out_8752897694032182675);
void car_h_31(double *state, double *unused, double *out_7202257015681761563);
void car_H_31(double *state, double *unused, double *out_7609365703552518750);
void car_predict(double *in_x, double *in_P, double *in_Q, double dt);
void car_set_mass(double x);
void car_set_rotational_inertia(double x);
void car_set_center_to_front(double x);
void car_set_center_to_rear(double x);
void car_set_stiffness_front(double x);
void car_set_stiffness_rear(double x);
}