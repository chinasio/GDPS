 % MakeLinesAirborne.m
% Gets the GPS and Meter input arrays and and using
% input grafic generates data lines which are stored in cell variables
%--------------------------------------------------------
% select the lines
 
if 1==0  % dshow on line plot
online=zeros(1,length(fgrav_plot));    
for j=1:nlin
 head=datenum(startline(j),'dd/mm/yyyy HH:MM:ss.FFF')*24*3600;  
 tail=datenum(endline(j),'dd/mm/yyyy HH:MM:ss.FFF')*24*3600;
  I=find(tgps > head); 
  x=I(1)
  I=find(tgps > tail); 
  y=I(1)
  online(x:y)=1;
end
 scrsz = get(0,'ScreenSize');    
 figure('Position',[100 40 scrsz(3)/1.2 scrsz(4)/1.2]),title('Select lines');
% figure(1),title('Select lines');
ax(1)=subplot(4,1,1);plot(fgrav_plot),title('Gravity'); % was fTCgrav
ax(2)=subplot(4,1,2);plot(fgpsacc),title('Gps acc');
ax(3)=subplot(4,1,3);plot( fdat.laccel),title('Long acc');
ax(4)=subplot(4,1,4);plot(online),title('On the line');
linkaxes([ax(1) ax(2) ax(3) ax(4)],'x');  
else
  scrsz = get(0,'ScreenSize');    
 figure('Position',[100 40 scrsz(3)/1.2 scrsz(4)/1.2]),title('Select lines');
% figure(1),title('Select lines');
ax(1)=subplot(4,1,1);plot(fgrav_plot),title('Gravity'); % was fTCgrav
ADsat=bitget(dat.status,14);
ax(2)=subplot(4,1,2);plot(ADsat),title('Saturation');
ax(3)=subplot(4,1,3);plot( fdat.laccel),title('Long acc');
ax(4)=subplot(4,1,4);plot(fEotvos),title('Eotvos');
linkaxes([ax(1) ax(2) ax(3) ax(4)],'x');
    
 end


 pause
n = inputdlg('how many lines?','Line',1,{'4'});
n = str2num(char(n));
nl=2*n;                   % set the number of lines x2
[pos,g] = ginput(nl); 

id=noflines+1; %
 


for j=0:2:nl-2
  x=round(pos(j+1));
  y=round(pos(j+2));

%  linePgrav{:,id}=fTCgrav(x:y);  % Total grav + GPS corrections 
 lmeterPgrav{:,id}=fgrav(x:y);  % Only meter full field grav with only drift correction
 lmeterg{:,id}=fgrav(x:y)/kfactor-offset;  % meter gravity no Kfactor or offset
 
% lGPStotalacc_OnSensor{:,id}=fGPStotalacc_OnSensor(x:y);
 lfGPS_Corrections{:,id}=fGPS_Corrections(x:y); %GPS corrections= Eotvos + GPS vertical acceleration (using etvos full)
 llong{:,id}=fdat.laccel(x:y);
 lcross{:,id}=fdat.xaccel(x:y);
 lpress{:,id}=fdat.pressure(x:y);
 ltemp{:,id}=fdat.temp(x:y);
 lve{:,id}=fve(x:y);
 llc{:,id}=flc(x:y);
 lxc{:,id}=fxc(x:y);
 lvcc{:,id}=fvcc(x:y);
 lal{:,id}=fal(x:y);
 lax{:,id}=fax(x:y);
 lmeter{:,id}=meterg(x:y);
 lddg{:,id}=ddg(x:y);
 lbeam{:,id}=fdat.beam(x:y);
 
 

 %lbl{:,id}=fbl(x:y);
 %lbx{:,id}=fbx(x:y);
 % lax2{:,id}=fax2(x:y);
 % lal2{:,id}=fal2(x:y);
 % lx2{:,id}=fx2(x:y);
 % ll2{:,id}=fl2(x:y);
 % ldrift{:,id}=fdriftcorr(x:y);
 % lsimlong{:,id}=fsimlong(x:y);
 % lsimcross{:,id}=fsimcross(x:y);
 
 lgpslong{:,id}=fgps_long(x:y);
 lgpslat{:,id}=fgps_lat(x:y);
 lgpsacc{:,id}=fgpsacc(x:y);
 lLevelError{:,id}=fLevelError(x:y);
% lLongTilt{:,id}=fLongTilt(x:y);
 lfgpsacclong{:,id}=fgpsacclong(x:y); % just for tunning thr model
 lfgpsacccross{:,id}=fgpsacccross(x:y);
 lfLatcorr{:,id}=fLatcorr(x:y);
 lfEotvos{:,id}=fEotvos(x:y);
 lgps_height{:,id}=fgps_elipsoidheight(x:y);
 lorto_height{:,id}=fgps_orthoheight(x:y);
%  legm{:,id}=fegm(x:y);
 ltide{:,id}=ftide(x:y);
% lypos{:,id}=ypos(x:y);
 lftiming_Meter{:,id}=ftiming_Meter(x:y); % used for timming controll
 lfTimingGPS{:,id}=fTimingGPS(x:y);         % used for timming controll
 
 lweek{:,id}=dat.GPSWeek(x:y);
 lweeksec{:,id}=dat.WeekSeconds(x:y);
 
 flight{:,id}=Flights(id);
 Lname{:,id}=Lnames(id);
 
 lstatus{:,id}=status(x:y);
 
 id=id+1;
 
 
 
end

close
close

%PlotLinesPosition;
% pause


noflines=id-1;
if(1==0)
 save thelines  llong lcross lfgpsacclong lfgpsacccross lve llc lxc ftide lddg lbeam  lweek lweeksec flight Lname ...
     lpress ltemp  lgpslong lgpslat lgpsacc lmeterPgrav lmeterg lfLatcorr lLevelError ...
     noflines n  lfEotvos lgps_height  lorto_height lftiming_Meter lfTimingGPS  lfGPS_Corrections sampling lstatus;
end
% clear;
% CSigma;





