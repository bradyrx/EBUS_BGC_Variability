function c = dic( s, t, pco2, alk, phosphate, silicate, diconly )
% compute dic as a function of pco2 and alk
% alk, po4 and silicate expected in units of µmol.kg^{-1}


%------------------------------------------------------
%---- contstants
co2_chem_tol = 1.0e-12;
co2_ph_high = 10.0;
co2_ph_low = 4.0;

if nargin < 6
    phosphate = 0.7;   % µmol.kg^{-1}
    silicate = 14;     % µmol.kg^{-1}
end


%------------------------------------------------------
%---- sort out argument sizes
args = {'s', 't',  'pco2', 'alk', 'phosphate', 'silicate'};          
numel_args = [numel(s),numel(t),numel(pco2),numel(alk),numel(phosphate),numel(silicate)];
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
if nargin < 7, diconly = false; end

verbose = false;
if N > 400
   verbose = true;
end

%------------------------------------------------------
%---- seawater state and chemistry
rho = sw_dens0( s, t );          % kg.m^{-3}

% _________________________________________________________________________
% calculate co2 equilibrium constants
[ co2eq ] = csys.co2eq_consts( t, s, 1 );
% co2eq.sol is in mol.kg^{-1}.atm^{-1}

c = struct( ...
    't',   t,...
    's',   s,...
    'pco2', pco2, ...
    'alk', alk, ...
    'pH', nan(d), ...
    'h_total', nan(d), ...
    'dic', nan(d), ...
    'co2aq', nan(d), ...
    'hco3', nan(d), ...
    'co3', nan(d), ...
    'fco2', nan(d), ...
    'phosphate', phosphate, ...
    'silicate', silicate, ...
    'rho', rho, ... 
    'co2eq', co2eq );
 
%------------------------------------------------------
%---- units conversion
phosphate = phosphate * 1.0e-6;   % convert: µmol.kg^{-1} to mol.kg^{-1}
silicate  = silicate * 1.0e-6;    % convert: µmol.kg^{-1} to mol.kg^{-1}
alk       = alk * 1.0e-6;         % convert: µmol.kg^{-1} to mol.kg^{-1}
fco2      = pco2 ./ co2eq.fugacity_coeff;
c.fco2    = fco2;
pco2      = pco2 * 1.0e-6;        % convert: µatm to atm

skip = isnan(s(:)) | isnan(t(:)) | isnan(alk(:)) | isnan(pco2(:)) | isnan(phosphate(:)) | isnan(silicate(:));
if all(skip),
    error('ALL NaNs passed to pCO2 routine.');
end
n_notnan = sum(~skip);

%------------------------------------------------------
%---- go
prnt = [1 round((0.1:0.1:1).*n_notnan) ];
guess = 1.e-8;
if verbose, fprintf('pCO2 computation...\n'); end
ii = 1;
timer = tic;

for i = 1:N
    if ~skip(i)
        % compute pH -- send eq-const values to calc_pH routine   
        [ f, df ] = csys.calc_pH_from_pco2_TA ( 1.0e20, ...
                                                alk(i), pco2(i), phosphate(i), silicate(i), ...
                                                co2eq.boron_total(i), co2eq.fluoride(i), co2eq.sulfate(i), ...
                                                co2eq.sol(i), co2eq.k_h2co3(i),co2eq.k_hco3(i), co2eq.k_oh(i),...
                                                co2eq.k_hbo2(i), co2eq.k_h3po4(i),co2eq.k_h2po4(i), co2eq.k_hpo4(i),...
                                                co2eq.k_hf(i), co2eq.k_hso4(i), co2eq.k_sioh4(i) );
    
        % calculate pH
        c.h_total(i) = csys.newton_safe( @csys.calc_pH_from_pco2_TA, 1.e-8, 10.0^(-co2_ph_low), 10.0^(-co2_ph_high), co2_chem_tol );
        if ~isnan(c.h_total(i))
            guess = c.h_total(i);
        end
        
        % Solve carbonate chemistry in surface
        h_pkg = c.h_total(i); % mol kg^{-1}
        
        h2 = h_pkg * h_pkg;
        
        co2aq = co2eq.sol(i) * pco2(i); % mol kg^{-1}
        
        dic = co2aq * ( 1 + co2eq.k_h2co3(i) / h_pkg + co2eq.k_h2co3(i) * co2eq.k_hco3(i) / h2 );
        
        hco3 = dic .* co2eq.k_h2co3(i) .* h_pkg ./ ...
               ( h2 + co2eq.k_h2co3(i) .* h_pkg + co2eq.k_h2co3(i) .* co2eq.k_hco3(i) );
        
        co3 = dic .* co2eq.k_h2co3(i) .* co2eq.k_hco3(i) ./ ...
              ( h2 + co2eq.k_h2co3(i) .* h_pkg + co2eq.k_h2co3(i) .* co2eq.k_hco3(i) );
        
        
        c.co2aq(i) = co2aq * 1e6;
        c.dic(i)   = dic * 1e6;
        c.hco3(i)  = hco3 * 1e6;
        c.co3(i)   = co3 * 1e6;  
        c.pH(i)    = -log10( c.h_total(i)); 
        if verbose
            if any( ii == prnt ), fprintf('%d/%d (tr: %.2f min)\n',ii,n_notnan,(n_notnan-ii)*toc(timer)/60/ii); end
        end

        ii = ii + 1;
    end
end

if verbose
    fprintf('\n')
end


if diconly
    c = c.dic;
end
