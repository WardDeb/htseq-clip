
# --------------------------------------------------
# gffCLIP class
# Authors: Thomas Schwarzl, schwarzl@embl.de
#          Nadia Ashraf, nadia.ashraf@embl.de
#          Marko Fritz, marko.fritz@embl.de
# Modified by: Sudeep Sahadevan, sudeep.sahadevan@embl.de
# EMBL Heidelberg
# --------------------------------------------------

from builtins import str
from builtins import object

import gzip
import logging
import sys
from collections import OrderedDict, defaultdict

import HTSeq
from Gene import Gene
from GeneLengthSummary import GeneLengthSummary
from GeneRegion import GeneRegion
from GTxFeature import GTxFeature
from output import Output

"""
The class gffCLIP reads in genomic location,
flattens the annotation and outputs the 
results as Bed file
"""

class GeneInfo(object):

    '''
    class for all gene feature related info, such as gene, intron, exon...
    '''

    def __init__(self, id, geneDefinitions = ["tRNA", "gene", "tRNAscan", "tRNA_gene"]):
        self.id  = id
        self._featList = []
        self._geneDefinitions = set(geneDefinitions)
        self._typeMap = {} # feature type to list index map
    
    def add_feature(self,f):
        '''
        add gene feature
        Arguments:
         f: HTSeq.GenomicFeature object
        '''
        self._featList.append(f)
        try:
            self._typeMap[f.type].append(len(self._featList)-1)
        except KeyError:
            self._typeMap[f.type]=[len(self._featList)-1]

    @property
    def gene(self):
        '''
        Get gene object
        @TODO: convert sys.stderr calls to logging.warning
        '''
        geneDef = list(self._geneDefinitions & set(self._typeMap.keys()))
        if len(geneDef)==0:
            sys.stderr.write('{}: No gene definitions found!...Skipping\n'.format(self.id))
            return None
        elif len(geneDef)>1:
            sys.stderr.write('{}: Multiple gene definitions found!...Skipping\n'.format(self.id))
            return None
        else:
            geneInd = self._typeMap[geneDef[0]]
            if len(geneInd)>1:
                if self._checkGeneFeature(geneInd):
                    sys.stderr.write('{}: Found multiple attributes for the same gene co-ordinates, using one at random\n'.format(self.id))
                    return self._featList[geneInd[0]]
                else:
                    sys.stderr.write('{}: Multiple gene features found!...Skipping\n'.format(self.id))
                    return None
            else:
                return self._featList[geneInd[0]]
    
    def _checkGeneFeature(self,geneInd):
        '''
        Helper function, if multiple gene features are found, 
        return true all the co-oridnates are same
        '''
        start_pos,end_pos,strand = set(),set(),set()
        for gi in geneInd:
            start_pos.add(self._featList[gi].iv.start)
            end_pos.add(self._featList[gi].iv.end)
            strand.add(self._featList[gi].iv.strand)
        if len(start_pos)==1 and len(end_pos)==1 and len(strand)==1:
            return True
        else:
            return False
    
    @property
    def features(self):
        '''
        Return all stored features
        '''
        return self._featList

