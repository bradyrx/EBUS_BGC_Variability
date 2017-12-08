% program to calculate wind speed from windstress

stress = (sqrt(SO_taux.^2 + SO_taux.^2)) / 1.2 * 100.^2 / 1e5;
% stress is sqrt(taux.^2+tauy.^2)/rho_air put into m^2/s^2s
% rho_air is 1.2 kg/m^3
for time = 1:50;
    last = stress(time,:);
    p = [.0000764 .000142 .0027 -1*last];
    r = roots(p);
    i = imag(r);
    good = find(i==0);
    speed(time,:) = r(good);
end

SO_speed = speed;
save /Volumes/roadie/CESM1-BEC/GECO.IAF.x1.CESM1.001/mat/SO_speed SO_speed
