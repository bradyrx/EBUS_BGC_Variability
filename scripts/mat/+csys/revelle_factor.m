function [ rf ] = revelle_factor( s, t, dic, co2, pH, gamma )
% gamma is the rain ratio paramter,
% see Zeebe and Wolf-Gladrow, pg 78
if nargin < 6, gamma = 0; end

eq = csys.co2eq_consts( t, s, 1 );
h = 10 .^ (-pH);
h2 = h .* h;
h3 = h .* h .* h;
k1 = eq.k_h2co3;
k2 = eq.k_hco3;
k1k2 = k1 .* k2;
kb = eq.k_hbo2;
bt = eq.boron_total;
kb_p_h_sq = ( kb + h ) .^ 2;
kw = eq.k_oh;

Ds = 1 + k1 ./ h + k1k2 ./ h2;

Dh = -co2 .* ( k1 ./ h2 + 2 .* k1k2 ./ h3 );

As = k1 ./ h + 2 .* k1k2 ./ h2; 

Ah = -co2 .* ( k1 ./ h2 + 4 .* k1k2 ./ h3 ) ...
    - kb .* bt ./ kb_p_h_sq ...
    - kw  ./ h2 ...
    - 1;

% dhdco2 = -As .* ( Ah .^ (-1) );
% ddicdco2 = Ds - Dh .* As ./ Ah;
% 
% rf0 = ( ddicdco2 .* co2 ./ dic ) .^ -1;

d = Dh .* As - Ds .* Ah;
c0 = -( dic ./ co2 ) .* ( Ah ./ d );
c1 =  ( dic ./ co2 ) .* ( 2 .* Dh ./ d );

rf = c0 + gamma .* c1;
