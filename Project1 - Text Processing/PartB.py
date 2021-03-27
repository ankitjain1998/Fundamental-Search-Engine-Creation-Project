#CS 121/INF 141 - INFORMATION RETRIVAL
#NAME: ANKIT JAIN
#ID: 96065117
#UCINETID: JAINA2

#IMPORTED MODULES
import sys
from PartA import WordFrequencies

#PROJECT 1 - TEXT PROCESSING

#PART B - INTERSECTION OF TWO FILES

'''
Program is meant to find the number of common
alphanumeric combinations between two text files

Run-time Complexity of each method is explained in the doc string
comment of the method, and the run-time complexity of the
entire program is explained at the end of the program
under the 'if __name__ == '__main__':' section
'''

class FileIntersection:
    '''
    Class is initialized by the two file names
    which are strings and two WordFrequencies object
    using the two files are created
    '''
    def __init__(self,file_1:str,file_2:str):
        '''
        Run-time Complexity = O(N)
        Method runs in linear time relative to size of input as
        simply the class is initialized by calling the get_result()
        method from Part A
        '''
        self.file_1_result = WordFrequencies(file_1).get_result() #WordFrequencies Method to get dictionary for the first file
        self.file_2_result = WordFrequencies(file_2).get_result() #WordFrequencies Method to get dictionary for the second file

    def intersection_output(self):
        '''
        Method converts the two list of keys from the initialized dictionaries
        which are converted to sets and then the 'and' command is used to obtain
        the intersection between the two files

        Run-time Complexity = O(N)
        Method runs in linear time relative to size of input as
        there is a conversion of list of keys from list to set
        and then the add method was made use of 
        '''
        try: #To catch for errors
            intersection_list = set(self.file_1_result.keys()) & set(self.file_2_result.keys())
            #List of keys of dictionaries are converted to sets and then 'and' method is used to obtain the intersection 
            print(len(intersection_list)) #Length of the set obtained from intersection gives the result which is printed
        except: #To allow errors to pass
            pass

if __name__ == '__main__':
    '''
    Run-Time Complexity of Part A = O(N)
    
    The overall run-time complexity of this
    program is O(N) as the intersection_output()
    method is called
    '''
    FileIntersection(sys.argv[1],sys.argv[2]).intersection_output()
