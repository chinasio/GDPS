function fac=calc_fac(lat,ht)
%Data Inputs
%1.Geodetic latitude: lat
%2.ELLIPSOIDAL height: ht
%Define Ellipsoidal Parameters
a = 6378137; %semi-major axis, WGS-84
g_e = 978032.53359; %equatorial normal gravity, WGS-84
f = 0.00335281066474; %flattening, WGS84
m = 0.00344978650684; %defined as (w^2*a^2*b)/GM, WGS-84
%use GEOCENTRIC latitude, which is defined as: phi
phi = atan(tand(lat).*((1-f).^2));
sphi2 = sin(phi).^2;
c1 = ((2.*g_e)./a);
term1 = (1+f+m-(2.*f.*sphi2)).*ht;
c2 = (3.*g_e./(a.^2));
term2 =ht.^2;
fac = (c1.*term1)-(c2.*term2);


end

