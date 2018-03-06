function [ f, df ] = calc_pH_from_DIC_TA ( x, ...
    alkalinity_in, borate_in, dic_in, fluoride_in, k_hbo2_in, k_h2co3_in, ...
    k_h2po4_in, k_h3po4_in, k_hco3_in, k_hf_in, k_hpo4_in, k_hso4_in, ...
    k_oh_in, k_sioh4_in, phosphate_in, silicate_in, sulfate_in )

% This routine expresses the total pH as a function of DIC and constants.
% It is used in the iterative solution for htotal. In the call [[x]] is the
% input value for htotal, f is the calculated value for TA and
% df is the value for dTA_{dhtotal}.
%
% A call which has a value of 1.0e20 for x and includes all
% optional arguments will set the value of the equilibrium constants for
% all subsequent calculations, until the routine is again called in this
% manner.  This allows the routine to be used as a callback function
% within a root finding function, without that function knowing anything
% about these constants, and without them being global variables.
%
% All concentrations passed to this routine in mol.kg^{-1}

persistent alkalinity
persistent boron_total
persistent dic
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


if x == 1.0e20
    alkalinity = alkalinity_in;
    boron_total = borate_in;
    dic = dic_in;
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

x_2 = x * x;
x_3 = x_2 * x;
k_12 = k_h2co3 * k_hco3;
k_12p = k_h3po4 * k_h2po4;
k_123p = k_12p * k_hpo4;
c = 1.0 + sulfate / k_hso4 + fluoride / k_hf;
a = x_3 + k_h3po4 * x_2 + k_12p * x + k_123p;
a2 = a * a;
da = 3.0 * x_2 + 2.0 * k_h3po4 * x + k_12p;
b = x_2 + k_h2co3 * x + k_12;
b2 = b * b;
db = 2.0 * x + k_h2co3;

% Calculate F:
% F = HCO3 + CO3 + Borate + OH + HPO4 + 2 * PO4 + Silicate + HFREE ...
%       + HSO4 + HF + H3PO4 - TA

f = ( k_h2co3 * x + 2.0 * k_12 ) * dic / b ...
    + boron_total / ( 1.0 + x / k_hbo2 ) + k_oh / x ...
    + ( k_12p * x + 2.0 * k_123p - x_3 ) * phosphate / a ...
    + silicate / ( 1.0 + x / k_sioh4 ) ...
    - x / c - sulfate / ( 1.0 + k_hso4 * c / x ) ...
    - fluoride / ( 1.0 + k_hf * c / x ) - alkalinity;

% calculate df=df/dx

df = ( ( b - x * db ) * k_h2co3 - 2.0 * k_12 * db ) * dic / b2 ...
    - boron_total / ( k_hbo2 * ( 1.0 + x / k_hbo2 )^2 ) - k_oh / x_2 ...
    + ( k_12p * ( a - x * da ) - 2.0 * k_123p * da ...
    - x_2 * ( 3.0 * a-x * da ) ) * phosphate / a2 ...
    - silicate / ( k_sioh4 * ( 1.0 + x / k_sioh4 )^2 ) ...
    - 1.0 / c ...
    - sulfate / ( 1.0 + k_hso4 * c / x )^2.0 ...
    * ( k_hso4 * c / x_2 ) ...
    - fluoride / ( 1.0 + k_hf * c / x )^2.0 ...
    * ( k_hf * c / x_2 );

return;