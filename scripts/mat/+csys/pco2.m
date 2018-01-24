function c = pco2( s, t, dic, alk, phosphate, silicate, pco2only )

%------------------------------------------------------
%---- contstants
co2_chem_tol = 1.0e-12;
co2_ph_high = 10.0;
co2_ph_low = 6.0;

if nargin < 6
    phosphate = 0.5;   % µmol.kg^{-1}
    silicate = 10;     % µmol.kg^{-1}
end

%------------------------------------------------------
%---- sort out argument sizes
args       = {'s', 't',  'dic', 'alk', 'phosphate', 'silicate'};          
numel_args = [numel(s),numel(t),numel(dic),numel(alk),numel(phosphate),numel(silicate)];
[N,I] = max(numel_args);

% arguments can be of either numel 1 or N
if ~all(numel_args==N | numel_args==1)
    error('arguments don''t match')
end 

% the size of the biggest argument
d = eval(['size(' args{I} ')']);

% expand or reshape args to match arg(I)
for i = 1:length(args)
    sz  = eval(['size(' args{i} ')']);  
    nel = eval(['numel(' args{i} ')']);  
    if ~all(sz == d)
        % if the number of elements is different, expand
        if nel ~= N
            eval([args{i} ' = ones(d) .* ' args{i} ';'])
        
        % if the shape is different, reshape
        else
            eval([args{i} ' = reshape(' args{i} ',d);'])
        end
    end           
end 
if nargin < 7, pco2only = false; end

verbose = false;
if N > 400
   verbose = true;
end

%------------------------------------------------------
%---- seawater state and chemistry
rho = sw_dens0(s,t); % kg.m^{-3}

%------------------------------------------------------
%---- calculate co2 equilibrium constants
[ co2eq ] = csys.co2eq_consts( t, s, 1 );
% co2eq.sol is in mol.kg^{-1}.atm^{-1}

if pco2only
    c = struct('fco2', nan(d));
else
    c = struct( ...
        't',   t,...
        's',   s,...
        'dic', dic, ...
        'alk', alk, ...
        'pH', nan(d), ...
        'h_total', nan(d), ...
        'co2aq', nan(d), ...
        'hco3', nan(d), ...
        'co3', nan(d), ...
        'pco2', nan(d), ...
        'fco2', nan(d), ...
        'phosphate', phosphate, ...
        'silicate', silicate, ...
        'rho', rho, ... 
        'co2eq', co2eq );
end
    
%------------------------------------------------------
%---- units conversion
phosphate = phosphate * 1.0e-6;   % convert from µmol.kg^{-1} to mol.kg^{-1}
silicate = silicate * 1.0e-6;     % convert from µmol.kg^{-1} to mol.kg^{-1}
alk = alk * 1.0e-6;               % convert from µmol.kg^{-1} to mol.kg^{-1}
dic = dic * 1.0e-6;               % convert from µmol.kg^{-1} to mol.m^{-3}

skip = isnan(s(:)) | isnan(t(:)) | isnan(dic(:)) | isnan(alk(:)) | isnan(phosphate(:)) | isnan(silicate(:));
if all(skip),
    error('ALL NaNs passed to pCO2 routine.');
end
n = numel(dic);
n_notnan = sum(~skip);

prnt = [1 round((0.1:0.1:1).*n_notnan) ];

guess = 1.e-8;
if verbose, fprintf('pCO2 computation...\n'); end
ii = 1;
timer = tic;

for i = 1:n
    if ~skip(i)
        % compute pH -- send eq-const values to calc_pH routine
        [ f, df ] = csys.calc_pH_from_DIC_TA ( 1.0e20, ...
                                               alk(i), ...
                                               co2eq.boron_total(i), dic(i), ...
                                               co2eq.fluoride(i), co2eq.k_hbo2(i), co2eq.k_h2co3(i), co2eq.k_h2po4(i), ...
                                               co2eq.k_h3po4(i), co2eq.k_hco3(i), co2eq.k_hf(i), co2eq.k_hpo4(i), co2eq.k_hso4(i), ...
                                               co2eq.k_oh(i), co2eq.k_sioh4(i), phosphate(i), silicate(i), ...
                                               co2eq.sulfate(i) );
        
        % calculate pH
        h_total = newton_safe( @csys.calc_pH_from_DIC_TA, guess, 10.0^(-co2_ph_low), 10.0^(-co2_ph_high), co2_chem_tol );
        if ~isnan(h_total)
            guess = h_total;
        end
        
        % Solve carbonate chemistry in surface
        h2 = h_total * h_total;

        co2aq = dic(i) * h2 ./ ...
                ( h2 + co2eq.k_h2co3(i) * h_total + co2eq.k_h2co3(i) * co2eq.k_hco3(i) );
        
        c.fco2(i) = co2aq ./ co2eq.sol(i) / 1.0e-6;            % units: µatm

        if ~pco2only
            c.h_total(i) = h_total;
            hco3 = dic(i) .* co2eq.k_h2co3(i) .* h_total ./ ...
                   ( h2 + co2eq.k_h2co3(i) .* h_total + co2eq.k_h2co3(i) .* co2eq.k_hco3(i) );
            
            co3 = dic(i) .* co2eq.k_h2co3(i) .* co2eq.k_hco3(i) ./ ...
                  ( h2 + co2eq.k_h2co3(i) .* h_total + co2eq.k_h2co3(i) .* co2eq.k_hco3(i) );
            
            c.co2aq(i) = co2aq / 1.0e-6;                         % units: µmol.kg^{-1}
            c.hco3(i) = hco3 / 1.0e-6;                           % units: µmol.kg^{-1}
            c.co3(i) = co3 / 1.0e-6;                             % units: µmol.kg^{-1}
            
            c.pco2(i) = c.fco2(i) .* co2eq.fugacity_coeff(i); % units: µatm
            c.pH(i) = -log10( h_total );            
        end

        if verbose
            if any( ii == prnt ), fprintf('%d/%d (tr: %.2f min)\n',ii,n_notnan,(n_notnan-ii)*toc(timer)/60/ii); end
        end
        ii = ii + 1;
    end
       
end

if verbose
    fprintf('\n')
end

if pco2only
    c = c.fco2;
end