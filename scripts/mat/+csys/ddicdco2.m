function [ dDICdCO2 ] = ddicdco2( s, t, dic, co2, pH)
% [ dDICdCO2 ] = ddicdco2( s, t, dic, co2, pH)
% compute the partial derivative of DIC wrt CO2
%
% input arguments:
% s:    salinity
% t:    temperature (°C)
% dic:  dissolved inorganic carbon (mok kg^{-1})
% co2:  dissolved co2 (mok kg^{-1})
% pH:   pH
%
% output arguments:
% dDICdCO2: partial derivative of DIC wrt CO2 (unitless)
%
% see Zeebe and Wolf-Gladrow (2001), pg 78
%
% Matthew Long, NCAR 2013

%-- get equilibrium constants
eq = csys.co2eq_consts( t, s, 1 );
k1 = eq.k_h2co3;
k2 = eq.k_hco3;
kb = eq.k_hbo2;
bt = eq.boron_total;
kw = eq.k_oh;
clear eq

%-- preliminaries
h = 10 .^ (-pH);
h2 = h .* h;
h3 = h .* h .* h;
k1k2 = k1 .* k2;
kb_p_h_sq = ( kb + h ) .^ 2;

%-- dDIC/d[CO2], pH = constant
Ds = 1 + k1 ./ h + k1k2 ./ h2;

%-- dDIC/d[H+], [CO2] = constant
Dh = -co2 .* ( k1 ./ h2 + 2 .* k1k2 ./ h3 );

%-- dAlk/d[CO2], pH = constant
As = k1 ./ h + 2 .* k1k2 ./ h2; 

%-- dAlk/d[H+], [CO2] = constant
Ah = -co2 .* ( k1 ./ h2 + 4 .* k1k2 ./ h3 ) ...
    - kb .* bt ./ kb_p_h_sq ...
    - kw  ./ h2 ...
    - 1;

%-- the result
dDICdCO2 = Ds - Dh .* As ./ Ah;
