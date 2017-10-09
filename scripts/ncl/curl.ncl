; NCL Script for computing wind stress curl over a fixed grid (not curvilinear).
;
; This script cannot handle any NaNs, so first need to convert NaN masks to 0.
; Currently written to take in a file with both TAUX and TAUY already regridded 
; (using CDO)

; BGC-active ensemble members.
ens_str = (/"001","002","009","010","011","012","013","014","015", \
            "016","017","018","019","020","021","022","023","024", \
            "025","026","027","028","029","030","031","032","033", \
            "034","035","101","102","103","104","105"/)

do i = 0, 34 ; Loop through ensemble members
    print("Working on " + ens_str(i) + "...")
    filedir = "/glade/u/home/rbrady/scratch/EBUS_BGC_Variability/CURLZ_monthly/dual_tau/"
    filename = "zeroed.remapped.TAU." + ens_str(i) + ".192001-201512.nc" 
    f = addfile(filedir + filename, "r")
    print("File loaded...")
    u = f->U
    ; Convert to N/m2
    u = u*0.1
    ; Convert to N/m2
    v = f->V
    v = v*0.1
    print("Computing curl...")
    curl = uv2vrF_Wrap(u,v)
    print("Curl computed...")

    ; Output netCDF file.
    filedir = "/glade/u/home/rbrady/scratch/EBUS_BGC_Variability/CURLZ_monthly/"
    filename = "CURLZ." + ens_str(i)+ ".192001-201512.nc"
    ncdf = addfile(filedir + filename, "c")
    curl@long_name = "curl of wind stress"
    curl@units = "N/m3"
    ncdf->curl = curl ;2D
end do
