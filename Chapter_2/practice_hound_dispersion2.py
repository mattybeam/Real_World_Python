#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 18 20:58:00 2021

@author: mbeamer
"""

import nltk
from nltk.corpus import stopwords
import matplotlib.pyplot as plt


def main():
    # Load text file.
    tokens = text_to_tokens('hound.txt')
    
    tokens = nltk.Text(tokens) # NLTK wrapper for automatic text analysis.
    
    dispersion = tokens.dispersion_plot(['Holmes',
                                     'Watson',
                                     'Mortimer',
                                     'Henry',
                                     'Barrymore',                                                                        
                                     'Stapleton',
                                     'Selden',
                                     'hound'])

def text_to_tokens(filename):
    """Read a text file and tokenize it."""
    with open(filename, encoding='utf-8', errors='ignore') as infile:
        corpus = infile.read()
    return nltk.word_tokenize(corpus)
    
if __name__ == '__main__':
    main()
    

