200 t 2000 0				/enable y2000 formats
H71 3 1 3			    	/use new hypoinverse station format
DIS 4 150 .5 3            		/Main Distance weighting
RMS 4 0.5 1.5 3        			/Residual weighting
ERR .5
DAM 7 20 0.5 0.9 0.012 0.02 0.6 75 500
*POS 1.73
MIN 6                  			/min number of stations

*WET 1. .5 .2 .1       			/weighting by pick quality
MAG 1 T 1 1                           /Set up magnitude calculation using specified settings
PRE 3, 1 4 0.0 9.0, 2 4 0.0 9.0, 3 4 0.0 9.0        /preferred magnitude settings


* OUTPUT
ERF T
TOP F
ZTR 30                  		/trial depth
STA 'stations_hypoinverse.dat'		/input station file
LET 5 2 0                               /Net Sta Chn Max 5 2
TYP Read in crustal model(s):
CRH 1 'vel_model_P.crh'			/read crust model for Vp 
CRH 2 'vel_model_S.crh' 		/read crust model for Vs
SAL 1 2
PHS 'hypoInput.arc'			/input phase file

FIL					/automatically set phase format from file
ARC 'hypoOut.arc'			/output archive file
PRT 'prtOut.prt'			/output print file
SUM 'catOut.sum'        		/output location summary
*RDM T
CAR 1
*LST 2
LOC					/locate the earthquake
STO
