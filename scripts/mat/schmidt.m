% program for calculating Schmidt number
load /Volumes/roadie/CESM1-BEC/GECO.IAF.x1.CESM1.001/mat/SO_temp.mat
t = nanmean(SO_temp);

Sc = 2073.1 - 125.62*t + 3.627*t^2 - 0.043219*t^3;

% SO Schmidt = 1.6465e3 = 1646.5