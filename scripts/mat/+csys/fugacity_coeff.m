function [ fugacity_coeff ] = calc_fugacity_coeff( T )

TK = T + 273.15;
TK2 = TK .* TK;
TK3 = TK2 .* TK;
p = 101325;
B = ( -1636.75 + 12.0408 .* TK - 3.27957e-2 .* TK2 + 3.16528e-5 .* TK3 );
B = B .* 10 ^ -6;
d = ( 57.7 - 0.118 .* TK ) .* 10 ^ -6;
R = 8.314; % J K^{-1} mol^{-1}
fugacity_coeff = exp( p .* ( B + 2 .* d ) ./ ( R .* TK ) );

return;