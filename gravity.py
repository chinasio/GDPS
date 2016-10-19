# gravity.py module

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from ConfigParser import SafeConfigParser
import datetime
import os

class Gravity:
	# TO DO: Setup exceptions for this class.

	# Class attributes

	# Semi-major axis
	_a = np.float64(6378137) # m

	# Semi-minor axis
	_b = np.float64(6356752.3141) # m

	# Flattening
	_f = (_a - _b) / _a

	# Earth rate of rotation
	_w = np.float64(7292115e-11) # rad/s

	# Equatorial gravity
	_gE = np.float64(9.7803267715) # m/s^2

	# Polar gravity
	_gP = np.float64(9.8321863685) # m/s^2

	# Eccentricity squared
	_e2 = np.float64(0.00669438002290)

	_mGal = np.float64(10e-5) # 1 mGal = 10^-5 m/s^2

	_zls_file_format = {'line_name':10, 'gravity':8, 'spring_tension':8, \
		'cross_coupling':7, 'raw_beam':8, 'vcc':8, 'al':8, 'ax':8, 've2':8, 'ax2':8, \
		'xacc2':8, 'lacc2':8, 'xacc':8, 'lacc':8, 'par_port':8, 'platform_per':6}

	def __init__(self):

		# Conversion and calibration factors
		self.eD = np.float64(1.11585e5) # ?
		self.nD = np.float64(1.11369e5) # ?

		self.meter_model = None
		self.k_factor = None
		self.pre_static_reading = None
		self.post_static_reading = None
		self.gravity_tie = None

		# legacy
		self.time_shift = None
		self.filter_length = None
		self.filter_type = None

	################################

	def read_meter_config(self, filepath):
		errors = []

		parser = SafeConfigParser()

		try:
			parser.read(filename)

		except OSError as why:
			errors.append(str(why))

		if not parser.has_section('Sensor'):
			print "Error: DGS config file missing Sensor section."
			return

		self.meter_model = parser.get('Sensor', 'Meter')
		self.k_factor = parser.get('Sensor', 'kfactor')

		# legacy
		self.time_shift = parser.get('Sensor', 'timeshift')
		self.filter_length = parser.get('Sensor', 'filtertime') # seconds
		self.filter_type = parser.get('Sensor', 'filtype')

		if not parser.has_section('Survey'):
			print "Error: DGS config file missing Survey section."
			return

		self.pre_static_reading = parser.get('Survey', 'PreStill')
		self.post_static_reading = parser.get('Survey', 'PostStill')
		self.gravity_tie = parser.get('Survey', 'TieGravity')

		if errors:
			raise Error(errors)

	def read_ZLS_format_file(self, filepath):
		col_names = ['line_name', 'year', 'day', 'hour', 'minute', 'second',\
			'gravity', 'spring_tension', 'cross_coupling', 'raw_beam', 'vcc', \
			'al', 'ax', 've2', 'ax2', 'xacc2', 'lacc2', 'xacc', 'lacc', \
			'par_port', 'platform_period']

		col_subset = ['gravity', 'spring_tension', 'cross_coupling', \
			'raw_beam', 'vcc', 'al', 'ax', 've2', 'ax2', 'xacc2', 'lacc2', \
			'xacc', 'lacc', 'par_port', 'platform_period']

		col_widths = [10, 4, 3, 2, 2, 2, 8, 8, 7, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 6]

		time_columns = ['year','day','hour','minute','second']

		df = pd.read_fwf(filepath, widths=col_widths, names=col_names)

		day_fmt = lambda x: '{:03d}'.format(x)
		time_fmt = lambda x: '{:02d}'.format(x)

		t = df['year'].map(str) + df['day'].map(day_fmt) + \
			df['hour'].map(time_fmt) + df['minute'].map(time_fmt) + \
			df['second'].map(time_fmt)

		df.index = pd.to_datetime(t, format='%Y%j%H%M%S')

		return df

	def import_ZLS_format_data(self, filepath, begin_time=None, end_time=None):
		# list files in directory
		# if begin_time and/or end_time are specified, filter files
		# read each file and concatenate the resulting dataframes
		print "import_data_ZLS_format"

	def import_DGS_format_data(self, filepath, filterdelay):
		# TO DO: Evaluate whether to apply filter delay here.
		# TO DO: Is filter delay specified in meter config?

		# Read data
		df = pd.read_csv(filepath)

		# Label columns
		df.columns = ['QC_gravity','Gravity','Long_accel', 'Cross_accel', 'Beam', \
		'Sensor_temp', 'Status', 'Checksum', 'Pressure', 'E_temp', 'VE', 'VCC', 'AL', \
		'AX', 'Latitude', 'Longitude', 'Speed', 'Heading', 'VMOND', 'Year', 'Month', \
		'Day', 'Hours', 'Minutes', 'Seconds']

		format1 = lambda x: '{:05.2f}'.format(x)
		format2 = lambda x: '{:02d}'.format(x)

		# Index data frame by datetime
		time = df['Hours'].map(format2) + ":" + df['Minutes'].map(format2) + \
		":" + df['Seconds'].map(format1)

		date = df['Month'].map(format2) + "-" + df['Day'].map(format2) + "-" + \
		df['Year'].map(str)

		# Index by datetime
		df.index =  pd.to_datetime(date + " " + time)

		# Determine time interval
		seconds = df['Seconds']
		dt = seconds[1] - seconds[0]

		# Filter delay in seconds
		delay = filterdelay * dt

		# print "-> Detected %0.3f second time interval." % dt
		# print "-> Using filter delay of %d samples (%0.3f s)." % (filterdelay, delay)

		# Apply filter delay
		df.index = df.index.shift(-delay, freq='S')

		return df

	def import_pos(self, filename, interval=0):

		print "Importing trajectory data from %s." % filename

		df = pd.read_csv(filename)

		# Index by datetime
		df.index = pd.to_datetime(df['GPS Date'] + " " + df['GPS Time'])

		# Shift from GPS to UTC
		df.index = df.index.shift(-16, freq='S')

		# Check time interval
		# 	interval = 0 -> auto
		#	interval != 0 -> manual

		if interval == 0:
			dt = (df.index[1] - df.index[0]).seconds
		else:
			dt = interval

		# Relabel columns
		df.columns = ['Date UTC','Time UTC','Proc Lat', 'Proc Lon', 'Proc Ortho Hgt', \
		'Proc Ell Ht', 'Num Sats', 'PDOP']

		print "-> Detected %0.3f second time interval." % dt

		return df

	################################

	def join_grav_pos(self, df1, df2):

		print "Combining data sets."

		# Add position data to main dataframe
		df = pd.concat([df1, df2[df2.columns[2:]]], axis=1, join_axes=[df1.index])

		# Drop rows where there is no position data
		df = df[pd.notnull(df['Proc Lat'])]

		return df

	################################

	def filter_gravity(self, df, window):

		print "Filtering gravity with a window of %d seconds." % window

		# Determine time interval
		dt = (df.index[1] - df.index[0]).seconds

		# Filter window in samples
		filterwindow = window / dt

		# Filter with moving average
		fieldname = 'Corr Gravity Filtered ' + str(window)
		df[fieldname] = pd.rolling_mean(df['Corr Gravity'], filterwindow)\

		return df

	################################

	def plot_grav_qc(self, df, lines):

		# setup pdf
		pp = PdfPages('multipage.pdf')

		# iterate through rows
		for index, row in lines.iterrows():

			lineID = row['Line_ID']
			startTime = row['Start_Time']
			endTime = row['End_Time']

			print lineID

			# extract subsets
			subset = df[pd.to_datetime(startTime) : pd.to_datetime(endTime)]

			statFormat = lambda x: '%15.2f' % x

			# compute statistics
			sensorMean = statFormat(subset['Gravity'].mean())
			sensorMin = statFormat(subset['Gravity'].min())
			sensorMax = statFormat(subset['Gravity'].max())
			sensorStd = statFormat(subset['Gravity'].std())

			longAccelMean = statFormat(subset['Long_accel'].mean())
			longAccelMin = statFormat(subset['Long_accel'].min())
			longAccelMax = statFormat(subset['Long_accel'].max())
			longAccelStd = statFormat(subset['Long_accel'].std())

			crossAccelMean = statFormat(subset['Cross_accel'].mean())
			crossAccelMin = statFormat(subset['Cross_accel'].min())
			crossAccelMax = statFormat(subset['Cross_accel'].max())
			crossAccelStd = statFormat(subset['Cross_accel'].std())

			plt.rc('figure', figsize=(11,8.5))

			fig1 = plt.figure()

			fig1.text(0.02,0.02,startTime + " - " + endTime)
			fig1.text(0.75,0.02,"Line ID: " + lineID)

			x = subset.index
			xLabels = (subset['Time'].tolist())[::120]

			ax1 = fig1.add_subplot(311)
			ax1.plot(x, subset['Gravity'])
			ax1.grid(True)
			ax1.set_title('Sensor', fontsize=12)
			ax1.set_xticks(x[::120])
			ax1.set_xticklabels(xLabels)
			ax1.tick_params(axis='both', which='major', labelsize=8, right='off', top='off', \
			bottom='off', left='off')
			ax1.set_xlim(x.min(), x.max())
			#ax1.set_ylim(-20000, 20000)
			ax1.set_ylabel('mGal', fontsize=10)

			ax2 = fig1.add_subplot(312)
			ax2.plot(x, subset['Long_accel'])
			ax2.grid(True)
			ax2.set_title('Long accel', fontsize=12)
			ax2.set_xticks(x[::120])
			ax2.set_xticklabels(xLabels)
			ax2.tick_params(axis='both', which='major', labelsize=8, right='off', top='off', \
			bottom='off', left='off')
			ax2.set_xlim(x.min(), x.max())
			ax2.set_ylabel('Gal', fontsize=10)

			ax3 = fig1.add_subplot(313)
			ax3.plot(x, subset['Cross_accel'])
			ax3.grid(True)
			ax3.set_title('Cross accel', fontsize=12)
			ax3.set_xticks(x[::120])
			ax3.set_xticklabels(xLabels)
			ax3.tick_params(axis='both', which='major', labelsize=8, right='off', top='off', \
			bottom='off', left='off')
			ax3.set_xlim(x.min(), x.max())
			ax3.set_ylabel('Gal', fontsize=10)
			ax3.set_xlabel('Time (UTC)', fontsize=10)

			fig1.subplots_adjust(hspace=.5)

			fig1.savefig(pp, format='pdf')
			plt.close()

			############################# histograms #############################
			fig2 = plt.figure()

			fig2.text(0.02,0.02,startTime + " - " + endTime)
			fig2.text(0.75,0.02,"Line ID: " + lineID)

			ax1 = fig2.add_subplot(311)
			subset['Gravity'].hist(bins=100)
			ax1.set_title('Sensor', fontsize=12)
			ax1.tick_params(axis='both', which='major', labelsize=8, right='off', top='off', \
			bottom='off', left='off')
			ax1.set_xlabel('mGal', fontsize=10)

			ax1.text(0.02,0.9,'Mean: ' + sensorMean + '\nMin: ' + sensorMin + \
			'\nMax: ' + sensorMax + \
			'\nStd: ' + sensorStd, \
			ha='left', va='top', transform=ax1.transAxes, fontsize=10, bbox=dict(facecolor='white', alpha=1))

			ax2 = fig2.add_subplot(312)
			subset['Long_accel'].hist(bins=100)
			ax2.set_title('Long accel', fontsize=12)
			ax2.tick_params(axis='both', which='major', labelsize=8, right='off', top='off', \
			bottom='off', left='off')
			ax2.set_xlabel('Gal', fontsize=10)

			ax2.text(0.02,0.9,'Mean: ' + longAccelMean + '\nMin: ' + longAccelMin + \
			'\nMax: ' + longAccelMax + \
			'\nStd: ' + longAccelStd, \
			ha='left', va='top', transform=ax2.transAxes, fontsize=10, bbox=dict(facecolor='white', alpha=1))

			ax3 = fig2.add_subplot(313)
			subset['Cross_accel'].hist(bins=100)
			ax3.set_title('Cross accel', fontsize=12)
			ax3.tick_params(axis='both', which='major', labelsize=8, right='off', top='off', \
			bottom='off', left='off')
			ax3.set_xlabel('Gal', fontsize=10)

			ax3.text(0.02,0.9,'Mean: ' + crossAccelMean + '\nMin: ' + crossAccelMin + \
			'\nMax: ' + crossAccelMax + \
			'\nStd: ' + crossAccelStd, \
			ha='left', va='top', transform=ax3.transAxes, fontsize=10, bbox=dict(facecolor='white', alpha=1))

			fig2.subplots_adjust(hspace=.5)

			fig2.savefig(pp, format='pdf')
			plt.close()

		pp.close()

	################################

	def lever_arm_correction(self, lat, lon, height, pitch, roll, heading, dx, dy, dz):
		# Returns corrected latitude, longitude, and height

		dlam = (dl*sin(radians(heading)) + dx*cos(radians(heading))) / (_eD*cos(lat))
		dphi = (dl*cos(radians(heading)) - dx*sin(radians(heading))) / _nD
		dH = dh + dl*sin(radians(pitch)) + dx*sin(radians(roll))

		lam = lon + dlam
		phi = lat + dphi
		H = height + dH

		# (return what?)

	################################

	def eotvos_correction(self, lat, lon, height):

		# Radius of curvature of equatorial meridian
		CN = _a / (np.sqrt(1 - _e2 * (np.sin(np.deg2rad(lat)))**2))

		# Radius of curvature of prime meridian
		CM = a * (1 - _e2) / ((1 - _e2 * (np.sin(np.deg2rad(lat)))**2)**(3/2))

		# Easting velocity
		VE = (CN + height)*np.cos(np.deg2rad(lat))*np.gradient(lon)

		# Northing velocity
		VN = (CM + height)*np.gradient(lat)

		eotvos = (VN**2 / _a) * (1 - height / _a + _f * (2 - 3 * (np.sin(np.deg2rad(lat)))**2)) + \
		(VE**2 / _a) * (1 - height/_a - _f * (np.sin(np.deg2rad(lat)))**2) + \
		2 * w * VE * np.cos(np.deg2rad(lat))

		return eotvos * _mGal

	################################

	def lat_correction(self, lat):
		return -9.7803267715 * ((1 + 0.00193185138639*(np.sin(np.deg2rad(lat)))**2) \
		/ np.sqrt(1 - 0.00669437999013*(np.sin(np.deg2rad(lat)))**2)) * _mGal

	################################

	def free_air_correction(self, height):
		return 0.3086 * height * _mGal

	################################

	def vert_accel_correction(self, height):
	# From SciPy.org documentation:
	# 	"The gradient is computed using second order accurate central differences in the
	#	 interior and either first differences or second order accurate one-sides
	#	 (forward or backwards) differences at the boundaries. The returned gradient hence
	#	 has the same shape as the input array."

		return pd.Series(np.gradient(np.gradient(height)), index=height.index) * _mGal
