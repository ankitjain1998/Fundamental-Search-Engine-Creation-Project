#CS 121/INF 141 - INFORMATION RETRIVAL
#NAME: ANKIT JAIN
#ID: 96065117
#UCINETID: JAINA2

#IMPORTED MODULES
import sys
import re
from collections import defaultdict

#PROJECT 1 - TEXT PROCESSING

#PART A - WORD FREQUENCIES

'''
Program is meant to find the number of occurences
of different alphanumeric combinations within a
given text file

Run-time Complexity of each method is explained in the doc string
comment of the method, and the run-time complexity of the
entire program is explained at the end of the program
under the 'if __name__ == '__main__':' section
'''

class WordFrequencies:
    '''
    Class initialized by the file name
    which is a string and with initial
    result set as None
    '''
    def __init__(self, file_name:str):
        '''
        Run-time Complexity = O(1)
        Method runs in constant time relative to size of input as
        simply the class is initialized
        '''
        self.name = file_name #File Name string is initialized
        self.result = None #Initialize result to None

    def generate_result(self):
        '''
        Method is responsible for generating
        the result and changing it from None if the file exists
        and generate a dictionary on the basis of the occurences
        of different words and alphanumeric characters in the file
        entered
        
        Run-time complexity of method = O(N)
        Method runs in linear time relative to size of input
        as it simply makes use of one dimensional for loops
        
        To improve run time complexity, I had to worsen space complexity by adding
        another list to store all words. I had initially combined the two for loops for
        simplicity but that increased run-time complexity to O(N^2) and hence I decided
        to bring in the list to reduce run-time complexity
        '''
        try: #To catch for errors
            self.result = defaultdict(int) #Change result from None to a dictionary to be returned
            #Compiler using regular expressions to differentiate all expressions other than alphanumeric characters
            re_compiler = re.compile('[^A-Za-z0-9]+')
            combined_lst = [] #Combined lst to obtain all alphanumeric combinations
            for line in open(self.name): #To see individual lines in the file
                u_line = re_compiler.sub(' ',line)#Using the above compiler to substitute all non alphanumeric characters with blank spaces
                combined_lst.extend(u_line.split())#To split the above line into spaces and then add to the list 
            for word in combined_lst: #To iterate through each alphanumeric combination which is present in the list
                self.result[word.lower()] += 1 #To iterate the word count by 1 each time there is an occurence from the list
            self.result = dict(self.result) #Convert from default dict to regular dictionary object
        except: #To allow errors to pass
            pass

    def get_result(self):
        '''
        Method is obtaining the result
        upon calling the generate_result
        method

        Run-time Complexity of method = O(N)
        Method runs in linear time relative to size of input
        as it calls the the generate_result() method
        '''
        self.generate_result() #Calls generate_result method
        return self.result #Returns updated result
    
    def output(self):
        '''
        Method prints the desired output

        Run-time Complexity = O(NlogN)
        Method runs in Quasilinear time relative to size of input
        due to the use of sorted method for lists in the function
        '''
        self.generate_result()#Calls generate_result method
        if self.result != None: #Only prints Output if the result is not None
            for word in sorted(self.result.keys(),key = lambda word:(-self.result[word],word)): #Sorts the list of words by frequency and alphabet
                print('{}\t{}'.format(word,self.result[word])) #Prints in desired format
             
if __name__ == '__main__':
    '''
    Run-Time Complexity of Part A = O(NLogN)
    
    The overall run-time complexity of this
    program is O(NLogN) as the output()
    method is called
    '''
    WordFrequencies(sys.argv[0]).output()

       
            
            
        
