#/usr/bin/python26
# -*- coding: utf-8 -*-

#Local Moran's I manually with python
# https://pypi.python.org/pypi/py_amoeba/0.2.3
# numpy
# scipy
# pysal
# rtree
# osgeo
# django
# progressbar


#cd to 
#or http://pysal.readthedocs.org/en/latest/users/tutorials/autocorrelation.html
import datetime
import os
import sys
import optparse
import csv
import urllib
import math
import xml.dom.minidom as dom
import re
import math
import shapefile as shp
DEBUG = "on"
statelist = ['MO'];
# ADMINLEVEL_2
#solrServer = "lcms-match2.pr.lhr.dtco.s.nokia.com"
solrServer = "tchilcmsas04b.hq.navteq.com"
# e.g., pdallcmsmmkr01 or lcms-match1.pr.lhr.dtco.s.nokia.com OR lcms-match2.pr.lhr.dtco.s.nokia.com OR tchilcmsas04b.hq.navteq.com:8080
solrPort = "8080"
# e.g., 8080 

#other urls like http://tchilcmsas04b.hq.navteq.com:8080/matchMakerSolr/main/select/?q=*%3A*&version=2.2&start=0&rows=10&wt=csv
#all fields queryable are //LCMS_CATEGORY_ID,PREFIX,UNPARSED_STREET_NUMBER,POI_LANGUAGE_CD,SUPPLIER,UPDATE_DATE,DISPLAY_LONG,PHONE,timestamp,CHAIN_FAMILY_NAME,STREET_TYPE,STREET_LANGUAGE,CHAIN_ID,DELETED,DISPLAY_LAT,POI_NAME_NGRAM,LATLON,FULL_STREET_BASE_NAME,HOUSE_NUMBER,PRIMARY_NAME,SUFFIX,PLACE_ID,PREFERRED_CONTACT,SUPPLIER_POIID,CONTACT,CHAIN_NAME,POI_ID,LOCATION_ID,POI_NAME,ADMINLEVEL_3,ADMINLEVEL_2,ADMINLEVEL_5,ADMINLEVEL_4,STREET_BASE_NAME,CHAIN_FAMILY_ID,ROUTING_LAT,POSTAL_CODE,ROUTING_LONG,ISO_COUNTRY_CD
#100-1000-0001,,"8920 Wornall Rd, Kansas City, MO 64114, United States",en,COREPOIXML,1396472888556,-94.595871,"816-4447675,+18164447675",2014-04-02T21:22:07.969Z,,RD,en,,false,38.9658318,The Stack BBQ,38.9658318,-94.595871,WORNALL RD,8920,The Stack BBQ,,8409yutx-55c3d670588b4f648047bcbc9bed6074,816-4447675,34768460,816-4447675,,8409yutxSS-b48cf8faa8c104d0e559ded8a30a983b4de75071~0002,NT_mEGSYCAZAspZSBa0O9PQ6D_8920,The Stack BBQ,Jackson,MO,,Kansas City,WORNALL,,38.9659996,64114,-94.5954819,USA
def do_debug(self, texttoprint):
	if DEBUG == "on":
		print(texttoprint)
		
		
