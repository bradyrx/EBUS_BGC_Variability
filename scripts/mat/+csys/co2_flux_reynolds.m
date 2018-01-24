function flux = co2_flux_reynolds(bar,prime)
    
    flds = fieldnames(bar);

    fice_possible  = {'fice','ECOSYS_IFRAC','IFRAC','ifrac'};
    ka_possible    = {'ka'};
    Dpco2_possible = {'Dpco2','DpCO2'};
    
    pco2atm_possible = {'pco2atm','ATM_CO2'};
    pco2ocn_possible = {'pco2ocn','pCO2SURF'};    
    
    fice  = '';
    ka    = '';
    Dpco2 = '';
    pco2ocn = '';
    pco2atm = '';
    
    for i = 1:length(flds)
        fice_nx = strcmp(fice_possible,flds{i});
        if any(fice_nx)
            fice = fice_possible{fice_nx};
        end
        
        ka_nx = strcmp(ka_possible,flds{i});
        if any(ka_nx)
            ka = ka_possible{ka_nx};
        end
        
        Dpco2_nx = strcmp(Dpco2_possible,flds{i});
        if any(Dpco2_nx)
            Dpco2 = Dpco2_possible{Dpco2_nx};
        end
        
        pco2atm_nx = strcmp(pco2atm_possible,flds{i});
        if any(pco2atm_nx)
            pco2atm = pco2atm_possible{pco2atm_nx};
        end

        pco2ocn_nx = strcmp(pco2ocn_possible,flds{i});
        if any(pco2ocn_nx)
            pco2ocn = pco2ocn_possible{pco2ocn_nx};
        end

    end
    
    if (isempty(fice) || isempty(ka)) || ( isempty(Dpco2) && ( isempty(pco2atm) && isempty(pco2ocn) ) )
        error('field not defined.');
    end
    
   
    if isempty(pco2atm) && isempty(pco2ocn)
        
        flux.fice  = (-1.0) .* prime.(fice) .* bar.(Dpco2) .* bar.(ka);    
        flux.ka    = (1 - bar.(fice)) .* prime.(ka) .* bar.(Dpco2);
        flux.Dpco2 = (1 - bar.(fice)) .* bar.(ka) .* prime.(Dpco2);
        
        flux.ficeka_cov    = (-1.0) .* prime.(fice) .* prime.(ka) .* bar.(Dpco2);
        flux.ficeDpco2_cov = (-1.0) .* prime.(fice) .* bar.(ka) .* prime.(Dpco2);
        flux.kaDpco2_cov   = (1 - bar.(fice)) .* prime.(ka) .* prime.(Dpco2);
               
        flux.triple_cov    = (-1.0) .* prime.(fice) .* prime.(ka) .* prime.(Dpco2);
        
        flds = fieldnames(flux);
        flux.total = 0;
        for i = 1:numel(flds)
            f = flds{i};
            flux.total = flux.total + flux.(f);    
        end
                
    else      
        flux.fice          = (-1.0) .* prime.(fice) .* bar.(ka) .* ( bar.(pco2atm) - bar.(pco2ocn) );
        flux.ka            = ( 1 - bar.(fice) ) .* prime.(ka) .* ( bar.(pco2atm) - bar.(pco2ocn) );
        flux.pco2atm       = ( 1 - bar.(fice) ) .* bar.(ka) .* prime.(pco2atm);
        flux.pco2ocn       = (-1.0) .* ( 1 - bar.(fice) ) .* bar.(ka) .* prime.(pco2ocn);
       
        flux.ficeka_cov    = (-1.0) .* prime.(fice) .* prime.(ka) .* ( bar.(pco2atm) - bar.(pco2ocn) );
        flux.ficeatm_cov   = (-1.0) .* (prime.(fice)) .* bar.(ka) .* prime.(pco2atm);
        flux.ficeocn_cov   = (prime.(fice)) .* bar.(ka) .* prime.(pco2ocn);
       
        flux.kaatm_cov     = ( 1 - bar.(fice) ) .* prime.(ka) .* prime.(pco2atm);
        flux.kaocn_cov     = (-1.0) .* ( 1 - bar.(fice) ) .* prime.(ka) .* prime.(pco2ocn);

        flux.ficekaatm_cov = (-1.0) .* prime.(pco2atm) .* (prime.(fice)) .* (prime.(ka));
        flux.ficekaocn_cov = prime.(pco2ocn) .* (prime.(fice)) .* (prime.(ka));
        
        flds = fieldnames(flux);
        flux.total = 0;
        for i = 1:numel(flds)
            f = flds{i};
            flux.total = flux.total + flux.(f);    
        end  
        
        flux.ficeka_bar = (-1.0) .* ( 1 - bar.(fice) ) .* bar.(ka);        
        flux.Dpco2     = (1 - bar.(fice)) .* bar.(ka) .* ( prime.(pco2atm) - prime.(pco2ocn));    
        
    end
    
    flux.long_name.fice    = 'f_{ice}^\prime';
    flux.long_name.ka      = '(k\alpha)^\prime';
    flux.long_name.pco2atm = '(pCO_2^{atm})^\prime';
    flux.long_name.pco2ocn = '(pCO_2^{ocn})^\prime';
    flux.long_name.Dpco2   = '(\DeltapCO_2)^\prime';

    flux.long_name.ficeka_cov    = 'f_{ice}^\prime(k\alpha)^\prime';
    flux.long_name.ficeatm_cov   = 'f_{ice}^\prime(pCO_2^{atm})^\prime';    
    flux.long_name.ficeocn_cov   = 'f_{ice}^\prime(pCO_2^{ocn})^\prime';    
        
    flux.long_name.kaatm_cov     = '(k\alpha)^\prime(pCO_2^{atm})^\prime';    
    flux.long_name.kaocn_cov     = '(k\alpha)^\prime(pCO_2^{ocn})^\prime';    
      
    flux.long_name.ficekaatm_cov     = 'f_{ice}^\prime(k\alpha)^\prime(pCO_2^{atm})^\prime';    
    flux.long_name.ficekaocn_cov     = 'f_{ice}^\prime(k\alpha)^\prime(pCO_2^{ocn})^\prime';    
    
    flux.long_name.total             = '(F_{CO_2})^\prime';
    


    
