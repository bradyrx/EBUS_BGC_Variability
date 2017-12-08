%% CO2 flux decomposition

%% Loading data

filename_ifrac = 'g.e11_LENS.GECOIAF.T62_g16.009.pop.h.ECOSYS_IFRAC.024901-031612.nc' ;
filename_fg = 'g.e11_LENS.GECOIAF.T62_g16.009.pop.h.FG_ALT_CO2.024901-031612.nc' ;
filename_pCO2 = 'g.e11_LENS.GECOIAF.T62_g16.009.pop.h.DpCO2_ALT_CO2.024901-031612.nc' ;
filename_k = 'g.e11_LENS.GECOIAF.T62_g16.009.pop.h.ECOSYS_XKW.024901-031612.nc' ;
filename_temp = 'g.e11_LENS.GECOIAF.T62_g16.009.pop.h.TEMP.024901-031612.nc' ;
filename_salt = 'g.e11_LENS.GECOIAF.T62_g16.009.pop.h.SALT.024901-031612.nc' ;
filename_rho = 'g.e11_LENS.GECOIAF.T62_g16.009.pop.h.RHO.024901-031612.nc' ;

% Read netCDF variables
time       = ncread(filename_ifrac,'time') ;
ifrac      = ncread(filename_ifrac,'ECOSYS_IFRAC') ;
lat        = ncread(filename_ifrac,'TLAT') ;
CO2_flux   = ncread(filename_fg,'FG_ALT_CO2') ;
dpCO2      = ncread(filename_pCO2,'DpCO2_ALT_CO2') ;
xkw        = ncread(filename_k,'ECOSYS_XKW') ;
temp       = ncread(filename_temp,'TEMP',[1 1 1 1],[Inf Inf 1 Inf]) ;
salt       = ncread(filename_salt,'SALT',[1 1 1 1],[Inf Inf 1 Inf]) ;
rho        = ncread(filename_rho,'RHO',[1 1 1 1],[Inf Inf 1 Inf]) ;

% Inverse CO2 flux
CO2_flux = -CO2_flux ;

%% Calculate solubility
% Change units of temperature to Kelvins
tempK = temp + 273.15 ;
tempK100 = tempK.*1e-2 ;
tempK1002 = tempK100.*tempK100 ;

sol = NaN(size(CO2_flux)) ;

[nrow,ncol] = size(lat) ;

for t = 1:length(time)
    for i = 1:nrow
        for j = 1:ncol
            
            sol(i,j,t) = exp(-162.8301 + (218.2968/tempK100(i,j,1,t)) ...
                + 90.9241*log(tempK100(i,j,1,t)) - 1.47696*tempK1002(i,j,1,t) ...
                + salt(i,j,1,t)*(0.025695 - 0.025225*tempK100(i,j,1,t) + ...
                0.0049867*tempK1002(i,j,1,t)));
            
        end
    end
end

%% Contribution of ifrac to trend in flux

% Find all points that are north of the Arctic Circle
[n,m] = find(lat >= 66) ;

c_xkw = 0 ;
c_sol = 0 ;
c_dpCO2 = 0 ;
c_rho = 0 ;
c_ifrac = 0 ;
mean_xkw = 0 ;
mean_sol = 0 ;
mean_dpCO2 = 0 ;
mean_rho = 0 ;
mean_ifrac = 0 ;

% Calculate the spatial and temporal mean
for t = 121:length(time)
    for i = 1:length(n)
        if ~isnan(xkw(n(i),m(i),t))
            c_xkw = c_xkw + 1 ;
            mean_xkw = mean_xkw + xkw(n(i),m(i),t)*(3.1536e7)/1e2 ;
        end
        if ~isnan(sol(n(i),m(i),t))
            c_sol = c_sol + 1 ;
            mean_sol = mean_sol + sol(n(i),m(i),t) ;
        end
        if ~isnan(dpCO2(n(i),m(i),t))
            c_dpCO2 = c_dpCO2 + 1 ;
            mean_dpCO2 = mean_dpCO2 + dpCO2(n(i),m(i),t)*1e-6 ;
        end
        if ~isnan(rho(n(i),m(i),t))
            c_rho = c_rho + 1 ;
            mean_rho = mean_rho + rho(n(i),m(i),1,t)*1e6 ;
        end
        if ~isnan(ifrac(n(i),m(i),t))
            c_ifrac = c_ifrac + 1 ;
            mean_ifrac = mean_ifrac + ifrac(n(i),m(i),t) ;
        end
    end
end

mean_xkw = mean_xkw/c_xkw ;
mean_sol = mean_sol/c_sol ;
mean_dpCO2 = mean_dpCO2/c_dpCO2 ;
mean_rho = mean_rho/c_rho ;
mean_ifrac = mean_ifrac/c_ifrac ;

dflux_dxkw = mean_sol*mean_rho*mean_dpCO2*(1-mean_ifrac) ;
dflux_dsol = mean_xkw*mean_rho*mean_dpCO2*(1-mean_ifrac) ;
dflux_dpCO2 = mean_xkw*mean_sol*mean_rho*(1-mean_ifrac) ;
dflux_drho = mean_xkw*mean_sol*mean_dpCO2*(1-mean_ifrac) ;
dflux_difrac = -1*mean_xkw*mean_sol*mean_dpCO2*mean_rho ;

