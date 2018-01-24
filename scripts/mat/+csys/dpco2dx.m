function dF = dpco2dx(Xbar, dX, F, dXinc)

%-----------------------------------------------------------------
%---- check inputs
flds = {'SALT','TEMP','DIC','ALK','PO4','SiO3'};

xbar_flds   = fieldnames(Xbar);
dx_flds = fieldnames(dX);
do_second_order = false;

%-- require xbar to have all field
%   require dX to have all fields to compute second order terms
for i = 1:numel(flds)
    if ~any(strcmp(xbar_flds,flds{i}))
        error('%s is missing from Xbar fields.',flds{i});
    end
    
    if ~any(strcmp(dx_flds,flds{i}))
        do_second_order = false;
    end
end

%-- eliminate irrelevant fields from Xbar
for i = 1:numel(xbar_flds)
    if ~any(strcmp(flds,xbar_flds{i}))
        Xbar = rmfield(Xbar,xbar_flds{i});
    end
end

%-- eliminate irrelevant fields from dX
for i = 1:numel(dx_flds)
    if ~any(strcmp(flds,dx_flds{i}))
        dX = rmfield(dX,dx_flds{i});
    end
end

%-- compute value of the function at initial state (if not supplied)
if nargin < 3 || isempty(F)
    F = csys.pco2(Xbar.SALT,Xbar.TEMP,Xbar.DIC,Xbar.ALK,Xbar.PO4,Xbar.SiO3,1);
    dF.pco2_bar = F;
end

%-- dXinc
if nargin < 4 || isempty(dXinc)
    dXinc = 1e-4;
end

%-----------------------------------------------------------------
%---- define dX with same sign and input, but small increment
for i = 1:numel(flds)
    fi = flds{i};
    dX.(fi) = sign( dX.(fi) ) .* dXinc .* Xbar.(fi);
end

%-----------------------------------------------------------------
%---- compute derivatives
for i = 1:numel(flds)     

    %-- fields
    fi = flds{i};
    deriv = ['d' fi];

    %-- evaluate function at perturbed condition dX(i)  
    p = Xbar;   
    p.(fi) = p.(fi) + dX.(fi);
    F_at_dXi = csys.pco2(p.SALT,p.TEMP,p.DIC,p.ALK,p.PO4,p.SiO3,1);
    
    %-- compute derivatives
    dF.(deriv) = F_at_dXi - F;
    dF.(deriv)(dX.(fi) ~= 0) = dF.(deriv)(dX.(fi) ~= 0) ./ dX.(fi)(dX.(fi) ~= 0);
    
    %-- second order terms?
    for j = 1:i
        
        %-- fields
        fj = flds{j};           
        deriv = ['d' fi 'd' fj];
        
        if do_second_order
            %-- evaluate at perturbed conditions dX(j)            
            p = Xbar;
            p.(fj) = p.(fj) + dX.(fj);
            F_at_dXj = csys.pco2(p.SALT,p.TEMP,p.DIC,p.ALK,p.PO4,p.SiO3,1);

            %-- evaluate at perturbed conditions dX(i)dX(j)
            p.(fi) = p.(fi) + dX.(fi);
            F_at_dXidXj = csys.pco2(p.SALT,p.TEMP,p.DIC,p.ALK,p.PO4,p.SiO3,1);
            
            %-- compute derivatives            
            dF.(deriv) = (F_at_dXidXj - F_at_dXj) - (F_at_dXi - F);           
            dF.(deriv)(dX.(fi) ~= 0) = dF.(deriv)(dX.(fi) ~= 0) ./ dX.(fi)(dX.(fi) ~= 0);            
            dF.(deriv)(dX.(fj) ~= 0) = dF.(deriv)(dX.(fj) ~= 0) ./ dX.(fj)(dX.(fj) ~= 0);            
        else
            dF.(deriv)               = nan(size(F));
        end        
    end   
end