def loop_Solr(stateAbbrv):
	""" This will perform the Solr query and save the file. """
	solr_output = open("outputcsv.csv", 'a')
	print("The results will be saved to this folder in output.csv")
	solr_output.write("PLACE_ID,SUPPLIER,LRO_BUILTUP,PRIMARY_NAME,LRO_DISPLAY_LONG,LRO_DISPLAY_LAT,POI_NAME,POSTAL_CODE,ISO_COUNTRY_CD\n")
	initialURL="http://"+solrServer+":"+str(solrPort)+"/matchMakerSolr/main/select/?fl=PLACE_ID,SUPPLIER,LRO_BUILTUP,PRIMARY_NAME,LRO_DISPLAY_LONG,LRO_DISPLAY_LAT,POI_NAME,POSTAL_CODE,ISO_COUNTRY_CD&q=*%3A*&fq=ADMINLEVEL_2%3A"+str(stateAbbrv)+"&rows=10"
	print(initialURL)
	# open the url, timeout after 3 seconds 
	resp = urllib2.urlopen(initialURL)
	# read the response
	xmlresp = dom.parseString(resp.read())
	# get the xml output once just to get the total number of results found
	results = xmlresp.getElementsByTagName('result')[0]
	thetotal = int((results.attributes["numFound"]).value)
	loopno = 0
	if thetotal == 0:
		print("skipping")
	else:
		# if there are more than 5000 results returned, the number of loops is generated by div by 500 then add 2
		if thetotal > 5000:
			loopno = ( thetotal / 5000 ) + 2
			#loopno = 2
		else:
			#if the total is less than 5000, no need to loop
			loopno = 2
		startctr = 0
		while startctr < loopno:
			startno = (startctr * 5000) + 1
			print ("Now looping Solr")
			# loop the solr results and get 5000 each and save to csv separator
			############################################ MODIFY ######################################################
			loopURL = "http://"+solrServer+":"+str(solrPort)+"/matchMakerSolr/main/select/?fl=POI_ID,SUPPLIER,LRO_BUILTUP,PRIMARY_NAME,LRO_DISPLAY_LONG,LRO_DISPLAY_LAT,POI_NAME,POSTAL_CODE,ISO_COUNTRY_CD&q=*%3A*&fq=ADMINLEVEL_2%3A"+str(stateAbbrv)+"&rows=5000&start="+str(startno)+"&wt=csv&csv.header=false&csv.separator=|"
			resp = urllib2.urlopen(loopURL)
			solr_output.write(resp.read())
			startctr += 1
	solr_output.close()
	return solr_output

