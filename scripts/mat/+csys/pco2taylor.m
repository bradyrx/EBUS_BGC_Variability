function OUT = pco2taylor(Xbar,Xnew,dXinc)

%-- constants
sbar = 35;
firstorder        = {'sss','sst','fw','sdic','salk','po4','si'};    
secondorder_auto  = {'sst_sst','sss_sss','dic_dic','alk_alk','po4_po4','si_si'};
secondorder_cross = {'sst_sss','dic_sss','alk_sss','po4_sss','si_sss',...
                    'alk_sst','dic_sst','po4_sst','si_sst',...
                    'alk_dic','po4_dic','si_dic',...
                    'po4_alk','si_alk',...
                    'si_po4'};

%-- return meta data only
if isempty(Xbar) && isempty(Xnew)
    OUT.sss  = 'SSS^\prime';
    OUT.sst  = 'SST^\prime';
    OUT.fw   = 'fw^\prime';
    OUT.dic  = 'DIC^\prime';
    OUT.alk  = 'ALK^\prime';
    OUT.sdic = 'sDIC^\prime';
    OUT.salk = 'sAlk^\prime';
    OUT.po4  = 'PO4^\prime';
    OUT.si   = 'SiO3^\prime';
    
    % second order terms: sum( ( dFdX * dX ) ^ 2 ) 
    OUT.sst_sst = 'SST^\primeSST^\prime';
    OUT.sss_sss = 'SSS^\primeSSS^\prime';
    OUT.dic_dic = 'DIC^\primeDIC^\prime';
    OUT.alk_alk = 'ALK^\primeALK^\prime';
    OUT.po4_po4 = 'PO4^\primePO4^\prime';
    OUT.si_si   = 'SiO3^\primeSiO3^\prime';
    
    OUT.sst_sss = 'SST^\primeSSS^\prime';
    OUT.dic_sss = 'DIC^\primeSSS^\prime';
    OUT.alk_sss = 'ALK^\primeSSS^\prime';
    OUT.po4_sss = 'PO4^\primeSSS^\prime';
    OUT.si_sss  = 'SiO3^\primeSSS^\prime';
    
    OUT.alk_sst = 'ALK^\primeSST^\prime';
    OUT.dic_sst = 'DIC^\primeSST^\prime';
    OUT.po4_sst = 'PO4^\primeSST^\prime';
    OUT.si_sst  = 'SiO3^\primeSST^\prime';
    
    OUT.alk_dic = 'ALK^\primeDIC^\prime';
    OUT.po4_dic = 'PO4^\primeDIC^\prime';
    OUT.si_dic  = 'SiO3^\primeDIC^\prime';
    
    OUT.po4_alk = 'PO4^\primeALK^\prime';
    OUT.si_alk  = 'SiO3^\primeALK^\prime';
    
    OUT.si_po4  = 'SiO3^\primePO4^\prime';
    
    OUT.total      = '\Sigma ((\partialpCO_2/\partialX) X^\prime)';
    OUT.trunc_err  = 'O(X_{i}^\prime^3,X_{i}^\primeX_{j}^\primeX_{k}^\prime)';
    
    OUT.firstorder = 'first order terms';
    OUT.secondorder = 'second order terms';
    return
end

%-- set options for derivative approximation
if nargin < 3
    err_only = false;
    dXinc = 8.6865e-05;
else
    err_only = true;
end


if ~isfield(Xbar,'pco2')
    Xbar.pco2 = csys.pco2(Xbar.SALT,Xbar.TEMP,Xbar.DIC,Xbar.ALK,Xbar.PO4,Xbar.SiO3,1);
end

if ~isfield(Xnew,'pco2')
    Xnew.pco2 = csys.pco2(Xnew.SALT,Xnew.TEMP,Xnew.DIC,Xnew.ALK,Xnew.PO4,Xnew.SiO3,1);
end

flds = {'SALT','TEMP','DIC','ALK','PO4','SiO3','sDIC','sALK','pco2'};
for i = 1:numel(flds)
    f = flds{i};
    dX.(f)   = Xnew.(f) - Xbar.(f);
end

dF = csys.dpco2dx(Xbar, dX, Xbar.pco2, dXinc);