% Calculate the monthly means
n_xkw = zeros(length(time)-120,1) ;
n_sol = zeros(length(time)-120,1) ;
n_dpCO2 = zeros(length(time)-120,1) ;
n_rho = zeros(length(time)-120,1) ;
n_ifrac = zeros(length(time)-120,1) ;
n_flux = zeros(length(time)-120,1) ;
monthly_xkw = zeros(length(time)-120,1) ;
monthly_sol = zeros(length(time)-120,1) ;
monthly_dpCO2 = zeros(length(time)-120,1) ;
monthly_rho = zeros(length(time)-120,1) ;
monthly_ifrac = zeros(length(time)-120,1) ;
monthly_flux = zeros(length(time)-120,1) ;

for t = 121:length(time)
    for i = 1:length(n)
        if ~isnan(xkw(n(i),m(i),t))
            n_xkw(t-120) = n_xkw(t-120) + 1 ;
            monthly_xkw(t-120) = monthly_xkw(t-120) + xkw(n(i),m(i),t)*(3.1536e7)/1e2 ;
        end
        if ~isnan(sol(n(i),m(i),t))
            n_sol(t-120) = n_sol(t-120) + 1 ;
            monthly_sol(t-120) = monthly_sol(t-120) + sol(n(i),m(i),t) ;
        end
        if ~isnan(dpCO2(n(i),m(i),t))
            n_dpCO2(t-120) = n_dpCO2(t-120) + 1 ;
            monthly_dpCO2(t-120) = monthly_dpCO2(t-120) + dpCO2(n(i),m(i),t)*1e-6 ;
        end
        if ~isnan(rho(n(i),m(i),t))
            n_rho(t-120) = n_rho(t-120) + 1 ;
            monthly_rho(t-120) = monthly_rho(t-120) + rho(n(i),m(i),1,t)*1e6 ;
        end
        if ~isnan(ifrac(n(i),m(i),t))
            n_ifrac(t-120) = n_ifrac(t-120) + 1 ;
            monthly_ifrac(t-120) = monthly_ifrac(t-120) + ifrac(n(i),m(i),t) ;
        end
        if ~isnan(CO2_flux(n(i),m(i),t))
            n_flux(t-120) = n_flux(t-120) + 1 ;
            monthly_flux(t-120) = monthly_flux(t-120) + ...
                CO2_flux(n(i),m(i),t)*(3.1536e7)/(1e5) ;
        end
    end
end

monthly_xkw = monthly_xkw./n_xkw ;
monthly_sol = monthly_sol./n_sol ;
monthly_dpCO2 = monthly_dpCO2./n_dpCO2 ;
monthly_rho = monthly_rho./n_rho ;
monthly_ifrac = monthly_ifrac./n_ifrac ;
monthly_flux = monthly_flux./n_flux ;

% Calculate the annual means
annual_xkw = NaN(58,1) ;
annual_sol = NaN(58,1) ;
annual_dpCO2 = NaN(58,1) ;
annual_rho = NaN(58,1) ;
annual_ifrac = NaN(58,1) ;
annual_flux = NaN(58,1) ;

for iyear = 1:58
    annual_xkw(iyear) = mean(monthly_xkw(12*iyear-11:12*iyear)) ;
    annual_sol(iyear) = mean(monthly_sol(12*iyear-11:12*iyear)) ;
    annual_dpCO2(iyear) = mean(monthly_dpCO2(12*iyear-11:12*iyear)) ;
    annual_rho(iyear) = mean(monthly_rho(12*iyear-11:12*iyear)) ;
    annual_ifrac(iyear) = mean(monthly_ifrac(12*iyear-11:12*iyear)) ;
    annual_flux(iyear) = mean(monthly_flux(12*iyear-11:12*iyear)) ;
end

% Calculate the trends
x = (1:1:58)' ;
p_xkw = polyfit(x,annual_xkw,1) ;
p_sol = polyfit(x,annual_sol,1) ;
p_dpCO2 = polyfit(x,annual_dpCO2,1) ;
p_rho = polyfit(x,annual_rho,1) ;
p_ifrac = polyfit(x,annual_ifrac,1) ;
p_flux = polyfit(x,annual_flux,1) ;

xkw_sensitivity = dflux_dxkw*p_xkw(1) ;
sol_sensitivity = dflux_dsol*p_sol(1) ;
dpCO2_sensitivity = dflux_dpCO2*p_dpCO2(1) ;
rho_sensitivity = dflux_drho*p_rho(1) ;
ifrac_sensitivity = dflux_difrac*p_ifrac(1) ;

sum_sensitivity = xkw_sensitivity + sol_sensitivity + dpCO2_sensitivity ...
    + rho_sensitivity + ifrac_sensitivity ;

% Plotting
trends = [p_flux(1);sum_sensitivity;xkw_sensitivity;sol_sensitivity;...
    rho_sensitivity;dpCO2_sensitivity;ifrac_sensitivity] ;
figure(34), clf
bar(trends,'FaceColor',[0 0.4470 0.7410])
grid on; box on;
set(gca,'FontSize',10,'YLim',[-22 22])
set(gca,'TickLabelInterpreter','latex','XTickLabel',{'$\Phi^\prime$',...
    '$\sum$',...
    '$\frac{\partial \Phi}{\partial k} k^\prime$',...
    '$\frac{\partial \Phi}{\partial S} S^\prime$',...
    '$\frac{\partial \Phi}{\partial \rho} \rho^\prime$',...
    '$\frac{\partial \Phi}{\partial p} {p}^\prime$',...
    '$\frac{\partial \Phi}{\partial ice} ice^\prime$'})
% ylabel({'Sensitivity (mol/m^2/year^2)',''},'FontSize',12)