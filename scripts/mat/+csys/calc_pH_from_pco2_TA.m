function [ f, df ] = calc_pH_from_pco2_TA ( h, ...
        alkalinity_in,pco2_in, phosphate_in, silicate_in,...
        borate_in, fluoride_in, sulfate_in, ...
        k0_in, k_h2co3_in,k_hco3_in, k_oh_in,...
        k_hbo2_in, k_h3po4_in,k_h2po4_in, k_hpo4_in,...
        k_hf_in, k_hso4_in, k_sioh4_in )

% This routine expresses the total pH as a function of pco2 and constants.
% It is used in the iterative solution for htotal. In the call [[h]] is the
% input value for htotal, f is the calculated value for TA and
% df is the value for dTA_{dhtotal}.
%
% A call which has a value of 1.0e20 for h and includes all
% optional arguments will set the value of the equilibrium constants for
% all subsequent calculations, until the routine is again called in this
% manner.  This allows the routine to be used as a callback function
% within a root finding function, without that function knowing anything
% about these constants, and without them being global variables.
%
% All concentrations passed to this routine in mol.kg^{-1}

persistent alkalinity
persistent boron_total
persistent pco2
persistent k0
persistent fluoride
persistent k_hbo2
persistent k_h2co3
persistent k_h2po4
persistent k_h3po4
persistent k_hco3
persistent k_hf
persistent k_hpo4
persistent k_hso4
persistent k_oh
persistent k_sioh4
persistent phosphate
persistent silicate
persistent sulfate


if h == 1.0e20
    alkalinity = alkalinity_in;
    boron_total = borate_in;
    pco2 = pco2_in;
    k0 = k0_in;
    fluoride = fluoride_in;
    k_hbo2 = k_hbo2_in;
    k_h2co3 = k_h2co3_in;
    k_h2po4 = k_h2po4_in;
    k_h3po4 = k_h3po4_in;
    k_hco3 = k_hco3_in;
    k_hf = k_hf_in;
    k_hpo4 = k_hpo4_in;
    k_hso4 = k_hso4_in;
    k_oh = k_oh_in;
    k_sioh4 = k_sioh4_in;
    phosphate = phosphate_in;
    silicate = silicate_in;
    sulfate = sulfate_in;
    f = 0;
    df = 0;
    return;
end

h_2 = h * h;
h_3 = h_2 * h;
k_01 = k0 * k_h2co3; 
k_012 = k_01 * k_hco3; 
k_12 = k_h2co3 * k_hco3;
k_12p = k_h3po4 * k_h2po4;
k_123p = k_12p * k_hpo4;
c = 1.0 + sulfate / k_hso4 + fluoride / k_hf;
a = h_3 + k_h3po4 * h_2 + k_12p * h + k_123p;
a2 = a * a;
da = 3.0 * h_2 + 2.0 * k_h3po4 * h + k_12p;
b = h_2 + k_h2co3 * h + k_12;
b2 = b * b;
db = 2.0 * h + k_h2co3;

% Calculate F:
% F = HCO3 + CO3 + Borate + OH + HPO4 + 2 * PO4 + Silicate + HFREE ...
%       + HSO4 + HF + H3PO4 - TA

f = k_01 * pco2 / h ...
    + 2 * k_012 * pco2 / h_2 ...
    + boron_total / ( 1.0 + h / k_hbo2 ) + k_oh / h ...
    + ( k_12p * h + 2.0 * k_123p - h_3 ) * phosphate / a ...
    + silicate / ( 1.0 + h / k_sioh4 ) ...
    - h / c - sulfate / ( 1.0 + k_hso4 * c / h ) ...
    - fluoride / ( 1.0 + k_hf * c / h ) - alkalinity;

% calculate df=df/dh

df = - k_01 * pco2 / h_2 ...
    - 4 * k_012 * pco2 / h_3 ...
    - boron_total / ( k_hbo2 * ( 1.0 + h / k_hbo2 )^2 ) ...
    - k_oh / h_2 ...
    + ( k_12p * ( a - h * da ) - 2.0 * k_123p * da ...
    - h_2 * ( 3.0 * a-h * da ) ) * phosphate / a2 ...
    - silicate / ( k_sioh4 * ( 1.0 + h / k_sioh4 )^2 ) ...
    - 1.0 / c ...
    - sulfate / ( 1.0 + k_hso4 * c / h )^2.0 ...
    * ( k_hso4 * c / h_2 ) ...
    - fluoride / ( 1.0 + k_hf * c / h )^2.0 ...
    * ( k_hf * c / h_2 );

return;