# -*- coding: utf-8 -*-
#Copyright (C) 2013 Dumur Étienne

#This program is free software; you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation; either version 2 of the License, or
#(at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License along
#with this program; if not, write to the Free Software Foundation, Inc.,
#51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import scipy.constants as cst
from scipy.special import ellipk, ellipe
import numpy as np

class TL:
	
	def __init__(self, epsilon_r = 11.68, tan_delta = 7e-4, kappa = 3.53e50, w = 19e-6, s = 11.5e-6, t = 100e-9, w_g = 200e-6):
		'''Class allowing the calculation of the parameters of a coplanar waveguide
			Input:
				- epsilon_r (float) : Relative permitivity of the substrat
				- tan_delta (float) : Loss tangent
				- kappa     (float) : Conductivity of the metal layer
				
				- w         (float) : Width of the central line in meter
				- s         (float) : Width of the gap separation in meter
				- t         (float) : Thickness of the metal layer in meter
				- w_g       (float) : Width of the ground plane in meter
		'''
		
		self.epsilon_r = epsilon_r
		self.tan_delta = tan_delta
		self.kappa     = kappa
		
		self.w   = w
		self.s   = s
		self.t   = t
		self.w_g = w_g
		
		self._a   = self.w/2.
		self._b   = self.w/2. + self.s
		self._t_H = self.t/2.
		
		
		self.lambda_0 = 40e-9
	
	def _variable_check(self, f):
		'''Test of which type is the varible send and return numpy.ndarray of the variable'''
		
		if isinstance(f, np.ndarray) :
			return f
		elif isinstance(f, list):
			return np.array(f)
		else:
			return np.array([f])
	
	#################################################################################
	#
	#
	#									geometry parameters
	#
	#
	#################################################################################
	
	def _defined_short_parameter(self):
		self._a   = self.w/2.
		self._b   = self.w/2. + self.s
		self._t_H = self.t/2.
	
	#################################################################################
	#
	#
	#									usefull function
	#
	#
	#################################################################################
	
	def _omega(self, f):
		'''Return the impulsion to a frequency'''
		return 2.*cst.pi*f
	
	
	#################################################################################
	#
	#
	#									Kinetic inductance calculation
	#
	#
	#################################################################################
	def _g(self):
		return (1./( 2*self._k0()**2*ellipk(self._k0())**2 ))*( -np.log(self.t/(4.*self.w)) - (self.w/(self.w + 2.*self.s)) * np.log(self.t/(4.*(self.w + 2.*self.s))) + ((2.*(self.w+self.s))/(self.w + 2.*self.s))*np.log(self.s/(self.w+self.s)) )
	
	def L_k(self):
		return cst.mu_0*self.lambda_0**2*self._g()/(self.t*self.w)
	
	#################################################################################
	#
	#
	#									ki coefficients
	#
	#
	#################################################################################
	
	def _k0(self):
		return self.w / (self.w + 2.*self.s)
	
	def _k1(self):
		return self._k0()*np.sqrt((1. - ((self.w+2.*self.s)/(self.w+2.*self.s+2*self.w_g))**2)/(1-((self.w)/(self.w+2.*self.s+2*self.w_g))**2))
	
	def _k2(self):
		return self._k0()*np.sqrt((1-((self.w + 2.*self.s)/(4.*self.w +2.*self.s))**2 )/( 1 - ((self.w)/(4.*self.w + 2*self.s))**2))
	
	#################################################################################
	#
	#
	#									pci coefficients
	#
	#
	#################################################################################
	
	def _pc0(self):
		return self._b/(2.*self._a*ellipk(np.sqrt(1 - self._k0()**2))**2.)
	
	def _pc1(self):
		return 1. + np.log((8.*np.pi*self._a)/(self._a + self._b)) + (self._a * np.log(self._b/self._a))/(self._a + self._b)
	
	def _pc2(self):
		return self._pc1() - (2.*self._a*ellipk(np.sqrt(1 - self._k0()**2))**2.)/self._b
	
	def _pc3(self):
		return (2*self._b**2*ellipe(np.sqrt(1-self._k0()**2)))/(self._a*(self._b + self._a)*ellipk(np.sqrt(1-self._k0()**2)))
	
	def _pc4(self):
		return ((self._b-self._a)/(self._b+self._a))*(np.log((8.*np.pi*self._a)/(self._a + self._b)) + self._a/self._b)
	
	def _pc5(self):
		return ((self._b-self._a)/(self._b+self._a))*np.log(3)
	
	def _pc6(self):
		return ((self._b-self._a)/(self._b+self._a))*np.log((24.*np.pi*self._b*(self._a+self._b))/((self._b-self._a)**2)) - (self._b*np.log(self._b/self._a))/(self._b+self._a)
	
	#################################################################################
	#
	#
	#									Inductance coefficients
	#
	#
	#################################################################################
	
	def _L_DC(self, w_1, w_2):
		return (cst.mu_0/(8.*np.pi))*((4.*self._g_L(w_1))/w_1**2 + (1./w_2**2)*(self._g_L(w_1 + 2.*self.s) + self._g_L(w_1 + 2*w_2 +2.*self.s) + 2.*self._g_L(w_2) - 2.*self._g_L(w_1 + w_2 + 2.*self.s)) - (4./(w_1*w_2))*(self._g_L(w_1+w_2+self.s) - self._g_L(w_1+self.s) +self._g_L(self.s) - self._g_L(w_2+self.s)))
	
	def _g_L(self, x):
		return (self.t**2/12. - x**2/2.)*np.log(1 + (x/self.t)**2) + (x**4/(12*self.t**2))*np.log(1 + (self.t/x)**2) - ((2.*x*self.t)/3.)*(np.arctan(x/self.t) + (x/self.t)**2*np.arctan(self.t/x))
	
	def _L_1(self):
		return self._L_DC(self.w, (3.*self.w)/2.) - cst.mu_0/(4.*self._F1())
	
	def _L_2(self):
		return np.sqrt(cst.mu_0/(2*self._omega_L2()*self.kappa))*((self._F_lc() + self._F_lg())/(4.*self._F_up(self.t/2.)**2))
	
	def _L_inf(self):
		return cst.mu_0/(4.*self._F_up(self.t/2.))
	
	#################################################################################
	#
	#
	#									F coefficients
	#
	#
	#################################################################################
	
	def _F_lc(self):
		if self._t_H<= self.s/2.:
			A = np.pi*self._b + self._b*np.log((8.*np.pi*self._a)/(self._a + self._b)) - (self._b - self._a)*np.log((self._b-self._a)/(self._b+self._a)) - self._b*np.log((2*self._t_H)/self.s)
			B = self._pc1()*self._pc3() - self._pc2() - self._b*self._pc4()/self._a + self._pc5() + (self._pc2() -self._pc3() + self._b/self._a - 1. - self._pc5())*np.log((2.*self._t_H)/self.s)
			C = self._pc3()*(1.-3.*self._pc1()/2.) + 3.*self._pc1()/2. -2.*self._pc2() + 1. +(3.*self._b*self._pc4())/(2.*self._a) - (self._b*(self._b-self._a))/(self._a*(self._b+self._a)) + (2.*self._pc2() + self._pc1()*(self._pc3() - 1.) - self._b*self._pc4()/self._a)*np.log((2.*self._t_H)/self.s)
			
			return (self._pc0()/self.s)*(A/(self._a+self._b) + self._t_H*B/self.s + (self._t_H/self.s)**2*C)
		else:
			return 1./(2.*self.s) + self._t_H/self.s**2 + (self._pc0()/self.s)*((np.pi*self._b)/(self._a+self._b) +self._pc6()/2. +(1./8.)*(-self._pc1() +self._pc3()*(self._pc1()+2.) -self._b*self._pc4()/self._a -(2.*(self._a**2 + self._b**2))/(self._a*(self._a+self._b))))
	
	def _F_lg(self):
		if self._t_H<= self.s/2.:
			A = np.pi*self._a + self._a*np.log((8.*np.pi*self._b)/(self._b-self._a)) - self._b *np.log((self._b-self._a)/(self._b+self._a)) - self._a*np.log((2*self._t_H)/self.s)
			B = (self._a*self._pc1()*self._pc3())/self._b +(1.-self._a/self._b)*self._pc1() - self._pc2() - self._pc4() - self._pc5() + (self._pc2() - self._a*self._pc3()/self._b +self._a/self._b - 1. +self._pc5())*np.log((2.*self._t_H)/self.s)
			C = ((self._a*self._pc3())/self._b)*(1.-3.*self._pc1()/2.) + (3.*self._a*self._pc1())/(2.*self._b) -2.*self._pc2() +2. - self._a/self._b +3.*self._pc4()/2. - (self._b-self._a)/(self._b+self._a) + (2.*self._pc2() + ((self._a*self._pc1())/self._b)*(self._pc3() - 1.) - self._pc4())*np.log((2.*self._t_H)/self.s)
		
			return (self._pc0()/self.s)*(A/(self._a+self._b) + self._t_H*B/self.s + (self._t_H/self.s)**2*C)
		else:
			return 1./(2.*self.s) + self._t_H/self.s**2 + (self._pc0()/self.s)*((np.pi*self._a)/(self._a+self._b) +self._pc6()/2. +(1./8.)*(-(self._a*self._pc1())/self._b +((self._a*self._pc3())/self._b)*(self._pc1()+2.) - self._pc4() -(2.*(self._a**2 + self._b**2))/(self._b*(self._a+self._b))))
	
	def _F1(self):
		return self._F_up(self.t/2.) + ellipk(self._k2())/ellipk(np.sqrt(1-self._k2()**2)) - ellipk(self._k1())/ellipk(np.sqrt(1-self._k1()**2))
	
	def _F_up(self, t):
		
		if t<= self.s/2. :
			return ellipk(self._k1())/ellipk(np.sqrt(1-self._k1()**2)) + self._pc0()*( (t/self.s)*(self._pc1() - np.log((2.*t)/self.s)) +(t/self.s)*(t/self.s)*(1. - (3.*self._pc2())/2. + self._pc2()*np.log((2.*t)/self.s)))
		else :
			return ellipk(self._k1())/ellipk(np.sqrt(1-self._k1()**2)) + (self._pc0()*(self._pc2() + 2.))/8. + t/self.s
	
	def _F_low(self):
		return ellipk(self._k1())/ellipk(np.sqrt(1 - self._k1()**2))
	
	#################################################################################
	#
	#
	#									omega_Li coefficients
	#
	#
	#################################################################################
	
	def _omega_L0(self):
		return 4./(cst.mu_0*self.kappa*self.t*self.w_g)
	
	def _omega_L1(self):
		return 4./(cst.mu_0*self.kappa*self.t*self.w)
	
	def _omega_L2(self):
		return 18./(cst.mu_0*self.kappa*self.t**2)
	
	#################################################################################
	#
	#
	#									nu_i coefficients
	#
	#
	#################################################################################
	
	def _nu_1(self):
		return np.log((self._L_DC(self.w, self.w_g) - self._L_inf())/self._L_1())/np.log(self._omega_L0()/self._omega_L1())
	
	def _nu_2(self):
		return np.log(self._L_1()/self._L_2())/np.log(self._omega_L1()/self._omega_L2())
	
	#################################################################################
	#
	#
	#									eta_i coefficients
	#
	#
	#################################################################################
	
	def _eta_1(self):
		return (self.w/self.w_g)**4*(self._nu_1()/(4.- self._nu_1()))
	
	def _eta_2(self):
		return (self.w/self.w_g)**2*(self._nu_1()/(4.- self._nu_1()))
	
	def _eta_3(self):
		return (((2.*self.t)/(9*self.w))**3)*((self._nu_2() - 1./2.)/(self._nu_2() + 5./2.))
	
	def _eta_4(self):
		return ((2.*self.t)/(9*self.w))*((self._nu_2() + 1./2.)/(self._nu_2() + 5./2.))
	
	#################################################################################
	#
	#
	#									a_iL coefficients
	#
	#
	#################################################################################
	
	def _a_3L(self):
		return ((self._nu_2() - self._nu_1())*(1. + self._eta_1())*(1. - self._eta_4()) + 4.*self._eta_2() + self._eta_4()*(1. - 3.*self._eta_1()))/((self._nu_1() - self._nu_2())*(1. + self._eta_1())*(1. - self._eta_3()) + 4. -self._eta_3()*(1. - 3.*self._eta_1()))
	
	def _a_2L(self):
		return (1./(1. + self._eta_1()))*( self._a_3L() * (1. - self._eta_3()) - self._eta_2() - self._eta_4() )
	
	def _a_4L(self):
		return -(9./2.)*(self.w/self.t)*(self._eta_4() + self._a_3L()*self._eta_3())
	
	def _a_5L(self):
		return (((2.*self.t)/(9.*self.w))**2)*self._a_3L() + self._a_4L()
	
	def _a_1L(self):
		return self._nu_1()/(4. - self._nu_1()) + self._eta_2()*self._a_2L()
	
	def _a_0L(self):
		return (1. - self._L_inf()/self._L_DC(self.w, self.w_g))*(self._a_1L() + (self.w/self.w_g)**2*self._a_2L())
	
	#################################################################################
	#
	#
	#									omega_ci coefficients
	#
	#
	#################################################################################
	
	def _omega_c1(self):
