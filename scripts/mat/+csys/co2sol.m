function co2_sol = co2sol(s,t,form)

% Temperature is expected in degrees C, salinity in parts per thousand.
    
    ZERO_C_IN_KELVIN = 273.15;
    if nargin < 3, form = 'fugacity'; end
    
    switch form
        case 'fugacity'
            a = [-162.8301, 218.2968, 90.9241, -1.47696];
            b = [ 0.025695, -0.025225, 0.0049867 ];
            
            t = ( t + ZERO_C_IN_KELVIN ) .* 0.01;
            t_sq = t .* t;
            t_inv = 1.0 ./ t;
            log_t = log( t );
            d0 = b(3) .* t_sq + b(2) .* t + b(1);
            
            
            % compute CO2 solubility in mol.kg^{-1}.atm^{-1}
            co2_sol = exp( a(1) + a(2) .* t_inv + a(3) .* log_t + ...
                a(4) .* t_sq + d0 .* s );
            
        case 'weiss74'
            
            % The result is in mol.kg^{-1}.atm^{-1}
            t_kel = t + ZERO_C_IN_KELVIN;
            co2_sol = exp( ...
                9345.17 ./ t_kel - 60.2409 + 23.3585 .* log( t_kel ./ 100 )...
                + s .* ( ...
                0.023517 - 0.00023656 .* t_kel + 0.0047036 .* ( t_kel ./ 100 ) .^ 2 ...
                ) );
    end
    % convert to mol.kg^{-1}.µatm^{-1}
    co2_sol = co2_sol .* 1.0e-6;
    