class gffCLIP(object):
    # @TODO: probably remove these
    # features = {}
    # inputFile  = ''
    # gtfFile    = ''
    # outputFile = ''
    # geneTypeAttrib = ''
    # geneNameAttrib = ''
    # geneIdAttrib = ''
    windowSize = 50
    windowStep = 20
    detailed   = True
    splitExons = True
    processGeneOnlyInformation = True
    geneDefinitions = ["tRNA", "gene", "tRNAscan", "tRNA_gene"] 
    
    logger    = logging.getLogger(__name__) 

    """
    gffCLIP: Init
    """
    def __init__(self, options):
        if hasattr(options, 'gff'):
            self.gtfFile = options.gff
            self.logger.debug("set gff")

        if hasattr(options, 'windowSize'):
            self.windowSize = options.windowSize

        if hasattr(options, 'windowStep'):
            self.windowStep = options.windowStep

        if hasattr(options, 'type'):
            self.geneType = options.type

        if hasattr(options,'name'):
            self.geneName = options.name

        if hasattr(options,'splitExons'):
            self.splitExons =  options.splitExons
        
        if hasattr(options,'id'):
            self.geneId = options.id
        
        #@TODO: do these options complicate things
        # if hasattr(options,'geneOnly'):
        #     self.processGeneOnlyInformation = options.geneOnly
        # if hasattr(options, 'detailed'):
        #     self.detailed = options.detailed
        self.fOutput = Output(options.output)
        self._geneMap = None # for unsorted GFF files
        self.summary = None # GeneSummary

    def process(self,unsorted = False):
        """
        This method goes through the gtf file and determines 
        the positions of exons and introns.

        Attention. At the moment, this is done iteratively. 
        All gene info of a gene has to be provided in 
        consecutive lines. An exception will be raised if
        the annotation is out of order.
        """
        self.logger.debug("Reading from '%s'" % self.gtfFile)
        
        # initializing gff reader
        gtf = HTSeq.GFF_Reader(self.gtfFile, end_included=True)
        
        
        # initializing gene length summary, which records total length of
        # chromosomes, gene types etc
        self.summary = GeneLengthSummary()
        self.summary.splitExons = self.splitExons
        
        # initializing field identifiers
        GTxFeature.geneTypeAttrib = self.geneType
        GTxFeature.geneNameAttrib = self.geneName
        GTxFeature.geneIdAttrib = self.geneId
        if unsorted:
            self._process_unsorted(gtf)
        else:
            self._process_sorted(gtf)
        self._write_summary()
        self.fOutput.close()
    
    def _process_sorted(self,gtf):
        '''
        Helper function, process chromosome co-ordinate sorted GFF files
        '''
        gene = None
        for f in gtf:
            # initialize a new feature object
            feature = GTxFeature(f)
            # if this feature is a gene (which is specified as certain ids in the gff field)
            if feature.isGene():
                # if new gene info is found, annotation the gene info
                self.processGene(gene)
                
                # then create a new Gene object
                gene = Gene(feature,self.splitExons)
                gene.splitExons = self.splitExons
                gene.processGeneOnlyInformation = self.processGeneOnlyInformation
                
            # else add the gene region info  
            else:
                # if there was no gene definition provided, raise an exception
                if gene is None:
                    raise Exception("GTF/GFF file provides gene feature info before the actual gene definition.")
                # else add the gene info to the genes
                else:
                    gene.add(feature)
        
        # annotation the last gene
        self.processGene(gene)
    
    def _process_unsorted(self,gtf):
        '''
        Helper function, process unsorted GFF files
        Arguments:
         gtf: HTSeq.GFFReader object
        '''
        self._geneMap = {}
        for f in gtf:
            if self.geneId not in f.attr:
                continue
            try:
                self._geneMap[f.attr[self.geneId]].add_feature(f)
            except KeyError:
                self._geneMap[f.attr[self.geneId]] = GeneInfo(f.attr[self.geneId])
                self._geneMap[f.attr[self.geneId]].add_feature(f)
        # sanity check
        if len(self._geneMap)==0:
            raise ValueError('Cannot parse gene features from {}! Please check this input file'.format(self.gtfFile))
        # for each feature in geneMap 
        for _, geneObj in self._geneMap.items():
            _gene = geneObj.gene
            if _gene is None:
                continue
            gene = Gene(GTxFeature(_gene))
            gene.splitExons = self.splitExons
            gene.processGeneOnlyInformation = self.processGeneOnlyInformation
            for f in geneObj.features:
                if f.type in set(self.geneDefinitions):
                    continue
                gene.add(GTxFeature(f))
            self.processGene(gene)

    """
    Processing gene
    """
    def processGene(self, gene):
        self.logger.debug("annotation gene function")
        if gene is not None:
            #gene.toBed()
            # write the gene as bed entries to output
            for be in gene.toBedDetailed():
                self.fOutput.write(be+'\n')
            # store the nucleotide length of the regions in the summary
            self.summary.add(gene)
    
    def _write_summary(self):
        '''
        Helper function: Write chromosome and gene type summary to the end of bed file
        '''
        for chrom,length in self.summary.chromosomes.items():
            self.fOutput.write('track chr {} {}\n'.format(chrom,length))
        for gtype,length in self.summary.genetypes.items():
            self.fOutput.write('track type {} {}\n'.format(gtype,length))

    """
    This functions calculates the sliding window positions
    """
    def slidingWindow(self,inputFile):
        if inputFile.endswith('.gz'):
            almnt_file  =  gzip.open(inputFile,'r')
        else:
            almnt_file = open(inputFile,'r')
        windowidMap = {}

        for line in almnt_file:
            if line.startswith("track"):
                continue
            line = line.split('\n')
            line = line[0].split('\t')

            name = line[3].split('@')
            featureNumber, _ = name[4].split('/')
            # this will creaet duplicate windowCount if there are multiple genes annotated to the same chromosomal locations
            # this needs to be reimplemented
            # if currentName == None or currentName != name[0]:
            #     currentName = name[0]
            #     windowCount = 1
            try:
                windowCount = windowidMap[name[0]]
                windowCount +=1
            except KeyError:
                windowidMap[name[0]] = 1
                windowCount = 1
            strand = line[5]

            start = int(line[1])
            end = int(line[2])

            pos1 = start
            pos2 = start + self.windowSize

            #if length shorter than given windowsize then the whole feature is one window
            #else split the current feature up by the given options
            # @TODO: add gene name, window id, UID to last
            
            if pos2 >= end:
                UID = "{0}:{1}{2:0>4}W{3:0>5}".format(name[0],name[3],featureNumber,windowCount)
                seq = (line[0], str(start), str(end), "@".join(name[:5]+[UID,str(windowCount)]), line[4], strand)
                self.fOutput.write(str('\t').join(seq) + "\n")
                windowCount+=1
            else:
                while pos2 < end:
                    UID = "{0}:{1}{2:0>4}W{3:0>5}".format(name[0],name[3],featureNumber,windowCount)
                    seq = (line[0], str(pos1), str(pos2), "@".join(name[:5]+[UID,str(windowCount)]), line[4], strand)
                    self.fOutput.write(str('\t').join(seq) + "\n")
                    pos1 = pos1 + self.windowStep
                    pos2 = pos2 + self.windowStep
                    windowCount+=1
                    if pos2 > end:
                        pos2 = end
                        UID = "{0}:{1}{2:0>4}W{3:0>5}".format(name[0],name[3],featureNumber,windowCount)
                        seq = (line[0], str(pos1), str(pos2), "@".join(name[:5]+[UID,str(windowCount)]), line[4], strand)
                        self.fOutput.write(str('\t').join(seq) + "\n")
                        windowCount+=1
            windowidMap[name[0]] = windowCount
        almnt_file.close()
        self.fOutput.close()
