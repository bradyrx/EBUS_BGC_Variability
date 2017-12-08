% program for calculating ff
load /Volumes/roadie/CESM1-BEC/GECO.IAF.x1.CESM1.001/mat/SO_temp.mat
tk = nanmean(SO_temp) + 273.15;
tk100 = tk * 1e-2;
tk1002 = tk100 * tk100;
load /Volumes/roadie/CESM1-BEC/GECO.IAF.x1.CESM1.001/mat/SO_salt.mat
s = nanmean(SO_salt);

ff = exp(-162.8301 + (218.2968/tk100) + 90.9241*log(tk100) - 1.47696*tk1002 + ...
    s*(0.025695 - 0.025225*tk100 + 0.0049867*tk1002));

% SO ff = 0.0541 mol/kg/atm