#		print self.kappa, self.epsilon_r
		return np.sqrt(2.)*(4./(cst.mu_0*self.kappa*self.t*self.w))
	
	def _omega_c2(self):
		return (8./(cst.mu_0*self.kappa))*((self.w + self.t)/(self.w*self.t))**2.
	
	#################################################################################
	#
	#
	#									omega_gi coefficients
	#
	#
	#################################################################################
	
	def _omega_g1(self):
		return 2./(cst.mu_0*self.kappa*self.t*self.w_g)
	
	def _omega_g2(self):
		return (2./(cst.mu_0*self.kappa))*((2*self.w_g + self.t)/(self.w_g*self.t))**2.
	
	#################################################################################
	#
	#
	#									gamma coefficients
	#
	#
	#################################################################################
	
	def _gamma_c(self):
		return (self._omega_c1()/self._omega_c2())**2
	
	def _gamma_g(self):
		return (self._omega_g1()/self._omega_g2())**2
	
	#################################################################################
	#
	#
	#									R_ci coefficients
	#
	#
	#################################################################################
	
	def _R_c0(self):
		return 1./(self.kappa*self.w*self.t)
	
	def _R_c1(self):
		return np.sqrt((self._omega_c2() * cst.mu_0)/(2.*self.kappa))*(self._F_lc()/(4.*self._F_up(self.t/2.)**2.))
	
	#################################################################################
	#
	#
	#									R_gi coefficients
	#
	#
	#################################################################################
	
	def _R_g0(self):
		return 1./(2.*self.kappa*self.w_g*self.t)
	
	def _R_g1(self):
		return np.sqrt((self._omega_g2() * cst.mu_0)/(2.*self.kappa))*(self._F_lg()/(4.*self._F_up(self.t/2.)**2.))
	
	#################################################################################
	#
	#
	#									nu coefficients
	#
	#
	#################################################################################
	
	def _nu_c(self):
		return np.log(self._R_c0()/self._R_c1())/np.log(self._omega_c1()/self._omega_c2())
	
	def _nu_g(self):
		return np.log(self._R_g0()/self._R_g1())/np.log(self._omega_g1()/self._omega_g2())
	
	#################################################################################
	#
	#
	#									a_ic coefficients
	#
	#
	#################################################################################
	
	def _a_4c(self):
		return (self._gamma_c()*self._nu_c() + (1./4.)*(1./2. - self._nu_c())*(4. - self._nu_c()*(1 - self._gamma_c()**2)))/(4. - self._nu_c() - (1./4.)*(1./2. - self._nu_c())*(4. - self._nu_c()*(1 - self._gamma_c()**2)))
	
	def _a_3c(self):
		return (1./4.)*(1./2. - self._nu_c())*(1. + self._a_4c())
	
	def _a_2c(self):
		return (1./self._gamma_c())*(self._a_4c() - self._a_3c())
	
	def _a_1c(self):
		return self._a_2c() + self._gamma_c()*self._a_3c()
	
	#################################################################################
	#
	#
	#									a_ig coefficients
	#
	#
	#################################################################################
	
	def _a_4g(self):
		return (self._gamma_g()*self._nu_g() + (1./4.)*(1./2. - self._nu_g())*(4. - self._nu_g()*(1 - self._gamma_g()**2)))/(4. - self._nu_g() - (1./4.)*(1./2. - self._nu_g())*(4. - self._nu_g()*(1 - self._gamma_g()**2)))
	
	def _a_3g(self):
		return (1./4.)*(1./2. - self._nu_g())*(1. + self._a_4g())
	
	def _a_2g(self):
		return (1./self._gamma_g())*(self._a_4g() - self._a_3g())
	
	def _a_1g(self):
		return self._a_2g() + self._gamma_g()*self._a_3g()
	
	#################################################################################
	#
	#
	#									R coefficients
	#
	#
	#################################################################################
	
	def _Rc(self, f):
		first_condition = np.ma.masked_less_equal(f, self._omega_c1()).mask
		second_condition = np.ma.masked_less_equal(f, self._omega_c2()).mask
		
		if first_condition:
			return self._R_c0()*(1. + self._a_1c()*(self._omega(f)/self._omega_c1())**2)
		elif [~first_condition] and second_condition:
			return self._R_c1()*(self._omega(f)/self._omega_c2())**self._nu_c()*(1. + self._a_2c()*(self._omega_c1()/self._omega(f))**2 + self._a_3c()*(self._omega(f)/self._omega_c2())**2)
		elif [~second_condition]:
			return np.sqrt((self._omega(f)*cst.mu_0)/(2.*self.kappa))*(self._F_lc()/(4.*self._F_up(self.t/2.)**2))*(1. + self._a_4c()*(self._omega_c2()/self._omega(f))**2)
		
	
	def _Rg(self, f):
		first_condition = np.ma.masked_less_equal(f, self._omega_g1()).mask
		second_condition = np.ma.masked_less_equal(f, self._omega_g2()).mask
		
		if first_condition:
			return self._R_g0()*(1. + self._a_1g()*(self._omega(f)/self._omega_g1())**2)
		elif [~first_condition] and second_condition:
			return self._R_g1()*(self._omega(f)/self._omega_g2())**self._nu_g()*(1. + self._a_2g()*(self._omega_g1()/self._omega(f))**2 + self._a_3g()*(self._omega(f)/self._omega_g2())**2)
		elif  [~second_condition]:
			return np.sqrt((self._omega(f)*cst.mu_0)/(2.*self.kappa))*(self._F_lg()/(4.*self._F_up(self.t/2.)**2))*(1. + self._a_4g()*(self._omega_g2()/self._omega(f))**2)
		
	#################################################################################
	#
	#
	#									Final result
	#
	#
	#################################################################################
	
	def L_l(self, f):
		'''Return the length inductance of the transmision line
				- Input :
					- Frequency (float | list | numpy.ndarray) in Hertz
				
				- Output :
					- Length inductance (numpy.ndarray) in Henrys per meter
		'''
		
		self._defined_short_parameter()
		f = self._variable_check(f)
		first_condition = np.ma.masked_less_equal(f, self._omega_L0()).mask
		second_condition = np.ma.masked_less_equal(f, self._omega_L1()).mask
		third_condition = np.ma.masked_less_equal(f, self._omega_L2()).mask
		
		if first_condition:
			return self._L_DC(self.w, self.w_g)*(1. + self._a_0L()*(self._omega(f)/self._omega_L0())**2.)
		elif [~first_condition] and second_condition :
			return self._L_inf() + self._L_1()*(self._omega(f)/self._omega_L1())**self._nu_1()*(1. + self._a_1L()*(self._omega_L0()/self._omega(f))**2. + self._a_2L()*(self._omega(f)/self._omega_L1())**2. )
		elif [~second_condition] and third_condition :
			return self._L_inf() +self._L_2()*(self._omega(f)/self._omega_L2())**self._nu_2()*(1. + self._a_3L()*(self._omega_L1()/self._omega(f))**2. + self._a_4L()*(self._omega(f)/self._omega_L2())**2. )
		elif [~second_condition] :
			return self._L_inf() + np.sqrt(cst.mu_0/(2.*self._omega(f)*self.kappa))*((self._F_lc() + self._F_lg())/(4.*self._F_up(self.t/2.)**2.))*(1. + self._a_5L()*(self._omega_L2()/self._omega(f)))
		
	
	def R_l(self, f):
		'''Return the length resistance of the transmision line
				- Input :
					- Frequency (float | list | numpy.ndarray) in Hertz
				
				- Output :
					- Length resistance (numpy.ndarray) in Ohms per meter
		'''
		
		self._defined_short_parameter()
		f = self._variable_check(f)
		return self._Rc(f) + self._Rg(f)
	
	def C_l(self, f):
		'''Return the length capacitance of the transmision line
				- Input :
					- Frequency (float | list | numpy.ndarray) in Hertz
				
				- Output :
					- Length capacitance (numpy.ndarray) in Farrad per meter
		'''
		
		self._defined_short_parameter()
		f = self._variable_check(f)
		return np.array([2.*cst.epsilon_0*(self._F_up(self.t) + self.epsilon_r*self._F_low())]*len(f))
	
	def G_l(self, f):
		'''Return the length conductance of the transmision line
				- Input :
					- Frequency (float | list | numpy.ndarray) in Hertz
				
				- Output :
					- Length conductance (numpy.ndarray) in Siemens per meter
		'''
		
		self._defined_short_parameter()
		f = self._variable_check(f)
		return 2.*self._omega(f)*cst.epsilon_0*self.epsilon_r*self.tan_delta*self._F_low()
	
	def Z_0(self, f):
		'''Return the norm of the characteristic impedance of the transmision line
				- Input :
					- Frequency (float | list | numpy.ndarray) in Hertz
				
				- Output :
					- Characteristic impedance (numpy.ndarray) in Ohms
		'''
		
		self._defined_short_parameter()
		f = self._variable_check(f)
		temp = np.sqrt((self.R_l(f) + 1j*self._omega(f)*self.L_l(f))/(self.G_l(f) + 1j*self._omega(f)*self.C_l(f)))
		return np.sqrt(temp.real**2 + temp.imag**2)
	
	def gamma(self, f):
		'''Return the gamma coefficient of the transmision line
				- Input :
					- Frequency (float | list | numpy.ndarray) in Hertz
				
				- Output :
					- Gamma coefficient (numpy.ndarray)
		'''
		
		self._defined_short_parameter()
		f = self._variable_check(f)
		return np.sqrt((self.R_l(f) + 1j*self._omega(f)*self.L_l(f))*(self.G_l(f) + 1j*self._omega(f)*self.C_l(f)))
	
	def alpha(self, f):
		'''Return the alpha coefficient of the transmision line
				- Input :
					- Frequency (float | list | numpy.ndarray) in Hertz
				
				- Output :
					- alpha coefficient (numpy.ndarray)
		'''
		return self.gamma(f).real
	
	def beta(self, f):
		'''Return the beta coefficient of the transmision line
				- Input :
					- Frequency (float | list | numpy.ndarray) in Hertz
				
				- Output :
					- Beta coefficient (numpy.ndarray)
		'''
		return self.gamma(f).imag
	
	def velocity(self, f):
		'''Return the velocity of the wave in the coplanar wave guide
				- Input :
					- Frequency (float | list | numpy.ndarray) in Hertz
				
				- Output :
					- Velocity (numpy.ndarray) in unit of c (speed of light)
		'''
		
		self._defined_short_parameter()
		f = self._variable_check(f)
		
		return 1./np.sqrt(self.C_l(f) * self.L_l(f))/cst.c
	
	
	def L_eq_lambda4(self, f, l):
		
		return 8.*l*self.L_l(f)/cst.pi**2.
	
	def C_eq_lambda4(self, f, l):
		
		return l*self.C_l(f)/2.
	
	def R_eq_lambda4(self, f, l):
		
		return self.Z_0(f)/self.alpha(f)/l
	
	def Q_lambda4(self, f, l):
		
		return cst.pi/(4.*self.alpha(f)*l)
	
	def resonance_frequency_lambda4(self, l):
		f = 9e9
		return 1./(2.*cst.pi*np.sqrt(self.L_eq_lambda4(f, l) * self.C_eq_lambda4(f, l)))