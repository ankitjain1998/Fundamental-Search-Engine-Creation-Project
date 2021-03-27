#PROJECT 3: COMPLETE SEARCH ENGINE

#NAME: ANKIT JAIN, OM RAMNIK MUNGRA
#ID: 96065117, 72248203

#GRAPHICAL USER INTERFACE MODEL
#IMPORTED MODULES
from tkinter import *
from omank import *

def search_engine_gui():
	#Function is similar[almost same] to the get_result function 
	#to be used upon when button is clicked to return results
	query_token_object = TokenDictionary(search_query.get())
	result = processing(query_token_object.get_token_dictionary())
	rank = 0
	result_string = "Number of Results: {}\n".format(len(result))
	result_string += 'Top 20 Results\n'
	for result_key in result[:20]:
		rank += 1
		result_string += 'Link {}: {}\n'.format(rank,result_key['url'])
	result_arena.delete('1.0',END)
	result_arena.insert(END,result_string)
    

if __name__ == '__main__':
	connect('load_everything10', host = 'localhost', port = 27017) #To establish connection

	#To create the window
	gui_window = Tk()
	gui_window.geometry("750x500")
	gui_window.title("OmAnk Search Engine")

	header = Label(gui_window, text = 'OmAnk Search Engine', font = ('Helvetica', 30),fg = 'red')
	header.grid(column = 0, row = 0) #For the title/label of the engine

	header = Label(gui_window, text = 'Enter Query', font = ('Helvetica', 20),fg = 'dark blue')
	header.grid(column = 0, row = 1) #For the query question/prompt for your answer

	search_query = Entry(gui_window, width = 20)
	search_query.focus()
	search_query.grid(column = 0, row = 2) #Allowing search query entry option for user

	button = Button(gui_window, text = 'Click for Results', font = ('Helvetica', 15), command = search_engine_gui)
	button.grid(column = 0, row = 3) #Button be clicked to obtain results and call the above search_engine_gui function

	scroll = Scrollbar(gui_window)
	scroll.grid(column = 0,row = 5, sticky = "W") #For Scroll bar
	result_arena = Text(gui_window, height = 100, width = 100, yscrollcommand = scroll.set) #For the arena where results are displayed
	result_arena.grid(column = 0,row = 5) 
	scroll.config(command = result_arena.yview) 

	gui_window.mainloop() #To execute GUI until termination 



