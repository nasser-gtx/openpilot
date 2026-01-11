#pragma once
#include "rednose/helpers/ekf.h"
extern "C" {
void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea);
void pose_err_fun(double *nom_x, double *delta_x, double *out_7405193010915679121);
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_5475328358876229061);
void pose_H_mod_fun(double *state, double *out_6838220648110086595);
void pose_f_fun(double *state, double dt, double *out_358648402757037661);
void pose_F_fun(double *state, double dt, double *out_4283680186500160360);
void pose_h_4(double *state, double *unused, double *out_5132188379361733090);
void pose_H_4(double *state, double *unused, double *out_8036168129992984699);
void pose_h_10(double *state, double *unused, double *out_1317789669870360968);
void pose_H_10(double *state, double *unused, double *out_6822252596821216619);
void pose_h_13(double *state, double *unused, double *out_103193819568861600);
void pose_H_13(double *state, double *unused, double *out_7198302118384234116);
void pose_h_14(double *state, double *unused, double *out_5774019743431067995);
void pose_H_14(double *state, double *unused, double *out_4953379697697612403);
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt);
}