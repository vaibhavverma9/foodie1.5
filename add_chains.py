import argparse as ap
import os, pickle
import pandas as pd
import openpyxl
import xlrd

from xlrd import open_workbook, XLRDError
from openpyxl import Workbook

## Check to make sure file is an excel (.xlsx) file
def test_book(filename):
	try:
		open_workbook(filename)
	except XLRDError:
		return False
	else:
		return True

## Adds together ratings of every chain in the folder
def compile_ratings(folder):
	## Set path to right folder in /csvfiles/chains
	script_dir = os.path.abspath(os.path.join(__file__ ,"../.."))
	dir_path = script_dir + "/csvfiles/chains/" + folder

	## Create empty dataframe
	df = pd.DataFrame(columns=['Item', 'Rating'])
	
	## Walk through each file
	for root, dirs, files in os.walk(dir_path, topdown=True):
		for name in files:
			xl_file = os.path.join(root, name)
			## Check to make sure it is an excel file
			if(test_book(xl_file) == True):
				## Append to dataframe by reading from Excel file
				df = df.append(pd.read_excel(xl_file, sheet_name='Ratings', index_col=None), ignore_index=True)
	print('Compiled Dataframe...')
	print(df)
	return df



def add_compiled_ratings(folder):
	script_dir = os.path.abspath(os.path.join(__file__ ,"../.."))
	dir_path = script_dir + "/csvfiles/chains/" + folder
	
	## Retrieve combined ratings from compile_ratings() function
	## Convert dataframe into a list, so it can later be added to each Ratings sheet
	df = compile_ratings(folder).values.tolist()

	## Walk through each file 
	for root, dirs, files in os.walk(dir_path, topdown=True):
		for name in files:
			file_name = os.path.join(root, name)
			## Check to make sure it is an excel file
			if(test_book(file_name) == True):
				book = openpyxl.load_workbook(file_name)
				sheet = book['Ratings']

				## Clear existing Ratings sheet of all values 
				for row in sheet['A2:C1000']:
					for cell in row:
						cell.value = ''
				
				## Add new compiled Ratings to existing Ratings sheet
				for i in range(2, len(df)+2):
					for j in range(1, 3):
						sheet.cell(row=i, column=j).value = df[i-2][j-1]
				book.save(file_name)
			


if __name__ == '__main__':
	parser = ap.ArgumentParser()
	parser.add_argument('-f', '--f_suffix', help='Filename Suffix', default='11.27.18')
	args = vars(parser.parse_args())
	f_suffix = args['f_suffix']
	add_compiled_ratings(f_suffix)

