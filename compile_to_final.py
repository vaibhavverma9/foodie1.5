import argparse as ap
import os, pickle
import pandas as pd


# Reads info from file 
def read_info(restaurant_tag):
	script_dir = os.path.abspath(os.path.join(__file__ ,"../.."))
	fname = script_dir + "/output_info/" + restaurant_tag + ".txt"
	with open(fname, 'rb') as f:
		info = pickle.load(f)
	return info

def generate_final(restaurant_tag):
	# set file paths to data inputs
	print("Setting file paths to inputs.")
	script_dir = os.path.abspath(os.path.join(__file__ ,"../.."))
	results_file_path = script_dir + "/csvfiles/sentences/labeled-rated/" + restaurant_tag + "-labeled-rated.xlsx"
	items_file_path = script_dir + "/csvfiles/items/" + restaurant_tag + "-items.xlsx"
	
	# set file paths to data outputs 
	print("Setting file paths to outputs.")
	file_path = script_dir + "/csvfiles/final/" + restaurant_tag + "-final.xlsx"
	writer = pd.ExcelWriter(file_path, engine='xlsxwriter')

	# save to info sheet
	# try:
	d1 = read_info(restaurant_tag)
	print(d1)
	df1 = pd.DataFrame(d1)
	df1 = df1[['Name', 'Address', 'City', 'State', 'Zipcode', 'Description', 'DollarSign', 'Latitude', 'Longitude', 'Neighborhood', 'Categories', 'FoursquareID', 'YelpID']]
	df1.to_excel(writer, index=False, sheet_name='Info')
	# except:
	# 	d1 = {'Name' : [], 'SourceRestaurantCode' : [], 'Address' : [], 'City' : [], 'State' : [], 'Zipcode' : [], 'DollarSign' : [], 'Latitude' : [], 'Longitude' : [], 'Neighborhood' : [], 'Categories' : [], 'FoursquareID' : [], 'ChainID' : []}
	# 	df1 = pd.DataFrame(d1)
	# 	df1.to_excel(writer, index=False, sheet_name='Info')

	# save to items sheet 
	print("Saving Items.")
	df2 = pd.read_excel(items_file_path)
	df2.to_excel(writer, index=False, sheet_name='Items')

	# save to ratings sheet 
	print("Saving Ratings.")
	df3 = pd.read_excel(results_file_path)
	df3 = df3[['Item', 'Rating', 'Sentence']]
	df3 = df3.sort_values(by=['Item'])
	df3.to_excel(writer, index=False, sheet_name='Ratings')

	print("Compiled.")
	writer.close()

if __name__ == '__main__':
	parser = ap.ArgumentParser()
	parser.add_argument('-t', '--restaurant_tag', help='Restaurant tag', default='girl-and-the-goat-chicago')

	args = vars(parser.parse_args())
	restaurant_tag = args['restaurant_tag']
	generate_final(restaurant_tag)