def text_to_pts(textfile, outputshp):
	""" Create a point shapefile from a pipe-delimited text file containing your data and return the points shapefile """
	# TODO read from the textfile to get the headers
	# for now just use set values
	#0POI_ID,1SUPPLIER,LRO_BUILTUP,3PRIMARY_NAME,4LRO_DISPLAY_LONG,5LRO_DISPLAY_LAT,6POI_NAME,POSTAL_CODE,ISO_COUNTRY_CD
	xList,yList,idList,nameList,supList=[],[],[],[],[]
	#read data from csv file and store in lists
	with open(textfile, 'r') as csvfile:
		r = csv.reader(csvfile, delimiter=',')
		ctr = 0
		for row in r:
			print(row)
			if ctr > 0: #skip header
				xList.append(float(row[4]))
				yList.append(float(row[5]))
				uidList.append(ctr)
				idList.append(row[0])
				nameList.append(row[6])
				supList.append(row[1])
				ctr += 1
	#Set up shapefile writer and create empty fields
	w = shp.Writer(shp.POINT)
	w.autoBalance = 1 #ensures gemoetry and attributes match
	w.field('X','F',10,8)
	w.field('Y','F',10,8)
	w.field('UID','C',10)
	w.field('PoiID','C',50)
	w.field('Name','C',100)
	w.field('Supplier','C',50)
	#loop through the data and write the shapefile
	for j,k in enumerate(xList):
		w.point(k,yList[j]) #write the geometry
		print(w.point(k,yList[j])
		w.record(k,yList[j],uidList[j], idList[j], nameList[j], supList[j]) #write the attributes
	w.save(outputshp)
	return outputshp


def get_bbox(shpfile):
	""" get a bounding box for a shapefile """
	sf = shapefile.Reader(shpfile)
	allshps = sf.shapeRecords()
	bbox = allshps[0].shape.bbox
	do_debug("original bounding box")
	do_debug(bbox)
	return bbox

def create_grid(shpfile, outputgrid):
	""" this creates a grid shapefile """
	bbox = get_bbox(shpfile)
	minx = bbox[0]
	miny = bbox[1]
	maxx = bbox[2]
	maxy = bbox[3]
	division = float(0.016000)
	# so if we have a bbox, we want to create a bbox every .016 we want to get the number of values 
	dx = (abs(maxx - minx)/division)
	nx = int(math.ceil(abs(maxx - minx)/division))
	ny = int(math.ceil(abs(maxy - miny)/division))
	w = shapefile.Writer(shapefile.POLYGON)
	w.autoBalance = 1
	w.field("ID")
	id=0
	for i in range(ny):
		for j in range(nx):
			id+=1
			vertices = []
			parts = []
			vertices.append([min(minx+dx*j,maxx),max(maxy-dy*i,miny)])
			vertices.append([min(minx+dx*(j+1),maxx),max(maxy-dy*i,miny)])
			vertices.append([min(minx+dx*(j+1),maxx),max(maxy-dy*(i+1),miny)])
			vertices.append([min(minx+dx*j,maxx),max(maxy-dy*(i+1),miny)])
			parts.append(vertices)
			w.poly(parts)
			w.record(id,"null","null")
	w.save(outputgrid)
	return outputgrid
	
def iterate_grid(inputshp, gridshp, intergrid):
	""" iterate over a grid shapefile and check to see if the points from the input shp are in the grid parts and create a new grid shapefile """
	# read the input files
	pt = shapefile.Reader(inputshp)
	sf = shapefile.Reader(gridshp)
	# create the copy of the grid
	w = shapefile.Writer(sf.shapeType)
	w.fields = list(sf.fields)
	w.field("POIID")
	w.field("LENGTH")
	# make shape objects
	gridShp = sf.shapeRecords()
	pointShp = pt.shapeRecords()
	#gridShp[0].shape.points[0] --> [-87.12, 100.23]
	fields = sf.fields[1:]
	ptfields = pt.fields[1:]
	# output is like fields[0]  --> ['OBJECTID', 'N', 9, 0]
	#fields_name = [field[0] for field in fields]
	#pt_fields_names = [ptfield[0] for ptfield in ptfields]
	#fields_names[0] --> 'OBJECTID'
	attributes = sf.records()
	ptatts = pt.records()
	# the poi id from the input shp is in field 3, and the destination grid shp for the poiids is field 1
	#attributes[0] --> [1, '000100', '1.533', 'Park']
	allGridShapes = sf.shapes()
	# len (shapes[0].parts) -- > 10
	# len(shapes) -- > 2584
	# firstpart=sf.shape(0)
	# firstpart.points = -- > all vertices for the first record
	ctr = 0
	for shapepart in allGridShapes:
		polyVert = shapepart.points
		# this is the poly part
		ptctr = 0
		poiList = []
		for coordPairs in pointShp:
			[[x,y]] = coordPairs.shape.points
			poiId = ptatts[ptctr][3]
			inChk = point_in_poly(x,y,polyVert)
			if inChk == "IN":
				poiList.append(poiId)
			ptctr += 1
		attributes[ctr].append(poiList, len(poiList))
		w.records.append(attributes[ctr])
		ctr += 1
	w._shapes.extend(sf.shapes())
	w.save(intergrid)
	
	
def point_in_poly(x,y,poly):
   # check if point is a vertex
   if (x,y) in poly: return "IN"

   # check if point is on a boundary
   for i in range(len(poly)):
      p1 = None
      p2 = None
      if i==0:
         p1 = poly[0]
         p2 = poly[1]
      else:
         p1 = poly[i-1]
         p2 = poly[i]
      if p1[1] == p2[1] and p1[1] == y and x > min(p1[0], p2[0]) and x < max(p1[0], p2[0]):
         return "IN"
      
   n = len(poly)
   inside = False

   p1x,p1y = poly[0]
   for i in range(n+1):
      p2x,p2y = poly[i % n]
      if y > min(p1y,p2y):
         if y <= max(p1y,p2y):
            if x <= max(p1x,p2x):
               if p1y != p2y:
                  xints = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
               if p1x == p2x or x <= xints:
                  inside = not inside
      p1x,p1y = p2x,p2y

   if inside: return "IN"
   else: return "OUT"


def verts_bbox(verts):
    xs = [v[0] for v in verts]
    ys = [v[1] for v in verts]
    return (min(xs), max(xs), min(ys), max(ys))
			
#def identify_neighbors():

#def add_match_to_array(value):

	

#Iterate through all the quadrats and find all the other quadrats that fit within that neighbor bounding box 
#and for each 
# combine all quadrats into one new shp
#iterate over each point in the new shp
# for each point, find the 
#calculate the (difference from the mean for each neighbor and multiply that by the weight of the neighbor) and sum the products, 
##could I do the distance weighted kNN instead?? 
#
#Then, multiply the sum by the variance ratio (the difference from the mean for the original feature’s attribute value divided by the variance [the variance is calculated by getting the average of the squared differences. The squared differences are found by subtracting the mean value for each value and then squaring the result.])and add that to the map/array/struct/dict[ { [X1-1,Y1-1,X2-1,Y2-1] : 3 , [placeid1,placeid2,placeid3], Mi },

#for item in statelist:
#textfile = loop_Solr(item)
text_to_pts("pts.csv", "outputshp1")
create_grid("outputshp1", "outputshp2")
iterate_grid("outputshp1", "outputshp2", "outputshp3")