% first order terms: sum( dFdX * dX ) 
dpCO2.sss  = dF.dSALT .* dX.SALT;
dpCO2.sst  = dF.dTEMP .* dX.TEMP;
dpCO2.fw   = dF.dDIC .* ( Xnew.sDIC .* dX.SALT ./ sbar) + dF.dALK .* (Xnew.sALK .* dX.SALT ./ sbar );
dpCO2.dic  = dF.dDIC .* dX.DIC;
dpCO2.alk  = dF.dALK .* dX.ALK;
dpCO2.sdic = dF.dDIC .* (dX.sDIC .* Xbar.SALT ./ sbar);
dpCO2.salk = dF.dALK .* (dX.sALK .* Xbar.SALT ./ sbar);
dpCO2.po4  = dF.dPO4 .* dX.PO4;
dpCO2.si   = dF.dSiO3 .* dX.SiO3;

% second order terms: sum( ( dFdX * dX ) ^ 2 ) 
dpCO2.sst_sst = 0.5 .* dF.dTEMPdTEMP .* dX.TEMP .* dX.TEMP;
dpCO2.sss_sss = 0.5 .* dF.dSALTdSALT .* dX.SALT .* dX.SALT;
dpCO2.dic_dic = 0.5 .* dF.dDICdDIC .* dX.DIC .* dX.DIC;
dpCO2.alk_alk = 0.5 .* dF.dALKdALK .* dX.ALK .* dX.ALK;
dpCO2.po4_po4 = 0.5 .* dF.dALKdALK .* dX.PO4 .* dX.PO4;
dpCO2.si_si   = 0.5 .* dF.dSiO3dSiO3 .* dX.SiO3 .* dX.SiO3;

dpCO2.sst_sss = dF.dTEMPdSALT .* dX.TEMP .* dX.SALT;
dpCO2.dic_sss = dF.dDICdSALT .* dX.DIC .* dX.SALT;
dpCO2.alk_sss = dF.dALKdSALT .* dX.ALK .* dX.SALT;
dpCO2.po4_sss = dF.dPO4dSALT .* dX.PO4 .* dX.SALT;
dpCO2.si_sss  = dF.dSiO3dSALT .* dX.SiO3 .* dX.SALT;

dpCO2.alk_sst = dF.dALKdTEMP .* dX.ALK .* dX.TEMP;
dpCO2.dic_sst = dF.dDICdTEMP .* dX.DIC .* dX.TEMP;
dpCO2.po4_sst = dF.dPO4dTEMP .* dX.PO4 .* dX.TEMP;
dpCO2.si_sst  = dF.dSiO3dTEMP .* dX.SiO3 .* dX.TEMP;

dpCO2.alk_dic = dF.dALKdDIC .* dX.ALK .* dX.DIC;
dpCO2.po4_dic = dF.dPO4dDIC .* dX.PO4 .* dX.DIC;
dpCO2.si_dic  = dF.dSiO3dDIC .* dX.SiO3 .* dX.DIC;

dpCO2.po4_alk = dF.dPO4dALK .* dX.PO4 .* dX.ALK;
dpCO2.si_alk  = dF.dSiO3dALK .* dX.SiO3 .* dX.ALK;

dpCO2.si_po4  = dF.dSiO3dPO4 .* dX.SiO3 .* dX.PO4;

% accumulate totals
dpCO2.firstorder = zeros(size(Xnew.pco2));
for i = 1:numel(firstorder)
    dpCO2.firstorder = dpCO2.firstorder + dpCO2.(firstorder{i});    
end

dpCO2.secondorder_auto = zeros(size(Xnew.pco2));
for i = 1:numel(secondorder_auto)
    dpCO2.secondorder_auto = dpCO2.secondorder_auto + dpCO2.(secondorder_auto{i});    
end

dpCO2.secondorder_cross = zeros(size(Xnew.pco2));
for i = 1:numel(secondorder_cross)
    dpCO2.secondorder_cross = dpCO2.secondorder_cross + dpCO2.(secondorder_cross{i});    
end

dpCO2.secondorder = dpCO2.secondorder_auto + dpCO2.secondorder_cross;
dpCO2.total       = dpCO2.firstorder + dpCO2.secondorder_auto + dpCO2.secondorder_cross;
dpCO2.trunc_err   = dpCO2.total - dX.pco2;
dpCO2.exact       = dX.pco2;

if err_only
    OUT = nansum( dpCO2.trunc_err(:) .^ 2 );
else
    OUT = dpCO2;
end