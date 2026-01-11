#include "pose.h"

namespace {
#define DIM 18
#define EDIM 18
#define MEDIM 18
typedef void (*Hfun)(double *, double *, double *);
const static double MAHA_THRESH_4 = 7.814727903251177;
const static double MAHA_THRESH_10 = 7.814727903251177;
const static double MAHA_THRESH_13 = 7.814727903251177;
const static double MAHA_THRESH_14 = 7.814727903251177;

/******************************************************************************
 *                      Code generated with SymPy 1.14.0                      *
 *                                                                            *
 *              See http://www.sympy.org/ for more information.               *
 *                                                                            *
 *                         This file is part of 'ekf'                         *
 ******************************************************************************/
void err_fun(double *nom_x, double *delta_x, double *out_7405193010915679121) {
   out_7405193010915679121[0] = delta_x[0] + nom_x[0];
   out_7405193010915679121[1] = delta_x[1] + nom_x[1];
   out_7405193010915679121[2] = delta_x[2] + nom_x[2];
   out_7405193010915679121[3] = delta_x[3] + nom_x[3];
   out_7405193010915679121[4] = delta_x[4] + nom_x[4];
   out_7405193010915679121[5] = delta_x[5] + nom_x[5];
   out_7405193010915679121[6] = delta_x[6] + nom_x[6];
   out_7405193010915679121[7] = delta_x[7] + nom_x[7];
   out_7405193010915679121[8] = delta_x[8] + nom_x[8];
   out_7405193010915679121[9] = delta_x[9] + nom_x[9];
   out_7405193010915679121[10] = delta_x[10] + nom_x[10];
   out_7405193010915679121[11] = delta_x[11] + nom_x[11];
   out_7405193010915679121[12] = delta_x[12] + nom_x[12];
   out_7405193010915679121[13] = delta_x[13] + nom_x[13];
   out_7405193010915679121[14] = delta_x[14] + nom_x[14];
   out_7405193010915679121[15] = delta_x[15] + nom_x[15];
   out_7405193010915679121[16] = delta_x[16] + nom_x[16];
   out_7405193010915679121[17] = delta_x[17] + nom_x[17];
}
void inv_err_fun(double *nom_x, double *true_x, double *out_5475328358876229061) {
   out_5475328358876229061[0] = -nom_x[0] + true_x[0];
   out_5475328358876229061[1] = -nom_x[1] + true_x[1];
   out_5475328358876229061[2] = -nom_x[2] + true_x[2];
   out_5475328358876229061[3] = -nom_x[3] + true_x[3];
   out_5475328358876229061[4] = -nom_x[4] + true_x[4];
   out_5475328358876229061[5] = -nom_x[5] + true_x[5];
   out_5475328358876229061[6] = -nom_x[6] + true_x[6];
   out_5475328358876229061[7] = -nom_x[7] + true_x[7];
   out_5475328358876229061[8] = -nom_x[8] + true_x[8];
   out_5475328358876229061[9] = -nom_x[9] + true_x[9];
   out_5475328358876229061[10] = -nom_x[10] + true_x[10];
   out_5475328358876229061[11] = -nom_x[11] + true_x[11];
   out_5475328358876229061[12] = -nom_x[12] + true_x[12];
   out_5475328358876229061[13] = -nom_x[13] + true_x[13];
   out_5475328358876229061[14] = -nom_x[14] + true_x[14];
   out_5475328358876229061[15] = -nom_x[15] + true_x[15];
   out_5475328358876229061[16] = -nom_x[16] + true_x[16];
   out_5475328358876229061[17] = -nom_x[17] + true_x[17];
}
void H_mod_fun(double *state, double *out_6838220648110086595) {
   out_6838220648110086595[0] = 1.0;
   out_6838220648110086595[1] = 0.0;
   out_6838220648110086595[2] = 0.0;
   out_6838220648110086595[3] = 0.0;
   out_6838220648110086595[4] = 0.0;
   out_6838220648110086595[5] = 0.0;
   out_6838220648110086595[6] = 0.0;
   out_6838220648110086595[7] = 0.0;
   out_6838220648110086595[8] = 0.0;
   out_6838220648110086595[9] = 0.0;
   out_6838220648110086595[10] = 0.0;
   out_6838220648110086595[11] = 0.0;
   out_6838220648110086595[12] = 0.0;
   out_6838220648110086595[13] = 0.0;
   out_6838220648110086595[14] = 0.0;
   out_6838220648110086595[15] = 0.0;
   out_6838220648110086595[16] = 0.0;
   out_6838220648110086595[17] = 0.0;
   out_6838220648110086595[18] = 0.0;
   out_6838220648110086595[19] = 1.0;
   out_6838220648110086595[20] = 0.0;
   out_6838220648110086595[21] = 0.0;
   out_6838220648110086595[22] = 0.0;
   out_6838220648110086595[23] = 0.0;
   out_6838220648110086595[24] = 0.0;
   out_6838220648110086595[25] = 0.0;
   out_6838220648110086595[26] = 0.0;
   out_6838220648110086595[27] = 0.0;
   out_6838220648110086595[28] = 0.0;
   out_6838220648110086595[29] = 0.0;
   out_6838220648110086595[30] = 0.0;
   out_6838220648110086595[31] = 0.0;
   out_6838220648110086595[32] = 0.0;
   out_6838220648110086595[33] = 0.0;
   out_6838220648110086595[34] = 0.0;
   out_6838220648110086595[35] = 0.0;
   out_6838220648110086595[36] = 0.0;
   out_6838220648110086595[37] = 0.0;
   out_6838220648110086595[38] = 1.0;
   out_6838220648110086595[39] = 0.0;
   out_6838220648110086595[40] = 0.0;
   out_6838220648110086595[41] = 0.0;
   out_6838220648110086595[42] = 0.0;
   out_6838220648110086595[43] = 0.0;
   out_6838220648110086595[44] = 0.0;
   out_6838220648110086595[45] = 0.0;
   out_6838220648110086595[46] = 0.0;
   out_6838220648110086595[47] = 0.0;
   out_6838220648110086595[48] = 0.0;
   out_6838220648110086595[49] = 0.0;
   out_6838220648110086595[50] = 0.0;
   out_6838220648110086595[51] = 0.0;
   out_6838220648110086595[52] = 0.0;
   out_6838220648110086595[53] = 0.0;
   out_6838220648110086595[54] = 0.0;
   out_6838220648110086595[55] = 0.0;
   out_6838220648110086595[56] = 0.0;
   out_6838220648110086595[57] = 1.0;
   out_6838220648110086595[58] = 0.0;
   out_6838220648110086595[59] = 0.0;
   out_6838220648110086595[60] = 0.0;
   out_6838220648110086595[61] = 0.0;
   out_6838220648110086595[62] = 0.0;
   out_6838220648110086595[63] = 0.0;
   out_6838220648110086595[64] = 0.0;
   out_6838220648110086595[65] = 0.0;
   out_6838220648110086595[66] = 0.0;
   out_6838220648110086595[67] = 0.0;
   out_6838220648110086595[68] = 0.0;
   out_6838220648110086595[69] = 0.0;
   out_6838220648110086595[70] = 0.0;
   out_6838220648110086595[71] = 0.0;
   out_6838220648110086595[72] = 0.0;
   out_6838220648110086595[73] = 0.0;
   out_6838220648110086595[74] = 0.0;
   out_6838220648110086595[75] = 0.0;
   out_6838220648110086595[76] = 1.0;
   out_6838220648110086595[77] = 0.0;
   out_6838220648110086595[78] = 0.0;
   out_6838220648110086595[79] = 0.0;
   out_6838220648110086595[80] = 0.0;
   out_6838220648110086595[81] = 0.0;
   out_6838220648110086595[82] = 0.0;
   out_6838220648110086595[83] = 0.0;
   out_6838220648110086595[84] = 0.0;
   out_6838220648110086595[85] = 0.0;
   out_6838220648110086595[86] = 0.0;
   out_6838220648110086595[87] = 0.0;
   out_6838220648110086595[88] = 0.0;
   out_6838220648110086595[89] = 0.0;
   out_6838220648110086595[90] = 0.0;
   out_6838220648110086595[91] = 0.0;
   out_6838220648110086595[92] = 0.0;
   out_6838220648110086595[93] = 0.0;
   out_6838220648110086595[94] = 0.0;
   out_6838220648110086595[95] = 1.0;
   out_6838220648110086595[96] = 0.0;
   out_6838220648110086595[97] = 0.0;
   out_6838220648110086595[98] = 0.0;
   out_6838220648110086595[99] = 0.0;
   out_6838220648110086595[100] = 0.0;
   out_6838220648110086595[101] = 0.0;
   out_6838220648110086595[102] = 0.0;
   out_6838220648110086595[103] = 0.0;
   out_6838220648110086595[104] = 0.0;
   out_6838220648110086595[105] = 0.0;
   out_6838220648110086595[106] = 0.0;
   out_6838220648110086595[107] = 0.0;
   out_6838220648110086595[108] = 0.0;
   out_6838220648110086595[109] = 0.0;
   out_6838220648110086595[110] = 0.0;
   out_6838220648110086595[111] = 0.0;
   out_6838220648110086595[112] = 0.0;
   out_6838220648110086595[113] = 0.0;
   out_6838220648110086595[114] = 1.0;
   out_6838220648110086595[115] = 0.0;
   out_6838220648110086595[116] = 0.0;
   out_6838220648110086595[117] = 0.0;
   out_6838220648110086595[118] = 0.0;
   out_6838220648110086595[119] = 0.0;
   out_6838220648110086595[120] = 0.0;
   out_6838220648110086595[121] = 0.0;
   out_6838220648110086595[122] = 0.0;
   out_6838220648110086595[123] = 0.0;
   out_6838220648110086595[124] = 0.0;
   out_6838220648110086595[125] = 0.0;
   out_6838220648110086595[126] = 0.0;
   out_6838220648110086595[127] = 0.0;
   out_6838220648110086595[128] = 0.0;
   out_6838220648110086595[129] = 0.0;
   out_6838220648110086595[130] = 0.0;
   out_6838220648110086595[131] = 0.0;
   out_6838220648110086595[132] = 0.0;
   out_6838220648110086595[133] = 1.0;
   out_6838220648110086595[134] = 0.0;
   out_6838220648110086595[135] = 0.0;
   out_6838220648110086595[136] = 0.0;
   out_6838220648110086595[137] = 0.0;
   out_6838220648110086595[138] = 0.0;
   out_6838220648110086595[139] = 0.0;
   out_6838220648110086595[140] = 0.0;
   out_6838220648110086595[141] = 0.0;
   out_6838220648110086595[142] = 0.0;
   out_6838220648110086595[143] = 0.0;
   out_6838220648110086595[144] = 0.0;
   out_6838220648110086595[145] = 0.0;
   out_6838220648110086595[146] = 0.0;
   out_6838220648110086595[147] = 0.0;
   out_6838220648110086595[148] = 0.0;
   out_6838220648110086595[149] = 0.0;
   out_6838220648110086595[150] = 0.0;
   out_6838220648110086595[151] = 0.0;
   out_6838220648110086595[152] = 1.0;
   out_6838220648110086595[153] = 0.0;
   out_6838220648110086595[154] = 0.0;
   out_6838220648110086595[155] = 0.0;
   out_6838220648110086595[156] = 0.0;
   out_6838220648110086595[157] = 0.0;
   out_6838220648110086595[158] = 0.0;
   out_6838220648110086595[159] = 0.0;
   out_6838220648110086595[160] = 0.0;
   out_6838220648110086595[161] = 0.0;
   out_6838220648110086595[162] = 0.0;
   out_6838220648110086595[163] = 0.0;
   out_6838220648110086595[164] = 0.0;
   out_6838220648110086595[165] = 0.0;
   out_6838220648110086595[166] = 0.0;
   out_6838220648110086595[167] = 0.0;
   out_6838220648110086595[168] = 0.0;
   out_6838220648110086595[169] = 0.0;
   out_6838220648110086595[170] = 0.0;
   out_6838220648110086595[171] = 1.0;
   out_6838220648110086595[172] = 0.0;
   out_6838220648110086595[173] = 0.0;
   out_6838220648110086595[174] = 0.0;
   out_6838220648110086595[175] = 0.0;
   out_6838220648110086595[176] = 0.0;
   out_6838220648110086595[177] = 0.0;
   out_6838220648110086595[178] = 0.0;
   out_6838220648110086595[179] = 0.0;
   out_6838220648110086595[180] = 0.0;
   out_6838220648110086595[181] = 0.0;
   out_6838220648110086595[182] = 0.0;
   out_6838220648110086595[183] = 0.0;
   out_6838220648110086595[184] = 0.0;
   out_6838220648110086595[185] = 0.0;
   out_6838220648110086595[186] = 0.0;
   out_6838220648110086595[187] = 0.0;
   out_6838220648110086595[188] = 0.0;
   out_6838220648110086595[189] = 0.0;
   out_6838220648110086595[190] = 1.0;
   out_6838220648110086595[191] = 0.0;
   out_6838220648110086595[192] = 0.0;
   out_6838220648110086595[193] = 0.0;
   out_6838220648110086595[194] = 0.0;
   out_6838220648110086595[195] = 0.0;
   out_6838220648110086595[196] = 0.0;
   out_6838220648110086595[197] = 0.0;
   out_6838220648110086595[198] = 0.0;
   out_6838220648110086595[199] = 0.0;
   out_6838220648110086595[200] = 0.0;
   out_6838220648110086595[201] = 0.0;
   out_6838220648110086595[202] = 0.0;
   out_6838220648110086595[203] = 0.0;
   out_6838220648110086595[204] = 0.0;
   out_6838220648110086595[205] = 0.0;
   out_6838220648110086595[206] = 0.0;
   out_6838220648110086595[207] = 0.0;
   out_6838220648110086595[208] = 0.0;
   out_6838220648110086595[209] = 1.0;
   out_6838220648110086595[210] = 0.0;
   out_6838220648110086595[211] = 0.0;
   out_6838220648110086595[212] = 0.0;
   out_6838220648110086595[213] = 0.0;
   out_6838220648110086595[214] = 0.0;
   out_6838220648110086595[215] = 0.0;
   out_6838220648110086595[216] = 0.0;
   out_6838220648110086595[217] = 0.0;
   out_6838220648110086595[218] = 0.0;
   out_6838220648110086595[219] = 0.0;
   out_6838220648110086595[220] = 0.0;
   out_6838220648110086595[221] = 0.0;
   out_6838220648110086595[222] = 0.0;
   out_6838220648110086595[223] = 0.0;
   out_6838220648110086595[224] = 0.0;
   out_6838220648110086595[225] = 0.0;
   out_6838220648110086595[226] = 0.0;
   out_6838220648110086595[227] = 0.0;
   out_6838220648110086595[228] = 1.0;
   out_6838220648110086595[229] = 0.0;
   out_6838220648110086595[230] = 0.0;
   out_6838220648110086595[231] = 0.0;
   out_6838220648110086595[232] = 0.0;
   out_6838220648110086595[233] = 0.0;
   out_6838220648110086595[234] = 0.0;
   out_6838220648110086595[235] = 0.0;
   out_6838220648110086595[236] = 0.0;
   out_6838220648110086595[237] = 0.0;
   out_6838220648110086595[238] = 0.0;
   out_6838220648110086595[239] = 0.0;
   out_6838220648110086595[240] = 0.0;
   out_6838220648110086595[241] = 0.0;
   out_6838220648110086595[242] = 0.0;
   out_6838220648110086595[243] = 0.0;
   out_6838220648110086595[244] = 0.0;
   out_6838220648110086595[245] = 0.0;
   out_6838220648110086595[246] = 0.0;
   out_6838220648110086595[247] = 1.0;
   out_6838220648110086595[248] = 0.0;
   out_6838220648110086595[249] = 0.0;
   out_6838220648110086595[250] = 0.0;
   out_6838220648110086595[251] = 0.0;
   out_6838220648110086595[252] = 0.0;
   out_6838220648110086595[253] = 0.0;
   out_6838220648110086595[254] = 0.0;
   out_6838220648110086595[255] = 0.0;
   out_6838220648110086595[256] = 0.0;
   out_6838220648110086595[257] = 0.0;
   out_6838220648110086595[258] = 0.0;
   out_6838220648110086595[259] = 0.0;
   out_6838220648110086595[260] = 0.0;
   out_6838220648110086595[261] = 0.0;
   out_6838220648110086595[262] = 0.0;
   out_6838220648110086595[263] = 0.0;
   out_6838220648110086595[264] = 0.0;
   out_6838220648110086595[265] = 0.0;
   out_6838220648110086595[266] = 1.0;
   out_6838220648110086595[267] = 0.0;
   out_6838220648110086595[268] = 0.0;
   out_6838220648110086595[269] = 0.0;
   out_6838220648110086595[270] = 0.0;
   out_6838220648110086595[271] = 0.0;
   out_6838220648110086595[272] = 0.0;
   out_6838220648110086595[273] = 0.0;
   out_6838220648110086595[274] = 0.0;
   out_6838220648110086595[275] = 0.0;
   out_6838220648110086595[276] = 0.0;
   out_6838220648110086595[277] = 0.0;
   out_6838220648110086595[278] = 0.0;
   out_6838220648110086595[279] = 0.0;
   out_6838220648110086595[280] = 0.0;
   out_6838220648110086595[281] = 0.0;
   out_6838220648110086595[282] = 0.0;
   out_6838220648110086595[283] = 0.0;
   out_6838220648110086595[284] = 0.0;
   out_6838220648110086595[285] = 1.0;
   out_6838220648110086595[286] = 0.0;
   out_6838220648110086595[287] = 0.0;
   out_6838220648110086595[288] = 0.0;
   out_6838220648110086595[289] = 0.0;
   out_6838220648110086595[290] = 0.0;
   out_6838220648110086595[291] = 0.0;
   out_6838220648110086595[292] = 0.0;
   out_6838220648110086595[293] = 0.0;
   out_6838220648110086595[294] = 0.0;
   out_6838220648110086595[295] = 0.0;
   out_6838220648110086595[296] = 0.0;
   out_6838220648110086595[297] = 0.0;
   out_6838220648110086595[298] = 0.0;
   out_6838220648110086595[299] = 0.0;
   out_6838220648110086595[300] = 0.0;
   out_6838220648110086595[301] = 0.0;
   out_6838220648110086595[302] = 0.0;
   out_6838220648110086595[303] = 0.0;
   out_6838220648110086595[304] = 1.0;
   out_6838220648110086595[305] = 0.0;
   out_6838220648110086595[306] = 0.0;
   out_6838220648110086595[307] = 0.0;
   out_6838220648110086595[308] = 0.0;
   out_6838220648110086595[309] = 0.0;
   out_6838220648110086595[310] = 0.0;
   out_6838220648110086595[311] = 0.0;
   out_6838220648110086595[312] = 0.0;
   out_6838220648110086595[313] = 0.0;
   out_6838220648110086595[314] = 0.0;
   out_6838220648110086595[315] = 0.0;
   out_6838220648110086595[316] = 0.0;
   out_6838220648110086595[317] = 0.0;
   out_6838220648110086595[318] = 0.0;
   out_6838220648110086595[319] = 0.0;
   out_6838220648110086595[320] = 0.0;
   out_6838220648110086595[321] = 0.0;
   out_6838220648110086595[322] = 0.0;
   out_6838220648110086595[323] = 1.0;
}
void f_fun(double *state, double dt, double *out_358648402757037661) {
   out_358648402757037661[0] = atan2((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), -(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]));
   out_358648402757037661[1] = asin(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]));
   out_358648402757037661[2] = atan2(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), -(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]));
   out_358648402757037661[3] = dt*state[12] + state[3];
   out_358648402757037661[4] = dt*state[13] + state[4];
   out_358648402757037661[5] = dt*state[14] + state[5];
   out_358648402757037661[6] = state[6];
   out_358648402757037661[7] = state[7];
   out_358648402757037661[8] = state[8];
   out_358648402757037661[9] = state[9];
   out_358648402757037661[10] = state[10];
   out_358648402757037661[11] = state[11];
   out_358648402757037661[12] = state[12];
   out_358648402757037661[13] = state[13];
   out_358648402757037661[14] = state[14];
   out_358648402757037661[15] = state[15];
   out_358648402757037661[16] = state[16];
   out_358648402757037661[17] = state[17];
}
void F_fun(double *state, double dt, double *out_4283680186500160360) {
   out_4283680186500160360[0] = ((-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*cos(state[0])*cos(state[1]) - sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*cos(state[0])*cos(state[1]) - sin(dt*state[6])*sin(state[0])*cos(dt*state[7])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_4283680186500160360[1] = ((-sin(dt*state[6])*sin(dt*state[8]) - sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*cos(state[1]) - (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*sin(state[1]) - sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(state[0]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*sin(state[1]) + (-sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) + sin(dt*state[8])*cos(dt*state[6]))*cos(state[1]) - sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(state[0]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_4283680186500160360[2] = 0;
   out_4283680186500160360[3] = 0;
   out_4283680186500160360[4] = 0;
   out_4283680186500160360[5] = 0;
   out_4283680186500160360[6] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(dt*cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) - dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_4283680186500160360[7] = (-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[6])*sin(dt*state[7])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[6])*sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) - dt*sin(dt*state[6])*sin(state[1])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + (-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))*(-dt*sin(dt*state[7])*cos(dt*state[6])*cos(state[0])*cos(state[1]) + dt*sin(dt*state[8])*sin(state[0])*cos(dt*state[6])*cos(dt*state[7])*cos(state[1]) - dt*sin(state[1])*cos(dt*state[6])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_4283680186500160360[8] = ((dt*sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + dt*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (dt*sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]))*(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2)) + ((dt*sin(dt*state[6])*sin(dt*state[8]) + dt*sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (-dt*sin(dt*state[6])*cos(dt*state[8]) + dt*sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]))*(-(sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) + (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) - sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/(pow(-(sin(dt*state[6])*sin(dt*state[8]) + sin(dt*state[7])*cos(dt*state[6])*cos(dt*state[8]))*sin(state[1]) + (-sin(dt*state[6])*cos(dt*state[8]) + sin(dt*state[7])*sin(dt*state[8])*cos(dt*state[6]))*sin(state[0])*cos(state[1]) + cos(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2) + pow((sin(dt*state[6])*sin(dt*state[7])*sin(dt*state[8]) + cos(dt*state[6])*cos(dt*state[8]))*sin(state[0])*cos(state[1]) - (sin(dt*state[6])*sin(dt*state[7])*cos(dt*state[8]) - sin(dt*state[8])*cos(dt*state[6]))*sin(state[1]) + sin(dt*state[6])*cos(dt*state[7])*cos(state[0])*cos(state[1]), 2));
   out_4283680186500160360[9] = 0;
   out_4283680186500160360[10] = 0;
   out_4283680186500160360[11] = 0;
   out_4283680186500160360[12] = 0;
   out_4283680186500160360[13] = 0;
   out_4283680186500160360[14] = 0;
   out_4283680186500160360[15] = 0;
   out_4283680186500160360[16] = 0;
   out_4283680186500160360[17] = 0;
   out_4283680186500160360[18] = (-sin(dt*state[7])*sin(state[0])*cos(state[1]) - sin(dt*state[8])*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_4283680186500160360[19] = (-sin(dt*state[7])*sin(state[1])*cos(state[0]) + sin(dt*state[8])*sin(state[0])*sin(state[1])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_4283680186500160360[20] = 0;
   out_4283680186500160360[21] = 0;
   out_4283680186500160360[22] = 0;
   out_4283680186500160360[23] = 0;
   out_4283680186500160360[24] = 0;
   out_4283680186500160360[25] = (dt*sin(dt*state[7])*sin(dt*state[8])*sin(state[0])*cos(state[1]) - dt*sin(dt*state[7])*sin(state[1])*cos(dt*state[8]) + dt*cos(dt*state[7])*cos(state[0])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_4283680186500160360[26] = (-dt*sin(dt*state[8])*sin(state[1])*cos(dt*state[7]) - dt*sin(state[0])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/sqrt(1 - pow(sin(dt*state[7])*cos(state[0])*cos(state[1]) - sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1]) + sin(state[1])*cos(dt*state[7])*cos(dt*state[8]), 2));
   out_4283680186500160360[27] = 0;
   out_4283680186500160360[28] = 0;
   out_4283680186500160360[29] = 0;
   out_4283680186500160360[30] = 0;
   out_4283680186500160360[31] = 0;
   out_4283680186500160360[32] = 0;
   out_4283680186500160360[33] = 0;
   out_4283680186500160360[34] = 0;
   out_4283680186500160360[35] = 0;
   out_4283680186500160360[36] = ((sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_4283680186500160360[37] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-sin(dt*state[7])*sin(state[2])*cos(state[0])*cos(state[1]) + sin(dt*state[8])*sin(state[0])*sin(state[2])*cos(dt*state[7])*cos(state[1]) - sin(state[1])*sin(state[2])*cos(dt*state[7])*cos(dt*state[8]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(-sin(dt*state[7])*cos(state[0])*cos(state[1])*cos(state[2]) + sin(dt*state[8])*sin(state[0])*cos(dt*state[7])*cos(state[1])*cos(state[2]) - sin(state[1])*cos(dt*state[7])*cos(dt*state[8])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_4283680186500160360[38] = ((-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (-sin(state[0])*sin(state[1])*sin(state[2]) - cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_4283680186500160360[39] = 0;
   out_4283680186500160360[40] = 0;
   out_4283680186500160360[41] = 0;
   out_4283680186500160360[42] = 0;
   out_4283680186500160360[43] = (-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))*(dt*(sin(state[0])*cos(state[2]) - sin(state[1])*sin(state[2])*cos(state[0]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*sin(state[2])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + ((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))*(dt*(-sin(state[0])*sin(state[2]) - sin(state[1])*cos(state[0])*cos(state[2]))*cos(dt*state[7]) - dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[7])*sin(dt*state[8]) - dt*sin(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_4283680186500160360[44] = (dt*(sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*sin(state[2])*cos(dt*state[7])*cos(state[1]))*(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2)) + (dt*(sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*cos(dt*state[7])*cos(dt*state[8]) - dt*sin(dt*state[8])*cos(dt*state[7])*cos(state[1])*cos(state[2]))*((-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) - (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) - sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]))/(pow(-(sin(state[0])*sin(state[2]) + sin(state[1])*cos(state[0])*cos(state[2]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*cos(state[2]) - sin(state[2])*cos(state[0]))*sin(dt*state[8])*cos(dt*state[7]) + cos(dt*state[7])*cos(dt*state[8])*cos(state[1])*cos(state[2]), 2) + pow(-(-sin(state[0])*cos(state[2]) + sin(state[1])*sin(state[2])*cos(state[0]))*sin(dt*state[7]) + (sin(state[0])*sin(state[1])*sin(state[2]) + cos(state[0])*cos(state[2]))*sin(dt*state[8])*cos(dt*state[7]) + sin(state[2])*cos(dt*state[7])*cos(dt*state[8])*cos(state[1]), 2));
   out_4283680186500160360[45] = 0;
   out_4283680186500160360[46] = 0;
   out_4283680186500160360[47] = 0;
   out_4283680186500160360[48] = 0;
   out_4283680186500160360[49] = 0;
   out_4283680186500160360[50] = 0;
   out_4283680186500160360[51] = 0;
   out_4283680186500160360[52] = 0;
   out_4283680186500160360[53] = 0;
   out_4283680186500160360[54] = 0;
   out_4283680186500160360[55] = 0;
   out_4283680186500160360[56] = 0;
   out_4283680186500160360[57] = 1;
   out_4283680186500160360[58] = 0;
   out_4283680186500160360[59] = 0;
   out_4283680186500160360[60] = 0;
   out_4283680186500160360[61] = 0;
   out_4283680186500160360[62] = 0;
   out_4283680186500160360[63] = 0;
   out_4283680186500160360[64] = 0;
   out_4283680186500160360[65] = 0;
   out_4283680186500160360[66] = dt;
   out_4283680186500160360[67] = 0;
   out_4283680186500160360[68] = 0;
   out_4283680186500160360[69] = 0;
   out_4283680186500160360[70] = 0;
   out_4283680186500160360[71] = 0;
   out_4283680186500160360[72] = 0;
   out_4283680186500160360[73] = 0;
   out_4283680186500160360[74] = 0;
   out_4283680186500160360[75] = 0;
   out_4283680186500160360[76] = 1;
   out_4283680186500160360[77] = 0;
   out_4283680186500160360[78] = 0;
   out_4283680186500160360[79] = 0;
   out_4283680186500160360[80] = 0;
   out_4283680186500160360[81] = 0;
   out_4283680186500160360[82] = 0;
   out_4283680186500160360[83] = 0;
   out_4283680186500160360[84] = 0;
   out_4283680186500160360[85] = dt;
   out_4283680186500160360[86] = 0;
   out_4283680186500160360[87] = 0;
   out_4283680186500160360[88] = 0;
   out_4283680186500160360[89] = 0;
   out_4283680186500160360[90] = 0;
   out_4283680186500160360[91] = 0;
   out_4283680186500160360[92] = 0;
   out_4283680186500160360[93] = 0;
   out_4283680186500160360[94] = 0;
   out_4283680186500160360[95] = 1;
   out_4283680186500160360[96] = 0;
   out_4283680186500160360[97] = 0;
   out_4283680186500160360[98] = 0;
   out_4283680186500160360[99] = 0;
   out_4283680186500160360[100] = 0;
   out_4283680186500160360[101] = 0;
   out_4283680186500160360[102] = 0;
   out_4283680186500160360[103] = 0;
   out_4283680186500160360[104] = dt;
   out_4283680186500160360[105] = 0;
   out_4283680186500160360[106] = 0;
   out_4283680186500160360[107] = 0;
   out_4283680186500160360[108] = 0;
   out_4283680186500160360[109] = 0;
   out_4283680186500160360[110] = 0;
   out_4283680186500160360[111] = 0;
   out_4283680186500160360[112] = 0;
   out_4283680186500160360[113] = 0;
   out_4283680186500160360[114] = 1;
   out_4283680186500160360[115] = 0;
   out_4283680186500160360[116] = 0;
   out_4283680186500160360[117] = 0;
   out_4283680186500160360[118] = 0;
   out_4283680186500160360[119] = 0;
   out_4283680186500160360[120] = 0;
   out_4283680186500160360[121] = 0;
   out_4283680186500160360[122] = 0;
   out_4283680186500160360[123] = 0;
   out_4283680186500160360[124] = 0;
   out_4283680186500160360[125] = 0;
   out_4283680186500160360[126] = 0;
   out_4283680186500160360[127] = 0;
   out_4283680186500160360[128] = 0;
   out_4283680186500160360[129] = 0;
   out_4283680186500160360[130] = 0;
   out_4283680186500160360[131] = 0;
   out_4283680186500160360[132] = 0;
   out_4283680186500160360[133] = 1;
   out_4283680186500160360[134] = 0;
   out_4283680186500160360[135] = 0;
   out_4283680186500160360[136] = 0;
   out_4283680186500160360[137] = 0;
   out_4283680186500160360[138] = 0;
   out_4283680186500160360[139] = 0;
   out_4283680186500160360[140] = 0;
   out_4283680186500160360[141] = 0;
   out_4283680186500160360[142] = 0;
   out_4283680186500160360[143] = 0;
   out_4283680186500160360[144] = 0;
   out_4283680186500160360[145] = 0;
   out_4283680186500160360[146] = 0;
   out_4283680186500160360[147] = 0;
   out_4283680186500160360[148] = 0;
   out_4283680186500160360[149] = 0;
   out_4283680186500160360[150] = 0;
   out_4283680186500160360[151] = 0;
   out_4283680186500160360[152] = 1;
   out_4283680186500160360[153] = 0;
   out_4283680186500160360[154] = 0;
   out_4283680186500160360[155] = 0;
   out_4283680186500160360[156] = 0;
   out_4283680186500160360[157] = 0;
   out_4283680186500160360[158] = 0;
   out_4283680186500160360[159] = 0;
   out_4283680186500160360[160] = 0;
   out_4283680186500160360[161] = 0;
   out_4283680186500160360[162] = 0;
   out_4283680186500160360[163] = 0;
   out_4283680186500160360[164] = 0;
   out_4283680186500160360[165] = 0;
   out_4283680186500160360[166] = 0;
   out_4283680186500160360[167] = 0;
   out_4283680186500160360[168] = 0;
   out_4283680186500160360[169] = 0;
   out_4283680186500160360[170] = 0;
   out_4283680186500160360[171] = 1;
   out_4283680186500160360[172] = 0;
   out_4283680186500160360[173] = 0;
   out_4283680186500160360[174] = 0;
   out_4283680186500160360[175] = 0;
   out_4283680186500160360[176] = 0;
   out_4283680186500160360[177] = 0;
   out_4283680186500160360[178] = 0;
   out_4283680186500160360[179] = 0;
   out_4283680186500160360[180] = 0;
   out_4283680186500160360[181] = 0;
   out_4283680186500160360[182] = 0;
   out_4283680186500160360[183] = 0;
   out_4283680186500160360[184] = 0;
   out_4283680186500160360[185] = 0;
   out_4283680186500160360[186] = 0;
   out_4283680186500160360[187] = 0;
   out_4283680186500160360[188] = 0;
   out_4283680186500160360[189] = 0;
   out_4283680186500160360[190] = 1;
   out_4283680186500160360[191] = 0;
   out_4283680186500160360[192] = 0;
   out_4283680186500160360[193] = 0;
   out_4283680186500160360[194] = 0;
   out_4283680186500160360[195] = 0;
   out_4283680186500160360[196] = 0;
   out_4283680186500160360[197] = 0;
   out_4283680186500160360[198] = 0;
   out_4283680186500160360[199] = 0;
   out_4283680186500160360[200] = 0;
   out_4283680186500160360[201] = 0;
   out_4283680186500160360[202] = 0;
   out_4283680186500160360[203] = 0;
   out_4283680186500160360[204] = 0;
   out_4283680186500160360[205] = 0;
   out_4283680186500160360[206] = 0;
   out_4283680186500160360[207] = 0;
   out_4283680186500160360[208] = 0;
   out_4283680186500160360[209] = 1;
   out_4283680186500160360[210] = 0;
   out_4283680186500160360[211] = 0;
   out_4283680186500160360[212] = 0;
   out_4283680186500160360[213] = 0;
   out_4283680186500160360[214] = 0;
   out_4283680186500160360[215] = 0;
   out_4283680186500160360[216] = 0;
   out_4283680186500160360[217] = 0;
   out_4283680186500160360[218] = 0;
   out_4283680186500160360[219] = 0;
   out_4283680186500160360[220] = 0;
   out_4283680186500160360[221] = 0;
   out_4283680186500160360[222] = 0;
   out_4283680186500160360[223] = 0;
   out_4283680186500160360[224] = 0;
   out_4283680186500160360[225] = 0;
   out_4283680186500160360[226] = 0;
   out_4283680186500160360[227] = 0;
   out_4283680186500160360[228] = 1;
   out_4283680186500160360[229] = 0;
   out_4283680186500160360[230] = 0;
   out_4283680186500160360[231] = 0;
   out_4283680186500160360[232] = 0;
   out_4283680186500160360[233] = 0;
   out_4283680186500160360[234] = 0;
   out_4283680186500160360[235] = 0;
   out_4283680186500160360[236] = 0;
   out_4283680186500160360[237] = 0;
   out_4283680186500160360[238] = 0;
   out_4283680186500160360[239] = 0;
   out_4283680186500160360[240] = 0;
   out_4283680186500160360[241] = 0;
   out_4283680186500160360[242] = 0;
   out_4283680186500160360[243] = 0;
   out_4283680186500160360[244] = 0;
   out_4283680186500160360[245] = 0;
   out_4283680186500160360[246] = 0;
   out_4283680186500160360[247] = 1;
   out_4283680186500160360[248] = 0;
   out_4283680186500160360[249] = 0;
   out_4283680186500160360[250] = 0;
   out_4283680186500160360[251] = 0;
   out_4283680186500160360[252] = 0;
   out_4283680186500160360[253] = 0;
   out_4283680186500160360[254] = 0;
   out_4283680186500160360[255] = 0;
   out_4283680186500160360[256] = 0;
   out_4283680186500160360[257] = 0;
   out_4283680186500160360[258] = 0;
   out_4283680186500160360[259] = 0;
   out_4283680186500160360[260] = 0;
   out_4283680186500160360[261] = 0;
   out_4283680186500160360[262] = 0;
   out_4283680186500160360[263] = 0;
   out_4283680186500160360[264] = 0;
   out_4283680186500160360[265] = 0;
   out_4283680186500160360[266] = 1;
   out_4283680186500160360[267] = 0;
   out_4283680186500160360[268] = 0;
   out_4283680186500160360[269] = 0;
   out_4283680186500160360[270] = 0;
   out_4283680186500160360[271] = 0;
   out_4283680186500160360[272] = 0;
   out_4283680186500160360[273] = 0;
   out_4283680186500160360[274] = 0;
   out_4283680186500160360[275] = 0;
   out_4283680186500160360[276] = 0;
   out_4283680186500160360[277] = 0;
   out_4283680186500160360[278] = 0;
   out_4283680186500160360[279] = 0;
   out_4283680186500160360[280] = 0;
   out_4283680186500160360[281] = 0;
   out_4283680186500160360[282] = 0;
   out_4283680186500160360[283] = 0;
   out_4283680186500160360[284] = 0;
   out_4283680186500160360[285] = 1;
   out_4283680186500160360[286] = 0;
   out_4283680186500160360[287] = 0;
   out_4283680186500160360[288] = 0;
   out_4283680186500160360[289] = 0;
   out_4283680186500160360[290] = 0;
   out_4283680186500160360[291] = 0;
   out_4283680186500160360[292] = 0;
   out_4283680186500160360[293] = 0;
   out_4283680186500160360[294] = 0;
   out_4283680186500160360[295] = 0;
   out_4283680186500160360[296] = 0;
   out_4283680186500160360[297] = 0;
   out_4283680186500160360[298] = 0;
   out_4283680186500160360[299] = 0;
   out_4283680186500160360[300] = 0;
   out_4283680186500160360[301] = 0;
   out_4283680186500160360[302] = 0;
   out_4283680186500160360[303] = 0;
   out_4283680186500160360[304] = 1;
   out_4283680186500160360[305] = 0;
   out_4283680186500160360[306] = 0;
   out_4283680186500160360[307] = 0;
   out_4283680186500160360[308] = 0;
   out_4283680186500160360[309] = 0;
   out_4283680186500160360[310] = 0;
   out_4283680186500160360[311] = 0;
   out_4283680186500160360[312] = 0;
   out_4283680186500160360[313] = 0;
   out_4283680186500160360[314] = 0;
   out_4283680186500160360[315] = 0;
   out_4283680186500160360[316] = 0;
   out_4283680186500160360[317] = 0;
   out_4283680186500160360[318] = 0;
   out_4283680186500160360[319] = 0;
   out_4283680186500160360[320] = 0;
   out_4283680186500160360[321] = 0;
   out_4283680186500160360[322] = 0;
   out_4283680186500160360[323] = 1;
}
void h_4(double *state, double *unused, double *out_5132188379361733090) {
   out_5132188379361733090[0] = state[6] + state[9];
   out_5132188379361733090[1] = state[7] + state[10];
   out_5132188379361733090[2] = state[8] + state[11];
}
void H_4(double *state, double *unused, double *out_8036168129992984699) {
   out_8036168129992984699[0] = 0;
   out_8036168129992984699[1] = 0;
   out_8036168129992984699[2] = 0;
   out_8036168129992984699[3] = 0;
   out_8036168129992984699[4] = 0;
   out_8036168129992984699[5] = 0;
   out_8036168129992984699[6] = 1;
   out_8036168129992984699[7] = 0;
   out_8036168129992984699[8] = 0;
   out_8036168129992984699[9] = 1;
   out_8036168129992984699[10] = 0;
   out_8036168129992984699[11] = 0;
   out_8036168129992984699[12] = 0;
   out_8036168129992984699[13] = 0;
   out_8036168129992984699[14] = 0;
   out_8036168129992984699[15] = 0;
   out_8036168129992984699[16] = 0;
   out_8036168129992984699[17] = 0;
   out_8036168129992984699[18] = 0;
   out_8036168129992984699[19] = 0;
   out_8036168129992984699[20] = 0;
   out_8036168129992984699[21] = 0;
   out_8036168129992984699[22] = 0;
   out_8036168129992984699[23] = 0;
   out_8036168129992984699[24] = 0;
   out_8036168129992984699[25] = 1;
   out_8036168129992984699[26] = 0;
   out_8036168129992984699[27] = 0;
   out_8036168129992984699[28] = 1;
   out_8036168129992984699[29] = 0;
   out_8036168129992984699[30] = 0;
   out_8036168129992984699[31] = 0;
   out_8036168129992984699[32] = 0;
   out_8036168129992984699[33] = 0;
   out_8036168129992984699[34] = 0;
   out_8036168129992984699[35] = 0;
   out_8036168129992984699[36] = 0;
   out_8036168129992984699[37] = 0;
   out_8036168129992984699[38] = 0;
   out_8036168129992984699[39] = 0;
   out_8036168129992984699[40] = 0;
   out_8036168129992984699[41] = 0;
   out_8036168129992984699[42] = 0;
   out_8036168129992984699[43] = 0;
   out_8036168129992984699[44] = 1;
   out_8036168129992984699[45] = 0;
   out_8036168129992984699[46] = 0;
   out_8036168129992984699[47] = 1;
   out_8036168129992984699[48] = 0;
   out_8036168129992984699[49] = 0;
   out_8036168129992984699[50] = 0;
   out_8036168129992984699[51] = 0;
   out_8036168129992984699[52] = 0;
   out_8036168129992984699[53] = 0;
}
void h_10(double *state, double *unused, double *out_1317789669870360968) {
   out_1317789669870360968[0] = 9.8100000000000005*sin(state[1]) - state[4]*state[8] + state[5]*state[7] + state[12] + state[15];
   out_1317789669870360968[1] = -9.8100000000000005*sin(state[0])*cos(state[1]) + state[3]*state[8] - state[5]*state[6] + state[13] + state[16];
   out_1317789669870360968[2] = -9.8100000000000005*cos(state[0])*cos(state[1]) - state[3]*state[7] + state[4]*state[6] + state[14] + state[17];
}
void H_10(double *state, double *unused, double *out_6822252596821216619) {
   out_6822252596821216619[0] = 0;
   out_6822252596821216619[1] = 9.8100000000000005*cos(state[1]);
   out_6822252596821216619[2] = 0;
   out_6822252596821216619[3] = 0;
   out_6822252596821216619[4] = -state[8];
   out_6822252596821216619[5] = state[7];
   out_6822252596821216619[6] = 0;
   out_6822252596821216619[7] = state[5];
   out_6822252596821216619[8] = -state[4];
   out_6822252596821216619[9] = 0;
   out_6822252596821216619[10] = 0;
   out_6822252596821216619[11] = 0;
   out_6822252596821216619[12] = 1;
   out_6822252596821216619[13] = 0;
   out_6822252596821216619[14] = 0;
   out_6822252596821216619[15] = 1;
   out_6822252596821216619[16] = 0;
   out_6822252596821216619[17] = 0;
   out_6822252596821216619[18] = -9.8100000000000005*cos(state[0])*cos(state[1]);
   out_6822252596821216619[19] = 9.8100000000000005*sin(state[0])*sin(state[1]);
   out_6822252596821216619[20] = 0;
   out_6822252596821216619[21] = state[8];
   out_6822252596821216619[22] = 0;
   out_6822252596821216619[23] = -state[6];
   out_6822252596821216619[24] = -state[5];
   out_6822252596821216619[25] = 0;
   out_6822252596821216619[26] = state[3];
   out_6822252596821216619[27] = 0;
   out_6822252596821216619[28] = 0;
   out_6822252596821216619[29] = 0;
   out_6822252596821216619[30] = 0;
   out_6822252596821216619[31] = 1;
   out_6822252596821216619[32] = 0;
   out_6822252596821216619[33] = 0;
   out_6822252596821216619[34] = 1;
   out_6822252596821216619[35] = 0;
   out_6822252596821216619[36] = 9.8100000000000005*sin(state[0])*cos(state[1]);
   out_6822252596821216619[37] = 9.8100000000000005*sin(state[1])*cos(state[0]);
   out_6822252596821216619[38] = 0;
   out_6822252596821216619[39] = -state[7];
   out_6822252596821216619[40] = state[6];
   out_6822252596821216619[41] = 0;
   out_6822252596821216619[42] = state[4];
   out_6822252596821216619[43] = -state[3];
   out_6822252596821216619[44] = 0;
   out_6822252596821216619[45] = 0;
   out_6822252596821216619[46] = 0;
   out_6822252596821216619[47] = 0;
   out_6822252596821216619[48] = 0;
   out_6822252596821216619[49] = 0;
   out_6822252596821216619[50] = 1;
   out_6822252596821216619[51] = 0;
   out_6822252596821216619[52] = 0;
   out_6822252596821216619[53] = 1;
}
void h_13(double *state, double *unused, double *out_103193819568861600) {
   out_103193819568861600[0] = state[3];
   out_103193819568861600[1] = state[4];
   out_103193819568861600[2] = state[5];
}
void H_13(double *state, double *unused, double *out_7198302118384234116) {
   out_7198302118384234116[0] = 0;
   out_7198302118384234116[1] = 0;
   out_7198302118384234116[2] = 0;
   out_7198302118384234116[3] = 1;
   out_7198302118384234116[4] = 0;
   out_7198302118384234116[5] = 0;
   out_7198302118384234116[6] = 0;
   out_7198302118384234116[7] = 0;
   out_7198302118384234116[8] = 0;
   out_7198302118384234116[9] = 0;
   out_7198302118384234116[10] = 0;
   out_7198302118384234116[11] = 0;
   out_7198302118384234116[12] = 0;
   out_7198302118384234116[13] = 0;
   out_7198302118384234116[14] = 0;
   out_7198302118384234116[15] = 0;
   out_7198302118384234116[16] = 0;
   out_7198302118384234116[17] = 0;
   out_7198302118384234116[18] = 0;
   out_7198302118384234116[19] = 0;
   out_7198302118384234116[20] = 0;
   out_7198302118384234116[21] = 0;
   out_7198302118384234116[22] = 1;
   out_7198302118384234116[23] = 0;
   out_7198302118384234116[24] = 0;
   out_7198302118384234116[25] = 0;
   out_7198302118384234116[26] = 0;
   out_7198302118384234116[27] = 0;
   out_7198302118384234116[28] = 0;
   out_7198302118384234116[29] = 0;
   out_7198302118384234116[30] = 0;
   out_7198302118384234116[31] = 0;
   out_7198302118384234116[32] = 0;
   out_7198302118384234116[33] = 0;
   out_7198302118384234116[34] = 0;
   out_7198302118384234116[35] = 0;
   out_7198302118384234116[36] = 0;
   out_7198302118384234116[37] = 0;
   out_7198302118384234116[38] = 0;
   out_7198302118384234116[39] = 0;
   out_7198302118384234116[40] = 0;
   out_7198302118384234116[41] = 1;
   out_7198302118384234116[42] = 0;
   out_7198302118384234116[43] = 0;
   out_7198302118384234116[44] = 0;
   out_7198302118384234116[45] = 0;
   out_7198302118384234116[46] = 0;
   out_7198302118384234116[47] = 0;
   out_7198302118384234116[48] = 0;
   out_7198302118384234116[49] = 0;
   out_7198302118384234116[50] = 0;
   out_7198302118384234116[51] = 0;
   out_7198302118384234116[52] = 0;
   out_7198302118384234116[53] = 0;
}
void h_14(double *state, double *unused, double *out_5774019743431067995) {
   out_5774019743431067995[0] = state[6];
   out_5774019743431067995[1] = state[7];
   out_5774019743431067995[2] = state[8];
}
void H_14(double *state, double *unused, double *out_4953379697697612403) {
   out_4953379697697612403[0] = 0;
   out_4953379697697612403[1] = 0;
   out_4953379697697612403[2] = 0;
   out_4953379697697612403[3] = 0;
   out_4953379697697612403[4] = 0;
   out_4953379697697612403[5] = 0;
   out_4953379697697612403[6] = 1;
   out_4953379697697612403[7] = 0;
   out_4953379697697612403[8] = 0;
   out_4953379697697612403[9] = 0;
   out_4953379697697612403[10] = 0;
   out_4953379697697612403[11] = 0;
   out_4953379697697612403[12] = 0;
   out_4953379697697612403[13] = 0;
   out_4953379697697612403[14] = 0;
   out_4953379697697612403[15] = 0;
   out_4953379697697612403[16] = 0;
   out_4953379697697612403[17] = 0;
   out_4953379697697612403[18] = 0;
   out_4953379697697612403[19] = 0;
   out_4953379697697612403[20] = 0;
   out_4953379697697612403[21] = 0;
   out_4953379697697612403[22] = 0;
   out_4953379697697612403[23] = 0;
   out_4953379697697612403[24] = 0;
   out_4953379697697612403[25] = 1;
   out_4953379697697612403[26] = 0;
   out_4953379697697612403[27] = 0;
   out_4953379697697612403[28] = 0;
   out_4953379697697612403[29] = 0;
   out_4953379697697612403[30] = 0;
   out_4953379697697612403[31] = 0;
   out_4953379697697612403[32] = 0;
   out_4953379697697612403[33] = 0;
   out_4953379697697612403[34] = 0;
   out_4953379697697612403[35] = 0;
   out_4953379697697612403[36] = 0;
   out_4953379697697612403[37] = 0;
   out_4953379697697612403[38] = 0;
   out_4953379697697612403[39] = 0;
   out_4953379697697612403[40] = 0;
   out_4953379697697612403[41] = 0;
   out_4953379697697612403[42] = 0;
   out_4953379697697612403[43] = 0;
   out_4953379697697612403[44] = 1;
   out_4953379697697612403[45] = 0;
   out_4953379697697612403[46] = 0;
   out_4953379697697612403[47] = 0;
   out_4953379697697612403[48] = 0;
   out_4953379697697612403[49] = 0;
   out_4953379697697612403[50] = 0;
   out_4953379697697612403[51] = 0;
   out_4953379697697612403[52] = 0;
   out_4953379697697612403[53] = 0;
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

void pose_update_4(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<3, 3, 0>(in_x, in_P, h_4, H_4, NULL, in_z, in_R, in_ea, MAHA_THRESH_4);
}
void pose_update_10(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<3, 3, 0>(in_x, in_P, h_10, H_10, NULL, in_z, in_R, in_ea, MAHA_THRESH_10);
}
void pose_update_13(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<3, 3, 0>(in_x, in_P, h_13, H_13, NULL, in_z, in_R, in_ea, MAHA_THRESH_13);
}
void pose_update_14(double *in_x, double *in_P, double *in_z, double *in_R, double *in_ea) {
  update<3, 3, 0>(in_x, in_P, h_14, H_14, NULL, in_z, in_R, in_ea, MAHA_THRESH_14);
}
void pose_err_fun(double *nom_x, double *delta_x, double *out_7405193010915679121) {
  err_fun(nom_x, delta_x, out_7405193010915679121);
}
void pose_inv_err_fun(double *nom_x, double *true_x, double *out_5475328358876229061) {
  inv_err_fun(nom_x, true_x, out_5475328358876229061);
}
void pose_H_mod_fun(double *state, double *out_6838220648110086595) {
  H_mod_fun(state, out_6838220648110086595);
}
void pose_f_fun(double *state, double dt, double *out_358648402757037661) {
  f_fun(state,  dt, out_358648402757037661);
}
void pose_F_fun(double *state, double dt, double *out_4283680186500160360) {
  F_fun(state,  dt, out_4283680186500160360);
}
void pose_h_4(double *state, double *unused, double *out_5132188379361733090) {
  h_4(state, unused, out_5132188379361733090);
}
void pose_H_4(double *state, double *unused, double *out_8036168129992984699) {
  H_4(state, unused, out_8036168129992984699);
}
void pose_h_10(double *state, double *unused, double *out_1317789669870360968) {
  h_10(state, unused, out_1317789669870360968);
}
void pose_H_10(double *state, double *unused, double *out_6822252596821216619) {
  H_10(state, unused, out_6822252596821216619);
}
void pose_h_13(double *state, double *unused, double *out_103193819568861600) {
  h_13(state, unused, out_103193819568861600);
}
void pose_H_13(double *state, double *unused, double *out_7198302118384234116) {
  H_13(state, unused, out_7198302118384234116);
}
void pose_h_14(double *state, double *unused, double *out_5774019743431067995) {
  h_14(state, unused, out_5774019743431067995);
}
void pose_H_14(double *state, double *unused, double *out_4953379697697612403) {
  H_14(state, unused, out_4953379697697612403);
}
void pose_predict(double *in_x, double *in_P, double *in_Q, double dt) {
  predict(in_x, in_P, in_Q, dt);
}
}

const EKF pose = {
  .name = "pose",
  .kinds = { 4, 10, 13, 14 },
  .feature_kinds = {  },
  .f_fun = pose_f_fun,
  .F_fun = pose_F_fun,
  .err_fun = pose_err_fun,
  .inv_err_fun = pose_inv_err_fun,
  .H_mod_fun = pose_H_mod_fun,
  .predict = pose_predict,
  .hs = {
    { 4, pose_h_4 },
    { 10, pose_h_10 },
    { 13, pose_h_13 },
    { 14, pose_h_14 },
  },
  .Hs = {
    { 4, pose_H_4 },
    { 10, pose_H_10 },
    { 13, pose_H_13 },
    { 14, pose_H_14 },
  },
  .updates = {
    { 4, pose_update_4 },
    { 10, pose_update_10 },
    { 13, pose_update_13 },
    { 14, pose_update_14 },
  },
  .Hes = {
  },
  .sets = {
  },
  .extra_routines = {
  },
};

ekf_lib_init(pose)
