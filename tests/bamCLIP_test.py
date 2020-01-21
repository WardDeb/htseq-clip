import os
import unittest
from argparse import Namespace

from clip.bamCLIP import bamCLIP

class TestBamCLIP(unittest.TestCase):
    '''
    Unit tests for module BamCLIP
    '''

    '''
    test01.bam is supposed to raise a ValueError in all cases
    '''
    def test01_extract_SS(self):
        optionsSS = Namespace(input = "tests/testBamCLIP/test01.bam", output = "tests/UnitTestOutput/testBamCLIP/test01_SS.bed", 
            minAlignmentQuality = 10, minReadLength = 0, maxReadLength = 0, maxReadIntervalLength=10000,
            primary = False,mate=1,choice='s' )
        bamS = bamCLIP(optionsSS)
        with self.assertRaises(ValueError):
            bamS.extract_StartSites()

    def test01_extract_MS(self):
        optionsSS = Namespace(input = "tests/testBamCLIP/test01.bam", output = "tests/UnitTestOutput/testBamCLIP/test01_SS.bed", 
            minAlignmentQuality = 10, minReadLength = 0, maxReadLength = 0, maxReadIntervalLength=10000,
            primary = False,mate=1,choice='m' )
        bamS = bamCLIP(optionsSS)
        with self.assertRaises(ValueError):
            bamS.extract_MiddleSites()
    
    def test01_extract_ES(self):
        optionsSS = Namespace(input = "tests/testBamCLIP/test01.bam", output = "tests/UnitTestOutput/testBamCLIP/test01_SS.bed", 
            minAlignmentQuality = 10, minReadLength = 0, maxReadLength = 0, maxReadIntervalLength=10000,
            primary = False,mate=1,choice='e' )
        bamS = bamCLIP(optionsSS)
        with self.assertRaises(ValueError):
            bamS.extract_EndSites()
    
    '''
    test03.bam is supposed to finish successfully in all cases
    '''
    def test03_extract_SS(self):
        
        optionsSS = Namespace(input = "tests/testBamCLIP/test03.bam", output = "tests/UnitTestOutput/testBamCLIP/test03_SS.bed", 
            minAlignmentQuality = 10, minReadLength = 0, maxReadLength = 0, maxReadIntervalLength=10000,
            primary = False,mate=1,choice='s' )
         
        bamS = bamCLIP(optionsSS)
        bamS.extract_StartSites()
                
        v1 = []
        v2 = []
        with open("tests/UnitTestOutput/testBamCLIP/test03_SS.bed", "r") as outputTest:
            for line in outputTest:
                v1.append(line)
        
        with open("tests/testBamCLIP/checktestBamCLIP/test03_SS_check.bed", "r") as checkTest:
            for line in checkTest:
                v2.append(line)
             
        self.assertEqual(v1, v2)

    
    def test03_extract_MS(self):
        
        optionsMS = Namespace(input = "tests/testBamCLIP/test03.bam", output = "tests/UnitTestOutput/testBamCLIP/test03_MS.bed", 
            minAlignmentQuality = 10, minReadLength = 0, maxReadLength = 0, maxReadIntervalLength=10000,
            primary = False,mate=1,choice='m' )
         
        bamM = bamCLIP(optionsMS)
        bamM.extract_MiddleSites()
                
        v1 = []
        v2 = []
        with open("tests/UnitTestOutput/testBamCLIP/test03_MS.bed", "r") as outputTest:
            for line in outputTest:
                v1.append(line)
        
        with open("tests/testBamCLIP/checktestBamCLIP/test03_MS_check.bed", "r") as checkTest:
            for line in checkTest:
                v2.append(line)
             
        self.assertEqual(v1, v2)
    
    def test03_extract_ES(self):
        
        optionsES = Namespace(input = "tests/testBamCLIP/test03.bam", output = "tests/UnitTestOutput/testBamCLIP/test03_ES.bed", 
            minAlignmentQuality = 10, minReadLength = 0, maxReadLength = 0, maxReadIntervalLength=10000,
            primary = False,mate=1,choice='e' )
         
        bamE = bamCLIP(optionsES)
        bamE.extract_EndSites()
                
        v1 = []
        v2 = []
        with open("tests/UnitTestOutput/testBamCLIP/test03_ES.bed", "r") as outputTest:
            for line in outputTest:
                v1.append(line)
        
        with open("tests/testBamCLIP/checktestBamCLIP/test03_ES_check.bed", "r") as checkTest:
            for line in checkTest:
                v2.append(line)
             
        self.assertEqual(v1, v2)
    
    def test03_extract_DEL(self):

        optionsD = Namespace(input = "tests/testBamCLIP/test03.bam", output = "tests/UnitTestOutput/testBamCLIP/test03_DEL.bed", 
            minAlignmentQuality = 10, minReadLength = 0, maxReadLength = 0, maxReadIntervalLength=10000,
            primary = False,mate=1,choice='e' )
        bamD = bamCLIP(optionsD)
        bamD.extract_DeletionSites()
                
        v1 = []
        v2 = []
        with open("tests/UnitTestOutput/testBamCLIP/test03_DEL.bed", "r") as outputTest:
            for line in outputTest:
                v1.append(line)
        
        with open("tests/testBamCLIP/checktestBamCLIP/test03_DEL_check.bed", "r") as checkTest:
            for line in checkTest:
                v2.append(line)
             
        self.assertEqual(v1, v2)
    
    def test03_extract_INS(self):

        optionsI = Namespace(input = "tests/testBamCLIP/test03.bam", output = "tests/UnitTestOutput/testBamCLIP/test03_INS.bed", 
            minAlignmentQuality = 10, minReadLength = 0, maxReadLength = 0, maxReadIntervalLength=10000,
            primary = False,mate=1,choice='e' )
        bamI= bamCLIP(optionsI)
        bamI.extract_InsertionSites()
                
        v1 = []
        v2 = []
        with open("tests/UnitTestOutput/testBamCLIP/test03_INS.bed", "r") as outputTest:
            for line in outputTest:
                v1.append(line)
        
        with open("tests/testBamCLIP/checktestBamCLIP/test03_INS_check.bed", "r") as checkTest:
            for line in checkTest:
                v2.append(line)
             
        self.assertEqual(v1, v2)

if __name__ == '__main__':
    unittest.main()
